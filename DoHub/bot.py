from __future__ import annotations
import re, os
from typing import Any, Dict, List
import pandas as pd
from pathlib import Path
from openai import OpenAI

# -------------------
# CONFIG
# -------------------
NGO_CSV_PATH = Path(__file__).parent / "ngos.csv"
OPENAI_MODEL = "gpt-4o-mini"   # reliable + cheap for recommendations

# init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
# PROMPT
# -------------------
SYSTEM_MSG = "You are an NGO recommender. Recommend the best NGOs for the user."

# -------------------
# LLM RANKING
# -------------------
def rank_with_llm(profile: Dict[str, Any], candidates_df: pd.DataFrame, n_results: int = 5) -> str:
    candidates = candidates_df.to_dict(orient="records")
    compact_candidates = "\n".join(f"- {c['name']} ({c['categories']}, {c['city']})" 
                                   for c in candidates[:5])

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

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        raw = resp.choices[0].message.content.strip()
        return raw

    except Exception as e:
        print("OpenAI API error:", e)
        return ""

# -------------------
# ENTRY POINT
# -------------------
def get_bot_response(profile: Dict[str, Any]) -> str:
    cands = filter_candidates(profile, top_k=15)
    ranked_text = rank_with_llm(profile, cands, n_results=5)
    if not ranked_text:
        fallback = "\n".join(f"- {row['name']} (heuristic filter)"
                             for _, row in cands.head(5).iterrows())
        return f"(LLM failed, showing heuristics)\n{fallback}"
    return ranked_text

