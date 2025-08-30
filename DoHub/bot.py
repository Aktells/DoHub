from __future__ import annotations
import re, requests, json
from typing import Any, Dict, List
import pandas as pd
from pathlib import Path

# -------------------
# CONFIG
# -------------------
NGO_CSV_PATH = Path(__file__).parent / "ngos.csv"
OLLAMA_URL   = "https://6240aee68a5c.ngrok-free.app/api/generate"   # or /api/chat
OLLAMA_MODEL = "llama3.2"   # or mistral, gemma:instruct

# -------------------
# DATA LOAD
# -------------------
try:
    NGOs = pd.read_csv(NGO_CSV_PATH).fillna("")
except FileNotFoundError:
    NGOs = pd.DataFrame(columns=["name", "city", "categories",
                                 "accepts_items", "accepts_volunteer_skills",
                                 "description"])

# -------------------
# HELPERS
# -------------------
def _normalize_tokens(s: str) -> List[str]:
    return [t.strip().lower() for t in re.split(r"[,/;]|\band\b|\bor\b", str(s)) if t.strip()]

def filter_candidates(profile: Dict[str, Any], top_k: int = 25) -> pd.DataFrame:
    city   = (profile.get("city") or "").strip().lower()
    needs  = set(_normalize_tokens(", ".join(profile.get("needs", []))))
    items  = set(_normalize_tokens(", ".join(profile.get("items_to_donate", []))))
    skills = set(_normalize_tokens(", ".join(profile.get("skills", []))))

    df = NGOs.copy()
    df["city_match"] = df["city"].str.lower().str.contains(city, na=False) if city else True

    need_overlap  = df["categories"].apply(lambda x: len(needs.intersection(set(_normalize_tokens(x)))) if needs else 0)
    item_overlap  = df["accepts_items"].apply(lambda x: len(items.intersection(set(_normalize_tokens(x)))) if items else 0)
    skill_overlap = df["accepts_volunteer_skills"].apply(lambda x: len(skills.intersection(set(_normalize_tokens(x)))) if skills else 0)

    df["score_pre"] = (
        df["city_match"].astype(int) * 3 +
        need_overlap * 3 +
        item_overlap * 2 +
        skill_overlap * 2
    )

    return df.sort_values(["score_pre"], ascending=False).head(top_k)

# -------------------
# PROMPT
# -------------------
SYSTEM_MSG = """
You are an NGO recommender.

TASK: Given a user profile and candidate NGOs, recommend the top matches. 

FORMAT: 
- NGO Name — short reason why it matches (cause, city, items/skills)
- NGO Name — short reason...
(max 5 recommendations)
"""

# -------------------
# LLM RANKING
# -------------------
def rank_with_llm(profile: Dict[str, Any], candidates_df: pd.DataFrame, n_results: int = 5) -> str:
    candidates = candidates_df.to_dict(orient="records")
    user_prompt = {
        "profile": profile,
        "candidates": candidates,
        "n_results": n_results
    }

    try:
        # Decide payload based on endpoint
        if "/api/chat" in OLLAMA_URL:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": json.dumps(user_prompt, indent=2)}
                ],
                "stream": False,
            }
        else:  # default to /api/generate
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_MSG}\n\nUser + NGOs:\n{json.dumps(user_prompt, indent=2)}",
                "stream": False,
            }

        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        # Different keys for different endpoints
        if "/api/chat" in OLLAMA_URL:
            raw = data.get("message", {}).get("content", "").strip()
        else:
            raw = data.get("response", "").strip()

        print("RAW LLM RESPONSE:", raw[:400])
        return raw

    except Exception as e:
        print("LLM error:", e)
        return ""

# -------------------
# ENTRY POINT
# -------------------
def get_bot_response(profile: Dict[str, Any]) -> str:
    cands = filter_candidates(profile, top_k=15)
    ranked_text = rank_with_llm(profile, cands, n_results=5)
    if not ranked_text:
        # fallback: just return top candidates
        fallback = "\n".join(f"- {row['name']} (heuristic filter)" 
                             for _, row in cands.head(5).iterrows())
        return f"(LLM failed, showing heuristics)\n{fallback}"
    return ranked_text

print("OLLAMA_URL in use:", OLLAMA_URL)
