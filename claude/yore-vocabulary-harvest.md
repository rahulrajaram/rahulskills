---
argument-hint: [--index DIR] [--limit N] [--common-terms N] [--stopwords FILE]
description: Extract candidate vocabulary terms from a Yore index for Whisper vocabulary curation
---

# Yore Vocabulary Harvest

**Arguments:** $ARGUMENTS

## Instructions

Gather a corpus-derived candidate vocabulary list from a built Yore index. This skill produces candidate terms only and does **not** call an LLM. Output feeds the `yore-vocabulary-llm-filter` skill or human review.

### Step 1: Resolve repository and index

Find the repo root and confirm an index exists.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
ls -la "${REPO_ROOT}/.yore/reverse_index.json" "${REPO_ROOT}/.yore/forward_index.json" 2>/dev/null || echo "INDEX_MISSING"
```

If `INDEX_MISSING`, build one first:

```bash
cd "$REPO_ROOT" && yore build --output .yore .
```

Use the installed `yore` binary. Fall back to `cargo run --quiet --` only if `yore` is not on PATH.

### Step 2: Harvest terms

Run vocabulary extraction in JSON mode. Default limit is 200; override with `--limit`.

```bash
yore vocabulary --index .yore \
  --format json \
  --limit 200 \
  --no-default-stopwords \
  $ARGUMENTS \
  > /tmp/vocabulary-harvest.json
```

### Step 3: Optional plain-text extraction

```bash
jq -r '.terms[].term' /tmp/vocabulary-harvest.json > /tmp/vocabulary-harvest.txt
```

### Step 4: Optional common-term filtering

If the user wants to exclude high-frequency corpus noise:

```bash
yore vocabulary --index .yore \
  --format json \
  --limit 200 \
  --common-terms 20 \
  --no-default-stopwords \
  > /tmp/vocabulary-harvest-common-filtered.json
```

### Expected Output

JSON payload with:
- `terms` array (each: `term`, `score`, `count`)
- `total` count before pagination
- Flags: `used_default_stopwords`, `auto_common_terms`, `include_stemming`

### Deliverables

- `/tmp/vocabulary-harvest.json` (structured)
- `/tmp/vocabulary-harvest.txt` (optional plain term list)
- Ready to pass to `/yore-vocabulary-llm-filter`

### Error Handling

If Yore returns an empty list, check:
- Index path is correct (default `.yore`)
- Index was built for the same repository/revision
- `--format` value is valid (`lines`, `json`, `prompt`)
