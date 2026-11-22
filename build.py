"""Build site/index.html from content/explainer.md.

Clip markers in the Markdown look like
    <!-- clip: SceneName | caption text -->
and become a <figure> with the rendered manim video from site/media/.

Usage:  python build.py
"""

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "content" / "explainer.md"
TEMPLATE = ROOT / "content" / "template.html"
OUT = ROOT / "site" / "index.html"

CLIP = re.compile(r"<!-- clip: (\w+) \| (.+?) -->")


def clip_figure(match):
    scene, caption = match.group(1), html.escape(match.group(2))
    return (
        f'<figure class="clip">'
        f'<video src="media/{scene}.mp4" poster="media/{scene}.png" '
        f'controls muted loop playsinline preload="none" aria-label="{caption}"></video>'
        f"<figcaption>{caption}</figcaption></figure>"
    )


def main():
    text = SRC.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"],
                           extension_configs={"toc": {"toc_depth": "2-2"}})  # list the parts only
    body = md.convert(text)
    body = CLIP.sub(clip_figure, body)
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("{{toc}}", md.toc).replace("{{body}}", body)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page):,} bytes)")


if __name__ == "__main__":
    main()
