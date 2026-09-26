#!/usr/bin/env python3
import csv
import gzip
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

NGSL_MAIN = "https://static1.squarespace.com/static/64336926d7c6bb38965fdf3b/t/644e0be4ad7bae3d45b9e62a/1682836452194/NGSL_1.2_stats.csv"
DICT_URL = "https://github.com/ahpxex/open-dictionary/releases/download/v2.0/distribution.jsonl.gz"
DICT_SHA256 = "69af69cdc685b5dce465613d1cc8fffb598eb46714f57cf73bd6606c2ceb7e43"
OUT = Path("dictionary-ngsl.js")
REPORT = Path("DICTIONARY_COVERAGE.md")

WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'.-]*$")


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "2809-reader dictionary builder"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def words_from_csv(data: bytes) -> list[str]:
    text = data.decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []
    header = [c.strip().lower() for c in rows[0]]
    idx = next((i for i, h in enumerate(header) if "lemma" in h or h in {"word", "headword"}), None)
    start = 1 if idx is not None else 0
    out = []
    for row in rows[start:]:
        if not row:
            continue
        cell = ""
        if idx is not None and idx < len(row):
            cell = row[idx].strip()
        else:
            for candidate in row[:3]:
                candidate = candidate.strip()
                if WORD_RE.match(candidate):
                    cell = candidate
                    break
        if cell and WORD_RE.match(cell):
            out.append(cell.lower())
    return out


def compact_entry(doc: dict) -> tuple[dict, list[str]]:
    senses = []
    seen = set()
    priority_rank = {"core": 0, "common": 1, "rare": 2}
    raw = []
    ipas = []
    forms = []
    for group in doc.get("pos_groups") or []:
        pos = group.get("pos") or ""
        for p in group.get("pronunciations") or []:
            ipa = (p.get("ipa") or "").strip()
            if ipa and ipa not in ipas:
                ipas.append(ipa)
        for f in group.get("forms") or []:
            form = (f.get("form") or "").strip().lower()
            if form and WORD_RE.match(form) and form not in forms:
                forms.append(form)
        for m in group.get("meanings") or []:
            priority = m.get("priority") or "rare"
            explanation = (m.get("learner_explanation") or "").strip()
            gloss = (m.get("short_gloss") or "").strip()
            if not explanation and not gloss:
                continue
            raw.append((priority_rank.get(priority, 9), priority, pos, gloss, explanation))
    raw.sort(key=lambda x: x[0])
    for _, priority, pos, gloss, explanation in raw:
        key = (pos, gloss, explanation)
        if key in seen:
            continue
        seen.add(key)
        senses.append({"p": priority, "pos": pos, "g": gloss, "z": explanation})
        if len(senses) >= 5:
            break
    return ({
        "summary": (doc.get("headword_summary") or "").strip(),
        "hook": (doc.get("memory_hook") or "").strip(),
        "ipa": ipas[:2],
        "senses": senses,
    }, forms)


def main():
    words = set(words_from_csv(get(NGSL_MAIN)))
    if len(words) != 2809:
        raise SystemExit(f"Expected 2809 NGSL headwords, got {len(words)}")

    blob = get(DICT_URL)
    digest = hashlib.sha256(blob).hexdigest()
    if digest != DICT_SHA256:
        raise SystemExit(f"Dictionary checksum mismatch: {digest}")

    found = {}
    forms_by_head = {}
    with gzip.GzipFile(fileobj=io.BytesIO(blob)) as gz:
        for raw_line in gz:
            try:
                doc = json.loads(raw_line)
            except Exception:
                continue
            head = (doc.get("normalized_headword") or doc.get("headword") or "").strip().lower()
            if head in words and head not in found:
                entry, forms = compact_entry(doc)
                if entry["senses"] or entry["summary"]:
                    found[head] = entry
                    forms_by_head[head] = forms
            if len(found) == len(words):
                break

    form_candidates = {}
    ambiguous = set()
    for head, forms in forms_by_head.items():
        for form in forms:
            if form == head or form in words:
                continue
            old = form_candidates.get(form)
            if old and old != head:
                ambiguous.add(form)
            else:
                form_candidates[form] = head
    form_map = {f: h for f, h in form_candidates.items() if f not in ambiguous}

    missing = sorted(words - found.keys())
    payload = json.dumps(found, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    fmap = json.dumps(form_map, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    OUT.write_text(
        "// NGSL 1.2 subset of Open Dictionary v2.0. Data: CC BY-SA 4.0.\n"
        "// Source: https://github.com/ahpxex/open-dictionary ; upstream: English Wiktionary/Wiktextract.\n"
        f"const LOCAL_DICTIONARY={payload};\nconst LOCAL_FORM_MAP={fmap};\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        "# Dictionary coverage\n\n"
        f"- NGSL 1.2 headwords: **{len(words)}**\n"
        f"- Local Chinese dictionary matches: **{len(found)}**\n"
        f"- Missing: **{len(missing)}**\n"
        f"- Bundled inflected-form mappings: **{len(form_map)}**\n"
        "- Source dictionary: **ahpxex/open-dictionary v2.0**\n"
        "- Dictionary-data license: **CC BY-SA 4.0**\n"
        "- Upstream: English Wiktionary via Wiktextract\n\n"
        + ("## Missing headwords\n\n" + "\n".join(f"- `{w}`" for w in missing) + "\n" if missing else ""),
        encoding="utf-8",
    )
    print(f"Built {len(found)}/{len(words)} entries; {len(form_map)} form mappings; missing {len(missing)}")


if __name__ == "__main__":
    main()
