# Naming and branding

Use only when naming or branding is selected. Reuse an existing approved name
and style; preparing a paragraph or investor document does not itself select
renaming, domain checks, or new fonts. Examples below are optional design choices.

## Explore names when requested

A good name for a decision product is chosen the way "counterpoint" was: by
**allegory** (the second voice arguing against the first until the resolution
is stronger — *exactly* the product), not because letters cluster near some
baseline. When the user has an instinct, clarify what the **theme** is, not
what the sound is.

### Check for negative real-world meanings before you commit

A name that "sounds fine" can carry a fatal unrelated meaning. Example from
experience: **"Kuru"** (and "kuru.ai") is the name of a fatal prion disease.
A medical/science-aware investor reads that immediately. Always safety-check
for:
- diseases, medical conditions, disasters, or other negative common nouns;
- a foreign-language word with a bad meaning you don't know;
- a crowded existing software/product category (e.g., Delphi the IDE).

Surface any concern to the user directly and let them decide — do not
silently override a name they chose. Recommended lines to offer: keep a
near-sound-alike, pick from a themed shortlist, or rebrand.

### Availability/TM/domain sanity check

For a requested new-name selection, perform the authorized preliminary checks
before recommending adoption, or mark them unverified. These are not legal
clearance and do not authorize registration or purchase. Relevant checks include:
- domain availability (e.g., `domain.com`, and `.ai` if it's an AI product),
- trademark/collision search,
- prior software category of the same word/phoneme.

## Build a brand mark, don't just type the name

Style the brand so it stands apart from the body:

- a **brand font** (distinct from the body font) — the mark uses this,
- a **body font** for everything else,
- an **accent color** used only for emphasis (pull-quote bar, links, the
  `.tld`/domain part of the mark).

### Brand/wordmark conventions that worked

- Put the product name in an ink color, and the **".ai" (or domain) in the
  accent color** — this is the more premium reading than coloring the whole
  word. (The inverse — accent on the whole word — is louder; offer it.)
- Optionally embolden the `.ai` while the name stays regular.
- Optionally add letter-spacing *between* characters in the name to open it
  up. Apply that spacing to the word only, not the `.tld`.
- Keep an internal namespace clean: a `.brand` span wraps the name, and a
  `.tld` span wraps the domain, so each can be styled independently.

## Colors

Choose an accent by what it signals for the product, and test on a page
before committing. For an enterprise/investor product:
- **Indigo / deep teal / deep desaturated purple** read authoritative and
  premium and won't "shout" on a white page.
- Magenta and hot saffron are bright — often too loud for an investor deck.
- "Chrome"/metallic slate is fine as a secondary metallic, weak as the primary
  hero color.

A left-to-right **gradient on the `.ai` from accent → gray** is a refined
modern look, but WeasyPrint does not reliably rasterize a gradient defined in
a separate `<svg>`. If you must do a gradient, bake an external `.svg` image
with the gradient inside the same file and reference it via `<img>` — or skip
it ("keep it simple"). Solid color is the dependable default.

## Fonts: embed locally, never depend on runtime Google Fonts

For a shareable PDF, prefer already-present licensed fonts and embed them.
If a new font is necessary, prepare its exact source, license, purpose, and local
path before requesting missing download authorization. Do not fetch fonts merely
because a branding example lists them.

A start of palette that works on the page, and personal notes:
- Body: Work Sans, Inter, Figtree are neutral-modern; IBM Plex Sans is
  enterprise-serious.
- Brand: Manrope, Sora, Space Grotesk (modern SaaS), Raleway/Montserrat
  (more traditional), Archivo (most striking).

Weights: brand mark regular-to-bold as desired; body uses regular plus bold
for headings. When a download is authorized, fetch only the weights needed — many Google
Fonts are variable fonts and serve one file per weight when requested via an
old-style UA, or serve a variable font when requested with a modern UA.

## Pretty-print a contrast page

To let the user choose: build a small HTML→PDF page showing the wordmark in
each candidate **brand font** on one side, and a real sentence in each
candidate **body font** on the other. Embed each font. Let the user iterate on
color and font separately.
