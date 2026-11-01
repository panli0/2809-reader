# Repair batch 2 — chapter and phrase quality

## Chapter balance

Word counts use alphabetic word tokens from the nine chapter paragraph arrays.

| Chapter | Words | Paragraphs | Longest paragraph |
|---|---:|---:|---:|
| 1 | 1835 | 29 | 112 |
| 2 | 1955 | 29 | 115 |
| 3 | 1818 | 37 | 111 |
| 4 | 2098 | 40 | 115 |
| 5 | 1960 | 42 | 115 |
| 6 | 1994 | 40 | 114 |
| 7 | 2102 | 26 | 115 |
| 8 | 2245 | 37 | 115 |
| 9 | 2287 | 34 | 115 |

- Average chapter length: **2033 words**
- Shortest / longest: **1818 / 2287 words**
- Every paragraph is **115 words or fewer** after sentence-aware splitting.

## Story and language work

- Added character and family-history beats to Chapter One.
- Added care-home evacuation, rescue, shelter inventory, and riverbank details to Chapter Five.
- Added resident testimony, worker testimony, and clearer hearing outcomes to Chapter Six.
- Rebalanced longer exposition in Chapters Four, Eight, and Nine while preserving the investigation and policy arc.
- Added natural PHaVE examples across the story rather than placing the phrases in a detached vocabulary dump.
- Added `collocations-3.js` through `collocations-10.js` and aligned all phrase contexts with current story sentences.

## Phrase checks

- PHaVE list: **150 / 150** items found in the nine chapters.
- Context bank: **284** records, **276** unique patterns.
- Unmatched context records: **0**.
- PHRASE 505: separate audit still pending.

## Dictionary and application checks

- NGSL local dictionary coverage: **2809 / 2809** with six project-maintained supplements.
- `fee` appears naturally in Chapter Three.
- Dictionary attribution distinguishes Open Dictionary, FreeDict, and project-maintained entries.
- Dictionary build script now includes project-maintained supplements in its coverage calculation.
- All chapter and collocation JavaScript files passed syntax compilation.
- Application, data loader, local dictionary UI, supplement, polysemy files, and service worker passed syntax compilation.
- Every script referenced by `index.html` is present in the branch.
- Every story/collocation asset is included in the service-worker cache; dictionary scripts are cached with their exact `?v=13` URLs for offline lookup; cache version is `river-year-v21`.

## Safety and release

- Original main commit remains `5b668d576c457210ea484e33529e945b5d188dc0`.
- Backup branch: `backup/pre-repair-2026-11-01`.
- Repair branch: `repair/reader-quality-2026-11-01`.
- `main` was verified to still point to the original commit.
- The repair branch has not been merged or deployed.
- Browser-based end-to-end tests and the PHRASE 505 audit remain outstanding.
