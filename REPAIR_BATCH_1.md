# Repair batch 1 — validation notes

## Safety and rollback
- Original main commit: `5b668d576c457210ea484e33529e945b5d188dc0`
- Exact backup branch: `backup/pre-repair-2026-11-01`
- Backup branch includes `RESTORE_PRE_REPAIR.md` with restore instructions.
- Work branch: `repair/reader-quality-2026-11-01`
- No changes have been made to `main`; nothing has been deployed.

## Changes in this batch
- Added the missing NGSL headword `fee` naturally to Chapter Three.
- Added a project-maintained Chinese dictionary supplement for the six NGSL words missing from the third-party dictionary datasets: `anymore`, `catalog`, `fascinate`, `okay`, `situate`, `underlie`.
- Updated dictionary loader and cache version to v13; added the supplement to the service-worker cache.
- Added 24 context-linked PHaVE-aligned phrasal-verb entries in `collocations-3.js` (some phrases have more than one in-story context).
- Updated collocation matching to split multi-sentence source contexts before matching.

## Validation
- All nine chapter files parsed as JSON payloads and retained their paragraph arrays.
- Chapter Three now contains `fee`; its body is 1812 words.
- Loader, supplement lookup, script inclusion, and service-worker asset references were checked.
- Automated browser/runtime and accessibility tests have not yet been run.
- Chapter-length balancing and full PHRASE/PHaVE coverage expansion remain in the next repair batch; this batch is not a final release.

## Chapter counts after the one-word insertion
- Chapter 1: 1487 words; 21 paragraphs
- Chapter 2: 1924 words; 22 paragraphs
- Chapter 3: 1812 words; 32 paragraphs
- Chapter 4: 2494 words; 33 paragraphs
- Chapter 5: 1427 words; 33 paragraphs
- Chapter 6: 1477 words; 28 paragraphs
- Chapter 7: 1836 words; 11 paragraphs
- Chapter 8: 2340 words; 28 paragraphs
- Chapter 9: 2517 words; 14 paragraphs
