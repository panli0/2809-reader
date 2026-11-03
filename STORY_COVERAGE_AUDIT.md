# Complete story coverage audit

This report checks the actual text in all nine chapter files. Dictionary entries, vocabulary notes, and audit files do not count as story-body coverage.

## 1. Base vocabulary

- NGSL + curated supplement targets: **2,809**
- Found in story body: **2,809 / 2,809**
- Missing: **0**
- Story word tokens: **10,404**
- Chapter word counts: Ch. 1: 1,132; Ch. 2: 1,312; Ch. 3: 1,040; Ch. 4: 1,551; Ch. 5: 877; Ch. 6: 1,074; Ch. 7: 1,008; Ch. 8: 1,283; Ch. 9: 1,127

### Missing base words

- None

## 2. Polysemy: every common meaning

- Polysemous headwords: **122**
- Required sense-context records: **248**
- Exact normalized contexts found in story body: **248 / 248**
- Missing sense contexts: **0**

### Missing sense contexts

- None

## 3. PHaVE 150 phrasal verbs

- Target phrases in source inventory: **150**
- Found in story: **150 / 150**
- Missing: **0**

### Missing phrases

- None

## 4. Collocation contexts

- Context records across ten collocation files: **284**
- Unique phrase patterns: **276**
- Exact normalized contexts found in story body: **284 / 284**
- Listed phrase demonstrated in its own context: **284 / 284**
- Missing contexts: **0**
- Context/pattern mismatches: **0**

### Missing collocation contexts

- None

### Contexts that do not demonstrate their listed phrase

- None

## 5. Compression

- Previous verified story length: **15,980 words**
- Compressed story length: **10,404 words**
- Reduction: **5,576 words (34.9%)**
- All 2,809 dictionary headwords, 248 common-sense contexts, 150 PHaVE phrases, and 284 collocation contexts remain in the actual chapter text.

## Matching rules

- Base words: actual chapter-body tokens, including bundled inflected forms.
- Polysemy: each curated common-meaning context must appear in the chapter body after quote and whitespace normalization.
- PHaVE: common verb inflections and separable-object constructions are checked within the same sentence; hyphenated compounds do not count as phrasal verbs.
- Collocations: every context record must appear in the chapter body after quote and whitespace normalization, and its own text must demonstrate the listed phrase (including common inflections, separable particles, and the documented A/B or gerund templates).

- Audited story commit: `985f2c0f5a7bf4fd3f2a0d979fd603743752149b`
- GitHub Actions verification: [run 41634495890](https://github.com/panli0/2809-reader/actions/runs/41634495890) — **success**.

## Reproducibility details

- Local dictionary entries: 2,803
- Curated dictionary supplements: 6
- Inflected-form mappings: 7,930
- Chapter files audited: 9
- Polysemy files audited: 4
- PHaVE target list duplicates: 0
- Collocation files audited: 10
