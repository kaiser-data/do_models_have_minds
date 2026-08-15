"""The model roster.

Two axes, deliberately:

**Primary — family variety at matched parameter count.** This is what makes the
deliverable a *card comparison*: same battery, same floor, different training
recipes at roughly the same size. If the floor-corrected numbers move with
family but not with size, the thing being measured is the recipe, not scale.

**Secondary — one family across sizes.** Qwen3.5 0.8B -> 9B, the cheapest clean
scale ladder available. This is the arm that speaks to Utility Engineering's
"coherence emerges with scale" claim (2502.08640, Fig. 4, r = 75.6% vs MMLU).

Self-hosted models are capped at ~9B on purpose: run time is the binding
constraint this sprint, and the interesting comparison is across families, not
at the top of the scale. Anything larger is reached through Nebius, where we pay
per token instead of per GPU-second.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    hf_id: str
    family: str
    params_b: float          # total parameters, billions
    active_b: float          # active parameters (== params_b for dense)
    tier: str                # "1-2B" | "3-4B" | "7-9B"
    gpu: str                 # Modal GPU type
    notes: str = ""

    @property
    def is_moe(self) -> bool:
        return self.active_b < self.params_b


# ---------------------------------------------------------------------------
# Self-hosted on Modal. Capped at ~9B.
# ---------------------------------------------------------------------------

SELF_HOSTED: list[Model] = [
    # --- ~1-2B ---------------------------------------------------------------
    Model("Qwen/Qwen3.5-0.8B",                  "qwen",    0.8, 0.8, "1-2B", "L4"),
    Model("Qwen/Qwen3.5-2B",                    "qwen",    2.0, 2.0, "1-2B", "L4"),
    Model("google/gemma-4-E2B-it",              "gemma",   2.0, 2.0, "1-2B", "L4"),
    Model("LiquidAI/LFM2.5-1.2B-Instruct",      "liquid",  1.2, 1.2, "1-2B", "L4"),
    Model("HuggingFaceTB/SmolLM2-1.7B-Instruct","smol",    1.7, 1.7, "1-2B", "L4"),
    # allenai/OLMo-2-0425-1B is deliberately absent: it is a BASE model with no
    # chat template. Its instruct siblings live in the 7-9B tier. Caught by the
    # wave-0 gate, which is what wave 0 is for.
    Model("meta-llama/Llama-3.2-1B-Instruct",   "llama",   1.2, 1.2, "1-2B", "L4", "GATED"),

    # --- ~3-4B : best speed/capability trade, the workhorse tier -------------
    Model("Qwen/Qwen3.5-4B",                    "qwen",    4.0, 4.0, "3-4B", "L4"),
    Model("google/gemma-3-4b-it",               "gemma",   4.3, 4.3, "3-4B", "L4", "GATED"),
    Model("LiquidAI/LFM2.5-2.6B",               "liquid",  2.6, 2.6, "3-4B", "L4"),
    Model("HuggingFaceTB/SmolLM3-3B",           "smol",    3.0, 3.0, "3-4B", "L4",
          "reasoning-capable — must run in non-thinking mode"),
    Model("microsoft/Phi-4-mini-instruct",      "phi",     3.8, 3.8, "3-4B", "L4"),
    Model("mistralai/Ministral-3-3B-Instruct-2512", "mistral", 3.0, 3.0, "3-4B", "L4"),
    Model("ibm-granite/granite-4.1-3b",         "granite", 3.0, 3.0, "3-4B", "L4"),

    # --- ~7-9B : the tier flagged as most interesting ------------------------
    Model("Qwen/Qwen3.5-9B",                    "qwen",    9.0, 9.0, "7-9B", "A10G"),
    Model("meta-llama/Llama-3.1-8B-Instruct",   "llama",   8.0, 8.0, "7-9B", "A10G", "GATED"),
    Model("allenai/Olmo-3-7B-Instruct",         "olmo",    7.0, 7.0, "7-9B", "A10G",
          "fully open training data"),
    Model("mistralai/Ministral-3-8B-Instruct-2512", "mistral", 8.0, 8.0, "7-9B", "A10G"),
    Model("ibm-granite/granite-4.1-8b",         "granite", 8.0, 8.0, "7-9B", "A10G"),
    Model("LiquidAI/LFM2.5-8B-A1B",             "liquid",  8.0, 1.0, "7-9B", "A10G",
          "MoE, 1B active — fastest model in the 8B tier"),
    Model("google/gemma-4-E4B-it",              "gemma",   4.0, 4.0, "7-9B", "L4",
          "gemma-4's largest small-tier release"),
]

# The scale ladder: one family, four sizes, size as the only variable.
SCALE_LADDER: list[str] = [
    "Qwen/Qwen3.5-0.8B",
    "Qwen/Qwen3.5-2B",
    "Qwen/Qwen3.5-4B",
    "Qwen/Qwen3.5-9B",
]

# ---------------------------------------------------------------------------
# Nebius — frontier reference points. Pay per token, never self-hosted.
#
# `first_token_ok` is measured, not assumed: it records whether the model puts
# its answer in the first sampled token under the verbatim Utility Engineering
# forced-choice prompt. Models that begin reasoning instead ("We", "The",
# "Here") cannot be scored by first-token logprob, and their numbers are NOT
# poolable with those that can (spec §7.4).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HostedModel:
    api_id: str
    family: str
    logprobs: bool
    first_token_ok: bool
    latency_s: float
    notes: str = ""


NEBIUS: list[HostedModel] = [
    HostedModel("google/gemma-3-27b-it",              "gemma",   True,  True,  0.39),
    HostedModel("meta-llama/Llama-3.3-70B-Instruct",  "llama",   True,  True,  0.40),
    HostedModel("Qwen/Qwen3-235B-A22B-Instruct-2507", "qwen",    True,  True,  0.58),
    HostedModel("Qwen/Qwen3-30B-A3B-Instruct-2507",   "qwen",    True,  True,  1.72),
    # --- measured NOT first-token-scoreable: reasoning preamble or control tokens
    HostedModel("openai/gpt-oss-120b",                "gpt-oss", True,  False, 0.40,
                "emits <|channel|> — harmony format, needs prefill"),
    HostedModel("zai-org/GLM-5.2",                    "glm",     True,  False, 0.82,
                "starts 'The'"),
    HostedModel("nvidia/Nemotron-3_5-Lightning",      "nemotron",True,  False, 0.86,
                "starts 'Here'"),
    HostedModel("MiniMaxAI/MiniMax-M2.5",             "minimax", True,  False, 0.86,
                "starts 'The'"),
    HostedModel("deepseek-ai/DeepSeek-V4-Flash",      "deepseek",True,  False, 0.97,
                "starts 'We'"),
    HostedModel("moonshotai/Kimi-K3",                 "kimi",    False, False, 0.96,
                "API refuses logprobs: DFLASH speculative decoding"),
]

NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"


def by_tier(tier: str) -> list[Model]:
    return [m for m in SELF_HOSTED if m.tier == tier]


def families() -> list[str]:
    return sorted({m.family for m in SELF_HOSTED})


def scoreable_hosted() -> list[HostedModel]:
    """Hosted models whose forced choice can be read from the first token.

    Everything else needs a prefill variant before it is comparable, and until
    it has one it does not go on a card next to these.
    """
    return [m for m in NEBIUS if m.logprobs and m.first_token_ok]
