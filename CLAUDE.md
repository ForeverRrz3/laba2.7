# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python lab assignment ("лабораторная работа 2.7") working with images via Pillow. The main script is `1.py`; it is a work in progress (only the `get_filename` input helper is defined so far — `main` and any image processing logic still need to be implemented).

Two sibling directories provide sample inputs the script is expected to read from:
- `brand_images_dataset/` — synthetic PNGs named by category and pattern (`NN_<palette>_<pattern>.png`, e.g. `01_warm_solid.png`, `17_warm_gradient_h.png`, `36_warm_noise.png`). Palettes: `warm`, `cold`, `nature`, `pastel`, `mono`. Patterns: `solid`, `gradient_v`, `gradient_h`, `noise`.
- `cats/` — additional image samples.

User-facing text in `1.py` mixes English prompts with Russian error messages — keep that style when extending it.

## Environment

A local virtualenv lives at `.venv/` with **Pillow** installed (no `requirements.txt`). Activate before running:

```bash
source .venv/bin/activate
python 1.py
```

Or invoke directly: `.venv/bin/python 1.py`.

`get_filename()` resolves paths via `os.path.isfile` relative to the current working directory, so run the script from the repo root (or pass paths like `brand_images_dataset/01_warm_solid.png` at the prompt).
