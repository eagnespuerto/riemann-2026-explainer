"""Build the site pages from the Markdown in content/.

Pages:
    content/explainer.md -> site/index.html     (part by part, with clips)
    content/pop-math.md  -> site/short.html     (short, no formulas)
    content/calculus.md  -> site/calculus.html  (calculus level, with KaTeX)

Clip markers in the Markdown look like
    <!-- clip: SceneName | caption text -->
and become a <figure> with the rendered manim video from site/media/.

Maths in $...$ or $$...$$ is kept away from Markdown (which would eat
underscores and backslashes) and rendered in the browser by KaTeX.

Usage:  python build.py
"""

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "content" / "template.html"

PAGES = [
    # (source, output, short title for the switcher)
    ("explainer.md", "index.html", "Part by part"),
    ("pop-math.md", "short.html", "Short"),
    ("calculus.md", "calculus.html", "Calculus level"),
]

CLIP = re.compile(r"<!-- clip: (\w+) \| (.+?) -->")
DISPLAY_MATH = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE_MATH = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)\$")

KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.querySelector('main'), {delimiters: [
    {left: '$$', right: '$$', display: true}, {left: '\\\\(', right: '\\\\)', display: false}]})"></script>"""


def clip_figure(match):
    scene, caption = match.group(1), html.escape(match.group(2))
    return (
        f'<figure class="clip">'
        f'<video src="media/{scene}.mp4" poster="media/{scene}.png" '
        f'controls muted loop playsinline preload="none" aria-label="{caption}"></video>'
        f"<figcaption>{caption}</figcaption></figure>"
    )


def shield_math(text):
    """Swap maths for placeholders so Markdown leaves it alone."""
    stash = []

    def keep(rendered):
        stash.append(rendered)
        return f"\x00MATH{len(stash) - 1}\x00"

    text = DISPLAY_MATH.sub(lambda m: keep("$$" + html.escape(m.group(1)) + "$$"), text)
    text = INLINE_MATH.sub(lambda m: keep(r"\(" + html.escape(m.group(1)) + r"\)"), text)
    return text, stash


def unshield_math(body, stash):
    return re.sub(r"\x00MATH(\d+)\x00", lambda m: stash[int(m.group(1))], body)


def switcher(current):
    links = []
    for _, out, label in PAGES:
        if out == current:
            links.append(f'<span aria-current="page">{label}</span>')
        else:
            links.append(f'<a href="{out}">{label}</a>')
    return '<nav class="versions" aria-label="Versions">' + " · ".join(links) + "</nav>"


def build(src, out, template):
    text = (ROOT / "content" / src).read_text(encoding="utf-8")
    text, stash = shield_math(text)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"],
                           extension_configs={"toc": {"toc_depth": "2-2"}})  # list the parts only
    body = unshield_math(CLIP.sub(clip_figure, md.convert(text)), stash)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    page = (template
            .replace("{{title}}", html.escape(title))
            .replace("{{head_extra}}", KATEX if stash else "")
            .replace("{{versions}}", switcher(out))
            .replace("{{toc}}", md.toc)
            .replace("{{body}}", body))
    (ROOT / "site" / out).write_text(page, encoding="utf-8")
    print(f"wrote site/{out} ({len(page):,} bytes, {len(stash)} maths)")


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    for src, out, _ in PAGES:
        build(src, out, template)


if __name__ == "__main__":
    main()
