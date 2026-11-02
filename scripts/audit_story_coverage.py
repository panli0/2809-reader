#!/usr/bin/env python3
"""Hard-gate audit for every required target in the nine-chapter story."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[’'][A-Za-z]+)*")
CHAPTER_RE = re.compile(r"chapter-(\d+)\.js$")
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])["”’]?\s+')
MAX_SEPARABLE_GAP = 8


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


def normalize_text(value: str) -> str:
    return re.sub(
        r"\s+", " ",
        str(value).replace("’", "'").replace("‘", "'")
        .replace("“", '"').replace("”", '"').lower()
    ).strip()


def phrase_token(token: str, forms: dict[str, str]) -> str:
    token = token.replace("’", "'").lower()
    # Add the common irregular form for PHaVE targets "lay out" and "lay down".
    if token == "laid":
        return "lay"
    return forms.get(token, token)


def main() -> int:
    dict_source = (ROOT / "dictionary-ngsl.js").read_text(encoding="utf-8")
    local_dict, _ = extract_js_json(dict_source, "const LOCAL_DICTIONARY=")
    form_map, _ = extract_js_json(dict_source, "const LOCAL_FORM_MAP=")

    supplement_source = (ROOT / "dictionary-supplement.js").read_text(encoding="utf-8")
    supplements, _ = extract_js_json(
        supplement_source, "const LOCAL_DICTIONARY_SUPPLEMENT="
    )
    targets = {str(w).lower() for w in local_dict} | {
        str(w).lower() for w in supplements
    }
    forms = {str(k).lower(): str(v).lower() for k, v in form_map.items()}

    chapter_files = sorted(
        (p for p in ROOT.glob("chapter-*.js") if CHAPTER_RE.search(p.name)),
        key=lambda p: int(CHAPTER_RE.search(p.name).group(1)),
    )
    if len(chapter_files) != 9:
        raise SystemExit(f"Expected 9 chapter files, found {len(chapter_files)}")

    chapter_word_counts = {}
    story_paragraphs = []
    present_words = set()
    total_tokens = 0

    for path in chapter_files:
        source = path.read_text(encoding="utf-8")
        chapter_obj, _ = extract_js_json(source, "CHAPTERS.push(")
        chapter_no = int(CHAPTER_RE.search(path.name).group(1))
        paragraphs = [str(p) for p in (chapter_obj.get("paragraphs") or [])]
        story_paragraphs.extend(paragraphs)

        chapter_tokens = 0
        for paragraph in paragraphs:
            tokens = TOKEN_RE.findall(paragraph)
            chapter_tokens += len(tokens)
            for token in tokens:
                for candidate in normalize_token(token):
                    head = forms.get(candidate, candidate)
                    if head in targets:
                        present_words.add(head)

        chapter_word_counts[chapter_no] = chapter_tokens
        total_tokens += chapter_tokens

    missing_words = sorted(targets - present_words)
    story_body = "\n".join(story_paragraphs)
    normalized_body = normalize_text(story_body)

    # Every curated common-meaning context must be present in the actual story.
    poly_files = sorted(ROOT.glob("poly-*.js"))
    if len(poly_files) != 4:
        raise SystemExit(f"Expected 4 polysemy files, found {len(poly_files)}")
    poly_heads = set()
    poly_records = []
    missing_poly = []
    for path in poly_files:
        source = path.read_text(encoding="utf-8")
        poly_data, _ = extract_js_json(source, "Object.assign(POLY,")
        for head, entries in poly_data.items():
            poly_heads.add(head)
            for entry in entries:
                context = str(entry.get("context") or "")
                record = f"{head} — {entry.get('sense', '')}"
                poly_records.append(record)
                if not context or normalize_text(context) not in normalized_body:
                    missing_poly.append(record)

    # The PHaVE inventory is the 150-item source list, not the context-bank labels.
    phave_text = (ROOT / "PHAVE_COVERAGE.md").read_text(encoding="utf-8")
    tick = chr(96)
    phrase_pattern = re.compile(
        r"^\s*\d+\.\s+" + re.escape(tick)
        + r"([^" + re.escape(tick) + r"]+)" + re.escape(tick),
        re.MULTILINE,
    )
    phrases = phrase_pattern.findall(phave_text)
    phrase_hits = set()
    for paragraph in story_paragraphs:
        for sentence in SENTENCE_SPLIT_RE.split(paragraph):
            tokens = [
                phrase_token(token, forms)
                for token in TOKEN_RE.findall(sentence)
            ]
            for phrase in phrases:
                parts = phrase.lower().split()
                if len(parts) != 2:
                    continue
                verb, particle = parts
                for index, token in enumerate(tokens):
                    if token != verb:
                        continue
                    stop = min(len(tokens), index + MAX_SEPARABLE_GAP + 2)
                    if particle in tokens[index + 1:stop]:
                        phrase_hits.add(phrase)
                        break

    missing_phrases = sorted(set(phrases) - phrase_hits)
    duplicate_phrases = len(phrases) - len(set(phrases))

    lines = [
        "# Complete story coverage audit",
        "",
        "This report checks the actual text in all nine chapter files.",
        "Dictionary entries, vocabulary notes, and audit files do not count as story-body coverage.",
        "",
        "## 1. Base vocabulary",
        "",
        f"- NGSL + curated supplement targets: **{len(targets)}**",
        f"- Found in story body: **{len(targets) - len(missing_words)} / {len(targets)}**",
        f"- Missing: **{len(missing_words)}**",
        f"- Story word tokens: **{total_tokens:,}**",
        "- Chapter word counts: " + "; ".join(
            f"Ch. {n}: {chapter_word_counts[n]:,}"
            for n in sorted(chapter_word_counts)
        ),
        "",
        "### Missing base words",
        "",
    ]
    lines.extend(f"- {word}" for word in missing_words)
    if not missing_words:
        lines.append("- None")

    lines.extend([
        "",
        "## 2. Polysemy: every common meaning",
        "",
        f"- Polysemous headwords: **{len(poly_heads)}**",
        f"- Required sense-context records: **{len(poly_records)}**",
        f"- Exact normalized contexts found in story body: **{len(poly_records) - len(missing_poly)} / {len(poly_records)}**",
        f"- Missing sense contexts: **{len(missing_poly)}**",
        "",
        "### Missing sense contexts",
        "",
    ])
    lines.extend(f"- {item}" for item in missing_poly)
    if not missing_poly:
        lines.append("- None")

    lines.extend([
        "",
        "## 3. PHaVE 150 phrasal verbs",
        "",
        f"- Target phrases in source inventory: **{len(phrases)}**",
        f"- Found in story: **{len(phrase_hits)} / {len(phrases)}**",
        f"- Missing: **{len(missing_phrases)}**",
        "",
        "### Missing phrases",
        "",
    ])
    lines.extend(f"- {phrase}" for phrase in missing_phrases)
    if not missing_phrases:
        lines.append("- None")

    lines.extend([
        "",
        "## Matching rules",
        "",
        "- Base words: actual chapter-body tokens, including bundled inflected forms.",
        "- Polysemy: each curated context must appear in the chapter body after quote and whitespace normalization.",
        "- PHaVE: common verb inflections and separable-object constructions are accepted only within the same sentence; up to eight intervening tokens are allowed.",
        "- The irregular form laid is normalized to lay for the PHaVE targets lay out and lay down.",
        "",
        "## Reproducibility details",
        "",
        f"- Local dictionary entries: {len(local_dict)}",
        f"- Curated dictionary supplements: {len(supplements)}",
        f"- Inflected-form mappings: {len(forms)}",
        f"- Chapter files audited: {len(chapter_files)}",
        f"- Polysemy files audited: {len(poly_files)}",
        f"- PHaVE target list duplicates: {duplicate_phrases}",
        "",
    ])

    report = "\n".join(lines)
    (ROOT / "STORY_COVERAGE_AUDIT.md").write_text(report, encoding="utf-8")
    print(report)

    failed = bool(
        missing_words or missing_poly or missing_phrases
        or len(targets) != 2809
        or len(poly_heads) != 122
        or len(poly_records) != 248
        or len(phrases) != 150
        or duplicate_phrases
    )
    print(
        "::notice title=Complete story coverage::"
        f"words {len(targets) - len(missing_words)}/{len(targets)}; "
        f"senses {len(poly_records) - len(missing_poly)}/{len(poly_records)}; "
        f"PHaVE {len(phrase_hits)}/{len(phrases)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
