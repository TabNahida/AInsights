import unittest

from benchmarks.validate_official_sources import (
    EXPLICIT_HF_RAW_SOURCES,
    OFFICIAL_HF_SOURCE_ORGS,
    OFFICIAL_HF_SOURCE_MODELS,
    PRIMARY_VENDOR_PAGE_SOURCE_IDS,
    PRIMARY_VENDOR_SOURCE_RAW_URLS,
    PRIMARY_VENDOR_SOURCE_URLS,
    VENDOR_MANIFEST_SOURCES,
    validate_payload,
    validate_vendor_manifest,
)


def _valid_payload():
    sources = [
        {
            "id": source_id,
            "url": url,
            "rawUrl": PRIMARY_VENDOR_SOURCE_RAW_URLS[source_id],
        }
        for source_id, url in PRIMARY_VENDOR_SOURCE_URLS.items()
    ]
    for source_id, organization in OFFICIAL_HF_SOURCE_ORGS.items():
        model_name = OFFICIAL_HF_SOURCE_MODELS[source_id]
        _raw_org, _raw_model, raw_kind = EXPLICIT_HF_RAW_SOURCES[source_id]
        base = f"https://huggingface.co/{organization}/{model_name}"
        sources.append(
            {
                "id": source_id,
                "url": base,
                "rawUrl": (
                    base
                    if raw_kind == "page"
                    else f"{base}/raw/main/README.md"
                ),
            }
        )
    return {"sources": sources}


def _valid_vendor_manifest():
    return {
        "version": 1,
        "sources": [
            {"key": key, "vendor": vendor, "kind": kind, "url": url}
            for key, (vendor, kind, url) in VENDOR_MANIFEST_SOURCES.items()
        ],
        "pages": [],
    }


class OfficialSourcePolicyTests(unittest.TestCase):
    def test_accepts_verified_dynamic_hugging_face_org(self):
        payload = _valid_payload()
        payload["sources"].append(
            {
                "id": "hf-zai-org-glm-6-card",
                "url": "https://huggingface.co/zai-org/GLM-6",
                "rawUrl": "https://huggingface.co/zai-org/GLM-6/raw/abc/README.md",
                "organization": "zai-org",
                "modelId": "zai-org/GLM-6",
                "revision": "abc",
                "autoDiscovered": True,
            }
        )
        manifest = {
            "models": [
                {
                    "organization": "zai-org",
                    "modelId": "zai-org/GLM-6",
                    "url": "https://huggingface.co/zai-org/GLM-6",
                    "rawUrl": "https://huggingface.co/zai-org/GLM-6/raw/abc/README.md",
                    "revision": "abc",
                }
            ]
        }

        validate_payload(payload, manifest)

    def test_rejects_spoofed_dynamic_org(self):
        payload = _valid_payload()
        payload["sources"].append(
            {
                "id": "hf-spoofed-glm-6-card",
                "url": "https://huggingface.co/random-user/GLM-6",
                "rawUrl": "https://huggingface.co/random-user/GLM-6/raw/main/README.md",
                "organization": "random-user",
                "modelId": "random-user/GLM-6",
                "revision": "main",
                "autoDiscovered": True,
            }
        )

        with self.assertRaisesRegex(ValueError, "unverified org"):
            validate_payload(payload)

    def test_rejects_non_vendor_primary_url_for_vendor_page_source(self):
        payload = _valid_payload()
        source = next(
            source
            for source in payload["sources"]
            if source["id"] == "qwen-qwen3-8-max-release"
        )
        source["url"] = "https://huggingface.co/Qwen/Qwen3.8-Max"

        with self.assertRaisesRegex(ValueError, "vendor page source"):
            validate_payload(payload)

    def test_rejects_vendor_example_placeholder(self):
        payload = _valid_payload()
        source = next(
            source
            for source in payload["sources"]
            if source["id"] == "zai-glm-5-3-release"
        )
        source["url"] = "https://vendor.example/zai-glm-5-3-release"

        with self.assertRaisesRegex(ValueError, "vendor page source"):
            validate_payload(payload)

    def test_rejects_spoofed_explicit_hf_raw_url(self):
        payload = _valid_payload()
        source = next(
            source
            for source in payload["sources"]
            if source["id"] == "kimi-k3-release"
        )
        source["rawUrl"] = "https://huggingface.co/random-user/Kimi-K3/raw/main/README.md"

        with self.assertRaisesRegex(ValueError, "raw source"):
            validate_payload(payload)

    def test_accepts_strict_official_vendor_manifest(self):
        manifest = _valid_vendor_manifest()
        manifest["pages"].append(
            {
                "vendor": "qwen",
                "name": "Qwen3.8-Max",
                "displayName": "Qwen3.8 Max",
                "url": "https://qwen.ai/blog?id=qwen3.8",
                "rawUrl": (
                    "https://qwen.ai/api/v2/article/retrieval?"
                    "language=en-US&path=qwen3.8&type=qwen_ai"
                ),
                "aliases": ["Qwen3.8 Max", "Qwen3.8-Max", "qwen3-8-max"],
                "sourceKey": "qwen-article-json",
                "sourceMetadata": {"path": "qwen3.8"},
            }
        )

        validate_vendor_manifest(manifest)

    def test_rejects_spoofed_vendor_manifest_page(self):
        manifest = _valid_vendor_manifest()
        manifest["pages"].append(
            {
                "vendor": "glm",
                "name": "GLM-6",
                "displayName": "GLM 6",
                "url": "https://docs.z.ai.evil.example/guides/llm/glm-6",
                "rawUrl": "https://docs.z.ai.evil.example/guides/llm/glm-6.md",
                "aliases": ["GLM 6", "GLM-6", "glm-6"],
                "sourceKey": "glm-docs-llms",
            }
        )

        with self.assertRaisesRegex(ValueError, "official URL policy"):
            validate_vendor_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
