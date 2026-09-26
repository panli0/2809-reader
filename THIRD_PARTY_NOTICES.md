# Third-party data and software notices

## Open Dictionary v2.0

The bundled Chinese learner-dictionary data in `dictionary-ngsl.js` is a filtered subset of **Open Dictionary v2.0** (`ahpxex/open-dictionary`).

- Project: https://github.com/ahpxex/open-dictionary
- Release: v2.0 (2026-08-05)
- Data license: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**
- Upstream lexical content: **English Wiktionary**, extracted through **Wiktextract**
- License: https://creativecommons.org/licenses/by-sa/4.0/

Open Dictionary states that its distribution data is derived from English Wiktionary and includes structured/generated learner-facing expansions. Redistribution requires attribution and ShareAlike under CC BY-SA 4.0. This project filters the release to NGSL 1.2 headwords and stores compact learner-facing fields such as summaries, prioritized meanings, IPA, and inflection mappings where available. The filtered dictionary data remains under CC BY-SA 4.0.

The production reader does **not** query Chinese Wiktionary or qwerty-learner at runtime for ordinary Chinese dictionary definitions.

## NGSL (New General Service List) 1.2

The vocabulary selection is based on the **New General Service List 1.2** by Charles Browne, Brent Culligan, and Joseph Phillips.

- Official project: https://www.newgeneralservicelist.com/
- NGSL 1.2 headwords used here: 2,809
- License: **CC BY-SA 4.0**

## Compromise

Optional verb-form assistance is provided by the Compromise JavaScript NLP library loaded from jsDelivr. If that external script is unavailable, the core reader and bundled dictionary continue to work.

- Project: https://github.com/spencermountain/compromise

## Notes

The project previously used a temporary NGSL Chinese JSON file from qwerty-learner and later experimented with runtime Chinese-Wiktionary lookup. Neither source is used by the production ordinary-word dictionary lookup now. Existing high-value contextual glosses for this story are project-authored annotations rather than copies of the temporary qwerty-learner dictionary.
