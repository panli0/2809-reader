#!/usr/bin/env python3
import csv
import gzip
import hashlib
import io
import json
import re
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NGSL_MAIN = "https://static1.squarespace.com/static/64336926d7c6bb38965fdf3b/t/644e0be4ad7bae3d45b9e62a/1682836452194/NGSL_1.2_stats.csv"
DICT_URL = "https://github.com/ahpxex/open-dictionary/releases/download/v2.0/distribution.jsonl.gz"
DICT_SHA256 = "69af69cdc685b5dce465613d1cc8fffb598eb46714f57cf73bd6606c2ceb7e43"
FREEDICT_URL = "https://download.freedict.org/dictionaries/eng-zho/2025.11.23/freedict-eng-zho-2025.11.23.src.tar.xz"
FREEDICT_SHA512 = "25aed0f1d7de68919aa9da1ba92d67f566ae4ea81660f42071c81fc21e56d4b210d61df379315678648c45ca7e52c4a0ba2eec009fbaab7c72e7472489e1fc4c"
OUT = Path("dictionary-ngsl.js")
REPORT = Path("DICTIONARY_COVERAGE.md")
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'.-]*$")
TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
GRAMMAR_LABELS = {"transitive", "intransitive", "ambitransitive", "ditransitive"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "2809-reader dictionary builder"})
    with urllib.request.urlopen(req, timeout=180) as r:
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
            form = (f.get("text") or "").strip().lower()
            if form and WORD_RE.match(form) and form not in forms:
                forms.append(form)
        for m in group.get("meanings") or []:
            priority = m.get("priority") or "rare"
            explanation = (m.get("learner_explanation") or "").strip()
            gloss = (m.get("short_gloss") or "").strip()
            grammar = []
            for label in m.get("labels") or []:
                normalized = str(label).strip().lower()
                if normalized in GRAMMAR_LABELS and normalized not in grammar:
                    grammar.append(normalized)
            if not explanation and not gloss:
                continue
            raw.append((priority_rank.get(priority, 9), priority, pos, gloss, explanation, grammar))
    raw.sort(key=lambda x: x[0])
    for _, priority, pos, gloss, explanation, grammar in raw:
        key = (pos, gloss, explanation, tuple(grammar))
        if key in seen:
            continue
        seen.add(key)
        sense = {"p": priority, "pos": pos, "g": gloss, "z": explanation}
        if grammar:
            sense["l"] = grammar
        senses.append(sense)
        if len(senses) >= 5:
            break
    return ({
        "src": "open-dictionary",
        "summary": (doc.get("headword_summary") or "").strip(),
        "hook": (doc.get("memory_hook") or "").strip(),
        "ipa": ipas[:2],
        "senses": senses,
    }, forms)


def freedict_subset(blob: bytes, targets: set[str]) -> dict[str, dict]:
    if not targets:
        return {}
    if hashlib.sha512(blob).hexdigest() != FREEDICT_SHA512:
        raise SystemExit("FreeDict archive checksum mismatch")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:xz") as archive:
        member = next(m for m in archive.getmembers() if m.name.endswith("eng-zho.tei"))
        stream = archive.extractfile(member)
        if stream is None:
            raise SystemExit("FreeDict TEI file missing")
        for _, element in ET.iterparse(stream, events=("end",)):
            if element.tag != "{http://www.tei-c.org/ns/1.0}entry":
                continue
            head = " ".join((element.findtext("./tei:form/tei:orth", "", TEI_NS) or "").split()).casefold()
            if head not in targets:
                element.clear()
                continue
            senses = []
            translations = []
            seen = set()
            for sense in element.findall("./tei:sense", TEI_NS):
                zh = " ".join((sense.findtext('./tei:cit[@type="trans"]/tei:quote', "", TEI_NS) or "").split())
                if not zh or zh in seen:
                    continue
                seen.add(zh)
                translations.append(zh)
                senses.append({"p": "common", "pos": "", "g": "", "z": zh})
                if len(senses) >= 5:
                    break
            if senses:
                result[head] = {
                    "src": "freedict",
                    "summary": "；".join(translations[:5]),
                    "hook": "",
                    "ipa": [],
                    "senses": senses,
                }
            element.clear()
            if len(result) == len(targets):
                break
    return result


def main():
    words = set(words_from_csv(get(NGSL_MAIN)))
    if len(words) != 2809:
        raise SystemExit(f"Expected 2809 NGSL headwords, got {len(words)}")

    blob = get(DICT_URL)
    if hashlib.sha256(blob).hexdigest() != DICT_SHA256:
        raise SystemExit("Open Dictionary checksum mismatch")

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

    primary_count = len(found)
    primary_missing = words - found.keys()
    supplemental = freedict_subset(get(FREEDICT_URL), set(primary_missing)) if primary_missing else {}
    found.update(supplemental)

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
        "// NGSL 1.2 local dictionary. Open Dictionary subset: CC BY-SA 4.0; FreeDict supplement: CC BY-SA 3.0.\n"
        "// See THIRD_PARTY_NOTICES.md for attribution and source details.\n"
        f"const LOCAL_DICTIONARY={payload};\nconst LOCAL_FORM_MAP={fmap};\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        "# Dictionary coverage\n\n"
        f"- NGSL 1.2 headwords: **{len(words)}**\n"
        f"- Open Dictionary v2.0 matches: **{primary_count}**\n"
        f"- FreeDict eng-zho supplements: **{len(supplemental)}**\n"
        f"- Total local Chinese dictionary matches: **{len(found)}**\n"
        f"- Missing: **{len(missing)}**\n"
        f"- Bundled inflected-form mappings: **{len(form_map)}**\n"
        "- Open Dictionary data license: **CC BY-SA 4.0**\n"
        "- FreeDict eng-zho data license: **CC BY-SA 3.0**\n\n"
        + ("## Missing headwords\n\n" + "\n".join(f"- `{w}`" for w in missing) + "\n" if missing else ""),
        encoding="utf-8",
    )
    print(f"Built {len(found)}/{len(words)} entries ({primary_count} Open Dictionary + {len(supplemental)} FreeDict); {len(form_map)} form mappings; missing {len(missing)}")


if __name__ == "__main__":
    main()
