from __future__ import annotations
import re, requests, json
from typing import Any, Dict, List
import pandas as pd
from pathlib import Path

# -------------------
# CONFIG
# -------------------
NGO_CSV_PATH = Path(__file__).parent / "ngos.csv"
# Point this to your ngrok/cloudflare tunnel URL
OLLAMA_URL   = "https://6240aee68a5c.ngrok-free.app/api/generate"   # or /api/chat
OLLAMA_MODEL = "llama3.2"   # can be llama3, mistral, gemma:instruct, etc.

# -------------------
# LOAD DATA
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
(max 5 recommendations, plain text only)
"""

# -------------------
# LLM CALL
# -------------------
def rank_with_llm(profile: Dict[str, Any], candidates_df: pd.DataFrame, n_results: int = 5) -> str:
    candidates = candidates_df.to_dict(orient="records")

    # Keep payload short (avoid ngrok issues)
    compact_candidates = [{"name": c["name"], "city": c["city"], "categories": c["categories"]}
                          for c in candidates[:10]]

    user_prompt = f"""
User profile:
City: {profile.get('city','')}
Needs: {', '.join(profile.get('needs', []))}
Items: {', '.join(profile.get('items_to_donate', []))}
Skills: {', '.join(profile.get('skills', []))}
Notes: {profile.get('notes','')}

Candidate NGOs:
{json.dumps(compact_candidates, indent=2)}

Return top {n_results} matches as bullet points.
"""

    try:
        # Decide payload based on endpoint
        if "/api/chat" in OLLAMA_URL:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
        else:  # /api/generate
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_MSG}\n\n{user_prompt}",
                "stream": False
            }

        # Make the request
        resp = requests.post(OLLAMA_URL, json=payload, timeout=90)
        resp.raise_for_status()

        # Try to decode JSON
        try:
            data = resp.json()
        except Exception:
            raw_text = resp.text
            print("RAW NON-JSON RESPONSE:", raw_text[:400])
            return raw_text

        # Robust extraction
        raw = ""
        if isinstance(data, dict):
            raw = (
                data.get("response") or
                (data.get("message", {}) or {}).get("content") or
                ""
            )
        elif isinstance(data, list):
            # Sometimes you get a list of chunks
            parts = []
            for item in data:
                if "response" in item:
                    parts.append(item["response"])
                elif "message" in item and "content" in item["message"]:
                    parts.append(item["message"]["content"])
            raw = "".join(parts)

        raw = raw.strip()
        if not raw:
            print("DEBUG full JSON:", json.dumps(data, indent=2)[:400])
        else:
            print("RAW LLM RESPONSE:", raw[:400])

        return raw

    except Exception as e:
        print("LLM error:", e)
        return ""

# -------------------
# ENTRY POINT
# -------------------
def get_bot_response(profile: Dict[str, Any]) -> str:
    import streamlit as st

    cands = filter_candidates(profile, top_k=15)
    ranked_text = rank_with_llm(profile, cands, n_results=5)

    # 🔎 Show raw debug info in sidebar
    with st.sidebar:
        st.subheader("🔎 Debug: LLM output")
        st.code(ranked_text if ranked_text else "(empty)")

    if not ranked_text:
        # fallback: just return top candidates
        fallback = "\n".join(f"- {row['name']} (heuristic filter)"
                             for _, row in cands.head(5).iterrows())
        return f"(LLM failed, showing heuristics)\n{fallback}"
    return ranked_text

# Debug info
print("OLLAMA_URL in use:", OLLAMA_URL)
print("OLLAMA_MODEL in use:", OLLAMA_MODEL)




