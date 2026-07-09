# i18n schema conventions

- One JSON file per language (`en.json`, `de.json`, `fr.json`)
- Flat key namespace using dotted keys:
  - `verification.support_ticket`
  - `verification.support_ticket_fallback`
- Values are plain strings with `{placeholder}` interpolation.

## Placeholder safety

- Placeholder names are lowercase snake_case.
- Runtime interpolation is best-effort:
  - if placeholder value is provided, it is substituted.
  - if missing, placeholder is preserved literally (`{name}`), avoiding crashes.

Locales:

en, bg, hr, cs, da, nl, fi, fr, de, el, hu, it, lt, no, pl, pt, ro, ru, es, sv, tr, uk
