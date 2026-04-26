"""
Common schema for sampling results.

ALL agents must conform to this schema. Any change requires PM approval
via GitHub issue + PR review.
"""
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime
import json


# -----------------------------
# Constants — DO NOT MODIFY
# -----------------------------
TEMPERATURE = 0.7
TOP_P = 0.95
MAX_TOKENS = 800
NUM_SAMPLES_PER_PROMPT = 3

# Ollama-specific: cap context window to avoid KV cache forcing CPU offload.
# Default 131072 makes deepseek-r1:70b spill 6 layers to CPU on RTX Pro 6000
# (40 GB KV cache); 4096 keeps all layers on GPU and gives ~30 t/s instead of 0.9.
# Our prompts are all <200 tokens and MAX_TOKENS=800, so 4096 is ample.
OLLAMA_NUM_CTX = 4096

# Some vendor APIs deprecate sampling params; for these providers we omit them
# at the API call site. JSON records still log the intended values (so
# validate_result passes), and runners must add a sampling_omitted note in
# raw_metadata. This is a vendor-imposed limitation, not a research-design
# choice — document explicitly in report Limitations section.
#
# Anthropic: as of 2026, `temperature` and `top_p` are deprecated on
# claude-opus-4-7 / claude-sonnet-4-6 endpoints (HTTP 400 if sent).
# Sampling falls back to API default.
VENDOR_SKIP_SAMPLING_PARAMS = {
    "anthropic": ["temperature", "top_p"],
}

# Provider categories
PROVIDERS = Literal["anthropic", "openai", "google", "groq", "ollama"]
FAMILIES = Literal[
    "claude", "gpt", "gemini", "llama",
    "kimi", "deepseek", "qwen", "glm", "gemma"
]
CATEGORIES = Literal["emotion", "moral", "uncertainty", "creative", "refusal"]
ANCHOR_PAIRS = Literal["A", "B", "C", None]


# -----------------------------
# Sampling Result Schema
# -----------------------------
@dataclass
class SamplingResult:
    """One row of sampling data. Written to data/raw/{model}/{prompt_id}_{sample}.json"""

    # Model identity
    model: str                          # short ID, e.g. "claude-opus-4-7"
    model_full_id: str                  # full versioned ID, e.g. "claude-opus-4-7-20260415"
    model_provider: str                 # see PROVIDERS
    model_family: str                   # see FAMILIES
    is_anchor: bool                     # True if part of an anchor pair
    anchor_pair: Optional[str]          # "A", "B", "C", or None

    # Prompt identity
    prompt_id: str                      # "Q001" .. "Q100"
    prompt_category: str                # see CATEGORIES
    prompt_text: str                    # exact prompt sent

    # Sampling parameters
    sample_index: int                   # 1, 2, or 3
    temperature: float = TEMPERATURE
    max_tokens: int = MAX_TOKENS
    top_p: float = TOP_P

    # Result
    timestamp_utc: str = ""             # ISO 8601
    response: str = ""                  # raw model output
    response_token_count: int = 0
    latency_ms: int = 0

    # Provenance
    raw_metadata: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, s: str) -> "SamplingResult":
        return cls(**json.loads(s))


# -----------------------------
# Model Registry
# -----------------------------
MODEL_REGISTRY = [
    # (id, provider, family, is_anchor, anchor_pair)
    ("claude-opus-4-7",    "anthropic", "claude",   False, None),
    ("claude-sonnet-4-6",  "anthropic", "claude",   True,  "A"),
    ("gpt-5-4",            "openai",    "gpt",      False, None),
    ("gpt-5-4-mini",       "openai",    "gpt",      True,  "B"),
    ("gemini-3-1-pro",     "google",    "gemini",   False, None),
    ("gemini-3-flash",     "google",    "gemini",   True,  "C"),
    ("llama-4-scout",      "groq",      "llama",    False, None),
    ("llama-3-3-70b",      "groq",      "llama",    False, None),
    ("kimi-k2",            "groq",      "kimi",     False, None),
    ("deepseek-r1-70b",    "ollama",    "deepseek", False, None),
    ("qwen3-6-35b-a3b",    "ollama",    "qwen",     False, None),
    ("gemma-4-31b",        "ollama",    "gemma",    False, None),
]

ALL_MODEL_IDS = [m[0] for m in MODEL_REGISTRY]


def get_model_meta(model_id: str) -> dict:
    """Look up provider/family/anchor info from the registry."""
    for mid, prov, fam, is_anchor, anchor in MODEL_REGISTRY:
        if mid == model_id:
            return {
                "provider": prov,
                "family": fam,
                "is_anchor": is_anchor,
                "anchor_pair": anchor,
            }
    raise ValueError(f"Unknown model: {model_id}")


# -----------------------------
# Validation
# -----------------------------
def validate_result(r: SamplingResult) -> list[str]:
    """Returns list of validation errors. Empty list = valid."""
    errs = []

    if r.model not in ALL_MODEL_IDS:
        errs.append(f"Unknown model: {r.model}")

    if r.prompt_category not in ["emotion", "moral", "uncertainty", "creative", "refusal"]:
        errs.append(f"Invalid category: {r.prompt_category}")

    if not r.prompt_id.startswith("Q") or len(r.prompt_id) != 4:
        errs.append(f"Invalid prompt_id format: {r.prompt_id}")

    if r.sample_index not in [1, 2, 3]:
        errs.append(f"Invalid sample_index: {r.sample_index}")

    if r.temperature != TEMPERATURE:
        errs.append(f"Temperature mismatch: {r.temperature} != {TEMPERATURE}")

    if not r.response:
        errs.append("Empty response")

    if not r.timestamp_utc:
        errs.append("Missing timestamp_utc")

    return errs
