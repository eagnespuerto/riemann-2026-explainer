# Riemann 2026 Explainer

[![Deploy site](https://github.com/eagnespuerto/riemann-2026-explainer/actions/workflows/pages.yml/badge.svg)](https://github.com/eagnespuerto/riemann-2026-explainer/actions/workflows/pages.yml)
[![Site](https://img.shields.io/badge/site-GitHub%20Pages-b5651d)](https://eagnespuerto.github.io/riemann-2026-explainer/)
[![Animations: Manim](https://img.shields.io/badge/animations-Manim%20CE%200.22-4b8bbe)](https://www.manim.community/)
[![Proof: Lean 4](https://img.shields.io/badge/proof-Lean%204-1d4ed8)](https://github.com/CocoSgt/riemann-hypothesis-lean)
[![Text: CC BY 4.0](https://img.shields.io/badge/text-CC%20BY%204.0-lightgrey)](LICENSE-CONTENT.md)
[![Code: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)

A part-by-part, pop-math explainer of **Levent Alpöge's Lean proof of the Riemann Hypothesis** (released 20 November 2026), as a static site with Manim animations.

**Read it:** <https://eagnespuerto.github.io/riemann-2026-explainer/>

## The proof itself

- Lean code on GitHub: **[CocoSgt/riemann-hypothesis-lean](https://github.com/CocoSgt/riemann-hypothesis-lean)**, an unmodified mirror of the author's release
- Author's release and 4-page note: <https://alpo.ge/> · <https://alpo.ge/remark.pdf>

All credit for the proof goes to Levent Alpöge. This repository only explains it.

## What's here

| Path | What it is |
|---|---|
| `content/explainer.md` | the explainer text, 12 parts, with clip markers |
| `manim/scenes.py` | five Manim scenes (zeros on the line, primes rebuilt from zeros, the mirror step, multiplicity, the theta-lift chain) |
| `manim/render.py` | renders each scene to `site/media/` with a poster frame |
| `build.py` | turns the Markdown into `site/index.html` |
| `site/` | the published static site |

The zeta zeros in the animations are real ones, computed with mpmath. The "primes rebuilt from zeros" clip uses the Riemann–von Mangoldt explicit formula with the first 0, 3, 10, 30 and 100 zeros.

## Build locally

```powershell
pip install -r requirements.txt
python manim/render.py
python build.py
python -m http.server -d site 8000
```

No LaTeX needed, because every label is plain text.

## Related

The same explainer, plus a shorter version and a calculus-level summary, lives in [random-unsorted-cloud-stuff/riemann-hypothesis-lean-summary](https://github.com/eagnespuerto/random-unsorted-cloud-stuff/tree/main/riemann-hypothesis-lean-summary).
