# Complete story coverage audit

Rechecked against the current compact branch on **2026-11-04**. This report counts the actual nine chapter files, not dictionary entries or coverage notes.

## 1. Base vocabulary

- NGSL 1.2 headwords: **2,809**
- Local Chinese dictionary entries: **2,803 Open Dictionary + 6 curated supplements**
- Base headwords found in story body: **2,809 / 2,809**
- Missing base headwords: **0**
- Inflected-form mappings used for matching: **7,930**
- Actual story word tokens: **11,385**

### Chapter word counts

| Chapter | Words |
|---|---:|
| 1 | 1,127 |
| 2 | 1,322 |
| 3 | 1,078 |
| 4 | 1,621 |
| 5 | 899 |
| 6 | 1,162 |
| 7 | 1,145 |
| 8 | 1,627 |
| 9 | 1,404 |
| **Total** | **11,385** |

## 2. Polysemy: every common meaning

- Polysemous headwords: **122**
- Required common-sense context records: **248**
- Exact normalized contexts found in story body: **248 / 248**
- Missing sense contexts: **0**

## 3. PHaVE 150 phrasal verbs

- Target phrases in source inventory: **150**
- Found in story: **150 / 150**
- Missing phrases: **0**
- Matching includes common verb forms and separable-object constructions within the same sentence.

## 4. Collocation contexts

- Context records across ten files: **284**
- Unique phrase patterns: **276**
- Exact normalized contexts found in story body: **284 / 284**
- Contexts demonstrating their own listed phrase: **284 / 284**
- Missing contexts: **0**
- Context/pattern mismatches: **0**

## 5. Compression

- Previous verified story length: **15,980 words**
- Current story length: **11,385 words**
- Reduction: **4,595 words (28.8%)**
- All 2,809 base headwords, 248 common-meaning contexts, 150 PHaVE phrases, and 284 collocation contexts remain in the actual chapter text.

## Matching rules

- Base words: actual chapter-body tokens, including the 7,930 bundled inflected-form mappings.
- Polysemy: each curated common-meaning context must occur in the chapter body after quote and whitespace normalization.
- PHaVE: common verb inflections and separable-object constructions are checked within the same sentence.
- Collocations: every context record must occur in the chapter body and demonstrate its own listed phrase.

## Reproducibility details

- Chapter files audited: **9**
- Polysemy files audited: **4**
- PHaVE source inventory duplicates: **0**
- Collocation files audited: **10**
- Last full programmatic audit source: `scripts/audit_story_coverage.py`
