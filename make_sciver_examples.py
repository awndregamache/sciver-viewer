#!/usr/bin/env python3
"""Generate a human-readable HTML page of SciVer examples — one Entailed and one
Refuted example per reasoning type (direct, analytical, parallel, sequential),
highlighting claim / evidence image(s) / gold label.

SciVer label convention:
  label == True  (Entailed)  -> claim == origin_statement     (a faithful claim)
  label == False (Refuted)   -> claim == perturbed_statement  (origin minimally
                                 altered to be false); perturbed_explanation says why.

Output: ./sciver_examples.html  (run with SciVer/ as cwd; image paths are relative)
"""
import json, html, os, sys, base64
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
# `--standalone` embeds the example images as base64 so the HTML is a single
# self-contained, shareable file (e.g. to commit to a git repo). Default keeps
# lightweight relative-path references into images/.
STANDALONE = "--standalone" in sys.argv
OUT = os.path.join(HERE, "sciver_examples_standalone.html" if STANDALONE
                   else "sciver_examples.html")

data = json.load(open(os.path.join(HERE, "testset.json")))

TYPE_BLURB = {
    "direct":     "Read a value or trend straight off a single chart/table.",
    "analytical": "Reason about <em>why</em> — the numbers may read correctly, "
                  "but the stated cause / interpretation can still be wrong.",
    "parallel":   "Combine evidence from <strong>two</strong> figures/tables to judge the claim.",
    "sequential": "Chained, multi-step reasoning: a result from one item feeds the next.",
}

_title_cache = {}
def paper_title(rec):
    pid = rec["paperid"]
    if pid not in _title_cache:
        try:
            p = json.load(open(os.path.join(HERE, "papers", pid + ".json")))
            _title_cache[pid] = p.get("title", "")
        except Exception:
            _title_cache[pid] = ""
    return _title_cache[pid]

def esc(s):
    return html.escape(str(s if s is not None else "")).replace("\n", "<br>")

def diff_statements(origin, perturbed):
    """Word-level diff of the true vs. perturbed statement. Returns (origin_html,
    perturbed_html) with changed tokens wrapped: removed text as <del> in the
    original, inserted text as <ins> in the perturbed version."""
    import re, difflib
    tok = lambda s: re.findall(r"\s+|\S+", str(s or ""))
    a, b = tok(origin), tok(perturbed)
    sm = difflib.SequenceMatcher(None, a, b)
    o_parts, p_parts = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        o_seg = esc("".join(a[i1:i2]))
        p_seg = esc("".join(b[j1:j2]))
        if tag == "equal":
            o_parts.append(o_seg)
            p_parts.append(p_seg)
        else:  # replace / delete / insert
            if o_seg:
                o_parts.append(f"<del>{o_seg}</del>")
            if p_seg:
                p_parts.append(f"<ins>{p_seg}</ins>")
    return "".join(o_parts), "".join(p_parts)

def img_src(path):
    # JSON stores e.g. "./SciVer/images/foo.png"; this file lives in SciVer/,
    # so strip the leading "./SciVer/" to get a path relative to this page.
    p = str(path).lstrip(".")
    for pre in ("/SciVer/", "SciVer/"):
        if p.startswith(pre):
            p = p[len(pre):]
            break
    return p

def src_attr(relpath):
    """In standalone mode, return a base64 data: URI so the image is embedded in
    the HTML; otherwise return the relative path into images/."""
    if not STANDALONE:
        return relpath
    with open(os.path.join(HERE, relpath), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def badge(label):
    cls = "sup" if label else "ref"
    txt = "Entailed" if label else "Refuted"
    return f'<span class="badge {cls}">{txt}</span>'

def evidence_imgs(rec):
    """Return [(item_label, type, src), ...] for the 1 or 2 evidence items."""
    if rec["claim_type"] in ("direct", "analytical"):
        return [(rec.get("item"), rec.get("type"), img_src(rec["image_path"]))]
    return [
        (rec.get("item1"), rec.get("item1_type"), img_src(rec["item1_path"])),
        (rec.get("item2"), rec.get("item2_type"), img_src(rec["item2_path"])),
    ]

def evidence_block(rec):
    figs = []
    for item, ity, src in evidence_imgs(rec):
        lbl = f"Item {esc(item)}" + (f" &middot; {esc(ity)}" if ity else "")
        figs.append(f"""
      <figure class="evi">
        <div class="evi-head"><span class="evi-id">{lbl}</span></div>
        <img src="{esc(src_attr(src))}" alt="evidence {esc(item)}" loading="lazy">
      </figure>""")
    cls = "evi-pair" if len(figs) == 2 else "evi-single"
    return f'<div class="{cls}">{"".join(figs)}</div>'

def meta_table(rec):
    secs = ", ".join(rec.get("section") or []) or "—"
    o_html, p_html = diff_statements(rec.get("origin_statement"),
                                     rec.get("perturbed_statement"))
    rows = [
        ("Gold label", badge(rec["label"])),
        ("Reasoning type", f'<code>{esc(rec["claim_type"])}</code>'),
        ("Cited section(s)", esc(secs)),
        ("Paper", f'arXiv <code>{esc(rec["paperid"])}</code> — {esc(paper_title(rec))}'),
        ("request_id", f'<code>{esc(rec.get("request_id"))}</code>'),
        ("Original (true) statement", f'<span class="stmt">{o_html}</span>'),
        ("Perturbed (false) statement", f'<span class="stmt">{p_html}</span>'),
    ]
    trs = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f"<table class='meta'>{trs}</table>"

def section(idx, rec):
    t = rec["claim_type"]
    refuted_note = ""
    if not rec["label"]:
        refuted_note = f"""
      <div class="callout">
        <strong>Why it's refuted.</strong> {esc(rec.get('perturbed_explanation'))}
      </div>"""
    return f"""
    <section class="card">
      <h2>Example {idx} &mdash; {esc(t)} {badge(rec['label'])}</h2>
      <p class="topic"><strong>{esc(t.capitalize())} reasoning.</strong>
         {TYPE_BLURB.get(t, "")}</p>

      <div class="claim">
        <span class="claim-label">CLAIM&nbsp;(verify against the evidence)</span>
        <p>{esc(rec['claim'])}</p>
      </div>
      {refuted_note}
      {evidence_block(rec)}

      <details><summary>Full metadata</summary>
        {meta_table(rec)}
        <p class="difflegend stmt">The two statements differ only by the minimal perturbation:
           <del>true tokens (green)</del> → <ins>perturbed tokens (red)</ins>.</p>
      </details>
    </section>"""

# Select one Entailed + one Refuted per reasoning type, in a stable order.
by_type = defaultdict(lambda: {True: None, False: None})
for rec in data:
    slot = by_type[rec["claim_type"]]
    if slot[rec["label"]] is None:
        slot[rec["label"]] = rec

ORDER = ["direct", "analytical", "parallel", "sequential"]
chosen = []
for t in ORDER:
    for lab in (True, False):
        if by_type[t][lab] is not None:
            chosen.append(by_type[t][lab])

body = "".join(section(i + 1, rec) for i, rec in enumerate(chosen))

PAGE = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SciVer — Example Claims</title>
<style>
  :root {{ --sup:#0a7d3c; --ref:#c2261d; --ink:#1a1a1a; --line:#e2e2e2; --bg:#f6f7f9; }}
  * {{ box-sizing:border-box; }}
  body {{ font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); margin:0; background:var(--bg); }}
  header.top {{ background:#11243b; color:#fff; padding:28px 6vw; }}
  header.top h1 {{ margin:0 0 6px; font-size:26px; }}
  header.top p {{ margin:4px 0; color:#cfdcec; max-width:78ch; }}
  main {{ padding:24px 6vw 64px; max-width:1100px; margin:0 auto; }}
  .legend {{ background:#fff; border:1px solid var(--line); border-radius:10px;
             padding:14px 18px; margin:20px 0 28px; }}
  .legend h3 {{ margin:0 0 8px; font-size:15px; text-transform:uppercase; letter-spacing:.04em; color:#555; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:12px;
           padding:22px 24px; margin:0 0 28px; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
  .card h2 {{ margin:0 0 4px; font-size:20px; text-transform:capitalize; }}
  .topic {{ color:#555; margin:.2em 0 1em; }}
  .badge {{ display:inline-block; font-weight:700; font-size:12.5px; letter-spacing:.04em;
            padding:3px 11px; border-radius:6px; color:#fff; text-transform:uppercase; }}
  .badge.sup {{ background:var(--sup); }} .badge.ref {{ background:var(--ref); }}
  .claim {{ border-left:5px solid #f0a202; background:#fffbf0; padding:12px 16px;
            border-radius:0 8px 8px 0; margin:14px 0 16px; }}
  .claim-label {{ font-size:11px; font-weight:700; letter-spacing:.08em; color:#a06a00; }}
  .claim p {{ margin:6px 0 0; font-size:17px; }}
  .callout {{ background:#fdeceb; border:1px solid #f3c9c5; border-radius:8px;
              padding:12px 16px; margin:0 0 18px; font-size:14.5px; }}
  .evi-pair {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  .evi-single {{ display:block; }}
  @media (max-width:760px) {{ .evi-pair {{ grid-template-columns:1fr; }} }}
  figure.evi {{ margin:0; border:1px solid var(--line); border-radius:8px; overflow:hidden; background:#fafafa; }}
  .evi-head {{ padding:8px 12px; background:#f0f2f5; border-bottom:1px solid var(--line); }}
  .evi-id {{ font:12px ui-monospace,Menlo,Consolas,monospace; color:#666; }}
  figure.evi img {{ display:block; width:100%; height:auto; }}
  details {{ margin-top:14px; }}
  summary {{ cursor:pointer; font-weight:600; color:#33506f; }}
  table.meta {{ border-collapse:collapse; width:100%; font-size:14px; margin-top:10px; }}
  table.meta th {{ text-align:left; width:210px; color:#555; font-weight:600; vertical-align:top;
                   padding:6px 10px; border-bottom:1px solid #eee; }}
  table.meta td {{ padding:6px 10px; border-bottom:1px solid #eee; }}
  code {{ font:13px ui-monospace,Menlo,Consolas,monospace; background:#f0f2f5; padding:1px 5px; border-radius:4px; }}
  .stmt del {{ background:#d7f0df; color:#0a5e2c; text-decoration:none; font-weight:700; padding:0 2px; border-radius:3px; }}
  .stmt ins {{ background:#fde2e0; color:#a3160c; text-decoration:none; font-weight:700; padding:0 2px; border-radius:3px; }}
  .difflegend {{ font-size:12.5px; color:#666; margin:2px 0 0; }}
  .muted {{ color:#888; }}
</style></head>
<body>
<header class="top">
  <h1>SciVer — Multimodal Scientific Claim Verification</h1>
  <p>Each item pairs a natural-language <strong>claim</strong> with the figure/table
     <strong>evidence</strong> from a paper it refers to, and a <strong>gold label</strong>:
     <span class="badge sup">Entailed</span> or <span class="badge ref">Refuted</span>.</p>
  <p>The benchmark's trick: <strong>Refuted claims are made by minimally perturbing a true
     statement</strong> (changing a number, flipping a comparison) — so the model must actually
     read the evidence, not pattern-match plausible text. The <em>perturbed_explanation</em> field
     (shown for refuted items) states exactly what's wrong.</p>
  <p style="font-size:13px;color:#9fb3c8">Test set &middot; 2,000 examples across four reasoning
     types. Below: one Entailed + one Refuted per type.</p>
</header>
<main>
  <div class="legend">
    <h3>How to read each example</h3>
    <p style="margin:.2em 0"><strong>Claim</strong> (amber box) → the sentence to verify &nbsp;·&nbsp;
       <strong>Evidence</strong> → the figure/table image(s) it cites &nbsp;·&nbsp;
       <strong>Gold label</strong> → the colored badge. Refuted items add a red
       “Why it's refuted” box; expand “Full metadata” for the original-vs-perturbed pair.</p>
  </div>
  {body}
  <p class="muted" style="font-size:13px">Generated by <code>make_sciver_examples.py</code> from
     <code>testset.json</code>. Keep this file in the <code>SciVer/</code> folder so the
     <code>images/</code> paths resolve.</p>
</main>
</body></html>"""

open(OUT, "w").write(PAGE)
print("Wrote", OUT, f"({len(PAGE)} bytes), {len(chosen)} examples")
# sanity: confirm every referenced image exists
missing = 0
for rec in chosen:
    for _, _, src in evidence_imgs(rec):
        ok = os.path.exists(os.path.join(HERE, src))
        if not ok:
            missing += 1
            print("  MISSING", src)
print("  image check:", "all present" if missing == 0 else f"{missing} missing")
