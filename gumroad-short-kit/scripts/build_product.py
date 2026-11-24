from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
TOPICS = ROOT / "topics.json"
DROP = ROOT / "data" / "daily_drop.json"
DIST = ROOT / "dist"
ZIP = ROOT / "Phone-Tips-Shorts-Studio.zip"


def safe_json(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copy2(SOURCE / name, DIST / name)
    (DIST / "topics.js").write_text(
        "window.TOPICS = " + safe_json(TOPICS) + ";\n", encoding="utf-8"
    )
    (DIST / "daily_drop.js").write_text(
        "window.DAILY_DROP = " + safe_json(DROP) + ";\n", encoding="utf-8"
    )
    (DIST / "README.txt").write_text(
        "PHONE TIPS SHORTS STUDIO\n\n"
        "Open index.html in a modern browser. The app works offline and saves nothing remotely.\n"
        "Use the source links to verify every device-specific step before recording.\n"
        "The daily creator drop is a draft, not a guarantee of accuracy or video performance.\n",
        encoding="utf-8",
    )
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST).as_posix())


if __name__ == "__main__":
    build()
    print(f"Built {ZIP.name} with app files at the archive root.")
