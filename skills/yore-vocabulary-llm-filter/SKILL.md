---
name: yore-vocabulary-llm-filter
description: "Build Whisper-specific vocabulary by removing common terms and keeping domain signals."
---

# Yore Vocabulary LLM Filter (Whisper Vocabulary)

Use this skill when you want to enrich Whisper's vocabulary with only the narrow subset of tokens it is unlikely to recognize reliably from generic software knowledge.

The goal is **Whisper transcription accuracy**: keep terms that a speech-to-text model would misspell, skip, or hallucinate — even if those terms look "unspeakable" as text (acronyms like `bm25`, project names like `yore`). Drop terms that are phonetically clear English words regardless of how technical they are.

## Prerequisites

- You have candidate terms from `yore-vocabulary-harvest` (JSON or newline list).
- `gptengage` is installed:

```bash
command -v ~/.local/bin/gptengage
```

- Optional stopword path you want the model to consider as already-known vocabulary.

## Input

Accept one of:

- `/tmp/vocabulary-harvest.json` produced by the harvest skill
- A plain text file with one candidate term per line

The default candidate size is 200 terms; increase `--limit` in the harvest step if recall is too low.

## Workflow

1. Build a clear prompt payload:

```text
Whisper is a speech-to-text model. You are classifying corpus-derived terms
to decide which ones belong in a custom Whisper vocabulary file that biases
transcription toward correct spelling.

IMPORTANT CONTEXT: The Whisper output is consumed by an LLM, not a human.
An LLM will easily resolve minor transcription variations like missing
hyphens, word splits, or casing ("fix links" vs "fix-links", "change log"
vs "changelog", "stop word" vs "stopword"). Therefore:
- Drop any compound term where both component words are recognizable English.
  The LLM reader will understand "canonical orphans" just as well as
  "canonical-orphans".
- Only keep terms where the PHONEMES THEMSELVES produce a wrong word —
  where Whisper would output a completely different word or nonsense, not
  just a formatting variant.

For each term, return a JSON object with: term, verdict, category, reason.

Verdicts:
- "keep": Whisper would produce a WRONG WORD or nonsense from the audio
  (e.g., "yore" → "your", "toml" → "tommel", "bm25" → "be em twenty five").
- "drop": Whisper would produce recognizable output that an LLM can interpret,
  even if formatting differs (hyphens, spacing, casing).
- "review": Genuinely borderline — the user should decide.
- "artifact": Stemming fragment or index noise, not a real term.

Categories (pick the most specific one):
- "acronym": e.g., BM25, ADR, LLM, CLI, TOML, YML
- "project-name": e.g., yore, gptengage
- "proper-noun": e.g., GitHub, Anthropic, Kubernetes
- "jargon": domain term with non-obvious spelling
- "phonetically-clear": sounds like normal English when spoken aloud
- "compound-clear": compound of recognizable English words (drop these)
- "stemming-artifact": truncated stem from indexing, not a real word
- "other": none of the above

Return strict JSON only — an object with a single key "terms" containing an array:
{
  "terms": [
    {"term": "bm25", "verdict": "keep", "category": "acronym", "reason": "Whisper would produce 'be em twenty five' — wrong word entirely"},
    {"term": "fix-links", "verdict": "drop", "category": "compound-clear", "reason": "Both words are clear English; LLM handles 'fix links' fine"}
  ]
}

No markdown fences, no commentary outside the JSON.
If both parts of a compound are recognizable English words, verdict is "drop".
If a term is a truncated stem (e.g., enforc, handl, rul, statu), verdict is "artifact".
Optimise for precision: only "keep" terms where the phonemes produce a genuinely wrong word.
```

2. Invoke the LLM through gptengage:

```bash
printf '%s\n' "$(cat /tmp/vocabulary-harvest.json)" | \
  ~/.local/bin/gptengage invoke claude \
  "Classify these terms for Whisper vocabulary. Return strict JSON per the schema above." \
  > /tmp/vocabulary-llm-filter.json
cat /tmp/vocabulary-llm-filter.json | sed -n '/^{/,/}$/p' > /tmp/vocabulary-llm-filter.strict.json
```

3. Extract decision files:

```bash
jq -r '.terms[] | select(.verdict == "keep") | .term' /tmp/vocabulary-llm-filter.strict.json | sort -u > .yore-domain-terms-llm.txt
jq -r '.terms[] | select(.verdict == "drop") | .term' /tmp/vocabulary-llm-filter.strict.json | sort -u > .yore-stopwords-llm.txt
jq -r '.terms[] | select(.verdict == "review") | .term' /tmp/vocabulary-llm-filter.strict.json | sort -u > .yore-vocabulary-review.txt
jq -r '.terms[] | select(.verdict == "artifact") | .term' /tmp/vocabulary-llm-filter.strict.json | sort -u > .yore-vocabulary-artifacts.txt
```

4. **Present a review table to the user before merging.**

Build and display a markdown table from the JSON so the user can approve, override, or discard individual terms:

```bash
echo "| Term | Verdict | Category | Reason |"
echo "|------|---------|----------|--------|"
jq -r '.terms[] | "| \(.term) | \(.verdict) | \(.category) | \(.reason) |"' /tmp/vocabulary-llm-filter.strict.json
```

Show summary counts:

```bash
echo ""
echo "keep: $(wc -l < .yore-domain-terms-llm.txt) | drop: $(wc -l < .yore-stopwords-llm.txt) | review: $(wc -l < .yore-vocabulary-review.txt) | artifact: $(wc -l < .yore-vocabulary-artifacts.txt)"
```

**Wait for user confirmation before proceeding to merge.** The user may move terms between buckets.

5. Merge confirmed `keep` terms into Whisper vocabulary:

```bash
# Shared/global Whisper vocabulary (preferred default)
mkdir -p "$HOME/.whisper"
touch "$HOME/.whisper/vocabulary.txt"
cat "$HOME/.whisper/vocabulary.txt" .yore-domain-terms-llm.txt \
  | sort -u > /tmp/whisper-vocab-global.txt
diff "$HOME/.whisper/vocabulary.txt" /tmp/whisper-vocab-global.txt || true
mv /tmp/whisper-vocab-global.txt "$HOME/.whisper/vocabulary.txt"
```

> Use only one scope initially: prefer global `$HOME/.whisper/vocabulary.txt` unless a repo-specific whitelist is required.

## Guardrails

- Require strict JSON from the model before writing any files.
- If JSON parsing fails, rerun with a tighter prompt and/or smaller term list.
- **Never auto-merge.** Always present the review table and wait for user approval.
- Stemming artifacts (verdict `artifact`) are discarded — never merge them.
- Review terms (verdict `review`) require explicit user decision — never auto-merge.
- Show diff before every merge so the user can see exactly what changes.
- Keep changes deterministic in CI; treat LLM output as curated recommendation.

## Output

- `/tmp/vocabulary-llm-filter.json` and `/tmp/vocabulary-llm-filter.strict.json` (raw vs normalized JSON)
- `.yore-domain-terms-llm.txt` (proposed keep terms)
- `.yore-stopwords-llm.txt` (proposed drop terms)
- `.yore-vocabulary-review.txt` (user-decision terms)
- `.yore-vocabulary-artifacts.txt` (discarded stemming noise)
- `$HOME/.whisper/vocabulary.txt` (shared vocabulary, updated only after user approval)
