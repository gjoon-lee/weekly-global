"""
judge.py – Yes/No filter using OpenAI SDK 1.x
"""

import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError    # 1.x interface

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assert client.api_key, "OPENAI_API_KEY missing in .env"

SYSTEM_MSG = (
    "You are the editor of a newsletter focused on Singapore's "
    "entertainment & content industries: gaming, OTT, film, broadcast, "
    "music, fashion IP, and tech media. Answer ONLY 'Yes' or 'No'."
)

def judge_article(url: str, title: str) -> bool:
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user",
                 "content": f"[Title] {title}\n[Link] {url}\nInclude?"},
            ],
            max_tokens=2,
            temperature=0,
        )
        answer = resp.choices[0].message.content.strip().lower()
        return answer.startswith("y")          # keep if “yes”
    except OpenAIError as e:
        print("GPT judge error:", e)
        return False
