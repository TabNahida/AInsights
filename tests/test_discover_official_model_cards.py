import unittest
from urllib.error import URLError

from benchmarks.discover_official_model_cards import (
    OFFICIAL_VENDORS,
    discover_manifest,
    discover_vendor_models,
    vendor_api_url,
)


def _hf_model(
    model_id,
    *,
    sha="abc",
    created_at="2026-08-05T00:00:00Z",
    pipeline_tag="text-generation",
):
    return {
        "id": model_id,
        "private": False,
        "sha": sha,
        "createdAt": created_at,
        "lastModified": created_at,
        "pipeline_tag": pipeline_tag,
        "tags": ["eval-results", "license:apache-2.0", "unrelated-tag"],
        "siblings": [{"rfilename": "README.md"}, {"rfilename": "config.json"}],
    }


class OfficialModelCardDiscoveryTests(unittest.TestCase):
    def test_vendor_query_is_scoped_to_verified_organization(self):
        url = vendor_api_url(OFFICIAL_VENDORS[0])

        self.assertIn("author=Qwen", url)
        self.assertIn("sort=createdAt", url)
        self.assertIn("full=true", url)

    def test_discovery_keeps_first_party_release_and_rejects_derivatives(self):
        qwen = OFFICIAL_VENDORS[0]
        payload = [
            _hf_model("Qwen/Qwen3.8-27B"),
            _hf_model("Qwen/Qwen3.8-27B-FP8"),
            _hf_model("Qwen/Qwen3.8-27B-Base"),
            _hf_model("Qwen/Qwen3-ASR-1.7B-hf", pipeline_tag="automatic-speech-recognition"),
            _hf_model("untrusted/Qwen4-27B"),
            _hf_model("Qwen/Embedding-Next"),
        ]

        models = discover_vendor_models(
            qwen,
            fetcher=lambda _url, _timeout: payload,
        )

        self.assertEqual([model["modelId"] for model in models], ["Qwen/Qwen3.8-27B"])
        model = models[0]
        self.assertEqual(model["displayName"], "Qwen3.8 27B")
        self.assertEqual(
            model["rawUrl"],
            "https://huggingface.co/Qwen/Qwen3.8-27B/raw/abc/README.md",
        )
        self.assertIn("qwen3-8-27b", model["aliases"])
        self.assertEqual(model["tags"], ["eval-results", "license:apache-2.0"])

    def test_failed_vendor_refresh_preserves_previous_manifest_entries(self):
        glm = OFFICIAL_VENDORS[1]
        previous_model = discover_vendor_models(
            glm,
            fetcher=lambda _url, _timeout: [_hf_model("zai-org/GLM-5.3")],
        )[0]
        previous = {
            "models": [previous_model]
        }

        def fetcher(url, _timeout):
            if "author=zai-org" in url:
                raise URLError("temporary")
            if "author=Qwen" in url:
                return [_hf_model("Qwen/Qwen3.8-27B")]
            return []

        manifest, statuses = discover_manifest(previous, fetcher=fetcher)

        model_ids = {model["modelId"] for model in manifest["models"]}
        self.assertIn("zai-org/GLM-5.3", model_ids)
        self.assertIn("Qwen/Qwen3.8-27B", model_ids)
        self.assertIn("refresh blocked: URLError", statuses["glm"])
        self.assertNotIn("generatedAt", manifest)

    def test_successful_vendor_refresh_replaces_older_vendor_entries(self):
        qwen = OFFICIAL_VENDORS[0]
        previous_model = discover_vendor_models(
            qwen,
            fetcher=lambda _url, _timeout: [_hf_model("Qwen/Qwen3.7-27B")],
        )[0]

        def fetcher(url, _timeout):
            if "author=Qwen" in url:
                return [_hf_model("Qwen/Qwen3.8-27B")]
            return []

        manifest, statuses = discover_manifest(
            {"models": [previous_model]},
            fetcher=fetcher,
        )

        self.assertEqual(
            {model["modelId"] for model in manifest["models"]},
            {"Qwen/Qwen3.8-27B"},
        )
        self.assertEqual(statuses["qwen"], "refreshed; discovered 1")

    def test_failed_refresh_does_not_preserve_spoofed_previous_url(self):
        glm = OFFICIAL_VENDORS[1]
        spoofed = discover_vendor_models(
            glm,
            fetcher=lambda _url, _timeout: [_hf_model("zai-org/GLM-5.3")],
        )[0]
        spoofed["rawUrl"] = "https://evil.example/zai-org/GLM-5.3/README.md"

        def fetcher(url, _timeout):
            if "author=zai-org" in url:
                raise URLError("temporary")
            if "author=Qwen" in url:
                return [_hf_model("Qwen/Qwen3.8-27B")]
            return []

        manifest, statuses = discover_manifest(
            {"models": [spoofed]},
            fetcher=fetcher,
        )

        self.assertNotIn(
            "zai-org/GLM-5.3",
            {model["modelId"] for model in manifest["models"]},
        )
        self.assertIn("preserved 0", statuses["glm"])


if __name__ == "__main__":
    unittest.main()
