---
name: yore-vocabulary-harvest
description: "Extract candidate vocabulary terms from a Yore index for stopword curation and domain filtering."
---

# Yore Vocabulary Harvest

Use this skill when the user wants to gather a corpus-derived candidate vocabulary list (for example, "top 200 terms") from a built Yore index.

## Scope

This skill produces candidate terms only. It does **not** call an LLM.
It is intended to feed a human review step or the LLM filter skill.

## Setup

1. Resolve repository root:

```bash
cd /path/to/repo
git rev-parse --show-toplevel
```

2. Ensure an index exists (`.yore` by default). If not, build one:

```bash
cargo run --quiet -- build --output .yore .
```

3. Confirm the index is present and readable:

```bash
ls -la .yore/{reverse_index.json,forward_index.json}
```

## Harvest Workflow

1. Run Yore vocabulary in JSON mode to capture the top terms:

```bash
cargo run --quiet -- \
  vocabulary --index .yore \
  --format json \
  --limit 200 \
  --no-default-stopwords \
  > /tmp/vocabulary-harvest.json
```

2. Optional: extract a plain list of terms for downstream tools:

```bash
jq -r '.terms[].term' /tmp/vocabulary-harvest.json > /tmp/vocabulary-harvest.txt
```

3. Optional: include a domain-seeded common-word exclusion set first:

```bash
cargo run --quiet -- \
  vocabulary --index .yore \
  --format json \
  --limit 200 \
  --common-terms 20 \
  --stopwords /path/to/custom/common-terms.txt \
  --no-default-stopwords \
  > /tmp/vocabulary-harvest-common-filtered.json
```

## Expected Output

- JSON payload from `--format json` with:
  - `terms` array
  - each term object includes `term`, `score`, `count`
  - `total` total candidate count before pagination
  - flags: `used_default_stopwords`, `auto_common_terms`, `include_stemming`

## Error Handling

- If Yore returns an empty list, check:
  - index path is correct
  - index was built for the same repository/revision
  - `--format` is valid (`lines`, `json`, `prompt`)

## Deliverables for Next Step

- `/tmp/vocabulary-harvest.json` (structured)
- `/tmp/vocabulary-harvest.txt` (optional plain term list)
- A stable `vocabulary-harvest` artifact that can be passed to the LLM filtering skill

