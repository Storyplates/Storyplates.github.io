from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import requests

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
API = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "nav", "footer", "header"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "nav", "footer", "header"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            clean = re.sub(r"\s+", " ", data).strip()
            if clean:
                self.parts.append(clean)


def source_text(url: str) -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": "PhoneTipsShortsStudio/1.0"})
    response.raise_for_status()
    parser = TextExtractor()
    parser.feed(response.text)
    text = re.sub(r"\s+", " ", " ".join(parser.parts))
    if len(text) < 400:
        raise RuntimeError("Official source did not return enough readable text; no release will be built.")
    return text[:12000]


def gemini_json(prompt: str) -> dict:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing; no product update was created.")
    for attempt in range(5):
        response = requests.post(
            API,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.45, "responseMimeType": "application/json"},
            },
            headers={"x-goog-api-key": key},
            timeout=90,
        )
        if response.status_code in (429, 500, 502, 503, 504) and attempt < 4:
            time.sleep(min(2**attempt, 16))
            continue
        response.raise_for_status()
        answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        try:
            return json.loads(answer)
        except json.JSONDecodeError as exc:
            raise RuntimeError("AI returned malformed JSON; no product update was created.") from exc
    raise RuntimeError("AI service did not respond after retries.")


def validate(item: dict, topic: dict) -> None:
    expected = {"title", "hook", "narration", "scenes", "description", "tags"}
    if set(item) != expected:
        raise RuntimeError("Daily draft is missing required fields; no upload will happen.")
    words = re.findall(r"\b[\w'-]+\b", item["narration"])
    if not 75 <= len(words) <= 130:
        raise RuntimeError("Daily narration length is outside the allowed range; no upload will happen.")
    if len(item["title"]) > 70 or len(item["scenes"]) != 4:
        raise RuntimeError("Daily title or scene count is invalid; no upload will happen.")
    if any(len(str(scene).split()) > 9 for scene in item["scenes"]):
        raise RuntimeError("A scene caption is too long; no upload will happen.")
    tags = item["tags"]
    if not isinstance(tags, list) or not 3 <= len(tags) <= 5 or len({str(tag).lower() for tag in tags}) != len(tags):
        raise RuntimeError("Tags are missing or duplicated; no upload will happen.")
    if topic["url"] not in item["description"]:
        raise RuntimeError("Official source link is missing; no upload will happen.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", default="topics.json")
    parser.add_argument("--out", default="data/daily_drop.json")
    args = parser.parse_args()
    topics = json.loads(Path(args.topics).read_text(encoding="utf-8-sig"))
    today = date.today()
    topic = topics[today.toordinal() % len(topics)]
    excerpt = source_text(topic["url"])
    prompt = f"""Create one original, practical YouTube Shorts creator brief using only the official source excerpt. It is a draft for a small creator, not a guarantee of virality. Do not copy source wording or imitate another creator. Do not invent menu paths, features, or security promises. Note that device menus may vary when relevant.
Topic: {topic['title']}
Official URL: {topic['url']}
Source excerpt: {excerpt}

Return JSON with exactly: title (70 chars max), hook (one natural question), narration (80-115 spoken words, warmly addresses one viewer, explains one useful action), scenes (exactly 4 captions, max 9 words each), description (two short sentences and the official URL), tags (3-5 specific relevant search tags, no unrelated trending tags)."""
    draft = gemini_json(prompt)
    validate(draft, topic)
    verdict = gemini_json(f"""Act as a strict factual and relevance editor. Compare every phone-setting claim with the official excerpt. Also check that all tags directly describe this topic. Return exactly JSON: {{\"pass\": true/false, \"tags_relevant\": true/false, \"reason\": \"...\"}}.
Official excerpt: {excerpt}
Draft: {json.dumps(draft, ensure_ascii=False)}""")
    if verdict.get("pass") is not True or verdict.get("tags_relevant") is not True:
        raise RuntimeError("Editor rejected this draft: " + str(verdict.get("reason", "no reason supplied")))
    output = {"date": today.isoformat(), "topic_id": topic["id"], "topic_title": topic["title"], "source_url": topic["url"], **draft}
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Daily creator drop passed format and source review.")


if __name__ == "__main__":
    main()
