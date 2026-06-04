# SciVer — Example Viewer

A small, self-contained HTML page that showcases examples from the
[SciVer benchmark](https://huggingface.co/datasets/chengyewang/SciVer)
([paper, ACL 2025](https://arxiv.org/abs/2506.15569)) — multimodal scientific
claim verification over charts and tables.

## What's here

| File | Purpose |
|------|---------|
| `sciver_examples.html` | **Open this in a browser.** Self-contained (images embedded) — no data download needed. |
| `make_sciver_examples.py` | Generator script that produces the page from the dataset. |

## What the viewer shows

Eight examples — one **Entailed** + one **Refuted** for each of SciVer's four
reasoning types (`direct`, `analytical`, `parallel`, `sequential`). Each card has:

- the **claim** the model must verify,
- the **evidence** figure/table image(s) it cites,
- the gold **label** (Entailed / Refuted),
- for refuted claims, the dataset's explanation of *why* it's false,
- a word-level **diff** of the true vs. perturbed statement (true tokens in
  green, perturbed tokens in red), showing the minimal perturbation that flips
  the label.

## Key thing to understand about the benchmark

Refuted claims are built by **minimally perturbing a true statement** — changing
a single number, comparison, or entity — so the false claim reads just as fluent
as the true one. A model can't judge by plausibility; it must read the evidence.
(The full benchmark gives the model the entire curated paper context, not just
the single image shown per card here.)

## Regenerating the page

Requires the SciVer dataset on disk (`testset.json`, `images/`, `papers/`),
downloaded from Hugging Face:

```bash
hf download chengyewang/SciVer --repo-type dataset --local-dir .
```

Then:

```bash
python3 make_sciver_examples.py --standalone   # self-contained, shareable
python3 make_sciver_examples.py                # lightweight, references images/
```

> The ~1.6 GB dataset (`images/`, `papers/`, `*.json`) is intentionally **not**
> committed — fetch it from Hugging Face at the link above.
