from __future__ import annotations
import re, os, requests
from typing import Any, Dict, List
import pandas as pd
from pathlib import Path

# -------------------
# CONFIG
# -------------------
NGO_CSV_PATH = Path(__file__).parent / "ngos.csv"
GROQ_URL     = "https://api.groq.com/openai/v1/chat"
GROQ_MODEL   = "llama3-8b-8192"   # fast + capable
# You'll need to set GROQ_API_KEY in secrets.toml

# -------------------
# LOAD NGO DATA
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
# LLM RANKING
# -------------------
def rank_with_llm(profile: Dict[str, Any], candidates_df: pd.DataFrame, n_results: int = 5) -> str:
    candidates = candidates_df.to_dict(orient="records")
    compact_candidates = "\n".join(
        f"- {c['name']} ({c['categories']}, {c['city']})"
        for c in candidates[:5]
    )

    user_prompt = f"""
User profile:
City: {profile.get('city','')}
Needs: {', '.join(profile.get('needs', []))}
Items: {', '.join(profile.get('items_to_donate', []))}
Skills: {', '.join(profile.get('skills', []))}
Notes: {profile.get('notes','')}

Candidate NGOs:
{compact_candidates}

Return top {n_results} matches as bullet points.
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an NGO recommender."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 500
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"(Groq API error: {e})"

# -------------------
# ENTRY POINT
# -------------------
def get_bot_response(profile: Dict[str, Any]) -> str:
    cands = filter_candidates(profile, top_k=15)
    ranked_text = rank_with_llm(profile, cands, n_results=5)
    if not ranked_text or ranked_text.startswith("("):
        fallback = "\n".join(f"- {row['name']} (heuristic filter)"
                             for _, row in cands.head(5).iterrows())
        return f"(LLM failed, showing heuristics)\n{fallback}"
    return ranked_text


