import unittest

from benchmarks.collect_benchmark_scores import (
    BENCHMARKS, OFFICIAL_SOURCE_SPECS, build_payload,
    official_seed_results_for_source, parse_markdown_source_scores,
)
from benchmarks.discover_official_model_cards import OFFICIAL_VENDORS, discover_vendor_models
from scripts.build_docs_site import build_site_payload


def source(source_id):
    return next(s for s in OFFICIAL_SOURCE_SPECS if s["id"] == source_id)


def grok_fixture():
    # The live page uses divs, not a HTML table; include distractor values outside it.
    tokens = ["CursorBench 4.0", "99%", "Model Improvements", "Grok 4.7", "xHigh",
              "Grok 4.6", "High", "GPT-5.6 Sol", "Max", "Fable 5.1", "Max"]
    for label, cells in [
        ("CursorBench 4.0", ["46.3%", "40.4%", "41.7%", "51.8%"]),
        ("DeepSWE v1.1", ["71.0%*", "65.2%", "72.7%", "70.0%"]),
        ("EEBench", ["64.0%", "53.0%", "39.4%", "56.4%"]),
        ("AA Briefcase v1.1", ["1,657", "1,546", "1,487", "1,678"]),
        ("Terminal-Bench 4.0", ["38.0%", "20.3%", "37.3%", "57.9%"]),
        ("Harvey Legal Agent Benchmark", ["19.6%", "15.8%", "2.5%", "6.7%"]),
        ("HealthBench Professional", ["56.7%", "48.5%", "60.5%", "62.1%"]),
    ]:
        tokens.extend([label, *cells])
    tokens.extend(["* high effort", "GDPval", "Elo score", "1735", "Fable 5.1", "(max)",
                   "1695", "Grok 4.7", "(xhigh)", "Safety & Cybersecurity"])
    return "".join(f"<div>{t}</div>" for t in tokens)


class September22ReleaseTests(unittest.TestCase):
    def test_grok_live_layout_preserves_footnote_and_elo(self):
        rows = parse_markdown_source_scores(grok_fixture(), source("spacexai-grok-4-7-release"))
        self.assertEqual(len(rows), 8)
        by_key = {r["benchmarkId"]: r for r in rows}
        self.assertEqual(by_key["deepswe-v1-1"]["model"], "Grok 4.7 (high)")
        self.assertEqual(by_key["deepswe-v1-1"]["effort"], "high")
        self.assertEqual(by_key["terminal-bench-4"]["value"], 38)
        self.assertEqual(by_key["cursorbench-4"]["value"], 46.3)
        self.assertEqual(by_key["aa-briefcase-v1-1-elo"]["unit"], "Elo")
        self.assertEqual(by_key["gdpval-grok-4-7-elo"]["value"], 1695)
        self.assertFalse(by_key["gdpval-grok-4-7-elo"]["evidenceEligible"])

    def test_changed_grok_configuration_requires_review(self):
        for old, new in [("xHigh", "High"), ("71.0%*", "71.0%"), ("38.0%", "38.0%*"), ("* high effort", "* medium effort")]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                parse_markdown_source_scores(grok_fixture().replace(old, new), source("spacexai-grok-4-7-release"))

    def test_mimo_table_versions_and_corrected_cybergym_are_separate(self):
        text = """| Benchmark | MiMo-V2.6 Pro | MiMo-V2.6 Flash | MiMo-V2.5 Pro |
| --- | --- | --- | --- |
| Terminal Bench 4.0 | 34.9 | 28.8 | 1.5 |
| Terminal Bench 2.1 | 89.9 | 87.6 | 65.2 |
| CyberGym | 94.0 | 95.1 | 40.0 |
| GDPval-AA 2.1 | 1673 | - | 1107 |
| MiMo VisualCoding | 72.3 | 71.5 | - |
"""
        pro = parse_markdown_source_scores(text, source("xiaomi-mimo-v2-6-pro-card"))
        flash = parse_markdown_source_scores(text, source("xiaomi-mimo-v2-6-flash-card"))
        self.assertEqual(len(pro), 5)
        self.assertEqual(len(flash), 4)
        self.assertEqual({r["benchmarkId"]: r["value"] for r in pro}["terminal-bench-4"], 34.9)
        cyber = next(r for r in pro if r["benchmarkId"].startswith("cybergym"))
        self.assertEqual(cyber["benchmarkId"], "cybergym-mimo-corrected")
        self.assertFalse(cyber["evidenceEligible"])
        self.assertTrue(all(r["model"] == "MiMo-V2.6-Pro" for r in pro))

    def test_site_binds_exact_models_without_filling_aa_or_copying_siblings(self):
        ids = {"xiaomi-mimo-v2-6-pro-card", "xiaomi-mimo-v2-6-flash-card", "spacexai-grok-4-7-release"}
        seeded = build_payload({}, "fixture")
        external = {"sources": [s for s in seeded["sources"] if s["id"] in ids],
                    "benchmarks": seeded["benchmarks"],
                    "results": [r for r in seeded["results"] if r["sourceId"] in ids]}
        rows = [{"model": name, "slug": slug, "SciCode": "50"} for name, slug in [
            ("MiMo-V2.6-Pro", "mimo-v2-6-pro"), ("MiMo-V2.5-Pro", "mimo-v2-5-pro"),
            ("Grok 4.7 (xhigh)", "grok-4-7"), ("Grok 4.7 (high)", "grok-4-7-high"),
            ("Grok 4.7 (low)", "grok-4-7-low"), ("Grok 4.6 (xhigh)", "grok-4-6-xhigh"),
        ]]
        models = {m["slug"]: m for m in build_site_payload(rows, external, {})["models"]}
        self.assertEqual(len(models["mimo-v2-6-pro"]["externalBenchmarks"]), 17)
        self.assertEqual(len(models["mimo-v2-6-flash"]["externalBenchmarks"]), 16)
        self.assertTrue(models["mimo-v2-6-flash"]["externalOnly"])
        self.assertEqual(len(models["grok-4-7"]["externalBenchmarks"]), 7)
        self.assertEqual(len(models["grok-4-7-high"]["externalBenchmarks"]), 1)
        self.assertEqual(models["grok-4-7-high"]["scores"]["benchmark:deepswe-v1-1"], 71)
        self.assertIsNone(models["grok-4-7"]["scores"]["benchmark:deepswe-v1-1"])
        for slug in ["mimo-v2-5-pro", "grok-4-7-low", "grok-4-6-xhigh"]:
            self.assertEqual(models[slug]["externalBenchmarks"], [])
        for m in models.values():
            self.assertIsNone(m["scores"]["Terminal-Bench v4.0"])

    def test_xiaomi_discovery_owns_release_and_excludes_derivatives(self):
        vendor = next(v for v in OFFICIAL_VENDORS if v.id == "xiaomi")
        names = ["XiaomiMiMo/MiMo-V2.6-Pro-RL", "XiaomiMiMo/MiMo-V2.6-Flash-RL",
                 "XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B", "XiaomiMiMo/MiMo-V2.6-Pro-GGUF",
                 "other/MiMo-V2.6-Pro-RL"]
        payload = [{"id": n, "sha": "abc", "siblings": [{"rfilename": "README.md"}]} for n in names]
        rows = discover_vendor_models(vendor, fetcher=lambda *_: payload)
        self.assertEqual({r["modelId"] for r in rows}, set(names[:2]))

    def test_source_registry_has_unique_ids_and_known_benchmarks(self):
        keys = [b["id"] for b in BENCHMARKS]
        self.assertEqual(len(keys), len(set(keys)))
        for spec in OFFICIAL_SOURCE_SPECS:
            if spec["id"] in {"xiaomi-mimo-v2-6-pro-card", "xiaomi-mimo-v2-6-flash-card", "spacexai-grok-4-7-release"}:
                for row in official_seed_results_for_source(spec):
                    self.assertIn(row["benchmarkId"], keys)
