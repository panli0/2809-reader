#!/usr/bin/env python3
"""Reproducible NGSL 1.2 coverage audit for the nine story chapters.

The target list is taken from the bundled local dictionary keys plus the
project-curated supplement. Inflected forms use the exact bundled form map.
This intentionally audits the story body, not dictionary coverage metadata.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[’'][A-Za-z]+)*")
CHAPTER_RE = re.compile(r"chapter-(\d+)\.js$")

def extract_js_json(source: str, marker: str):
    start = source.index(marker) + len(marker)
    value, end = json.JSONDecoder().raw_decode(source, start)
    return value, end

def normalize_token(token: str) -> list[str]:
    token = token.replace("’", "'").lower()
    if token.endswith("'s") and len(token) > 2:
        token = token[:-2]
    elif token.endswith("s'") and len(token) > 2:
        token = token[:-1]
    contractions = {
        "don't": ("do", "not"), "doesn't": ("do", "not"),
        "didn't": ("do", "not"), "can't": ("can", "not"),
        "cannot": ("cannot",), "couldn't": ("could", "not"),
        "wouldn't": ("would", "not"), "shouldn't": ("should", "not"),
        "mustn't": ("must", "not"), "needn't": ("need", "not"),
        "mightn't": ("might", "not"), "isn't": ("is", "not"),
        "aren't": ("are", "not"), "wasn't": ("was", "not"),
        "weren't": ("were", "not"), "haven't": ("have", "not"),
        "hasn't": ("has", "not"), "hadn't": ("had", "not"),
        "won't": ("will", "not"), "shan't": ("shall", "not"),
        "ain't": ("be", "not"),
    }
    if token in contractions:
        return list(contractions[token])
    for suffix in ("'re", "'ve", "'ll", "'m", "'d"):
        if token.endswith(suffix) and len(token) > len(suffix):
            return [token[:-len(suffix)]]
    return [token]

def main():
    dict_source = (ROOT / "dictionary-ngsl.js").read_text(encoding="utf-8")
    local_dict, _ = extract_js_json(dict_source, "const LOCAL_DICTIONARY=")
    form_map, _ = extract_js_json(dict_source, "const LOCAL_FORM_MAP=")

    supplement_source = (ROOT / "dictionary-supplement.js").read_text(encoding="utf-8")
    supplements, _ = extract_js_json(supplement_source, "const LOCAL_DICTIONARY_SUPPLEMENT=")
    targets = {str(w).lower() for w in local_dict} | {str(w).lower() for w in supplements}
    forms = {str(k).lower(): str(v).lower() for k, v in form_map.items()}

    chapter_files = sorted(
        (p for p in ROOT.glob("chapter-*.js") if CHAPTER_RE.search(p.name)),
        key=lambda p: int(CHAPTER_RE.search(p.name).group(1)),
    )
    if len(chapter_files) != 9:
        raise SystemExit(f"Expected 9 chapter files, found {len(chapter_files)}")

    present_counts = Counter()
    chapter_counts = defaultdict(Counter)
    chapter_word_counts = {}
    total_tokens = 0
    for path in chapter_files:
        source = path.read_text(encoding="utf-8")
        chapter_obj, _ = extract_js_json(source, "CHAPTERS.push(")
        chapter_no = int(CHAPTER_RE.search(path.name).group(1))
        paragraphs = chapter_obj.get("paragraphs") or []
        text = "\n".join(str(p) for p in paragraphs)
        tokens = TOKEN_RE.findall(text)
        chapter_word_counts[chapter_no] = len(tokens)
        total_tokens += len(tokens)
        for token in tokens:
            for candidate in normalize_token(token):
                candidate = candidate.lower()
                head = candidate if candidate in targets else forms.get(candidate)
                if head in targets:
                    present_counts[head] += 1
                    chapter_counts[head][chapter_no] += 1

    missing = sorted(targets - set(present_counts))
    total = len(targets)
    lines = [
        "# NGSL story-body coverage audit",
        "",
        "This report is generated from the actual nine chapter JS story files.",
        "Target headwords are the keys in dictionary-ngsl.js plus",
        "dictionary-supplement.js; inflected forms use the bundled LOCAL_FORM_MAP.",
        "Dictionary availability alone is not counted as story coverage.",
        "",
        f"- Target headwords: **{total}**",
        f"- Found in story body: **{total - len(missing)}**",
        f"- Missing from story body: **{len(missing)}**",
        f"- Coverage: **{(total - len(missing)) / total:.2%}**",
        f"- Story word tokens: **{total_tokens:,}**",
        f"- Chapter word counts: " + "; ".join(f"Ch. {n}: {chapter_word_counts[n]:,}" for n in sorted(chapter_word_counts)),
        "",
        "## Missing headwords",
        "",
    ]
    lines.extend(f"- {word}" for word in missing)
    lines.extend(["", "## Reproducibility details", "",
                  f"- Dictionary entries: {len(local_dict)}",
                  f"- Curated supplement entries: {len(supplements)}",
                  f"- Inflected-form mappings: {len(forms)}",
                  f"- Chapter files audited: {len(chapter_files)}",
                  ""])
    report = "\n".join(lines)
    (ROOT / "STORY_COVERAGE_AUDIT.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"::notice title=NGSL story coverage::{total - len(missing)}/{total}; missing {len(missing)}")

if __name__ == "__main__":
    main()
