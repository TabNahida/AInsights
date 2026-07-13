"""Collect source-backed external benchmark scores for the docs site.

Some model launch pages expose benchmark tables as stable HTML text; others use
images or heavily protected pages. This script keeps the output deterministic by
falling back to curated seed rows with explicit source URLs when direct refresh
is blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from http.client import IncompleteRead
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_scores.json"
OPENAI_GPT55_URL = "https://openai.com/index/introducing-gpt-5-5/"
OPENAI_GPT56_URL = "https://openai.com/index/gpt-5-6/"
ANTHROPIC_OPUS47_URL = "https://www.anthropic.com/news/claude-opus-4-7?pubDate=20260416"
ANTHROPIC_FABLE5_URL = "https://www.anthropic.com/news/claude-fable-5-mythos-5"
GOOGLE_GEMINI31_URL = "https://deepmind.google/models/model-cards/gemini-3-1-pro/"
GOOGLE_GEMMA4_URL = "https://ai.google.dev/gemma/docs/core/model_card_4"
COHERE_NORTH_MINI_CODE_URL = "https://docs.cohere.com/docs/north-mini-code-1.0"
QWEN3_URL = "https://qwen.ai/blog?id=qwen3"
QWEN25_URL = "https://qwen.ai/blog?id=qwen2.5"
QWEN2_URL = "https://qwen.ai/blog?id=qwen2"
QWEN25_CODER_URL = "https://qwen.ai/blog?id=qwen2.5-coder"
QWEN25_MAX_URL = "https://qwen.ai/blog?id=qwen2.5-max"
QWEN36_PLUS_URL = "https://qwen.ai/blog?id=qwen3.6"
QWEN36_27B_URL = "https://qwen.ai/blog?id=qwen3.6-27b"
QWEN36_MAX_PREVIEW_URL = "https://qwen.ai/blog?id=qwen3.6-max-preview"
DEEPSEEK_V4_PRO_URL = "https://api-docs.deepseek.com/news/news260424"
KIMI_K26_URL = "https://www.kimi.com/blog/kimi-k2-6"
KIMI_K27_CODE_URL = "https://www.kimi.com/resources/kimi-k2-7-code"
KIMI_K27_CODE_HF_URL = "https://huggingface.co/moonshotai/Kimi-K2.7-Code"
KIMI_K2_THINKING_URL = "https://moonshotai.github.io/Kimi-K2/thinking"
KIMI_K25_URL = "https://www.kimi.com/blog/kimi-k2-5"
KIMI_K2_URL = "https://moonshotai.github.io/Kimi-K2/"
KIMI_K2_0905_URL = "https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905"
GLM51_URL = "https://docs.z.ai/guides/llm/glm-5.1"
GLM52_URL = "https://docs.z.ai/guides/llm/glm-5.2"
GLM52_HF_URL = "https://huggingface.co/zai-org/GLM-5.2"
GLM47_URL = "https://docs.z.ai/guides/llm/glm-4.7"
GLM46_URL = "https://docs.z.ai/guides/llm/glm-4.6"
GLM45_URL = "https://z.ai/blog/glm-4.5"
GLM45_RAW_URL = GLM45_URL
MINIMAX_M3_URL = "https://www.minimax.io/models/text/m3"
MINIMAX_M27_REPORT_URL = "https://arxiv.org/abs/2605.26494"
MINIMAX_M25_URL = "https://www.minimax.io/news/minimax-m25"
MINIMAX_M2_URL = "https://www.minimax.io/news/minimax-m2"
MINIMAX_M1_URL = "https://github.com/MiniMax-AI/MiniMax-M1"
XIAOMI_MIMO25_URL = "https://platform.xiaomimimo.com/docs/en-US/news/v2.5-open-sourced"
XAI_GROK41_FAST_URL = "https://x.ai/news/grok-4-1-fast"
NVIDIA_NEMOTRON3_NANO_URL = "https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Nano-Technical-Report.pdf"
NVIDIA_NEMOTRON3_SUPER_URL = "https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Super-Technical-Report.pdf"
NVIDIA_NEMOTRON3_ULTRA_URL = "https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf"

MODEL_ALIASES = {
    "GPT-5.6 Sol": [
        "GPT-5.6 Sol",
        "GPT-5.6 Sol (max)",
        "GPT-5.6 Sol (xhigh)",
        "GPT-5.6 Sol (high)",
        "GPT-5.6 Sol (medium)",
        "GPT-5.6 Sol (low)",
        "GPT-5.6 Sol (Non-reasoning)",
        "gpt-5-6-sol",
        "gpt-5-6-sol-xhigh",
        "gpt-5-6-sol-high",
        "gpt-5-6-sol-medium",
        "gpt-5-6-sol-low",
        "gpt-5-6-sol-non-reasoning",
    ],
    "GPT-5.6 Terra": [
        "GPT-5.6 Terra",
        "GPT-5.6 Terra (max)",
        "GPT-5.6 Terra (xhigh)",
        "GPT-5.6 Terra (high)",
        "GPT-5.6 Terra (medium)",
        "GPT-5.6 Terra (low)",
        "GPT-5.6 Terra (Non-reasoning)",
        "gpt-5-6-terra",
        "gpt-5-6-terra-xhigh",
        "gpt-5-6-terra-high",
        "gpt-5-6-terra-medium",
        "gpt-5-6-terra-low",
        "gpt-5-6-terra-non-reasoning",
    ],
    "GPT-5.6 Luna": [
        "GPT-5.6 Luna",
        "GPT-5.6 Luna (max)",
        "GPT-5.6 Luna (xhigh)",
        "GPT-5.6 Luna (high)",
        "GPT-5.6 Luna (medium)",
        "GPT-5.6 Luna (low)",
        "GPT-5.6 Luna (Non-reasoning)",
        "gpt-5-6-luna",
        "gpt-5-6-luna-xhigh",
        "gpt-5-6-luna-high",
        "gpt-5-6-luna-medium",
        "gpt-5-6-luna-low",
        "gpt-5-6-luna-non-reasoning",
    ],
    "GPT-5.5": ["GPT-5.5", "GPT-5.5 (xhigh)", "gpt-5-5", "gpt-5-5-xhigh"],
    "GPT-5.4": ["GPT-5.4", "GPT-5.4 (xhigh)", "gpt-5-4", "gpt-5-4-xhigh"],
    "GPT-5.5 Pro": ["GPT-5.5 Pro", "GPT-5.5 Pro (xhigh)", "gpt-5-5-pro"],
    "GPT-5.4 Pro": ["GPT-5.4 Pro", "GPT-5.4 Pro (xhigh)", "gpt-5-4-pro"],
    "Claude Opus 4.7": [
        "Claude Opus 4.7",
        "Claude Opus 4.7 (max)",
        "Claude Opus 4.7 (Non-reasoning, high)",
        "Claude Opus 4.7 (Adaptive Reasoning)",
        "claude-opus-4-7",
    ],
    "Claude Opus 4.6": [
        "claude-opus-4-6-adaptive",
        "Claude Opus 4.6",
        "Claude Opus 4.6 (max)",
        "Claude Opus 4.6 (high)",
        "claude-opus-4-6",
    ],
    "Claude Fable 5": [
        "Claude Fable 5",
        "Claude Fable 5 (with fallback)",
        "Claude Fable 5 (with fallback) [R]",
        "claude-fable-5",
    ],
    "Gemini 3.1 Pro": ["Gemini 3.1 Pro", "Gemini 3.1 Pro Preview", "Gemini 3.1 Pro (high)", "gemini-3-1-pro-preview", "gemini-3-1-pro-high"],
    "Gemma 4 31B": ["Gemma 4 31B", "Gemma-4-31B", "gemma-4-31b-it"],
    "Gemma 4 26B A4B": ["Gemma 4 26B A4B", "Gemma-4-26B-A4B", "gemma-4-26b-a4b-it"],
    "Gemma 4 E4B": ["Gemma 4 E4B", "Gemma-4-E4B", "gemma-4-e4b-it"],
    "Gemma 4 E2B": ["Gemma 4 E2B", "Gemma-4-E2B", "gemma-4-e2b-it"],
    "Qwen3.6 27B": ["Qwen3.6 27B", "Qwen3.6-27B", "Qwen/Qwen3.6-27B", "qwen3-6-27b"],
    "Qwen3.6 35B A3B": ["Qwen3.6 35B A3B", "Qwen3.6-35B-A3B", "qwen3-6-35b-a3b"],
    "Qwen3.6 Plus": ["Qwen3.6 Plus", "Qwen3.6-Plus", "qwen3.6-plus", "qwen3-6-plus"],
    "Qwen3.6 Max Preview": ["Qwen3.6 Max Preview", "Qwen3.6-Max-Preview", "qwen3.6-max-preview", "qwen3-6-max-preview"],
    "Qwen3 235B [R]": [
        "Qwen3 235B [R]",
        "Qwen3-235B-A22B",
        "Qwen3-235B-A22B-Instruct",
        "Qwen/Qwen3-235B-A22B",
        "qwen3-235b-a22b-instruct-reasoning",
        "qwen3-235b-a22b",
    ],
    "Qwen3 32B [R]": [
        "Qwen3 32B [R]",
        "Qwen3-32B",
        "Qwen3-32B-Instruct",
        "Qwen/Qwen3-32B",
        "qwen3-32b-instruct-reasoning",
    ],
    "Qwen3 30B [R]": [
        "Qwen3 30B [R]",
        "Qwen3-30B-A3B",
        "Qwen3-30B-A3B-Instruct",
        "Qwen/Qwen3-30B-A3B",
        "qwen3-30b-a3b-instruct-reasoning",
        "qwen3-30b-a3b",
    ],
    "Qwen3 4B [R]": [
        "Qwen3 4B [R]",
        "Qwen3-4B",
        "Qwen3-4B-Instruct",
        "Qwen/Qwen3-4B",
        "qwen3-4b-instruct-reasoning",
    ],
    "Qwen3.5 397B A17B": ["Qwen3.5 397B A17B", "Qwen3.5-397B-A17B", "qwen3-5-397b-a17b"],
    "Qwen3.5 27B": ["Qwen3.5 27B", "Qwen3.5-27B", "qwen3-5-27b"],
    "Qwen2.5 Max": ["Qwen2.5 Max", "Qwen2.5-Max", "qwen-2-5-max", "qwen-max-2025-01-25"],
    "Qwen2.5 72B": [
        "Qwen2.5 72B",
        "Qwen2.5-72B-Instruct",
        "Qwen/Qwen2.5-72B-Instruct",
        "qwen2-5-72b-instruct",
    ],
    "Qwen2.5 Instruct 32B": [
        "Qwen2.5 Instruct 32B",
        "Qwen2.5-32B-Instruct",
        "Qwen/Qwen2.5-32B-Instruct",
        "qwen2.5-32b-instruct",
        "qwen2-5-32b-instruct",
    ],
    "Qwen2.5 Turbo": ["Qwen2.5 Turbo", "Qwen-Turbo", "qwen-turbo"],
    "Qwen2.5 Coder 7B": [
        "Qwen2.5 Coder 7B",
        "Qwen2.5 Coder 7B ",
        "Qwen2.5-Coder-7B-Instruct",
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "qwen2-5-coder-7b-instruct",
    ],
    "Qwen2 72B": [
        "Qwen2 72B",
        "Qwen2-72B-Instruct",
        "Qwen/Qwen2-72B-Instruct",
        "qwen2-72b-instruct",
    ],
    "DeepSeek V4 Pro (Max)": ["DeepSeek V4 Pro (Max)", "DeepSeek-V4-Pro Max", "DS-V4-Pro Max", "deepseek-v4-pro"],
    "DeepSeek V4 Pro (High)": ["DeepSeek V4 Pro (High)", "DeepSeek-V4-Pro High", "deepseek-v4-pro-high"],
    "DeepSeek V4 Pro": ["DeepSeek V4 Pro", "DeepSeek-V4-Pro Non-Think", "deepseek-v4-pro-non-reasoning"],
    "DeepSeek V4 Flash (Max)": ["DeepSeek V4 Flash (Max)", "DeepSeek-V4-Flash Max", "deepseek-v4-flash"],
    "DeepSeek V4 Flash (High)": ["DeepSeek V4 Flash (High)", "DeepSeek-V4-Flash High", "deepseek-v4-flash-high"],
    "DeepSeek V4 Flash": ["DeepSeek V4 Flash", "DeepSeek-V4-Flash Non-Think", "deepseek-v4-flash-non-reasoning"],
    "Kimi K2.6": ["Kimi K2.6", "Kimi-K2.6", "K2.6 Thinking", "moonshotai/Kimi-K2.6", "kimi-k2-6"],
    "Kimi K2.7 Code": ["Kimi K2.7 Code", "Kimi-K2.7-Code", "moonshotai/Kimi-K2.7-Code", "kimi-k2-7-code"],
    "Kimi K2 Thinking": ["Kimi K2 Thinking", "Kimi-K2-Thinking", "K2 Thinking", "moonshotai/Kimi-K2-Thinking"],
    "Kimi K2.5": ["Kimi K2.5", "Kimi-K2.5", "moonshotai/Kimi-K2.5"],
    "Kimi K2 0905": ["Kimi K2 0905", "Kimi-K2-Instruct-0905", "moonshotai/Kimi-K2-Instruct-0905"],
    "Kimi K2": ["Kimi K2", "Kimi-K2", "Kimi-K2-Instruct"],
    "GLM-5.1": ["GLM-5.1", "GLM 5.1", "zai-org/GLM-5.1", "glm-5-1"],
    "GLM-5.2": [
        "GLM-5.2",
        "GLM 5.2",
        "GLM-5.2 (max)",
        "GLM-5.2 (max) [R]",
        "zai-org/GLM-5.2",
        "glm-5-2",
        "glm-5-2-non-reasoning",
    ],
    "GLM-5": ["GLM-5", "GLM 5", "zai-org/GLM-5"],
    "GLM-4.7": ["GLM-4.7", "GLM 4.7", "zai-org/GLM-4.7"],
    "GLM-4.6": ["GLM-4.6", "GLM 4.6", "zai-org/GLM-4.6"],
    "GLM-4.5": ["GLM-4.5", "GLM 4.5", "zai-org/GLM-4.5"],
    "GLM-4.5-Air": ["GLM-4.5-Air", "GLM 4.5 Air", "zai-org/GLM-4.5-Air"],
    "MiniMax-M3": ["MiniMax-M3", "MiniMax M3", "MiniMaxAI/MiniMax-M3", "minimax-m3"],
    "MiniMax-M2.7": ["MiniMax-M2.7", "MiniMax M2.7", "MiniMaxAI/MiniMax-M2.7", "minimax-m2-7"],
    "MiniMax-M2.5": ["MiniMax-M2.5", "MiniMax M2.5", "minimax-m2.5", "minimax-m25"],
    "MiniMax-M2.1": ["MiniMax-M2.1", "MiniMax M2.1", "minimax-m2.1"],
    "MiniMax-M2": ["MiniMax-M2", "MiniMax M2", "minimax-m2"],
    "MiniMax M1 80k": ["MiniMax M1 80k", "MiniMax-M1-80K", "MiniMax-M1-80k", "minimax-m1-80k"],
    "MiniMax M1 40k": ["MiniMax M1 40k", "MiniMax-M1-40K", "MiniMax-M1-40k", "minimax-m1-40k"],
    "MiMo-V2.5-Pro": ["MiMo-V2.5-Pro", "mimo-v2.5-pro", "XiaomiMiMo/MiMo-V2.5-Pro"],
    "North Mini Code": [
        "North Mini Code",
        "North Mini Code [R]",
        "north-mini-code",
        "north-mini-code-1-0",
    ],
    "Grok 4.1 Fast": ["Grok 4.1 Fast", "Grok-4.1-Fast", "grok-4-1-fast", "grok-4-1-fast-reasoning", "grok-4-1-fast-non-reasoning"],
    "Nemotron 3 Ultra": ["Nemotron 3 Ultra", "NVIDIA Nemotron 3 Ultra", "N-3-Ultra", "nemotron-3-ultra"],
    "NVIDIA Nemotron 3 Super [R]": [
        "NVIDIA Nemotron 3 Super [R]",
        "NVIDIA Nemotron 3 Super",
        "Nemotron 3 Super",
        "N-3-Super",
        "Nemotron-3-Super-120B-A12B",
        "nvidia-nemotron-3-super-120b-a12b",
    ],
    "NVIDIA Nemotron 3 Nano [R]": [
        "NVIDIA Nemotron 3 Nano [R]",
        "NVIDIA Nemotron 3 Nano",
        "Nemotron 3 Nano",
        "N-3-Nano",
        "Nemotron-3-Nano-30B-A3B",
        "nvidia-nemotron-3-nano-30b-a3b-reasoning",
        "nvidia-nemotron-3-nano-30b-a3b",
    ],
}

OPENAI_MODEL_COLUMNS = [
    "GPT-5.5",
    "GPT-5.4",
    "GPT-5.5 Pro",
    "GPT-5.4 Pro",
    "Claude Opus 4.7",
    "Gemini 3.1 Pro",
]

BENCHMARKS = [
    {
        "id": "swe-bench-pro",
        "label": "SWE-Bench Pro",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWE",
        "openaiLabel": "SWE-Bench Pro (Public)",
    },
    {
        "id": "terminal-bench-2",
        "label": "Terminal-Bench 2.0",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "TERM",
        "openaiLabel": "Terminal-Bench 2.0",
    },
    {
        "id": "terminal-bench",
        "label": "Terminal-Bench",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "TERM",
    },
    {
        "id": "terminal-bench-hard",
        "label": "Terminal-Bench Hard",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "TERM+",
    },
    {
        "id": "frontiercode-diamond",
        "label": "FrontierCode Diamond",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "FCD",
    },
    {
        "id": "swe-bench-verified",
        "label": "SWE-bench Verified",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWE-V",
    },
    {
        "id": "swe-bench-multilingual",
        "label": "SWE-bench Multilingual",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWE-M",
    },
    {
        "id": "multi-swe-bench",
        "label": "Multi-SWE-Bench",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "MSWE",
    },
    {
        "id": "swe-bench-openhands",
        "label": "SWE-Bench (OpenHands)",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWE-O",
    },
    {
        "id": "expert-swe-internal",
        "label": "Expert-SWE (Internal)",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "EXP",
        "openaiLabel": "Expert-SWE (Internal)",
    },
    {
        "id": "gdpval-wins-ties",
        "label": "GDPval (wins or ties)",
        "category": "Professional work",
        "unit": "%",
        "icon": "GDP",
        "openaiLabel": "GDPval (wins or ties)",
    },
    {
        "id": "gdpval-aa-elo",
        "label": "GDPval-AA Elo",
        "category": "Professional work",
        "unit": "Elo",
        "icon": "GDP",
    },
    {
        "id": "gdp-pdf",
        "label": "GDP.pdf",
        "category": "Knowledge work vision",
        "unit": "%",
        "icon": "PDF",
    },
    {
        "id": "finance-agent-v1-1",
        "label": "Finance Agent v1.1",
        "category": "Professional work",
        "unit": "%",
        "icon": "FIN",
    },
    {
        "id": "osworld-verified",
        "label": "OSWorld-Verified",
        "category": "Computer use",
        "unit": "%",
        "icon": "OS",
        "openaiLabel": "OSWorld-Verified",
    },
    {
        "id": "toolathlon",
        "label": "Toolathlon",
        "category": "Tool use",
        "unit": "%",
        "icon": "TOOL",
        "openaiLabel": "Toolathlon",
    },
    {
        "id": "automationbench",
        "label": "AutomationBench",
        "category": "Tool use",
        "unit": "%",
        "icon": "AUTO",
    },
    {
        "id": "browsecomp",
        "label": "BrowseComp",
        "category": "Tool use",
        "unit": "%",
        "icon": "WEB",
        "openaiLabel": "BrowseComp",
    },
    {
        "id": "posttrainbench",
        "label": "PostTrainBench",
        "category": "Agentic training",
        "unit": "%",
        "icon": "PTB",
    },
    {
        "id": "browsecomp-context",
        "label": "BrowseComp (Context Manage)",
        "category": "Tool use",
        "unit": "%",
        "icon": "WEB+",
    },
    {
        "id": "hle-tools",
        "label": "HLE w/ tools",
        "category": "Tool use",
        "unit": "%",
        "icon": "HLE+",
    },
    {
        "id": "mcp-atlas",
        "label": "MCP-Atlas Public",
        "category": "Tool use",
        "unit": "%",
        "icon": "MCP",
    },
    {
        "id": "frontiermath-tier-1-3",
        "label": "FrontierMath Tier 1-3",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM",
        "openaiLabel": "FrontierMath Tier 1–3",
    },
    {
        "id": "frontiermath-tier-4",
        "label": "FrontierMath Tier 4",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM4",
        "openaiLabel": "FrontierMath Tier 4",
    },
    {
        "id": "cybergym",
        "label": "CyberGym",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "CY",
        "openaiLabel": "CyberGym",
    },
    {
        "id": "exploitbench-cap",
        "label": "ExploitBench (Cap%)",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "EX",
    },
    {
        "id": "mmlu-pro",
        "label": "MMLU-Pro",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "MMLU",
    },
    {
        "id": "gpqa-diamond",
        "label": "GPQA Diamond",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "GPQA",
    },
    {
        "id": "hle",
        "label": "Humanity's Last Exam",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "HLE",
    },
    {
        "id": "critpt",
        "label": "CritPt",
        "category": "Reasoning",
        "unit": "%",
        "icon": "CPT",
    },
    {
        "id": "blueprint-bench-2",
        "label": "Blueprint-Bench 2",
        "category": "Spatial reasoning",
        "unit": "%",
        "icon": "BP",
    },
    {
        "id": "biomysterybench-hard",
        "label": "BioMysteryBench hard",
        "category": "Biology",
        "unit": "%",
        "icon": "BIO",
    },
    {
        "id": "biomysterybench-human-solved",
        "label": "BioMysteryBench human solved",
        "category": "Biology",
        "unit": "%",
        "icon": "BIO",
    },
    {
        "id": "legal-agent-benchmark",
        "label": "Legal Agent Benchmark",
        "category": "Legal",
        "unit": "%",
        "icon": "LAW",
    },
    {
        "id": "healthbench-professional",
        "label": "HealthBench Professional",
        "category": "Health",
        "unit": "%",
        "icon": "HB",
    },
    {
        "id": "livecodebench",
        "label": "LiveCodeBench",
        "category": "Coding",
        "unit": "%",
        "icon": "LCB",
    },
    {
        "id": "kimi-code-bench-v2",
        "label": "Kimi Code Bench v2",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "KCB",
    },
    {
        "id": "programbench",
        "label": "ProgramBench",
        "category": "Code generation",
        "unit": "%",
        "icon": "PROG",
    },
    {
        "id": "mls-bench-lite",
        "label": "MLS Bench Lite",
        "category": "ML coding",
        "unit": "%",
        "icon": "MLS",
    },
    {
        "id": "scicode",
        "label": "SciCode",
        "category": "Coding",
        "unit": "%",
        "icon": "SCI",
    },
    {
        "id": "aime-2024",
        "label": "AIME 2024",
        "category": "Math",
        "unit": "%",
        "icon": "A24",
    },
    {
        "id": "aime-2025",
        "label": "AIME 2025",
        "category": "Math",
        "unit": "%",
        "icon": "A25",
    },
    {
        "id": "aime-2026",
        "label": "AIME 2026",
        "category": "Math",
        "unit": "%",
        "icon": "A26",
    },
    {
        "id": "hmmt-2026-feb",
        "label": "HMMT Feb 2026",
        "category": "Math",
        "unit": "%",
        "icon": "H26",
    },
    {
        "id": "hmmt-2025-nov",
        "label": "HMMT Nov 2025",
        "category": "Math",
        "unit": "%",
        "icon": "H25",
    },
    {
        "id": "imoanswerbench",
        "label": "IMOAnswerBench",
        "category": "Math",
        "unit": "%",
        "icon": "IMO",
    },
    {
        "id": "skillsbench",
        "label": "SkillsBench Avg5",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SKL",
    },
    {
        "id": "qwenwebbench",
        "label": "QwenWebBench",
        "category": "Frontend coding",
        "unit": "Elo",
        "icon": "WEB",
    },
    {
        "id": "claw-eval",
        "label": "Claw-Eval Avg",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "CLAW",
    },
    {
        "id": "nl2repo",
        "label": "NL2Repo",
        "category": "Repository generation",
        "unit": "%",
        "icon": "N2R",
    },
    {
        "id": "deepswe",
        "label": "DeepSWE",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "DSWE",
    },
    {
        "id": "frontierswe-dominance",
        "label": "FrontierSWE Dominance",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "FSWE",
    },
    {
        "id": "swe-marathon",
        "label": "SWE-Marathon",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWEM",
    },
    {
        "id": "kimi-claw-24-7",
        "label": "Kimi Claw 24/7 Bench",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "CLAW",
    },
    {
        "id": "mcp-mark-verified",
        "label": "MCP Mark Verified",
        "category": "Tool use",
        "unit": "%",
        "icon": "MCPV",
    },
    {
        "id": "tau-bench",
        "label": "τ-Bench",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU",
    },
    {
        "id": "tau-bench-airline",
        "label": "τ-Bench Airline",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU-A",
    },
    {
        "id": "tau-bench-retail",
        "label": "τ-Bench Retail",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU-R",
    },
    {
        "id": "bfcl-v3",
        "label": "BFCL v3",
        "category": "Tool use",
        "unit": "%",
        "icon": "BFCL",
    },
    {
        "id": "bfcl-v4",
        "label": "BFCL v4",
        "category": "Tool use",
        "unit": "%",
        "icon": "BFCL",
    },
    {
        "id": "arc-agi-2",
        "label": "ARC-AGI-2",
        "category": "Abstract reasoning",
        "unit": "%",
        "icon": "ARC",
    },
    {
        "id": "livecodebench-pro-elo",
        "label": "LiveCodeBench Pro",
        "category": "Coding",
        "unit": "Elo",
        "icon": "LCB+",
    },
    {
        "id": "apex-agents",
        "label": "APEX-Agents",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "APEX",
    },
    {
        "id": "tau2-bench-retail",
        "label": "τ²-Bench Retail",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU2",
    },
    {
        "id": "tau2-bench-airline",
        "label": "τ²-Bench Airline",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU2",
    },
    {
        "id": "tau2-bench-telecom",
        "label": "τ²-Bench Telecom",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU2",
    },
    {
        "id": "tau2-bench-average",
        "label": "τ²-Bench Avg",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU2",
    },
    {
        "id": "tau2-bench-weighted",
        "label": "τ²-Bench Weighted",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU2",
    },
    {
        "id": "mmmu-pro",
        "label": "MMMU-Pro",
        "category": "Multimodal reasoning",
        "unit": "%",
        "icon": "MMMU",
    },
    {
        "id": "mmmlu",
        "label": "MMMLU",
        "category": "Multilingual knowledge",
        "unit": "%",
        "icon": "MLU",
    },
    {
        "id": "charxiv-no-tools",
        "label": "CharXiv Reasoning",
        "category": "Visual reasoning",
        "unit": "%",
        "icon": "CX",
    },
    {
        "id": "charxiv-tools",
        "label": "CharXiv Reasoning w/ tools",
        "category": "Visual reasoning",
        "unit": "%",
        "icon": "CX+",
    },
    {
        "id": "mrcr-v2-128k",
        "label": "MRCR v2 128K",
        "category": "Long context",
        "unit": "%",
        "icon": "MRCR",
    },
    {
        "id": "mrcr-v2-1m",
        "label": "MRCR v2 1M",
        "category": "Long context",
        "unit": "%",
        "icon": "MRCR",
    },
    {
        "id": "bigbench-extra-hard",
        "label": "BigBench Extra Hard",
        "category": "Reasoning",
        "unit": "%",
        "icon": "BBEH",
    },
    {
        "id": "codeforces-elo",
        "label": "Codeforces Elo",
        "category": "Coding",
        "unit": "Elo",
        "icon": "CF",
    },
    {
        "id": "deepsearchqa-f1",
        "label": "DeepSearchQA F1",
        "category": "Agentic search",
        "unit": "%",
        "icon": "DSQ",
    },
    {
        "id": "mathvision-python",
        "label": "MathVision w/ Python",
        "category": "Multimodal math",
        "unit": "%",
        "icon": "MV",
    },
    {
        "id": "v-star-python",
        "label": "V* w/ Python",
        "category": "Visual reasoning",
        "unit": "%",
        "icon": "V*",
    },
    {
        "id": "research-eval-reka",
        "label": "Research-Eval Reka",
        "category": "Agentic search",
        "unit": "%",
        "icon": "REKA",
    },
    {
        "id": "frames",
        "label": "FRAMES",
        "category": "Agentic search",
        "unit": "%",
        "icon": "FRM",
    },
    {
        "id": "x-browse",
        "label": "X Browse",
        "category": "Agentic search",
        "unit": "%",
        "icon": "XB",
    },
    {
        "id": "terminal-bench-2-1",
        "label": "Terminal-Bench 2.1",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "TERM",
    },
    {
        "id": "ifbench",
        "label": "IFBench",
        "category": "Instruction following",
        "unit": "%",
        "icon": "IF",
    },
    {
        "id": "aa-lcr",
        "label": "AA-LCR",
        "category": "Long context",
        "unit": "%",
        "icon": "LCR",
    },
    {
        "id": "fullstackbench",
        "label": "FullStackBench",
        "category": "Coding",
        "unit": "%",
        "icon": "FSB",
    },
    {
        "id": "pinchbench",
        "label": "PinchBench",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "PIN",
    },
    {
        "id": "taubench-v3-average",
        "label": "TauBench v3 Avg",
        "category": "Agentic workflow",
        "unit": "%",
        "icon": "TAU3",
    },
    {
        "id": "ifbench-prompt-loose",
        "label": "IFBench Prompt Loose",
        "category": "Instruction following",
        "unit": "%",
        "icon": "IF",
    },
    {
        "id": "multi-challenge",
        "label": "Multi-Challenge",
        "category": "Instruction following",
        "unit": "%",
        "icon": "MC",
    },
    {
        "id": "ruler-1m",
        "label": "RULER 1M",
        "category": "Long context",
        "unit": "%",
        "icon": "RUL",
    },
    {
        "id": "longbench-v2-1m",
        "label": "LongBench v2 ≤1M",
        "category": "Long context",
        "unit": "%",
        "icon": "LB2",
    },
    {
        "id": "mmlu-prox",
        "label": "MMLU-ProX",
        "category": "Multilingual knowledge",
        "unit": "%",
        "icon": "MPX",
    },
    {
        "id": "wmt24-plusplus",
        "label": "WMT24++",
        "category": "Multilingual generation",
        "unit": "%",
        "icon": "WMT",
    },
    {
        "id": "agents-last-exam",
        "label": "Agents' Last Exam",
        "category": "Agentic reasoning",
        "unit": "%",
        "icon": "ALE",
    },
    {
        "id": "management-consulting-internal",
        "label": "Management Consulting Tasks (Internal)",
        "category": "Professional work",
        "unit": "%",
        "icon": "MGT",
    },
    {
        "id": "big-finance-bench",
        "label": "Big Finance Bench",
        "category": "Professional work",
        "unit": "%",
        "icon": "BFB",
    },
    {
        "id": "deepswe-v1-1",
        "label": "DeepSWE v1.1",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "DSWE",
    },
    {
        "id": "genebench-pro",
        "label": "GeneBench Pro",
        "category": "Biology",
        "unit": "%",
        "icon": "GENE",
    },
    {
        "id": "lifescibench",
        "label": "LifeSciBench",
        "category": "Life sciences",
        "unit": "%",
        "icon": "LIFE",
    },
    {
        "id": "medchembench-internal",
        "label": "MedChemBench (Internal)",
        "category": "Chemistry",
        "unit": "%",
        "icon": "MED",
    },
    {
        "id": "osworld-2",
        "label": "OSWorld 2.0",
        "category": "Computer use",
        "unit": "%",
        "icon": "OS2",
    },
    {
        "id": "benchcad",
        "label": "BenchCAD",
        "category": "Computer-aided design",
        "unit": "%",
        "icon": "CAD",
    },
    {
        "id": "benchcad-python",
        "label": "BenchCAD (Python tool)",
        "category": "Computer-aided design",
        "unit": "%",
        "icon": "CAD+",
    },
    {
        "id": "capture-the-flag",
        "label": "Capture-the-Flag Challenges",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "CTF",
    },
    {
        "id": "sec-bench-pro",
        "label": "SEC-Bench Pro",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "SEC",
    },
    {
        "id": "exploitbench",
        "label": "ExploitBench",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "EX",
    },
    {
        "id": "exploitgym",
        "label": "ExploitGym",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "EXG",
    },
    {
        "id": "internal-research-debugging",
        "label": "Internal Research Debugging Evaluation",
        "category": "Research coding",
        "unit": "%",
        "icon": "DBG",
    },
    {
        "id": "kernelgen-1p",
        "label": "KernelGen 1P",
        "category": "Systems coding",
        "unit": "%",
        "icon": "KRN",
    },
    {
        "id": "nanogpt",
        "label": "NanoGPT",
        "category": "ML coding",
        "unit": "%",
        "icon": "NGPT",
    },
    {
        "id": "posttrainbench-lite",
        "label": "PostTrainBench Lite",
        "category": "Agentic training",
        "unit": "%",
        "icon": "PTB",
    },
    {
        "id": "rsi-index",
        "label": "RSI Index",
        "category": "Self-improvement",
        "unit": "%",
        "icon": "RSI",
    },
    {
        "id": "mmmu-pro-no-tools",
        "label": "MMMU Pro (no tools)",
        "category": "Multimodal reasoning",
        "unit": "%",
        "icon": "MMMU",
    },
    {
        "id": "mmmu-pro-tools",
        "label": "MMMU Pro (with tools)",
        "category": "Multimodal reasoning",
        "unit": "%",
        "icon": "MMMU+",
    },
    {
        "id": "frontiermath-tier-1-3-v2",
        "label": "FrontierMath Tier 1-3 (v2)",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM2",
    },
    {
        "id": "frontiermath-tier-4-v2",
        "label": "FrontierMath Tier 4 (v2)",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM4",
    },
    {
        "id": "openai-mrcr-v2-256k-512k",
        "label": "OpenAI MRCR v2 8-needle 256K-512K",
        "category": "Long context",
        "unit": "%",
        "icon": "MRCR",
    },
    {
        "id": "openai-mrcr-v2-512k-1m",
        "label": "OpenAI MRCR v2 8-needle 512K-1M",
        "category": "Long context",
        "unit": "%",
        "icon": "MRCR",
    },
    {
        "id": "graphwalks-bfs-256k-f1",
        "label": "GraphWalks BFS 256K F1",
        "category": "Long context",
        "unit": "%",
        "icon": "GW",
    },
    {
        "id": "graphwalks-bfs-1m-f1",
        "label": "GraphWalks BFS 1M F1",
        "category": "Long context",
        "unit": "%",
        "icon": "GW",
    },
    {
        "id": "arc-agi-3",
        "label": "ARC-AGI-3",
        "category": "Abstract reasoning",
        "unit": "%",
        "icon": "ARC3",
    },
]

SEED_OPENAI_VALUES = {
    "swe-bench-pro": [58.6, 57.7, None, None, 64.3, 54.2],
    "terminal-bench-2": [82.7, 75.1, None, None, 69.4, 68.5],
    "expert-swe-internal": [73.1, 68.5, None, None, None, None],
    "gdpval-wins-ties": [84.9, 83.0, 82.3, 82.0, 80.3, 67.3],
    "osworld-verified": [78.7, 75.0, None, None, 78.0, None],
    "toolathlon": [55.6, 54.6, None, None, None, 48.8],
    "browsecomp": [84.4, 82.7, 90.1, 89.3, 79.3, 85.9],
    "frontiermath-tier-1-3": [51.7, 47.6, 52.4, 50.0, 43.8, 36.9],
    "frontiermath-tier-4": [35.4, 27.1, 39.6, 38.0, 22.9, 16.7],
    "cybergym": [81.8, 79.0, None, None, 73.1, None],
}

OFFICIAL_SOURCE_SPECS: list[dict[str, Any]] = [
    {
        "id": "openai-gpt-5-6-release",
        "label": "OpenAI GPT-5.6 official release evaluations",
        "url": OPENAI_GPT56_URL,
        "rawUrl": OPENAI_GPT56_URL,
        "category": "Official model release",
        "note": "OpenAI official GPT-5.6 release tables covering Sol, Terra, and Luna across professional work, coding, science, computer use, cybersecurity, reasoning, tool use, and long-context evaluations.",
        "columns": {
            "GPT-5.6 Sol": "GPT-5.6 Sol",
            "GPT-5.6 Terra": "GPT-5.6 Terra",
            "GPT-5.6 Luna": "GPT-5.6 Luna",
        },
        "rowLabels": {
            "Agents' Last Exam": "agents-last-exam",
            "GDPval-AA v2": "gdpval-aa-elo",
            "Management Consulting Tasks (Internal)": "management-consulting-internal",
            "Big Finance Bench": "big-finance-bench",
            "SWE-Bench Pro": "swe-bench-pro",
            "DeepSWE v1.1": "deepswe-v1-1",
            "Terminal-Bench 2.1": "terminal-bench-2-1",
            "GeneBench Pro": "genebench-pro",
            "LifeSciBench": "lifescibench",
            "MedChemBench (Internal)": "medchembench-internal",
            "HealthBench Professional": "healthbench-professional",
            "OSWorld 2.0": "osworld-2",
            "BrowseComp": "browsecomp",
            "BenchCAD": "benchcad",
            "BenchCAD (python tool)": "benchcad-python",
            "Capture-the-Flag Challenges": "capture-the-flag",
            "SEC-Bench Pro": "sec-bench-pro",
            "ExploitBench": "exploitbench",
            "ExploitGym": "exploitgym",
            "Internal Research Debugging Evaluation": "internal-research-debugging",
            "KernelGen 1P": "kernelgen-1p",
            "NanoGPT": "nanogpt",
            "PostTrainBench Lite": "posttrainbench-lite",
            "RSI Index": "rsi-index",
            "MMMU Pro (no tools)": "mmmu-pro-no-tools",
            "MMMU Pro (with tools)": "mmmu-pro-tools",
            "gdp.pdf": "gdp-pdf",
            "GPQA Diamond": "gpqa-diamond",
            "FrontierMath Tier 1-3 (v2)": "frontiermath-tier-1-3-v2",
            "FrontierMath Tier 4 (v2)": "frontiermath-tier-4-v2",
            "AutomationBench": "automationbench",
            "Toolathlon": "toolathlon",
            "OpenAI MRCR v2 8-needle 256K-512K": "openai-mrcr-v2-256k-512k",
            "OpenAI MRCR v2 8-needle 512K-1M": "openai-mrcr-v2-512k-1m",
            "GraphWalks BFS 256k f1": "graphwalks-bfs-256k-f1",
            "GraphWalks BFS 1mil f1": "graphwalks-bfs-1m-f1",
            "ARC-AGI-3": "arc-agi-3",
        },
        "scores": {
            "GPT-5.6 Sol": {
                "agents-last-exam": 52.7,
                "gdpval-aa-elo": 1747.8,
                "management-consulting-internal": 43.2,
                "big-finance-bench": 53.0,
                "swe-bench-pro": 64.6,
                "deepswe-v1-1": 72.7,
                "terminal-bench-2-1": 88.8,
                "genebench-pro": 28.7,
                "lifescibench": 59.9,
                "medchembench-internal": 48.3,
                "healthbench-professional": 60.5,
                "osworld-2": 62.6,
                "browsecomp": 90.4,
                "benchcad": 70.6,
                "benchcad-python": 83.4,
                "capture-the-flag": 96.7,
                "sec-bench-pro": 71.2,
                "exploitbench": 73.5,
                "exploitgym": 33.7,
                "internal-research-debugging": 68.3,
                "kernelgen-1p": 61.1,
                "nanogpt": 9.69,
                "posttrainbench-lite": 50.3,
                "rsi-index": 57.9,
                "mmmu-pro-no-tools": 83.0,
                "mmmu-pro-tools": 84.6,
                "gdp-pdf": 30.7,
                "gpqa-diamond": 94.6,
                "frontiermath-tier-1-3-v2": 89.0,
                "frontiermath-tier-4-v2": 83.0,
                "automationbench": 18.1,
                "toolathlon": 58.0,
                "openai-mrcr-v2-256k-512k": 91.5,
                "openai-mrcr-v2-512k-1m": 73.8,
                "graphwalks-bfs-256k-f1": 90.7,
                "graphwalks-bfs-1m-f1": 77.1,
                "arc-agi-3": 7.78,
            },
            "GPT-5.6 Terra": {
                "agents-last-exam": 50.4,
                "gdpval-aa-elo": 1593.0,
                "management-consulting-internal": 37.2,
                "big-finance-bench": 51.0,
                "swe-bench-pro": 63.4,
                "deepswe-v1-1": 69.6,
                "terminal-bench-2-1": 87.4,
                "genebench-pro": 23.3,
                "lifescibench": 56.0,
                "medchembench-internal": 35.0,
                "healthbench-professional": 57.7,
                "osworld-2": 50.2,
                "browsecomp": 87.5,
                "benchcad": 62.3,
                "benchcad-python": 78.2,
                "capture-the-flag": 91.8,
                "sec-bench-pro": 57.7,
                "exploitbench": 52.9,
                "exploitgym": 23.2,
                "internal-research-debugging": 67.8,
                "kernelgen-1p": 49.2,
                "nanogpt": 14.5,
                "posttrainbench-lite": 51.5,
                "rsi-index": 56.3,
                "mmmu-pro-no-tools": 80.7,
                "mmmu-pro-tools": 82.0,
                "gdp-pdf": 24.7,
                "gpqa-diamond": 92.9,
                "frontiermath-tier-1-3-v2": 84.9,
                "frontiermath-tier-4-v2": 68.3,
                "automationbench": 15.2,
                "toolathlon": 53.1,
                "openai-mrcr-v2-256k-512k": 89.6,
                "openai-mrcr-v2-512k-1m": 72.5,
                "graphwalks-bfs-256k-f1": 76.9,
                "graphwalks-bfs-1m-f1": 71.2,
                "arc-agi-3": 0.8,
            },
            "GPT-5.6 Luna": {
                "agents-last-exam": 50.3,
                "gdpval-aa-elo": 1591.8,
                "management-consulting-internal": 35.4,
                "big-finance-bench": 36.0,
                "swe-bench-pro": 62.7,
                "deepswe-v1-1": 67.2,
                "terminal-bench-2-1": 84.7,
                "genebench-pro": 10.8,
                "lifescibench": 51.2,
                "medchembench-internal": 30.4,
                "healthbench-professional": 55.7,
                "osworld-2": 45.6,
                "browsecomp": 83.3,
                "benchcad": 63.1,
                "benchcad-python": 73.9,
                "capture-the-flag": 85.2,
                "sec-bench-pro": 48.9,
                "exploitbench": 33.2,
                "exploitgym": 12.4,
                "internal-research-debugging": 50.8,
                "kernelgen-1p": 22.4,
                "nanogpt": 1.66,
                "posttrainbench-lite": 29.6,
                "rsi-index": 41.9,
                "mmmu-pro-no-tools": 78.4,
                "mmmu-pro-tools": 79.5,
                "gdp-pdf": 22.7,
                "gpqa-diamond": 92.3,
                "frontiermath-tier-1-3-v2": 78.6,
                "frontiermath-tier-4-v2": 58.5,
                "automationbench": 14.9,
                "toolathlon": 53.4,
                "openai-mrcr-v2-256k-512k": 41.3,
                "openai-mrcr-v2-512k-1m": 41.3,
                "graphwalks-bfs-256k-f1": 81.3,
                "graphwalks-bfs-1m-f1": 51.2,
                "arc-agi-3": 0.18,
            },
        },
    },
    {
        "id": "anthropic-claude-opus-4-7-release",
        "label": "Anthropic Claude Opus 4.7 official release",
        "url": ANTHROPIC_OPUS47_URL,
        "rawUrl": ANTHROPIC_OPUS47_URL,
        "category": "Official release",
        "note": "Anthropic official release chart covering Opus 4.7, Opus 4.6, GPT-5.4, Gemini 3.1 Pro, and Mythos Preview across agentic coding, search, tool use, reasoning, and finance benchmarks.",
        "columns": {
            "Opus 4.7": "Claude Opus 4.7",
            "Claude Opus 4.7": "Claude Opus 4.7",
            "Opus 4.6": "Claude Opus 4.6",
            "Claude Opus 4.6": "Claude Opus 4.6",
        },
        "rowLabels": {
            "SWE-bench Pro": "swe-bench-pro",
            "SWE-bench Verified": "swe-bench-verified",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "Humanity's Last Exam": "hle",
            "HLE with tools": "hle-tools",
            "BrowseComp": "browsecomp",
            "MCP-Atlas": "mcp-atlas",
            "OSWorld-Verified": "osworld-verified",
            "Finance Agent v1.1": "finance-agent-v1-1",
            "CyberGym": "cybergym",
            "GPQA Diamond": "gpqa-diamond",
            "CharXiv Reasoning": "charxiv-no-tools",
            "CharXiv Reasoning with tools": "charxiv-tools",
            "MMMLU": "mmmlu",
        },
        "scores": {
            "Claude Opus 4.7": {
                "swe-bench-pro": 64.3,
                "swe-bench-verified": 87.6,
                "terminal-bench-2": 69.4,
                "hle": 46.9,
                "hle-tools": 54.7,
                "browsecomp": 79.3,
                "mcp-atlas": 77.3,
                "osworld-verified": 78.0,
                "finance-agent-v1-1": 64.4,
                "cybergym": 73.1,
                "gpqa-diamond": 94.2,
                "charxiv-no-tools": 82.1,
                "charxiv-tools": 91.0,
                "mmmlu": 91.5,
            },
            "Claude Opus 4.6": {
                "swe-bench-pro": 53.4,
                "swe-bench-verified": 80.8,
                "terminal-bench-2": 65.4,
                "hle": 40.0,
                "hle-tools": 53.3,
                "browsecomp": 83.7,
                "mcp-atlas": 75.8,
                "osworld-verified": 72.7,
                "finance-agent-v1-1": 60.1,
                "cybergym": 73.8,
                "gpqa-diamond": 91.3,
                "charxiv-no-tools": 69.1,
                "charxiv-tools": 84.7,
                "mmmlu": 91.1,
            },
        },
    },
    {
        "id": "anthropic-claude-fable-5-docs",
        "label": "Anthropic Claude Fable 5 and Mythos 5 official release",
        "url": ANTHROPIC_FABLE5_URL,
        "rawUrl": ANTHROPIC_FABLE5_URL,
        "category": "Official release",
        "modelAliases": MODEL_ALIASES["Claude Fable 5"],
        "note": (
            "Anthropic release table for Claude Mythos 5 / Fable 5. Reported Mythos and Fable scores are "
            "within 1-3 percentage points unless starred; the table shows the higher score of the two, and "
            "starred rows can differ more because Fable falls back to Opus 4.8 for some cyber and biology requests."
        ),
        "columns": {"Claude Mythos 5 / Fable 5": "Claude Fable 5", "Claude Fable 5": "Claude Fable 5"},
        "rowLabels": {
            "SWE-Bench Pro": "swe-bench-pro",
            "FrontierCode (Diamond)": "frontiercode-diamond",
            "GDPval-AA": "gdpval-aa-elo",
            "GDP.pdf": "gdp-pdf",
            "Blueprint-Bench 2": "blueprint-bench-2",
            "AutomationBench": "automationbench",
            "OSWorld-Verified": "osworld-verified",
            "Legal Agent Benchmark": "legal-agent-benchmark",
            "Humanity's Last Exam no tools": "hle",
            "Humanity's Last Exam with tools": "hle-tools",
            "BioMysteryBench hard": "biomysterybench-hard",
            "BioMysteryBench human solved": "biomysterybench-human-solved",
            "Terminal-Bench 2.1": "terminal-bench-2-1",
            "ExploitBench (Cap%)": "exploitbench-cap",
            "HealthBench Professional": "healthbench-professional",
        },
        "scores": {
            "Claude Fable 5": {
                "swe-bench-pro": 80.3,
                "frontiercode-diamond": 29.3,
                "gdpval-aa-elo": 1932,
                "gdp-pdf": 29.8,
                "blueprint-bench-2": 38.6,
                "automationbench": 17.4,
                "osworld-verified": 85.0,
                "legal-agent-benchmark": 13.3,
                "hle": 59.0,
                "hle-tools": 64.5,
                "biomysterybench-hard": 46.1,
                "biomysterybench-human-solved": 83.9,
                "terminal-bench-2-1": 88.0,
                "exploitbench-cap": 78.0,
                "healthbench-professional": 66.0,
            },
        },
    },
    {
        "id": "qwen-qwen3-release",
        "label": "Qwen3 official release",
        "url": QWEN3_URL,
        "rawUrl": QWEN3_URL,
        "category": "Official release",
        "note": (
            "Qwen.ai Qwen3 release page. Seed values are read from the official benchmark images for "
            "Qwen3-235B-A22B, Qwen3-32B, Qwen3-30B-A3B, and Qwen3-4B; Qwen3 rows are matched to the "
            "site's reasoning variants because the release notes indicate think mode is used for the main evaluations."
        ),
        "columns": {
            "Qwen3-235B-A22B": "Qwen3 235B [R]",
            "Qwen3-32B": "Qwen3 32B [R]",
            "Qwen3-30B-A3B": "Qwen3 30B [R]",
            "Qwen3-4B": "Qwen3 4B [R]",
        },
        "rowLabels": {
            "AIME'24": "aime-2024",
            "AIME 24": "aime-2024",
            "AIME'25": "aime-2025",
            "AIME 25": "aime-2025",
            "LiveCodeBench": "livecodebench",
            "CodeForces": "codeforces-elo",
            "GPQA": "gpqa-diamond",
            "BFCL": "bfcl-v3",
            "BFCL v3": "bfcl-v3",
        },
        "scores": {
            "Qwen3 235B [R]": {
                "aime-2024": 85.7,
                "aime-2025": 81.5,
                "livecodebench": 70.7,
                "codeforces-elo": 2056,
                "bfcl-v3": 70.8,
            },
            "Qwen3 32B [R]": {
                "aime-2024": 81.4,
                "aime-2025": 72.9,
                "livecodebench": 65.7,
                "codeforces-elo": 1977,
                "bfcl-v3": 70.3,
            },
            "Qwen3 30B [R]": {
                "aime-2024": 80.4,
                "aime-2025": 70.9,
                "livecodebench": 62.6,
                "codeforces-elo": 1974,
                "gpqa-diamond": 65.8,
                "bfcl-v3": 69.1,
            },
            "Qwen3 4B [R]": {
                "aime-2024": 73.8,
                "aime-2025": 65.6,
                "livecodebench": 54.2,
                "codeforces-elo": 1671,
                "gpqa-diamond": 55.9,
                "bfcl-v3": 65.9,
            },
        },
    },
    {
        "id": "qwen-qwen2-release",
        "label": "Qwen2 official release",
        "url": QWEN2_URL,
        "rawUrl": "https://qwenlm.github.io/blog/qwen2/",
        "category": "Official release",
        "note": "Qwen.ai/Qwen legacy official release page for Qwen2. Seed rows use the published Qwen2-72B-Instruct evaluation table.",
        "columns": {"Qwen2-72B-Instruct": "Qwen2 72B"},
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "GPQA": "gpqa-diamond",
            "LiveCodeBench": "livecodebench",
        },
        "scores": {
            "Qwen2 72B": {
                "mmlu-pro": 64.4,
                "gpqa-diamond": 42.4,
                "livecodebench": 35.7,
            }
        },
    },
    {
        "id": "qwen-qwen2-5-release",
        "label": "Qwen2.5 official release",
        "url": QWEN25_URL,
        "rawUrl": QWEN25_URL,
        "category": "Official release",
        "note": "Qwen.ai Qwen2.5 release page with official image tables for Qwen2.5-72B-Instruct, Qwen2.5-32B-Instruct, and Qwen-Turbo.",
        "columns": {
            "Qwen2.5-72B-Instruct": "Qwen2.5 72B",
            "Qwen2.5-32B-Instruct": "Qwen2.5 Instruct 32B",
            "Qwen-Turbo": "Qwen2.5 Turbo",
        },
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "GPQA": "gpqa-diamond",
            "LiveCodeBench": "livecodebench",
        },
        "scores": {
            "Qwen2.5 72B": {
                "mmlu-pro": 71.1,
                "gpqa-diamond": 49.0,
                "livecodebench": 55.5,
            },
            "Qwen2.5 Instruct 32B": {
                "mmlu-pro": 69.0,
                "gpqa-diamond": 49.5,
                "livecodebench": 51.2,
            },
            "Qwen2.5 Turbo": {
                "mmlu-pro": 64.8,
                "gpqa-diamond": 44.4,
                "livecodebench": 43.1,
            },
        },
    },
    {
        "id": "qwen-qwen2-5-coder-release",
        "label": "Qwen2.5-Coder official release",
        "url": QWEN25_CODER_URL,
        "rawUrl": QWEN25_CODER_URL,
        "category": "Official release",
        "note": "Qwen.ai Qwen2.5-Coder release page. General and math rows are HTML tables; LiveCodeBench is read from the official code benchmark image.",
        "columns": {"Qwen2.5-Coder-7B-Instruct": "Qwen2.5 Coder 7B"},
        "rowLabels": {
            "AIME24": "aime-2024",
            "MMLU-Pro": "mmlu-pro",
            "GPQA": "gpqa-diamond",
            "LiveCodeBench": "livecodebench",
        },
        "scores": {
            "Qwen2.5 Coder 7B": {
                "aime-2024": 10.0,
                "mmlu-pro": 45.6,
                "gpqa-diamond": 35.6,
                "livecodebench": 35.9,
            }
        },
    },
    {
        "id": "qwen-qwen2-5-max-release",
        "label": "Qwen2.5-Max official release",
        "url": QWEN25_MAX_URL,
        "rawUrl": QWEN25_MAX_URL,
        "category": "Official release",
        "note": "Qwen.ai Qwen2.5-Max release page. Seed values use the official instruct-model comparison chart.",
        "columns": {"Qwen2.5-Max": "Qwen2.5 Max"},
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "GPQA-Diamond": "gpqa-diamond",
            "LiveCodeBench": "livecodebench",
        },
        "scores": {
            "Qwen2.5 Max": {
                "mmlu-pro": 76.1,
                "gpqa-diamond": 60.1,
                "livecodebench": 38.7,
            }
        },
    },
    {
        "id": "qwen-qwen3-6-27b-card",
        "label": "Qwen3.6-27B official release",
        "url": QWEN36_27B_URL,
        "rawUrl": QWEN36_27B_URL,
        "category": "Official release",
        "note": "Qwen.ai release page with Qwen3.6/Qwen3.5 benchmark table. Hugging Face is intentionally not used as the primary source for Qwen-family rows.",
        "columns": {
            "Qwen3.5-27B": "Qwen3.5 27B",
            "Qwen3.5-397B-A17B": "Qwen3.5 397B A17B",
            "Qwen3.6-35B-A3B": "Qwen3.6 35B A3B",
            "Qwen3.6-27B": "Qwen3.6 27B",
        },
        "textColumns": [
            "Qwen3.5-27B",
            "Qwen3.5-397B-A17B",
            "Gemma4-31B",
            "Claude 4.5 Opus",
            "Qwen3.6-35B-A3B",
            "Qwen3.6-27B",
        ],
        "rowLabels": {
            "SWE-bench Verified": "swe-bench-verified",
            "SWE-bench Pro": "swe-bench-pro",
            "SWE-bench Multilingual": "swe-bench-multilingual",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "SkillsBench Avg5": "skillsbench",
            "QwenWebBench": "qwenwebbench",
            "NL2Repo": "nl2repo",
            "Claw-Eval Avg": "claw-eval",
            "MMLU-Pro": "mmlu-pro",
            "GPQA Diamond": "gpqa-diamond",
            "HLE": "hle",
            "LiveCodeBench v6": "livecodebench",
            "HMMT Feb 26": "hmmt-2026-feb",
            "AIME26": "aime-2026",
        },
        "scores": {
            "Qwen3.5 27B": {
                "swe-bench-verified": 75.0,
                "swe-bench-pro": 51.2,
                "swe-bench-multilingual": 69.3,
                "terminal-bench-2": 41.6,
                "skillsbench": 27.2,
                "qwenwebbench": 1068,
                "nl2repo": 27.3,
                "claw-eval": 64.3,
                "mmlu-pro": 86.1,
                "gpqa-diamond": 85.5,
                "hle": 24.3,
                "livecodebench": 80.7,
                "hmmt-2026-feb": 84.3,
                "aime-2026": 92.6,
            },
            "Qwen3.5 397B A17B": {
                "swe-bench-verified": 76.2,
                "swe-bench-pro": 50.9,
                "swe-bench-multilingual": 69.3,
                "terminal-bench-2": 52.5,
                "skillsbench": 30.0,
                "qwenwebbench": 1186,
                "nl2repo": 32.2,
                "claw-eval": 70.7,
                "mmlu-pro": 87.8,
                "gpqa-diamond": 88.4,
                "hle": 28.7,
                "livecodebench": 83.6,
                "hmmt-2026-feb": 87.9,
                "aime-2026": 93.3,
            },
            "Qwen3.6 35B A3B": {
                "swe-bench-verified": 73.4,
                "swe-bench-pro": 49.5,
                "swe-bench-multilingual": 67.2,
                "terminal-bench-2": 51.5,
                "skillsbench": 28.7,
                "qwenwebbench": 1397,
                "nl2repo": 29.4,
                "claw-eval": 68.7,
                "mmlu-pro": 85.2,
                "gpqa-diamond": 86.0,
                "hle": 21.4,
                "livecodebench": 80.4,
                "hmmt-2026-feb": 83.6,
                "aime-2026": 92.7,
            },
            "Qwen3.6 27B": {
                "swe-bench-verified": 77.2,
                "swe-bench-pro": 53.5,
                "swe-bench-multilingual": 71.3,
                "terminal-bench-2": 59.3,
                "skillsbench": 48.2,
                "qwenwebbench": 1487,
                "nl2repo": 36.2,
                "claw-eval": 72.4,
                "mmlu-pro": 86.2,
                "gpqa-diamond": 87.8,
                "hle": 24.0,
                "livecodebench": 83.9,
                "hmmt-2026-feb": 84.3,
                "aime-2026": 94.1,
            },
        },
    },
    {
        "id": "qwen-qwen3-6-plus-release",
        "label": "Qwen3.6-Plus official release",
        "url": QWEN36_PLUS_URL,
        "rawUrl": QWEN36_PLUS_URL,
        "category": "Official release",
        "note": "Qwen.ai proprietary model release page. Seed values are from the official launch benchmark image/table when HTML parsing cannot read the rendered image.",
        "columns": {"Qwen3.6-Plus": "Qwen3.6 Plus", "Qwen3.6 Plus": "Qwen3.6 Plus"},
        "rowLabels": {
            "SWE-bench Verified": "swe-bench-verified",
            "SWE-Bench Verified": "swe-bench-verified",
            "SWE-bench Pro": "swe-bench-pro",
            "SWE-bench Multilingual": "swe-bench-multilingual",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "NL2Repo": "nl2repo",
        },
        "scores": {
            "Qwen3.6 Plus": {
                "swe-bench-verified": 78.8,
                "swe-bench-pro": 56.6,
                "swe-bench-multilingual": 73.8,
                "terminal-bench-2": 61.6,
                "nl2repo": 37.9,
            },
        },
    },
    {
        "id": "qwen-qwen3-6-max-preview-release",
        "label": "Qwen3.6-Max-Preview official release",
        "url": QWEN36_MAX_PREVIEW_URL,
        "rawUrl": QWEN36_MAX_PREVIEW_URL,
        "category": "Official release",
        "note": "Qwen.ai proprietary preview release. Seeded rows are limited to values derivable from official deltas over Qwen3.6-Plus; image-only absolute rows are left for parser/OCR follow-up.",
        "columns": {"Qwen3.6-Max-Preview": "Qwen3.6 Max Preview"},
        "rowLabels": {
            "SWE-bench Pro": "swe-bench-pro",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "SkillsBench": "skillsbench",
            "QwenWebBench": "qwenwebbench",
            "SciCode": "scicode",
            "NL2Repo": "nl2repo",
        },
        "scores": {
            "Qwen3.6 Max Preview": {
                "terminal-bench-2": 65.4,
                "nl2repo": 42.9,
            }
        },
    },
    {
        "id": "deepseek-v4-pro-card",
        "label": "DeepSeek-V4 official release",
        "url": DEEPSEEK_V4_PRO_URL,
        "rawUrl": DEEPSEEK_V4_PRO_URL,
        "category": "Official release",
        "note": "DeepSeek API Docs V4 preview release. Seed values mirror the official release report; Hugging Face is kept out of source URLs for this top-model collector.",
        "columns": {
            "V4-Flash Non-Think": "DeepSeek V4 Flash",
            "V4-Flash High": "DeepSeek V4 Flash (High)",
            "V4-Flash Max": "DeepSeek V4 Flash (Max)",
            "V4-Pro Non-Think": "DeepSeek V4 Pro",
            "V4-Pro High": "DeepSeek V4 Pro (High)",
            "V4-Pro Max": "DeepSeek V4 Pro (Max)",
            "DS-V4-Pro Max": "DeepSeek V4 Pro (Max)",
        },
        "rowLabels": {
            "MMLU-Pro (EM)": "mmlu-pro",
            "GPQA Diamond (Pass@1)": "gpqa-diamond",
            "HLE (Pass@1)": "hle",
            "LiveCodeBench (Pass@1)": "livecodebench",
            "HMMT 2026 Feb (Pass@1)": "hmmt-2026-feb",
            "Terminal Bench 2.0 (Acc)": "terminal-bench-2",
            "SWE Verified (Resolved)": "swe-bench-verified",
            "SWE Pro (Resolved)": "swe-bench-pro",
            "SWE Multilingual (Resolved)": "swe-bench-multilingual",
            "BrowseComp (Pass@1)": "browsecomp",
            "HLE w/ tools (Pass@1)": "hle-tools",
            "GDPval-AA (Elo)": "gdpval-aa-elo",
            "MCPAtlas (Pass@1)": "mcp-atlas",
            "MCPAtlas Public (Pass@1)": "mcp-atlas",
            "Toolathlon (Pass@1)": "toolathlon",
        },
        "scores": {
            "DeepSeek V4 Flash": {
                "mmlu-pro": 83.0,
                "gpqa-diamond": 71.2,
                "hle": 8.1,
                "livecodebench": 55.2,
                "hmmt-2026-feb": 40.8,
                "terminal-bench-2": 49.1,
                "swe-bench-verified": 73.7,
                "swe-bench-pro": 49.1,
                "swe-bench-multilingual": 69.7,
                "mcp-atlas": 64.0,
                "toolathlon": 40.7,
            },
            "DeepSeek V4 Flash (High)": {
                "mmlu-pro": 86.4,
                "gpqa-diamond": 87.4,
                "hle": 29.4,
                "livecodebench": 88.4,
                "hmmt-2026-feb": 91.9,
                "terminal-bench-2": 56.6,
                "swe-bench-verified": 78.6,
                "swe-bench-pro": 52.3,
                "swe-bench-multilingual": 70.2,
                "browsecomp": 53.5,
                "hle-tools": 40.3,
                "mcp-atlas": 67.4,
                "toolathlon": 43.5,
            },
            "DeepSeek V4 Flash (Max)": {
                "mmlu-pro": 86.2,
                "gpqa-diamond": 88.1,
                "hle": 34.8,
                "livecodebench": 91.6,
                "hmmt-2026-feb": 94.8,
                "terminal-bench-2": 56.9,
                "swe-bench-verified": 79.0,
                "swe-bench-pro": 52.6,
                "swe-bench-multilingual": 73.3,
                "browsecomp": 73.2,
                "hle-tools": 45.1,
                "gdpval-aa-elo": 1395,
                "mcp-atlas": 69.0,
                "toolathlon": 47.8,
            },
            "DeepSeek V4 Pro": {
                "mmlu-pro": 82.9,
                "gpqa-diamond": 72.9,
                "hle": 7.7,
                "livecodebench": 56.8,
                "hmmt-2026-feb": 31.7,
                "terminal-bench-2": 59.1,
                "swe-bench-verified": 73.6,
                "swe-bench-pro": 52.1,
                "swe-bench-multilingual": 69.8,
                "mcp-atlas": 69.4,
                "toolathlon": 46.3,
            },
            "DeepSeek V4 Pro (High)": {
                "mmlu-pro": 87.1,
                "gpqa-diamond": 89.1,
                "hle": 34.5,
                "livecodebench": 89.8,
                "hmmt-2026-feb": 94.0,
                "terminal-bench-2": 63.3,
                "swe-bench-verified": 79.4,
                "swe-bench-pro": 54.4,
                "swe-bench-multilingual": 74.1,
                "browsecomp": 80.4,
                "hle-tools": 44.7,
                "mcp-atlas": 74.2,
                "toolathlon": 49.0,
            },
            "DeepSeek V4 Pro (Max)": {
                "mmlu-pro": 87.5,
                "gpqa-diamond": 90.1,
                "hle": 37.7,
                "livecodebench": 93.5,
                "hmmt-2026-feb": 95.2,
                "terminal-bench-2": 67.9,
                "swe-bench-verified": 80.6,
                "swe-bench-pro": 55.4,
                "swe-bench-multilingual": 76.2,
                "browsecomp": 83.4,
                "hle-tools": 48.2,
                "gdpval-aa-elo": 1554,
                "mcp-atlas": 73.6,
                "toolathlon": 51.8,
            },
        },
    },
    {
        "id": "kimi-k2-6-card",
        "label": "Kimi K2.6 official release",
        "url": KIMI_K26_URL,
        "rawUrl": KIMI_K26_URL,
        "category": "Official release",
        "note": "Moonshot AI Kimi.com release page with coding, agentic, search, and visual-agent benchmark tables.",
        "columns": {"Kimi K2.6": "Kimi K2.6", "K2.6 Thinking": "Kimi K2.6"},
        "rowLabels": {
            "SWE Bench Resolved": "swe-bench-verified",
            "SWE Bench Pro": "swe-bench-pro",
            "SWE-Multilingual": "swe-bench-multilingual",
            "Diamond": "gpqa-diamond",
            "GPQA-Diamond": "gpqa-diamond",
            "Terminalbench 2": "terminal-bench-2",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "MathArena Aime 2026": "aime-2026",
            "MathArena Hmmt Feb 2026": "hmmt-2026-feb",
            "Humanity's Last Exam (Full) w/ tools": "hle-tools",
            "BrowseComp": "browsecomp",
            "DeepSearchQA (f1-score)": "deepsearchqa-f1",
            "Toolathlon": "toolathlon",
            "OSWorld-Verified": "osworld-verified",
            "LiveCodeBench v6": "livecodebench",
            "MMMU-Pro": "mmmu-pro",
            "MathVision w/ python": "mathvision-python",
            "V* w/ python": "v-star-python",
        },
        "scores": {
            "Kimi K2.6": {
                "swe-bench-verified": 80.2,
                "swe-bench-pro": 58.6,
                "swe-bench-multilingual": 76.7,
                "gpqa-diamond": 90.5,
                "terminal-bench-2": 66.7,
                "aime-2026": 96.4,
                "hmmt-2026-feb": 92.7,
                "hle-tools": 54.0,
                "browsecomp": 83.2,
                "deepsearchqa-f1": 92.5,
                "toolathlon": 50.0,
                "livecodebench": 89.6,
                "mmmu-pro": 79.4,
                "mathvision-python": 93.2,
            }
        },
    },
    {
        "id": "kimi-k2-7-code-card",
        "label": "Kimi K2.7 Code official release",
        "url": KIMI_K27_CODE_URL,
        "rawUrl": KIMI_K27_CODE_URL,
        "category": "Official release",
        "note": "Moonshot AI Kimi.com release page and official model card for Kimi K2.7 Code with coding and agentic benchmark tables.",
        "columns": {
            "Kimi K2.6": "Kimi K2.6",
            "Kimi K2.7 Code": "Kimi K2.7 Code",
            "GPT-5.5": "GPT-5.5",
            "Claude Opus 4.8": "Claude Opus 4.8",
        },
        "textColumns": ["Kimi K2.6", "Kimi K2.7 Code", "GPT-5.5", "Claude Opus 4.8"],
        "rowLabels": {
            "Kimi Code Bench v2": "kimi-code-bench-v2",
            "Program Bench": "programbench",
            "ProgramBench": "programbench",
            "MLS Bench Lite": "mls-bench-lite",
            "Kimi Claw 24/7 Bench": "kimi-claw-24-7",
            "MCP Atlas": "mcp-atlas",
            "MCP-Atlas": "mcp-atlas",
            "MCP Mark Verified": "mcp-mark-verified",
            "MCPMark Verified": "mcp-mark-verified",
        },
        "scores": {
            "Kimi K2.7 Code": {
                "kimi-code-bench-v2": 62.0,
                "programbench": 53.6,
                "mls-bench-lite": 35.1,
                "kimi-claw-24-7": 46.9,
                "mcp-atlas": 76.0,
                "mcp-mark-verified": 81.1,
            }
        },
    },
    {
        "id": "kimi-k2-thinking-card",
        "label": "Kimi K2 Thinking official release",
        "url": KIMI_K2_THINKING_URL,
        "rawUrl": KIMI_K2_THINKING_URL,
        "category": "Official release",
        "note": "Moonshot AI official Kimi K2 Thinking release page with search, coding, and reasoning benchmarks.",
        "columns": {"K2 Thinking": "Kimi K2 Thinking"},
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "GPQA": "gpqa-diamond",
            "BrowseComp": "browsecomp",
            "SWE-bench Verified": "swe-bench-verified",
            "SWE-bench Multilingual": "swe-bench-multilingual",
            "SciCode": "scicode",
            "LiveCodeBenchV6": "livecodebench",
            "Terminal-Bench": "terminal-bench",
        },
        "scores": {
            "Kimi K2 Thinking": {
                "mmlu-pro": 84.6,
                "gpqa-diamond": 84.5,
                "browsecomp": 60.2,
                "hle-tools": 44.9,
                "swe-bench-verified": 71.3,
                "swe-bench-multilingual": 61.1,
                "scicode": 44.8,
                "livecodebench": 83.1,
                "terminal-bench": 47.1,
            }
        },
    },
    {
        "id": "kimi-k2-5-card",
        "label": "Kimi K2.5 official release",
        "url": KIMI_K25_URL,
        "rawUrl": KIMI_K25_URL,
        "category": "Official release",
        "note": "Moonshot AI Kimi.com K2.5 release page evaluation results.",
        "columns": {"Kimi K2.5": "Kimi K2.5"},
        "rowLabels": {
            "SWE Bench Resolved": "swe-bench-verified",
            "SWE Bench Pro": "swe-bench-pro",
            "Diamond": "gpqa-diamond",
            "Terminalbench 2": "terminal-bench-2",
            "MathArena Aime 2026": "aime-2026",
            "HLE-Full w/ tools": "hle-tools",
            "BrowseComp": "browsecomp",
            "LiveCodeBench v6": "livecodebench",
            "MMMU-Pro": "mmmu-pro",
        },
        "scores": {
            "Kimi K2.5": {
                "swe-bench-verified": 76.8,
                "swe-bench-pro": 50.7,
                "gpqa-diamond": 87.6,
                "terminal-bench-2": 50.8,
                "aime-2026": 95.83,
                "hle-tools": 50.2,
                "browsecomp": 74.9,
                "livecodebench": 85.0,
                "mmmu-pro": 78.5,
            }
        },
    },
    {
        "id": "kimi-k2-0905-card",
        "label": "Kimi K2 0905 official model card",
        "url": KIMI_K2_0905_URL,
        "rawUrl": KIMI_K2_0905_URL,
        "category": "Official model card",
        "note": "Moonshot AI official Hugging Face model card for Kimi-K2-Instruct-0905. Reported K2 0905 values are mean results over five full-test-set runs.",
        "columns": {"K2-Instruct-0905": "Kimi K2 0905", "Kimi-K2-Instruct-0905": "Kimi K2 0905"},
        "textColumns": ["K2-Instruct-0905"],
        "rowLabels": {
            "SWE-Bench verified": "swe-bench-verified",
            "SWE-Bench Multilingual": "swe-bench-multilingual",
            "Multi-SWE-Bench": "multi-swe-bench",
            "Terminal-Bench": "terminal-bench",
        },
        "scores": {
            "Kimi K2 0905": {
                "swe-bench-verified": 69.2,
                "swe-bench-multilingual": 55.9,
                "multi-swe-bench": 33.5,
                "terminal-bench": 44.5,
            }
        },
    },
    {
        "id": "kimi-k2-github",
        "label": "Kimi K2 official GitHub report",
        "url": KIMI_K2_URL,
        "rawUrl": KIMI_K2_URL,
        "category": "Official technical report",
        "note": "Moonshot AI Kimi K2 GitHub README and technical report benchmark table.",
        "columns": {"Kimi-K2-Instruct": "Kimi K2", "Kimi K2": "Kimi K2"},
        "rowLabels": {
            "SWE-bench Verified": "swe-bench-verified",
            "AIME 2024": "aime-2024",
            "GPQA-Diamond": "gpqa-diamond",
            "LiveCodeBench v6": "livecodebench",
        },
        "scores": {
            "Kimi K2": {
                "swe-bench-verified": 65.8,
                "aime-2024": 69.6,
                "gpqa-diamond": 75.1,
                "livecodebench": 53.7,
            }
        },
    },
    {
        "id": "zai-glm-4-6-card",
        "label": "Z.ai GLM-4.6 official model card",
        "url": GLM46_URL,
        "rawUrl": GLM46_URL,
        "category": "Official release",
        "note": "Z.ai developer documentation / GLM-4.6 release page. Seed values preserve the official benchmark image for agentic, reasoning, and coding evaluations.",
        "columns": {"GLM-4.6": "GLM-4.6"},
        "rowLabels": {
            "AIME 25": "aime-2025",
            "GPQA": "gpqa-diamond",
            "LiveCodeBench v6": "livecodebench",
            "HLE": "hle",
            "HLE w/ Tools": "hle-tools",
            "BrowseComp": "browsecomp",
            "SWE-bench Verified": "swe-bench-verified",
            "Terminal-Bench": "terminal-bench",
            "tau2-Bench": "tau2-bench-weighted",
        },
        "scores": {
            "GLM-4.6": {
                "aime-2025": 93.9,
                "gpqa-diamond": 81.0,
                "livecodebench": 82.8,
                "hle": 17.2,
                "hle-tools": 30.4,
                "browsecomp": 45.1,
                "swe-bench-verified": 68.0,
                "terminal-bench": 40.5,
                "tau2-bench-weighted": 75.9,
            }
        },
    },
    {
        "id": "zai-glm-5-2-card",
        "label": "Z.ai GLM-5.2 official model card",
        "url": GLM52_URL,
        "rawUrl": GLM52_HF_URL,
        "category": "Official release",
        "note": "Z.ai GLM-5.2 official page and model card with long-horizon reasoning, coding, and agentic benchmark table.",
        "columns": {
            "GLM-5.2": "GLM-5.2",
            "GLM-5.1": "GLM-5.1",
            "Qwen3.7-Max": "Qwen3.7-Max",
            "MiniMax M3": "MiniMax-M3",
            "DeepSeek-V4-Pro": "DeepSeek V4 Pro",
            "Claude Opus 4.8": "Claude Opus 4.8",
            "GPT-5.5": "GPT-5.5",
            "Gemini 3.1 Pro": "Gemini 3.1 Pro",
        },
        "textColumns": [
            "GLM-5.2",
            "GLM-5.1",
            "Qwen3.7-Max",
            "MiniMax M3",
            "DeepSeek-V4-Pro",
            "Claude Opus 4.8",
            "GPT-5.5",
            "Gemini 3.1 Pro",
        ],
        "rowLabels": {
            "HLE": "hle",
            "HLE (w/ Tools)": "hle-tools",
            "CritPt": "critpt",
            "AIME 2026": "aime-2026",
            "HMMT Nov. 2025": "hmmt-2025-nov",
            "HMMT Feb. 2026": "hmmt-2026-feb",
            "IMOAnswerBench": "imoanswerbench",
            "GPQA-Diamond": "gpqa-diamond",
            "SWE-bench Pro": "swe-bench-pro",
            "NL2Repo": "nl2repo",
            "DeepSWE": "deepswe",
            "ProgramBench": "programbench",
            "Terminal Bench 2.1 (Terminus-2)": "terminal-bench-2-1",
            "Terminal Bench 2.1 (Best Reported Harness)": "terminal-bench-2-1",
            "FrontierSWE (Dominance)": "frontierswe-dominance",
            "PostTrainBench": "posttrainbench",
            "SWE-Marathon": "swe-marathon",
            "MCP-Atlas (Public Set)": "mcp-atlas",
            "Tool-Decathlon": "toolathlon",
        },
        "scores": {
            "GLM-5.2": {
                "hle": 40.5,
                "hle-tools": 54.7,
                "critpt": 20.9,
                "aime-2026": 99.2,
                "hmmt-2025-nov": 94.4,
                "hmmt-2026-feb": 92.5,
                "imoanswerbench": 91.0,
                "gpqa-diamond": 91.2,
                "swe-bench-pro": 62.1,
                "nl2repo": 48.9,
                "deepswe": 46.2,
                "programbench": 63.7,
                "terminal-bench-2-1": 81.0,
                "frontierswe-dominance": 74.4,
                "posttrainbench": 34.3,
                "swe-marathon": 13.0,
                "mcp-atlas": 76.8,
                "toolathlon": 48.2,
            }
        },
    },
    {
        "id": "zai-glm-5-1-card",
        "label": "Z.ai GLM-5.1 official model card",
        "url": GLM51_URL,
        "rawUrl": GLM51_URL,
        "category": "Official release",
        "note": "Z.ai developer documentation / official release page with GLM-5.1, GLM-5, and GLM-4.7 benchmark table.",
        "columns": {
            "GLM-5.1": "GLM-5.1",
            "GLM-5": "GLM-5",
            "GLM-4.7": "GLM-4.7",
        },
        "rowLabels": {
            "HLE": "hle",
            "HLE (w/ Tools)": "hle-tools",
            "AIME 2026": "aime-2026",
            "HMMT Feb. 2026": "hmmt-2026-feb",
            "GPQA-Diamond": "gpqa-diamond",
            "SWE-Bench Pro": "swe-bench-pro",
            "SWE-bench Verified": "swe-bench-verified",
            "SWE-bench Multilingual": "swe-bench-multilingual",
            "NL2Repo": "nl2repo",
            "Terminal-Bench 2.0 (Terminus-2)": "terminal-bench-2",
            "Terminal-Bench 2.0 (Terminus 2)": "terminal-bench-2",
            "CyberGym": "cybergym",
            "BrowseComp": "browsecomp",
            "BrowseComp (w/ Context Manage)": "browsecomp-context",
            "MCP-Atlas (Public Set)": "mcp-atlas",
            "Tool-Decathlon": "toolathlon",
        },
        "scores": {
            "GLM-5.1": {
                "hle": 31.0,
                "hle-tools": 52.3,
                "aime-2026": 95.3,
                "hmmt-2026-feb": 82.6,
                "gpqa-diamond": 86.2,
                "swe-bench-pro": 58.4,
                "nl2repo": 42.7,
                "terminal-bench-2": 63.5,
                "cybergym": 68.7,
                "browsecomp": 68.0,
                "browsecomp-context": 79.3,
                "mcp-atlas": 71.8,
                "toolathlon": 40.7,
            },
            "GLM-5": {
                "hle": 30.5,
                "hle-tools": 50.4,
                "aime-2026": 95.4,
                "hmmt-2026-feb": 82.8,
                "gpqa-diamond": 86.0,
                "swe-bench-pro": 55.1,
                "nl2repo": 35.9,
                "terminal-bench-2": 56.2,
                "cybergym": 48.3,
                "browsecomp": 62.0,
                "browsecomp-context": 75.9,
                "mcp-atlas": 69.2,
                "toolathlon": 38.0,
            },
            "GLM-4.7": {
                "hle": 24.8,
                "hle-tools": 42.8,
                "aime-2026": 92.9,
                "gpqa-diamond": 85.7,
                "swe-bench-verified": 73.8,
                "swe-bench-multilingual": 66.7,
                "terminal-bench-2": 41.0,
                "cybergym": 23.5,
                "browsecomp": 52.0,
                "browsecomp-context": 67.5,
                "mcp-atlas": 52.0,
                "toolathlon": 23.8,
            },
        },
    },
    {
        "id": "zai-glm-4-5-report",
        "label": "Z.ai GLM-4.5 official report",
        "url": GLM45_URL,
        "rawUrl": GLM45_RAW_URL,
        "category": "Official technical report",
        "note": "Z.ai GLM-4.5 official blog/report covering ARC benchmarks.",
        "columns": {"GLM-4.5": "GLM-4.5", "GLM-4.5-Air": "GLM-4.5-Air"},
        "rowLabels": {
            "MMLU Pro": "mmlu-pro",
            "MMLU-Pro": "mmlu-pro",
            "AIME 24": "aime-2024",
            "SciCode": "scicode",
            "GPQA": "gpqa-diamond",
            "HLE": "hle",
            "LCB": "livecodebench",
            "SWE-bench Verified": "swe-bench-verified",
            "Terminal-Bench": "terminal-bench",
            "TAU-Bench": "tau-bench",
            "BFCL V3": "bfcl-v3",
            "BrowseComp": "browsecomp",
        },
        "scores": {
            "GLM-4.5": {
                "mmlu-pro": 84.6,
                "aime-2024": 91.0,
                "scicode": 41.7,
                "gpqa-diamond": 79.1,
                "hle": 14.4,
                "livecodebench": 72.9,
                "swe-bench-verified": 64.2,
                "terminal-bench": 37.5,
                "tau-bench": 70.1,
                "bfcl-v3": 77.8,
                "browsecomp": 26.4,
            },
            "GLM-4.5-Air": {
                "mmlu-pro": 81.4,
                "aime-2024": 89.4,
                "scicode": 37.3,
                "gpqa-diamond": 75.0,
                "hle": 10.6,
                "livecodebench": 70.7,
                "swe-bench-verified": 57.6,
                "terminal-bench": 30.0,
            },
        },
    },
    {
        "id": "google-gemini-3-1-pro-card",
        "label": "Google DeepMind Gemini 3.1 Pro model card",
        "url": GOOGLE_GEMINI31_URL,
        "rawUrl": GOOGLE_GEMINI31_URL,
        "category": "Official model card",
        "note": "Google DeepMind model card with cross-model benchmark context and Gemini 3.1 Pro results.",
        "columns": {"Gemini 3.1 Pro": "Gemini 3.1 Pro", "Gemini 3.1 Pro Preview": "Gemini 3.1 Pro"},
        "rowLabels": {
            "ARC-AGI-2": "arc-agi-2",
            "GPQA Diamond": "gpqa-diamond",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "SWE-Bench Verified": "swe-bench-verified",
            "SWE-Bench Pro (Public)": "swe-bench-pro",
            "LiveCodeBench Pro": "livecodebench-pro-elo",
            "SciCode": "scicode",
            "APEX-Agents": "apex-agents",
            "GDPval-AA Elo": "gdpval-aa-elo",
            "Retail": "tau2-bench-retail",
            "Telecom": "tau2-bench-telecom",
            "MCP Atlas": "mcp-atlas",
            "BrowseComp": "browsecomp",
            "MMMU-Pro": "mmmu-pro",
            "MMMLU": "mmmlu",
            "MRCR v2 (8-needle) 128k": "mrcr-v2-128k",
            "MRCR v2 (8-needle) 1M": "mrcr-v2-1m",
        },
        "scores": {
            "Gemini 3.1 Pro": {
                "arc-agi-2": 77.1,
                "gpqa-diamond": 94.3,
                "terminal-bench-2": 68.5,
                "swe-bench-verified": 80.6,
                "swe-bench-pro": 54.2,
                "livecodebench-pro-elo": 2887,
                "scicode": 59.0,
                "apex-agents": 33.5,
                "gdpval-aa-elo": 1317,
                "tau2-bench-retail": 90.8,
                "tau2-bench-telecom": 99.3,
                "mcp-atlas": 69.2,
                "browsecomp": 85.9,
                "mmmu-pro": 80.5,
                "mmmlu": 92.6,
                "mrcr-v2-128k": 84.9,
                "mrcr-v2-1m": 26.3,
            }
        },
    },
    {
        "id": "google-gemma-4-card",
        "label": "Google Gemma 4 official model card",
        "url": GOOGLE_GEMMA4_URL,
        "rawUrl": GOOGLE_GEMMA4_URL,
        "category": "Official model card",
        "note": "Google Gemma model card covering Gemma 4 31B, 26B-A4B, E4B, and E2B instruction-tuned benchmarks.",
        "columns": {
            "31B": "Gemma 4 31B",
            "Gemma 4 31B": "Gemma 4 31B",
            "26B A4B": "Gemma 4 26B A4B",
            "Gemma 4 26B A4B": "Gemma 4 26B A4B",
            "E4B": "Gemma 4 E4B",
            "Gemma 4 E4B": "Gemma 4 E4B",
            "E2B": "Gemma 4 E2B",
            "Gemma 4 E2B": "Gemma 4 E2B",
        },
        "rowLabels": {
            "MMLU Pro": "mmlu-pro",
            "MMLU-Pro": "mmlu-pro",
            "GPQA Diamond": "gpqa-diamond",
            "BigBench Extra Hard": "bigbench-extra-hard",
            "AIME 2026": "aime-2026",
            "MMMLU": "mmmlu",
            "LiveCodeBench v6": "livecodebench",
            "Codeforces ELO": "codeforces-elo",
        },
        "scores": {
            "Gemma 4 31B": {
                "mmlu-pro": 85.2,
                "gpqa-diamond": 84.3,
                "bigbench-extra-hard": 74.4,
                "aime-2026": 89.2,
                "mmmlu": 88.4,
                "livecodebench": 80.0,
                "codeforces-elo": 2150,
            },
            "Gemma 4 26B A4B": {
                "mmlu-pro": 82.6,
                "gpqa-diamond": 82.3,
                "bigbench-extra-hard": 64.8,
                "aime-2026": 88.3,
                "mmmlu": 86.3,
                "livecodebench": 77.1,
                "codeforces-elo": 1718,
            },
            "Gemma 4 E4B": {
                "mmlu-pro": 69.4,
                "gpqa-diamond": 58.6,
                "bigbench-extra-hard": 33.1,
                "aime-2026": 42.5,
                "mmmlu": 76.6,
                "livecodebench": 52.0,
                "codeforces-elo": 940,
            },
            "Gemma 4 E2B": {
                "mmlu-pro": 60.0,
                "gpqa-diamond": 43.4,
                "bigbench-extra-hard": 21.9,
                "aime-2026": 37.5,
                "mmmlu": 67.4,
                "livecodebench": 44.0,
            },
        },
    },
    {
        "id": "minimax-m3-release",
        "label": "MiniMax M3 official release",
        "url": MINIMAX_M3_URL,
        "rawUrl": MINIMAX_M3_URL,
        "category": "Official release",
        "note": "MiniMax M3 official model page. Seed rows use text-visible values for BrowseComp and PostTrainBench; other chart-only values are left for parser/OCR follow-up.",
        "columns": {"MiniMax M3": "MiniMax-M3", "MiniMax-M3": "MiniMax-M3"},
        "rowLabels": {
            "BrowseComp": "browsecomp",
            "PostTrainBench": "posttrainbench",
        },
        "scores": {
            "MiniMax-M3": {
                "browsecomp": 83.5,
                "posttrainbench": 37.1,
            }
        },
    },
    {
        "id": "minimax-m2-7-report",
        "label": "MiniMax M2.7 technical report",
        "url": MINIMAX_M27_REPORT_URL,
        "rawUrl": MINIMAX_M27_REPORT_URL,
        "category": "Official technical report",
        "note": "MiniMax M2 series technical report with M2.7 headline values across agentic coding, agentic cowork, and reasoning/knowledge. GDPval-AA is omitted from seeds because this dataset's GDPval-AA slot is Elo-based, while the report value is a percentage.",
        "columns": {"MiniMax-M2.7": "MiniMax-M2.7", "MiniMax M2.7": "MiniMax-M2.7"},
        "rowLabels": {
            "SWE-bench Pro": "swe-bench-pro",
            "SWE-bench Multilingual": "swe-bench-multilingual",
            "Multi-SWE-bench": "multi-swe-bench",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "BrowseComp": "browsecomp",
            "Toolathlon": "toolathlon",
            "AIME 2026": "aime-2026",
            "GPQA-Diamond": "gpqa-diamond",
        },
        "scores": {
            "MiniMax-M2.7": {
                "swe-bench-pro": 56.2,
                "swe-bench-multilingual": 76.5,
                "multi-swe-bench": 52.7,
                "terminal-bench-2": 57.0,
                "browsecomp": 77.8,
                "toolathlon": 46.3,
                "aime-2026": 94.2,
                "gpqa-diamond": 89.8,
            }
        },
    },
    {
        "id": "minimax-m2-5-release",
        "label": "MiniMax M2.5 official release",
        "url": MINIMAX_M25_URL,
        "rawUrl": MINIMAX_M25_URL,
        "category": "Official release",
        "note": "MiniMax M2.5 release page with official benchmark charts for M2.5 and M2.1 across agentic coding and reasoning evaluations.",
        "columns": {
            "MiniMax-M2.5": "MiniMax-M2.5",
            "MiniMax M2.5": "MiniMax-M2.5",
            "MiniMax-M2.1": "MiniMax-M2.1",
            "MiniMax M2.1": "MiniMax-M2.1",
        },
        "rowLabels": {
            "SWE-Bench Verified": "swe-bench-verified",
            "SWE-Bench Pro": "swe-bench-pro",
            "Terminal Bench 2": "terminal-bench-2",
            "Multi-SWE-Bench": "multi-swe-bench",
            "SWE-Bench Multilingual": "swe-bench-multilingual",
            "AIME25": "aime-2025",
            "GPQA-D": "gpqa-diamond",
            "HLE w/o tools": "hle",
            "SciCode": "scicode",
            "IFBench": "ifbench",
            "AA-LCR": "aa-lcr",
        },
        "scores": {
            "MiniMax-M2.5": {
                "swe-bench-verified": 80.2,
                "swe-bench-pro": 55.4,
                "terminal-bench-2": 51.7,
                "multi-swe-bench": 51.3,
                "swe-bench-multilingual": 74.1,
                "aime-2025": 86.3,
                "gpqa-diamond": 85.2,
                "hle": 19.4,
                "scicode": 44.4,
                "ifbench": 70.0,
                "aa-lcr": 69.5,
            },
            "MiniMax-M2.1": {
                "swe-bench-verified": 74.0,
                "swe-bench-pro": 49.7,
                "terminal-bench-2": 47.9,
                "multi-swe-bench": 47.2,
                "swe-bench-multilingual": 71.9,
                "aime-2025": 83.0,
                "gpqa-diamond": 83.0,
                "hle": 22.2,
                "scicode": 41.0,
                "ifbench": 70.0,
                "aa-lcr": 62.0,
            },
        },
    },
    {
        "id": "minimax-m2-release",
        "label": "MiniMax M2 official release",
        "url": MINIMAX_M2_URL,
        "rawUrl": MINIMAX_M2_URL,
        "category": "Official release",
        "note": "MiniMax M2 release page with official agentic benchmark charts. Seed rows keep the chart values where the page renders the data as images.",
        "columns": {"MiniMax-M2": "MiniMax-M2", "MiniMax M2": "MiniMax-M2"},
        "rowLabels": {
            "SWE-bench Verified": "swe-bench-verified",
            "Multi-SWE-Bench": "multi-swe-bench",
            "Terminal-Bench": "terminal-bench",
            "BrowseComp": "browsecomp",
        },
        "scores": {
            "MiniMax-M2": {
                "swe-bench-verified": 69.4,
                "multi-swe-bench": 36.2,
                "terminal-bench": 46.3,
                "browsecomp": 44.0,
            }
        },
    },
    {
        "id": "minimax-m1-card",
        "label": "MiniMax M1 official GitHub report",
        "url": MINIMAX_M1_URL,
        "rawUrl": MINIMAX_M1_URL,
        "category": "Official technical report",
        "note": "MiniMax-AI official GitHub README benchmark table for MiniMax-M1-80K and MiniMax-M1-40K.",
        "columns": {
            "MiniMax-M1-80K": "MiniMax M1 80k",
            "MiniMax-M1-80k": "MiniMax M1 80k",
            "MiniMax-M1-40K": "MiniMax M1 40k",
            "MiniMax-M1-40k": "MiniMax M1 40k",
        },
        "rowLabels": {
            "AIME 2024": "aime-2024",
            "AIME 2025": "aime-2025",
            "LiveCodeBench": "livecodebench",
            "FullStackBench": "fullstackbench",
            "GPQA Diamond": "gpqa-diamond",
            "HLE": "hle",
            "MMLU-Pro": "mmlu-pro",
            "SWE-bench Verified": "swe-bench-verified",
            "TAU-bench (airline)": "tau-bench-airline",
            "TAU-bench (retail)": "tau-bench-retail",
        },
        "scores": {
            "MiniMax M1 80k": {
                "aime-2024": 86.0,
                "aime-2025": 76.9,
                "livecodebench": 65.0,
                "fullstackbench": 68.3,
                "gpqa-diamond": 70.0,
                "hle": 8.4,
                "mmlu-pro": 81.1,
                "swe-bench-verified": 56.0,
                "tau-bench-airline": 62.0,
                "tau-bench-retail": 63.5,
            },
            "MiniMax M1 40k": {
                "aime-2024": 83.3,
                "aime-2025": 74.6,
                "livecodebench": 62.3,
                "fullstackbench": 67.6,
                "gpqa-diamond": 69.2,
                "hle": 7.2,
                "mmlu-pro": 80.6,
                "swe-bench-verified": 55.6,
                "tau-bench-airline": 60.0,
                "tau-bench-retail": 67.8,
            },
        },
    },
    {
        "id": "xiaomi-mimo-v2-5-release",
        "label": "Xiaomi MiMo-V2.5 official release",
        "url": XIAOMI_MIMO25_URL,
        "rawUrl": XIAOMI_MIMO25_URL,
        "category": "Official release",
        "note": "Xiaomi MiMo official release/open-source page. Seed rows retain official benchmark values when the page renders charts as images.",
        "columns": {"mimo-v2.5-pro": "MiMo-V2.5-Pro", "MiMo-V2.5-Pro": "MiMo-V2.5-Pro"},
        "rowLabels": {
            "SWE Bench Resolved": "swe-bench-verified",
            "SWE-Bench Verified": "swe-bench-verified",
            "SWE Bench Pro": "swe-bench-pro",
            "SWE-Bench Pro": "swe-bench-pro",
            "Terminalbench 2": "terminal-bench-2",
            "Terminal-Bench 2.0": "terminal-bench-2",
            "Diamond": "gpqa-diamond",
            "MMLU Pro": "mmlu-pro",
            "General": "claw-eval",
        },
        "scores": {
            "MiMo-V2.5-Pro": {
                "swe-bench-verified": 78.9,
                "swe-bench-pro": 57.2,
                "terminal-bench-2": 68.4,
                "gpqa-diamond": 66.7,
                "mmlu-pro": 68.5,
                "claw-eval": 64.0,
            }
        },
    },
    {
        "id": "cohere-north-mini-code-card",
        "label": "Cohere North Mini Code model card",
        "url": COHERE_NORTH_MINI_CODE_URL,
        "rawUrl": COHERE_NORTH_MINI_CODE_URL,
        "category": "Official model card",
        "coverage": "North Mini Code reference",
        "scoreStatus": "reference",
        "modelAliases": MODEL_ALIASES["North Mini Code"],
        "note": (
            "Cohere documentation for North Mini Code: model ID north-mini-code-1-0, "
            "256K context window, 64K max output, Apache 2.0 license, and agentic coding use cases."
        ),
    },
    {
        "id": "xai-grok-4-1-fast-release",
        "label": "xAI Grok 4.1 Fast official release",
        "url": XAI_GROK41_FAST_URL,
        "rawUrl": XAI_GROK41_FAST_URL,
        "category": "Official release",
        "note": "xAI release page for Grok 4.1 Fast and Agent Tools API with tool-calling and agentic-search benchmark tables.",
        "columns": {
            "Grok 4.1 Fast": "Grok 4.1 Fast",
            "Grok 4.1 Fast Agent Tools API": "Grok 4.1 Fast",
        },
        "rowLabels": {
            "τ²-bench Telecom": "tau2-bench-telecom",
            "Berkeley Function Calling v4 Benchmark": "bfcl-v4",
            "Research-Eval Reka": "research-eval-reka",
            "FRAMES": "frames",
            "X Browse": "x-browse",
        },
        "scores": {
            "Grok 4.1 Fast": {
                "tau2-bench-telecom": 100.0,
                "bfcl-v4": 72.0,
                "research-eval-reka": 63.9,
                "frames": 87.6,
                "x-browse": 56.3,
            }
        },
    },
    {
        "id": "nvidia-nemotron-3-super-report",
        "label": "NVIDIA Nemotron 3 Super technical report",
        "url": NVIDIA_NEMOTRON3_SUPER_URL,
        "rawUrl": NVIDIA_NEMOTRON3_SUPER_URL,
        "category": "Official technical report",
        "note": "NVIDIA Research technical report for Nemotron 3 Super. Seed rows preserve the BF16 evaluation suite from the published PDF table.",
        "columns": {
            "N-3-Super": "NVIDIA Nemotron 3 Super [R]",
            "Nemotron 3 Super": "NVIDIA Nemotron 3 Super [R]",
        },
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "GPQA (no tools)": "gpqa-diamond",
            "LiveCodeBench (v6 2024-08↔2025-05)": "livecodebench",
            "SciCode (subtask)": "scicode",
            "HLE (no tools)": "hle",
            "Terminal Bench (hard subset)": "terminal-bench-hard",
            "TauBench V2 Airline": "tau2-bench-airline",
            "TauBench V2 Retail": "tau2-bench-retail",
            "TauBench V2 Telecom": "tau2-bench-telecom",
            "TauBench V2 Average": "tau2-bench-average",
            "IFBench (prompt)": "ifbench",
            "Scale AI Multi-Challenge": "multi-challenge",
            "AA-LCR": "aa-lcr",
            "RULER 1M": "ruler-1m",
            "MMLU-ProX": "mmlu-prox",
        },
        "scores": {
            "NVIDIA Nemotron 3 Super [R]": {
                "mmlu-pro": 83.73,
                "gpqa-diamond": 79.23,
                "livecodebench": 78.69,
                "scicode": 42.05,
                "hle": 18.26,
                "terminal-bench-hard": 25.78,
                "tau2-bench-airline": 56.25,
                "tau2-bench-retail": 62.83,
                "tau2-bench-telecom": 64.36,
                "tau2-bench-average": 61.15,
                "ifbench": 72.58,
                "multi-challenge": 55.23,
                "aa-lcr": 58.31,
                "ruler-1m": 91.64,
                "mmlu-prox": 79.35,
            }
        },
    },
    {
        "id": "nvidia-nemotron-3-nano-report",
        "label": "NVIDIA Nemotron 3 Nano technical report",
        "url": NVIDIA_NEMOTRON3_NANO_URL,
        "rawUrl": NVIDIA_NEMOTRON3_NANO_URL,
        "category": "Official technical report",
        "note": "NVIDIA Research technical report for Nemotron 3 Nano. Seed rows preserve the BF16 evaluation suite from the published PDF table.",
        "columns": {
            "N-3-Nano BF16": "NVIDIA Nemotron 3 Nano [R]",
            "N-3-Nano": "NVIDIA Nemotron 3 Nano [R]",
        },
        "rowLabels": {
            "MMLU-Pro": "mmlu-pro",
            "AIME25 (no tools)": "aime-2025",
            "GPQA (no tools)": "gpqa-diamond",
            "LiveCodeBench (v6 2024-08↔2025-05)": "livecodebench",
            "SciCode (subtask)": "scicode",
            "HLE (no tools)": "hle",
            "HLE (with tools)": "hle-tools",
            "TauBench V2 Airline": "tau2-bench-airline",
            "TauBench V2 Retail": "tau2-bench-retail",
            "TauBench V2 Telecom": "tau2-bench-telecom",
            "TauBench V2 Average": "tau2-bench-average",
            "BFCL v4": "bfcl-v4",
            "IFBench (prompt)": "ifbench",
            "AA-LCR": "aa-lcr",
            "MMLU-ProX": "mmlu-prox",
        },
        "scores": {
            "NVIDIA Nemotron 3 Nano [R]": {
                "mmlu-pro": 78.30,
                "aime-2025": 89.06,
                "gpqa-diamond": 73.04,
                "livecodebench": 68.25,
                "scicode": 33.28,
                "hle": 10.57,
                "hle-tools": 15.48,
                "tau2-bench-airline": 48.00,
                "tau2-bench-retail": 56.91,
                "tau2-bench-telecom": 42.21,
                "tau2-bench-average": 49.04,
                "bfcl-v4": 53.76,
                "ifbench": 71.51,
                "aa-lcr": 35.85,
                "mmlu-prox": 59.50,
            }
        },
    },
    {
        "id": "nvidia-nemotron-3-ultra-report",
        "label": "NVIDIA Nemotron 3 Ultra technical report",
        "url": NVIDIA_NEMOTRON3_ULTRA_URL,
        "rawUrl": NVIDIA_NEMOTRON3_ULTRA_URL,
        "category": "Official technical report",
        "note": "NVIDIA Research technical report for Nemotron 3 Ultra. The PDF is kept as the official source and seed rows preserve the published benchmark table.",
        "columns": {"N-3-Ultra": "Nemotron 3 Ultra", "Nemotron 3 Ultra": "Nemotron 3 Ultra"},
        "rowLabels": {
            "Terminal Bench 2.1": "terminal-bench-2-1",
            "SWE-Bench Verifeid": "swe-bench-verified",
            "SWE-Bench Verified": "swe-bench-verified",
            "SWE-Bench Multilingual": "swe-bench-multilingual",
            "BrowseComp": "browsecomp",
            "LiveCodeBench (v6)": "livecodebench",
            "GPQA (no tools)": "gpqa-diamond",
            "SciCode (subtask)": "scicode",
            "HLE (no tools)": "hle",
            "HLE (with tools)": "hle-tools",
            "MMLU-Pro": "mmlu-pro",
            "PinchBench": "pinchbench",
            "TauBench V3 Average": "taubench-v3-average",
            "IFBench (prompt loose)": "ifbench-prompt-loose",
            "Multi-Challenge": "multi-challenge",
            "RULER (1M)": "ruler-1m",
            "Longbench v2": "longbench-v2-1m",
            "MMLU-ProX": "mmlu-prox",
            "WMT24++": "wmt24-plusplus",
        },
        "scores": {
            "Nemotron 3 Ultra": {
                "terminal-bench-2-1": 56.4,
                "swe-bench-verified": 71.9,
                "swe-bench-multilingual": 67.7,
                "browsecomp": 44.4,
                "livecodebench": 89.0,
                "gpqa-diamond": 87.0,
                "scicode": 44.6,
                "hle": 26.7,
                "hle-tools": 37.4,
                "mmlu-pro": 86.8,
                "pinchbench": 90.0,
                "taubench-v3-average": 70.9,
                "ifbench-prompt-loose": 81.7,
                "multi-challenge": 63.8,
                "ruler-1m": 94.7,
                "longbench-v2-1m": 61.9,
                "mmlu-prox": 83.0,
                "wmt24-plusplus": 83.7,
            }
        },
    },
]


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tokens: list[str] = []

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if text:
            self.tokens.append(text)


class _HTMLTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            if self._table_depth == 0:
                self._current_table = []
            self._table_depth += 1
        elif self._table_depth and tag == "tr":
            self._current_row = []
        elif self._table_depth and tag in {"td", "th"}:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._current_cell is not None:
            self._current_cell.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._current_cell is not None:
            self._current_cell.append(f"&#{name};")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append(_clean_markdown_cell(" ".join(self._current_cell)))
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if any(cell for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_depth:
            self._table_depth -= 1
            if self._table_depth == 0 and self._current_table:
                self.tables.append(self._current_table)
                self._current_table = None


def fetch_html(url: str, timeout: float = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_openai_scores(html: str) -> dict[str, list[float | None]]:
    tokens = visible_text_tokens(html)
    try:
        start = tokens.index("Evaluations")
        tokens = tokens[start:]
    except ValueError:
        pass

    scores: dict[str, list[float | None]] = {}
    for benchmark in BENCHMARKS:
        label = benchmark.get("openaiLabel")
        if not label:
            continue
        index = _find_label_index(tokens, label)
        if index is None:
            continue
        values = _next_percent_values(tokens[index + 1 :], len(OPENAI_MODEL_COLUMNS))
        if len(values) == len(OPENAI_MODEL_COLUMNS):
            scores[benchmark["id"]] = values
    return scores


def visible_text_tokens(html: str) -> list[str]:
    parser = _VisibleTextParser()
    parser.feed(html)
    return parser.tokens


def build_payload(
    openai_scores: dict[str, list[float | None]],
    collection_status: str,
    source_statuses: dict[str, str] | None = None,
    official_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    benchmarks = [
        {key: value for key, value in benchmark.items() if key != "openaiLabel"}
        for benchmark in BENCHMARKS
    ]
    source_statuses = source_statuses or {}
    source = {
        "id": "openai-gpt-5-5",
        "label": "OpenAI GPT-5.5 launch evaluations",
        "url": OPENAI_GPT55_URL,
        "category": "Official model release",
        "collectionStatus": collection_status,
        "note": "Official OpenAI table covering GPT-5.5, GPT-5.4, GPT-5.5 Pro, GPT-5.4 Pro, Claude Opus 4.7, and Gemini 3.1 Pro.",
    }
    additional_sources = []
    for spec in OFFICIAL_SOURCE_SPECS:
        official_source = {
            "id": spec["id"],
            "label": spec["label"],
            "url": spec["url"],
            "category": spec.get("category") or "Official model card",
            "collectionStatus": source_statuses.get(spec["id"], "seeded-official-values"),
            "note": spec.get("note") or "",
        }
        for key in ("coverage", "focus", "scoreStatus", "modelAliases", "modelKeys"):
            if spec.get(key):
                official_source[key] = spec[key]
        additional_sources.append(official_source)
    results = []
    for benchmark in BENCHMARKS:
        values = openai_scores.get(benchmark["id"], SEED_OPENAI_VALUES.get(benchmark["id"], []))
        for model_name, value in zip(OPENAI_MODEL_COLUMNS, values):
            if value is None:
                continue
            results.append(
                {
                    "benchmarkId": benchmark["id"],
                    "benchmarkLabel": benchmark["label"],
                    "model": model_name,
                    "modelAliases": MODEL_ALIASES.get(model_name, [model_name]),
                    "value": value,
                    "unit": benchmark["unit"],
                    "sourceId": source["id"],
                    "sourceUrl": source["url"],
                    "sourceLabel": source["label"],
                }
            )
    results.extend(official_results if official_results is not None else official_seed_results())

    return {
        "version": 1,
        "generatedAt": generated_at,
        "sources": [source, *additional_sources],
        "benchmarks": benchmarks,
        "results": results,
    }


def collect(timeout: float = 30) -> dict[str, Any]:
    try:
        html = fetch_html(OPENAI_GPT55_URL, timeout=timeout)
        parsed = parse_openai_scores(html)
    except (HTTPError, URLError, TimeoutError, OSError, IncompleteRead) as exc:
        official_results, source_statuses = collect_official_sources(timeout=timeout)
        return build_payload(
            SEED_OPENAI_VALUES,
            f"seeded-official-values; refresh blocked: {exc.__class__.__name__}",
            source_statuses,
            official_results,
        )

    missing = {benchmark["id"] for benchmark in BENCHMARKS} - set(parsed)
    if missing:
        merged = {**SEED_OPENAI_VALUES, **parsed}
        openai_status = f"partial-refresh; seeded {len(missing)} benchmark rows"
    else:
        merged = parsed
        openai_status = "refreshed"

    official_results, source_statuses = collect_official_sources(timeout=timeout)
    return build_payload(merged, openai_status, source_statuses, official_results)


def collect_official_sources(timeout: float = 30) -> tuple[list[dict[str, Any]], dict[str, str]]:
    results: list[dict[str, Any]] = []
    statuses: dict[str, str] = {}
    for spec in OFFICIAL_SOURCE_SPECS:
        seed_rows = official_seed_results_for_source(spec)
        try:
            text = fetch_html(str(spec.get("rawUrl") or spec["url"]), timeout=timeout)
            parsed_rows = parse_markdown_source_scores(text, spec)
        except (HTTPError, URLError, TimeoutError, OSError, IncompleteRead) as exc:
            results.extend(seed_rows)
            status_prefix = "seeded-official-values" if seed_rows else "reference-only"
            statuses[spec["id"]] = f"{status_prefix}; refresh blocked: {exc.__class__.__name__}"
            continue

        if parsed_rows:
            merged_rows = merge_result_rows(seed_rows, parsed_rows)
            statuses[spec["id"]] = (
                "refreshed"
                if len(parsed_rows) >= len(seed_rows)
                else f"partial-refresh; parsed {len(parsed_rows)} of {len(seed_rows)} seeded scores"
            )
            results.extend(merged_rows)
        elif seed_rows:
            results.extend(seed_rows)
            statuses[spec["id"]] = "seeded-official-values; no parseable benchmark table found"
        else:
            statuses[spec["id"]] = "reference-only; no parseable benchmark table found"
    return results, statuses


def official_seed_results() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in OFFICIAL_SOURCE_SPECS:
        results.extend(official_seed_results_for_source(spec))
    return results


def official_seed_results_for_source(spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scores_by_model = spec.get("scores", {})
    for model_name, scores in scores_by_model.items():
        for benchmark_id, value in scores.items():
            rows.append(_result_row(spec, str(model_name), str(benchmark_id), value))
    return rows


def merge_result_rows(
    seed_rows: list[dict[str, Any]],
    parsed_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = {
        (row.get("sourceId"), row.get("model"), row.get("benchmarkId")): row
        for row in seed_rows
    }
    for row in parsed_rows:
        merged[(row.get("sourceId"), row.get("model"), row.get("benchmarkId"))] = row
    return list(merged.values())


def parse_markdown_source_scores(text: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
    column_model_by_key = {
        _normalize_label(column): model
        for column, model in spec.get("columns", {}).items()
    }
    benchmark_by_key = {
        _normalize_label(label): benchmark_id
        for label, benchmark_id in spec.get("rowLabels", {}).items()
    }
    results: list[dict[str, Any]] = []
    for table in html_tables(text) + markdown_tables(text):
        if not table:
            continue
        header = table[0]
        column_indexes = {
            index: column_model_by_key[_normalize_label(cell)]
            for index, cell in enumerate(header)
            if _normalize_label(cell) in column_model_by_key
        }
        if not column_indexes:
            continue
        for row in table[1:]:
            if not row:
                continue
            benchmark_id = _benchmark_id_from_row(row, benchmark_by_key)
            if not benchmark_id:
                continue
            for index, model_name in column_indexes.items():
                if index >= len(row):
                    continue
                value = _numeric_cell(row[index])
                if value is None:
                    continue
                results.append(_result_row(spec, model_name, benchmark_id, value))
    if not results and spec.get("textColumns"):
        results.extend(parse_plain_text_source_scores(text, spec))
    return dedupe_result_rows(results)


def parse_plain_text_source_scores(text: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
    text_columns = [str(column) for column in spec.get("textColumns", [])]
    column_models = [spec.get("columns", {}).get(column) for column in text_columns]
    if not any(column_models):
        return []
    results: list[dict[str, Any]] = []
    row_labels = sorted(spec.get("rowLabels", {}).items(), key=lambda item: len(item[0]), reverse=True)
    for raw_line in text.splitlines():
        line = _clean_markdown_cell(raw_line)
        if not line:
            continue
        for label, benchmark_id in row_labels:
            tail = _line_tail_after_label(line, label)
            if tail is None:
                continue
            values = [_numeric_cell(match.group(0)) for match in re.finditer(r"-?\d+(?:,\d{3})*(?:\.\d+)?", tail)]
            values = [value for value in values if value is not None]
            if len(values) < len(column_models):
                continue
            for index, model_name in enumerate(column_models):
                if not model_name:
                    continue
                results.append(_result_row(spec, str(model_name), str(benchmark_id), values[index]))
            break
    return results


def markdown_tables(text: str) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [_clean_markdown_cell(cell) for cell in stripped.strip("|").split("|")]
            if _is_markdown_separator(cells):
                continue
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def html_tables(text: str) -> list[list[list[str]]]:
    if "<table" not in text.lower():
        return []
    parser = _HTMLTableParser()
    parser.feed(text)
    return parser.tables


def dedupe_result_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for row in rows:
        deduped[(row.get("sourceId"), row.get("model"), row.get("benchmarkId"))] = row
    return list(deduped.values())


def _benchmark_id_from_row(row: list[str], benchmark_by_key: dict[str, str]) -> str | None:
    for cell in row[:2]:
        key = _normalize_label(cell)
        if key in benchmark_by_key:
            return benchmark_by_key[key]
        for benchmark_key, benchmark_id in sorted(benchmark_by_key.items(), key=lambda item: len(item[0]), reverse=True):
            if benchmark_key and (key.startswith(benchmark_key) or benchmark_key in key):
                return benchmark_id
    return None


def _line_tail_after_label(line: str, label: str) -> str | None:
    index = line.lower().find(label.lower())
    if index >= 0:
        return line[index + len(label) :]
    normalized_line = _normalize_label(line)
    normalized_label = _normalize_label(label)
    if normalized_line.startswith(normalized_label):
        return line
    return None


def _result_row(spec: dict[str, Any], model_name: str, benchmark_id: str, value: Any) -> dict[str, Any]:
    benchmark = next((item for item in BENCHMARKS if item["id"] == benchmark_id), {})
    return {
        "benchmarkId": benchmark_id,
        "benchmarkLabel": benchmark.get("label") or benchmark_id,
        "model": model_name,
        "modelAliases": MODEL_ALIASES.get(model_name, [model_name]),
        "value": value,
        "unit": benchmark.get("unit") or "%",
        "sourceId": spec["id"],
        "sourceUrl": spec["url"],
        "sourceLabel": spec["label"],
    }


def _clean_markdown_cell(cell: str) -> str:
    cell = re.sub(r"<[^>]+>", " ", cell)
    cell = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", cell)
    cell = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cell)
    cell = cell.replace("`", "").replace("*", "")
    cell = cell.replace("$", "")
    cell = re.sub(r"_\{([^}]*)\}", r" \1", cell)
    return re.sub(r"\s+", " ", cell).strip()


def _is_markdown_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", cell.strip()) for cell in cells)


def _numeric_cell(cell: str) -> float | None:
    if not cell or cell.strip() in {"-", "—", "–"}:
        return None
    match = re.search(r"-?\d+(?:,\d{3})*(?:\.\d+)?", cell)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def retain_previous_results_on_blocked_refresh(
    payload: dict[str, Any],
    previous_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if not previous_payload:
        return payload

    current_rows_by_source: dict[str, list[dict[str, Any]]] = {}
    for row in payload.get("results", []):
        current_rows_by_source.setdefault(str(row.get("sourceId") or ""), []).append(row)

    previous_rows_by_source: dict[str, list[dict[str, Any]]] = {}
    for row in previous_payload.get("results", []):
        previous_rows_by_source.setdefault(str(row.get("sourceId") or ""), []).append(row)

    merged_results: list[dict[str, Any]] = []
    source_ids: set[str] = set()
    for source in payload.get("sources", []):
        source_id = str(source.get("id") or "")
        source_ids.add(source_id)
        current_rows = current_rows_by_source.get(source_id, [])
        previous_rows = previous_rows_by_source.get(source_id, [])
        status = str(source.get("collectionStatus") or "")
        if "refresh blocked:" in status and previous_rows:
            current_rows = merge_result_rows(current_rows, previous_rows)
            blocked_reason = status[status.index("refresh blocked:") :]
            source["collectionStatus"] = f"stale-retained; {blocked_reason}"
        merged_results.extend(current_rows)

    for source_id, rows in current_rows_by_source.items():
        if source_id not in source_ids:
            merged_results.extend(rows)
    payload["results"] = merged_results
    return payload


def write_payload(output_json: Path, timeout: float = 30) -> dict[str, Any]:
    previous_payload: dict[str, Any] | None = None
    try:
        previous_payload = json.loads(output_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    payload = collect(timeout=timeout)
    retain_previous_results_on_blocked_refresh(payload, previous_payload)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def write_seed_payload(output_json: Path) -> dict[str, Any]:
    source_statuses = {
        spec["id"]: "seeded-official-values"
        for spec in OFFICIAL_SOURCE_SPECS
    }
    payload = build_payload(
        {},
        "seeded-official-values",
        source_statuses,
        official_seed_results(),
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _find_label_index(tokens: list[str], label: str) -> int | None:
    normalized_label = _normalize_label(label)
    for index, token in enumerate(tokens):
        if _normalize_label(token).startswith(normalized_label):
            return index
    return None


def _next_percent_values(tokens: list[str], count: int) -> list[float | None]:
    values: list[float | None] = []
    for token in tokens:
        if token == "-":
            values.append(None)
        else:
            match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", token)
            if not match:
                continue
            values.append(float(match.group(1)))
        if len(values) == count:
            return values
    return values


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect benchmark scores for the static site.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="JSON payload to write.")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds.")
    parser.add_argument("--seed-only", action="store_true", help="Write curated official seed rows without HTTP refresh.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = write_seed_payload(Path(args.output_json)) if args.seed_only else write_payload(Path(args.output_json), timeout=args.timeout)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    official_sources = [source for source in payload["sources"] if source["id"] != "openai-gpt-5-5"]
    refreshed = sum(1 for source in official_sources if source.get("collectionStatus") == "refreshed")
    fallback = len(official_sources) - refreshed
    print(
        f"Wrote {args.output_json} with {len(payload['results'])} benchmark scores "
        f"({payload['sources'][0]['collectionStatus']}; "
        f"{refreshed} official sources refreshed, {fallback} seeded/reference)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
