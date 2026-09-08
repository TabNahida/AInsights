import gzip
import hashlib
import io
import json
import unittest
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ArtificialAnalysis import scrape_artificial_analysis as scraper
from ArtificialAnalysis.scrape_artificial_analysis import (
    DataManifest,
    build_raw_scores_rows,
    download_creator_logos,
    extract_data_manifests,
    extract_default_data,
    fetch_manifest_payload,
    fetch_rich_manifest_model_rows,
    merge_manifest_rows_with_prior,
    normalize_manifest_model_row,
    validate_raw_scores_csv,
    write_raw_scores_csv,
    write_raw_scores_csv_atomically,
)


def _model_rows(count, *, prefix="model", score_offset=0):
    return [
        {
            "short_name": f"Model {index}",
            "slug": f"{prefix}-{index}",
            "intelligence_index": score_offset + index + 1,
        }
        for index in range(count)
    ]


def _write_valid_snapshot(path: Path, *, count=None, prefix="model", score_offset=0):
    count = scraper.MINIMUM_MODEL_ROWS if count is None else count
    write_raw_scores_csv(
        build_raw_scores_rows(
            _model_rows(count, prefix=prefix, score_offset=score_offset)
        ),
        path,
    )


def _flight_html(text: str) -> str:
    return f"<script>self.__next_f.push([1,{json.dumps(text)}])</script>"


def _encrypted_manifest(payload, key: bytes) -> bytes:
    compressed = gzip.compress(json.dumps(payload).encode("utf-8"))
    iv = hashlib.sha256(key).digest()[:12]
    return AESGCM(key).encrypt(iv, compressed, None)


def _scicode_refresh_fixture():
    prior_models = _model_rows(50)
    for index, row in enumerate(prior_models):
        row["scicode"] = 0.8 - index / 100
    sources = [
        {
            "slug": row["slug"],
            "shortName": row["short_name"],
            "creator": {"name": "Lab"},
            "contextWindowTokens": 128000,
            "intelligenceIndex": row["intelligence_index"],
            "scicode": None if index < 40 else row["scicode"],
        }
        for index, row in enumerate(prior_models)
    ]
    sources[-1]["scicode"] = 0  # A published zero is a score, not a withdrawal.
    sources.append({**sources[-2], "slug": "new-model", "shortName": "New Model", "scicode": 0.99})
    return sources, build_raw_scores_rows(prior_models)


class ArtificialAnalysisScraperTests(unittest.TestCase):
    def test_extract_default_data_from_next_flight_chunks(self):
        html = (
            '<script>self.__next_f.push([1,"prefix {\\"defaultData\\":[{'
            '\\"short_name\\":\\"Model A\\",\\"slug\\":\\"model-a\\",'
            '\\"intelligence_index\\":42.5}"])</script>'
            '<script>self.__next_f.push([1,"],\\"other\\":true}} suffix"])</script>'
        )

        rows = extract_default_data(html)

        self.assertEqual(rows, [{"short_name": "Model A", "slug": "model-a", "intelligence_index": 42.5}])

    def test_extracts_all_encrypted_data_manifest_references(self):
        key_a = "11" * 32
        key_b = "22" * 32
        html = _flight_html(
            "prefix "
            + json.dumps({"manifest": {"path": "/data/one.txt", "key": key_a}})
            + " middle "
            + json.dumps({"manifest": {"path": "/data/two.txt", "key": key_b}})
        )

        manifests = extract_data_manifests(html)

        self.assertEqual(
            manifests,
            [
                DataManifest(path="/data/one.txt", key=key_a),
                DataManifest(path="/data/two.txt", key=key_b),
            ],
        )

    def test_fetch_manifest_decrypts_aes_gcm_gzip_json(self):
        key = bytes(range(32))
        payload = {"models": [{"slug": "model-a"}], "fallbackPriceByModelSlug": {}}
        ciphertext = _encrypted_manifest(payload, key)

        class FakeResponse:
            headers = {"Content-Length": str(len(ciphertext))}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, limit=-1):
                return ciphertext if limit < 0 else ciphertext[:limit]

        manifest = DataManifest(path="/data/models.txt", key=key.hex())
        with patch.object(scraper, "urlopen", return_value=FakeResponse()) as mocked:
            result = fetch_manifest_payload(
                manifest,
                "https://artificialanalysis.ai/models",
                timeout=5,
            )

        self.assertEqual(result, payload)
        self.assertEqual(mocked.call_args.args[0].full_url, "https://artificialanalysis.ai/data/models.txt")

    def test_manifest_rejects_cross_origin_url_and_invalid_key(self):
        valid_key = "11" * 32
        with self.assertRaisesRegex(ValueError, "same artificialanalysis.ai origin"):
            fetch_manifest_payload(
                DataManifest(path="https://example.com/data/models.txt", key=valid_key),
                "https://artificialanalysis.ai/models",
            )
        with self.assertRaisesRegex(ValueError, "64 hexadecimal"):
            fetch_manifest_payload(
                DataManifest(path="/data/models.txt", key="not-a-key"),
                "https://artificialanalysis.ai/models",
            )

    def test_manifest_enforces_ciphertext_size_limit(self):
        key = bytes(range(32))
        ciphertext = _encrypted_manifest({"models": []}, key)

        class FakeResponse:
            headers = {"Content-Length": str(len(ciphertext))}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        with (
            patch.object(scraper, "MAX_MANIFEST_CIPHERTEXT_BYTES", len(ciphertext) - 1),
            patch.object(scraper, "urlopen", return_value=FakeResponse()),
            self.assertRaisesRegex(ValueError, "exceeds the allowed size limit"),
        ):
            fetch_manifest_payload(
                DataManifest(path="/data/models.txt", key=key.hex()),
                "https://artificialanalysis.ai/models",
            )

    def test_rich_manifest_selection_skips_non_model_payload(self):
        key_a = "11" * 32
        key_b = "22" * 32
        html = _flight_html(
            json.dumps({"manifest": {"path": "/data/one.txt", "key": key_a}})
            + json.dumps({"manifest": {"path": "/data/two.txt", "key": key_b}})
        )
        rich_rows = [
            {
                "slug": f"model-{index}",
                "shortName": f"Model {index}",
                "creator": {"name": "Lab"},
                "contextWindowTokens": 1000,
            }
            for index in range(scraper.MINIMUM_MODEL_ROWS)
        ]

        with patch.object(
            scraper,
            "fetch_manifest_payload",
            side_effect=[{"notModels": []}, {"models": rich_rows}],
        ):
            result = fetch_rich_manifest_model_rows(
                html,
                "https://artificialanalysis.ai/models",
            )

        self.assertEqual(result, rich_rows)

    def test_normalizes_rich_manifest_scores_without_double_scaling(self):
        source = {
            "slug": "qwen3-8-27b",
            "name": "Qwen3.8 27B",
            "shortName": "Qwen3.8 27B",
            "isReasoning": True,
            "releaseDate": "2026-08-14",
            "modelWeightsSourceUrl": "https://huggingface.co/Qwen/Qwen3.8-27B",
            "contextWindowTokens": 256000,
            "openSourceCategorization": "permissive",
            "creator": {
                "name": "Alibaba",
                "slug": "alibaba",
                "color": "#ff7018",
                "logo": "/img/logos/alibaba_small.svg",
            },
            "intelligenceIndex": 52.0246606497206,
            "agenticIndex": 50.877412371134,
            "intelligenceIndexCost": {
                "total": 1042.4279677945385,
                "input": 363.86623579453845,
                "output": 678.561732,
                "reasoning": 564.53049,
                "answer": 114.031242,
            },
            "gdpvalNormalized": 0.522955,
            "tauBanking": 0.480412371134021,
            "omniscienceBreakdown": {
                "accuracy": 0.15583333333333332,
                "hallucinationRate": 0.30286278381046394,
            },
            "inputModalityText": True,
            "outputModalityText": True,
        }

        output = build_raw_scores_rows([normalize_manifest_model_row(source)])[0]

        self.assertEqual(output["model_key"], "Qwen3.8 27B [R]")
        self.assertEqual(output["model_url"], "https://huggingface.co/Qwen/Qwen3.8-27B")
        self.assertEqual(output["context_window_tokens"], 256000.0)
        self.assertEqual(output["open_source_categorization"], "permissive")
        self.assertEqual(output["AA Intelligence Index"], 52.0247)
        self.assertEqual(output["AA Agentic Index"], 50.8774)
        self.assertEqual(output["AA Intelligence Index Cost (USD)"], 1042.428)
        self.assertEqual(output["AA Intelligence Index Input Cost (USD)"], 363.8662)
        self.assertEqual(output["AA Intelligence Index Output Cost (USD)"], 678.5617)
        self.assertEqual(output["AA Intelligence Index Reasoning Cost (USD)"], 564.5305)
        self.assertEqual(output["AA Intelligence Index Answer Cost (USD)"], 114.0312)
        self.assertEqual(output["GDPval-AA"], 52.2955)
        self.assertEqual(output["τ³-Banking"], 48.0412)
        self.assertEqual(output["AA-Omniscience Accuracy"], 15.5833)
        self.assertEqual(output["AA-Omniscience Non-Hallucination Rate"], 69.7137)

    def test_manifest_merge_preserves_columns_absent_from_new_schema(self):
        source = {
            "slug": "model-0",
            "shortName": "Renamed Model",
            "isReasoning": False,
            "intelligenceIndex": 42,
            "price1mInputTokens": None,
            "gdpvalNormalized": 0.0,
            "gpqa": None,
        }
        candidate = build_raw_scores_rows([normalize_manifest_model_row(source)])
        prior = {column: "" for column in scraper.raw_scores_fieldnames()}
        prior.update(
            {
                "slug": "model-0",
                "model": "Old Model",
                "model_key": "Old Model",
                "model_url": "/models/model-0",
                "context_window_tokens": "128000",
                "Input Price Per 1M Tokens (USD)": "1.25",
                "AA Coding Index": "31",
                "AA Intelligence Index": "40",
                "GDPval-AA v2": "40",
                "GDPval-AA v2_rank": "1",
                "GDPval-AA": "-13.064",
                "GPQA Diamond": "90",
                "GPQA Diamond_rank": "1",
            }
        )

        merged = merge_manifest_rows_with_prior(candidate, [source], [prior])[0]

        self.assertEqual(merged["model"], "Renamed Model")
        self.assertEqual(merged["AA Intelligence Index"], 42.0)
        self.assertEqual(merged["model_url"], "/models/model-0")
        self.assertEqual(merged["context_window_tokens"], "128000")
        self.assertEqual(merged["Input Price Per 1M Tokens (USD)"], "1.25")
        self.assertEqual(merged["AA Coding Index"], "31")
        self.assertEqual(merged["GDPval-AA v2"], "40")
        self.assertEqual(merged["GDPval-AA v2_rank"], "1")
        self.assertEqual(merged["GDPval-AA"], 0.0)
        self.assertEqual(merged["GDPval-AA_rank"], 1)
        self.assertEqual(merged["GPQA Diamond"], "")
        self.assertEqual(merged["GPQA Diamond_rank"], "")

    def test_manifest_merge_keeps_ranks_computed_from_unrounded_values(self):
        sources = [
            {
                "slug": "model-a",
                "shortName": "Model A",
                "gdpvalNormalized": 0.5000004,
            },
            {
                "slug": "model-b",
                "shortName": "Model B",
                "gdpvalNormalized": 0.5000003,
            },
        ]
        candidates = build_raw_scores_rows(
            [normalize_manifest_model_row(row) for row in sources]
        )
        priors = [
            {"slug": "model-a"},
            {"slug": "model-b"},
        ]

        merged = merge_manifest_rows_with_prior(candidates, sources, priors)

        self.assertEqual([row["GDPval-AA"] for row in merged], [50.0, 50.0])
        self.assertEqual([row["GDPval-AA_rank"] for row in merged], [1, 2])

    def test_build_raw_scores_rows_formats_scores_and_ranks(self):
        rows = [
            {
                "short_name": "Reasoning Model",
                "reasoning_model": True,
                "slug": "reasoning-model-high",
                "input_modality_text": True,
                "input_modality_image": True,
                "input_modality_speech": False,
                "input_modality_video": None,
                "output_modality_text": True,
                "output_modality_image": False,
                "output_modality_speech": False,
                "output_modality_video": False,
                "release_date": "2026-01-01",
                "model_url": "/models/reasoning-model",
                "model_creators": {
                    "name": "Lab A",
                    "slug": "lab-a",
                    "color": "#123456",
                    "logo_small_url": "/img/logos/lab-a-small.svg",
                    "logo_url": "/img/logos/lab-a.svg",
                },
                "intelligence_index": 55.5,
                "coding_index": 44.4,
                "agentic_index": 33.3,
                "cache_hit_price": 0.25,
                "price_1m_input_tokens": 1.5,
                "price_1m_output_tokens": 10,
                "intelligence_index_cost": {
                    "total_cost": 123.45,
                    "input_cost": 23.45,
                    "output_cost": 100,
                    "reasoning_cost": 75,
                    "answer_cost": 25,
                },
                "gdpval": 1500,
                "gdpval_v2": 1600,
                "terminalbench_hard": 0.5,
                "terminalbench_v2_1": 0.7,
                "tau2": 0.25,
                "tau_banking": 0.35,
                "lcr": 0.75,
                "omniscience_breakdown": {
                    "total": {
                        "accuracy": 0.8,
                        "non_hallucination_rate": 0.9,
                    }
                },
                "hle": 0.1,
                "gpqa": 0.8,
                "scicode": 0.6,
                "ifbench": 0.7,
                "critpt": 0.2,
                "apex_agents": 0.3,
                "it_bench_sre": 0.4,
                "mmmu_pro": 0.55,
                "livecodebench": 0.65,
                "aime25": 0.95,
            },
            {
                "short_name": "Plain Model",
                "reasoning_model": False,
                "gdpval": 1000,
                "gdpval_v2": 1200,
                "terminalbench_hard": 0.25,
                "terminalbench_v2_1": 0.45,
                "tau_banking": 0.15,
                "gpqa": None,
            },
        ]

        output = build_raw_scores_rows(rows)

        self.assertEqual(output[0]["model_key"], "Reasoning Model [R]")
        self.assertEqual(output[0]["model"], "Reasoning Model")
        self.assertEqual(output[0]["is_reasoning"], "true")
        self.assertEqual(output[0]["slug"], "reasoning-model-high")
        self.assertEqual(output[0]["input_modality_text"], "true")
        self.assertEqual(output[0]["input_modality_image"], "true")
        self.assertEqual(output[0]["input_modality_speech"], "false")
        self.assertEqual(output[0]["input_modality_video"], "")
        self.assertEqual(output[0]["output_modality_text"], "true")
        self.assertEqual(output[0]["output_modality_image"], "false")
        self.assertEqual(output[0]["creator"], "Lab A")
        self.assertEqual(output[0]["creator_slug"], "lab-a")
        self.assertEqual(output[0]["creator_color"], "#123456")
        self.assertEqual(output[0]["creator_logo_small_url"], "https://artificialanalysis.ai/img/logos/lab-a-small.svg")
        self.assertEqual(output[0]["release_date"], "2026-01-01")
        self.assertEqual(output[0]["AA Intelligence Index"], 55.5)
        self.assertEqual(output[0]["AA Coding Index"], 44.4)
        self.assertEqual(output[0]["AA Agentic Index"], 33.3)
        self.assertEqual(output[0]["AA Intelligence Index Cost (USD)"], 123.45)
        self.assertEqual(output[0]["AA Intelligence Index Input Cost (USD)"], 23.45)
        self.assertEqual(output[0]["AA Intelligence Index Output Cost (USD)"], 100.0)
        self.assertEqual(output[0]["AA Intelligence Index Reasoning Cost (USD)"], 75.0)
        self.assertEqual(output[0]["AA Intelligence Index Answer Cost (USD)"], 25.0)
        self.assertEqual(output[0]["Cache Hit Price Per 1M Tokens (USD)"], 0.25)
        self.assertEqual(output[0]["Input Price Per 1M Tokens (USD)"], 1.5)
        self.assertEqual(output[0]["Output Price Per 1M Tokens (USD)"], 10.0)
        self.assertEqual(output[0]["GDPval-AA v2"], 55.0)
        self.assertEqual(output[0]["Terminal-Bench v2.1"], 70.0)
        self.assertEqual(output[0]["τ³-Banking"], 35.0)
        self.assertEqual(output[0]["AA-Omniscience Accuracy"], 80.0)
        self.assertEqual(output[0]["AA-Omniscience Non-Hallucination Rate"], 90.0)
        self.assertEqual(output[0]["GPQA Diamond_rank"], 1)
        self.assertEqual(output[1]["model_key"], "Plain Model")
        self.assertEqual(output[1]["GDPval-AA v2"], 35.0)
        self.assertEqual(output[1]["GDPval-AA v2_rank"], 2)
        self.assertEqual(output[1]["GPQA Diamond_rank"], "")

    def test_build_raw_scores_rows_treats_next_undefined_sentinel_as_blank(self):
        rows = [
            {
                "short_name": "Model B",
                "slug": "model-b",
                "model_creators": {"name": "Lab B"},
                "intelligence_index_cost": "$undefined",
            }
        ]

        output = build_raw_scores_rows(rows)

        self.assertEqual(output[0]["AA Intelligence Index Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Input Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Output Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Reasoning Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Answer Cost (USD)"], "")

    def test_download_creator_logos_writes_deduped_logo_assets(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<svg></svg>"

        rows = [
            {"model_creators": {"logo_small_url": "/img/logos/kimi_small.png"}},
            {"model_creators": {"logo_small_url": "/img/logos/kimi_small.png"}},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(scraper, "urlopen", return_value=FakeResponse()) as mocked:
                count = download_creator_logos(rows, Path(tmpdir), timeout=5)

            self.assertEqual(count, 1)
            self.assertEqual(mocked.call_count, 1)
            self.assertTrue((Path(tmpdir) / "kimi_small.png").exists())

    def test_raw_scores_csv_uses_lf_line_endings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "scores.csv"

            write_raw_scores_csv([{}], output)

            content = output.read_bytes()
            self.assertIn(b"\n", content)
            self.assertNotIn(b"\r\n", content)

    def test_atomic_write_validates_and_replaces_existing_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output)
            replacement_rows = build_raw_scores_rows(
                _model_rows(scraper.MINIMUM_MODEL_ROWS, score_offset=100)
            )
            real_replace = scraper.os.replace

            with patch.object(scraper.os, "replace", wraps=real_replace) as mocked_replace:
                write_raw_scores_csv_atomically(replacement_rows, output)

            self.assertEqual(mocked_replace.call_count, 1)
            validated = validate_raw_scores_csv(output)
            self.assertEqual(float(validated[0]["AA Intelligence Index"]), 101.0)
            self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])

    def test_atomic_write_failure_preserves_existing_snapshot_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output)
            original = output.read_bytes()
            replacement_rows = build_raw_scores_rows(
                _model_rows(scraper.MINIMUM_MODEL_ROWS, score_offset=100)
            )

            with patch.object(scraper.os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    write_raw_scores_csv_atomically(replacement_rows, output)

            self.assertEqual(output.read_bytes(), original)
            self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])

    def test_raw_json_atomic_write_failure_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "raw.json"
            output.write_text('{"status":"old"}', encoding="utf-8")

            with patch.object(scraper.os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    scraper._write_text_atomically(output, '{"status":"new"}')

            self.assertEqual(output.read_text(encoding="utf-8"), '{"status":"old"}')
            self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])

    def test_atomic_write_rejects_large_row_loss_and_preserves_prior_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output, count=100)
            original = output.read_bytes()
            candidate = build_raw_scores_rows(_model_rows(75))

            with self.assertRaisesRegex(ValueError, "lost too many rows"):
                write_raw_scores_csv_atomically(candidate, output)

            self.assertEqual(output.read_bytes(), original)

    def test_large_score_loss_requires_corroboration_before_replacing_snapshot(self):
        sources, prior = _scicode_refresh_fixture()
        candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            write_raw_scores_csv(prior, output)
            original = output.read_bytes()

            with self.assertRaisesRegex(ValueError, "lost too much 'SciCode' coverage"):
                write_raw_scores_csv_atomically(candidates, output)

            self.assertEqual(output.read_bytes(), original)

    def test_corroborated_withdrawals_refresh_new_models_and_clear_scores_and_ranks(self):
        sources, prior = _scicode_refresh_fixture()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            write_raw_scores_csv(prior, output)
            with (
                patch.object(scraper, "fetch_html", return_value="page") as fetch_html,
                patch.object(scraper, "fetch_rich_manifest_model_rows", return_value=sources),
                patch.object(scraper, "extract_data_manifests", return_value=[DataManifest("/data/eval", "11" * 32)]),
                patch.object(scraper, "fetch_manifest_payload", return_value={"models": list(reversed(sources))}),
                redirect_stderr(stderr),
            ):
                result = scraper.main(["--output-dir", tmpdir, "--skip-logos"])

            self.assertEqual(result, 0)
            self.assertEqual(fetch_html.call_count, 2)
            self.assertEqual(fetch_html.call_args.args[0], "https://artificialanalysis.ai/evaluations/scicode")
            by_slug = {row["slug"]: row for row in validate_raw_scores_csv(output)}
            self.assertEqual(len(by_slug), 51)
            for index in range(40):
                self.assertEqual(by_slug[f"model-{index}"]["SciCode"], "")
                self.assertEqual(by_slug[f"model-{index}"]["SciCode_rank"], "")
            self.assertEqual(by_slug["new-model"]["SciCode"], "99.0")
            self.assertEqual(by_slug["new-model"]["SciCode_rank"], "1")
            self.assertEqual(by_slug["model-40"]["SciCode_rank"], "2")
            self.assertEqual(by_slug["model-49"]["SciCode"], "0.0")
            self.assertEqual(by_slug["model-49"]["SciCode_rank"], "11")
            self.assertIn("40 previously published scores are now null", stderr.getvalue())

    def test_withdrawal_corroboration_rejects_incomplete_or_conflicting_evaluation(self):
        for fault in ("missing model", "duplicate model", "missing key", "score conflict", "malformed score", "changed retained score"):
            with self.subTest(fault=fault):
                sources, prior = _scicode_refresh_fixture()
                candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
                secondary = [dict(row) for row in sources]
                if fault == "missing model":
                    secondary.pop()
                elif fault == "duplicate model":
                    secondary.append(dict(secondary[0]))
                elif fault == "missing key":
                    del secondary[0]["scicode"]
                elif fault == "score conflict":
                    secondary[0]["scicode"] = 0.8
                elif fault == "malformed score":
                    secondary[0]["scicode"] = "not scored"
                else:
                    secondary[-1]["scicode"] = 0.5

                with (
                    patch.object(scraper, "fetch_html", return_value="page"),
                    patch.object(scraper, "extract_data_manifests", return_value=[DataManifest("/data/eval", "11" * 32)]),
                    patch.object(scraper, "fetch_manifest_payload", return_value={"models": secondary}),
                    self.assertRaisesRegex(ValueError, "Could not corroborate 'SciCode'"),
                ):
                    scraper.confirm_manifest_score_removals(candidates, sources, prior)

    def test_missing_manifest_score_keys_do_not_authorize_withdrawals(self):
        sources, prior = _scicode_refresh_fixture()
        for row in sources[:40]:
            del row["scicode"]
        candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
        with patch.object(scraper, "fetch_html") as fetch_html:
            confirmed = scraper.confirm_manifest_score_removals(candidates, sources, prior)
        self.assertEqual(confirmed, {})
        fetch_html.assert_not_called()
        with self.assertRaisesRegex(ValueError, "lost too much 'SciCode' coverage"):
            scraper._validate_candidate_against_prior(candidates, prior, confirmed_score_removals=confirmed)

    def test_withdrawal_corroboration_unavailable_keeps_valid_prior_with_allow_stale(self):
        sources, prior = _scicode_refresh_fixture()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            write_raw_scores_csv(prior, output)
            original = output.read_bytes()
            stderr = io.StringIO()
            with (
                patch.object(scraper, "fetch_html", side_effect=["models page", OSError("evaluation unavailable"), "legacy page"]),
                patch.object(scraper, "fetch_rich_manifest_model_rows", return_value=sources),
                patch.object(scraper, "extract_default_data", side_effect=ValueError("no legacy rows")),
                redirect_stderr(stderr),
            ):
                result = scraper.main(["--output-dir", tmpdir, "--skip-logos", "--allow-stale"])
            self.assertEqual(result, 0)
            self.assertEqual(output.read_bytes(), original)
            self.assertIn("evaluation unavailable", stderr.getvalue())
            self.assertIn("keeping the validated prior snapshot", stderr.getvalue())

    def test_confirmed_withdrawals_do_not_weaken_remaining_score_or_other_column_guards(self):
        sources, prior = _scicode_refresh_fixture()
        candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
        confirmed = {"SciCode": {f"model-{index}" for index in range(40)}}
        for row in candidates[40:50]:
            row["SciCode"] = ""
        with self.assertRaisesRegex(ValueError, "lost too much 'SciCode' coverage"):
            scraper._validate_candidate_against_prior(candidates, prior, confirmed_score_removals=confirmed)

        candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
        for row in prior:
            row["GPQA Diamond"] = "80"
        with self.assertRaisesRegex(ValueError, "lost too much 'GPQA Diamond' coverage"):
            scraper._validate_candidate_against_prior(candidates, prior, confirmed_score_removals=confirmed)

    def test_normal_coverage_does_not_fetch_withdrawal_verification_page(self):
        sources, prior = _scicode_refresh_fixture()
        for row in sources:
            row["scicode"] = 0
        candidates = build_raw_scores_rows([normalize_manifest_model_row(row) for row in sources])
        with patch.object(scraper, "fetch_html") as fetch_html:
            self.assertEqual(scraper.confirm_manifest_score_removals(candidates, sources, prior), {})
        fetch_html.assert_not_called()

    def test_allow_stale_keeps_valid_snapshot_when_live_refresh_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output)
            original = output.read_bytes()
            stderr = io.StringIO()

            with patch.object(scraper, "fetch_html", side_effect=ValueError("payload changed")):
                with redirect_stderr(stderr):
                    result = scraper.main(
                        ["--output-dir", tmpdir, "--skip-logos", "--allow-stale"]
                    )

            self.assertEqual(result, 0)
            self.assertEqual(output.read_bytes(), original)
            self.assertIn("warning: Artificial Analysis refresh failed", stderr.getvalue())
            self.assertIn("keeping the validated prior snapshot", stderr.getvalue())

    def test_default_mode_remains_strict_when_live_refresh_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output)
            original = output.read_bytes()
            stderr = io.StringIO()

            with patch.object(scraper, "fetch_html", side_effect=ValueError("payload changed")):
                with redirect_stderr(stderr):
                    result = scraper.main(["--output-dir", tmpdir, "--skip-logos"])

            self.assertEqual(result, 1)
            self.assertEqual(output.read_bytes(), original)
            self.assertIn("error: Could not load Artificial Analysis model rows", stderr.getvalue())

    def test_allow_stale_fails_when_existing_snapshot_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            output.write_text("not,a,valid,snapshot\n", encoding="utf-8")
            stderr = io.StringIO()

            with patch.object(scraper, "fetch_html", side_effect=ValueError("payload changed")):
                with redirect_stderr(stderr):
                    result = scraper.main(
                        ["--output-dir", tmpdir, "--skip-logos", "--allow-stale"]
                    )

            self.assertEqual(result, 1)
            self.assertIn("is not a valid fallback", stderr.getvalue())

    def test_logo_failure_is_best_effort_after_successful_csv_refresh(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stderr = io.StringIO()
            rows = _model_rows(scraper.MINIMUM_MODEL_ROWS)

            with (
                patch.object(scraper, "fetch_html", return_value="page"),
                patch.object(scraper, "extract_default_data", return_value=rows),
                patch.object(
                    scraper,
                    "download_creator_logos",
                    side_effect=OSError("logo CDN unavailable"),
                ),
                redirect_stderr(stderr),
            ):
                result = scraper.main(
                    [
                        "--output-dir",
                        tmpdir,
                        "--logo-output-dir",
                        str(Path(tmpdir) / "logos"),
                    ]
                )

            self.assertEqual(result, 0)
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            self.assertEqual(len(validate_raw_scores_csv(output)), scraper.MINIMUM_MODEL_ROWS)
            self.assertIn("warning: Could not refresh provider logos", stderr.getvalue())

    def test_invalid_manifest_candidate_falls_back_to_valid_legacy_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rich_rows = [
                {
                    "slug": f"rich-{index}",
                    "shortName": f"Rich {index}",
                    "creator": {"name": "Rich Lab"},
                    "contextWindowTokens": 1000,
                }
                for index in range(scraper.MINIMUM_MODEL_ROWS)
            ]
            legacy_rows = _model_rows(
                scraper.MINIMUM_MODEL_ROWS,
                prefix="legacy",
            )

            with (
                patch.object(scraper, "fetch_html", return_value="page"),
                patch.object(
                    scraper,
                    "fetch_rich_manifest_model_rows",
                    return_value=rich_rows,
                ),
                patch.object(
                    scraper,
                    "extract_default_data",
                    return_value=legacy_rows,
                ),
            ):
                result = scraper.main(
                    ["--output-dir", tmpdir, "--skip-logos"]
                )

            self.assertEqual(result, 0)
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            validated = validate_raw_scores_csv(output)
            self.assertEqual(validated[0]["slug"], "legacy-0")

    def test_allow_stale_does_not_mask_atomic_replace_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / scraper.RAW_SCORES_FILENAME
            _write_valid_snapshot(output)
            original = output.read_bytes()
            stderr = io.StringIO()

            with (
                patch.object(scraper, "fetch_html", return_value="page"),
                patch.object(
                    scraper,
                    "fetch_rich_manifest_model_rows",
                    side_effect=ValueError("no manifest"),
                ),
                patch.object(
                    scraper,
                    "extract_default_data",
                    return_value=_model_rows(scraper.MINIMUM_MODEL_ROWS),
                ),
                patch.object(scraper.os, "replace", side_effect=OSError("disk failure")),
                redirect_stderr(stderr),
            ):
                result = scraper.main(
                    ["--output-dir", tmpdir, "--skip-logos", "--allow-stale"]
                )

            self.assertEqual(result, 1)
            self.assertEqual(output.read_bytes(), original)
            self.assertIn("error: disk failure", stderr.getvalue())
            self.assertNotIn("keeping the validated prior snapshot", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
