import os, openai, textwrap
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise(url: str) -> str:
    prompt = (
        f"다음 기사를 요약해줘 (한국어): {url}\n"
        "포맷은 '헤드라인/핵심 포인트 3개/시사점 1개', 120~150자."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 한국어 기자입니다."},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=256,
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()
