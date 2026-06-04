# SciVer — Example Viewer

**▶ Live viewer: https://awndregamache.github.io/sciver-viewer/sciver_examples.html**
(opens in any browser — no clone or download needed)

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

## Data source, license & citation

All examples shown here come from the **SciVer** dataset by Wang et al. — this
repo is just a viewer and claims no ownership of the data.

- **Dataset:** [chengyewang/SciVer on Hugging Face](https://huggingface.co/datasets/chengyewang/SciVer)
- **Paper:** [SciVer: Evaluating Foundation Models for Multimodal Scientific Claim Verification](https://aclanthology.org/2025.acl-long.420/) (ACL 2025) · [arXiv:2506.15569](https://arxiv.org/abs/2506.15569)
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt **with attribution**.

If you use the data, please cite the original authors:

```bibtex
@inproceedings{wang-etal-2025-sciver,
    title = "{S}ci{V}er: Evaluating Foundation Models for Multimodal Scientific Claim Verification",
    author = "Wang, Chengye  and
      Shen, Yifei  and
      Kuang, Zexi  and
      Cohan, Arman  and
      Zhao, Yilun",
    booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.acl-long.420/",
    doi = "10.18653/v1/2025.acl-long.420",
    pages = "8562--8579",
    ISBN = "979-8-89176-251-0"
}
```
