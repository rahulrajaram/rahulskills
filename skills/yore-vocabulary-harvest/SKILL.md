---
name: yore-vocabulary-harvest
description: "Extract candidate vocabulary terms from a Yore index for stopword curation and domain filtering."
argument-hint: "[--index DIR] [--limit N] [--common-terms N] [--stopwords FILE]"
---

# Yore Vocabulary Harvest

Gather a corpus-derived candidate vocabulary list (for example, "top 200 terms")
from a built Yore index. This produces candidates only and makes no LLM call.
It can feed human review or `yore-vocabulary-llm-filter`.

## Setup

Resolve these bindings from the request and local evidence before harvesting:

- `corpus_root`: the requested corpus, usually the target repository. Use the
  current repository only when context identifies it as the intended corpus.
- `index_dir`: an absolute path; default to `.yore` under `corpus_root`, and
  resolve a supplied relative `--index` against that corpus. Check readable
  `reverse_index.json` and `forward_index.json` and any available source-root,
  revision or build metadata. Report unknown freshness rather than inventing it.
- `yore_cmd`: an argument array for an existing Yore executable verified through
  its help/provenance. If only a known Yore checkout is available, inspect its
  existing build/invocation route and bind its executable explicitly. Never run
  bare `cargo run` in the target corpus: its Cargo binary may be unrelated.
  Report unavailable tooling without fetching or installing it. Building from
  source is a separate action within existing build/dependency permissions.
- Harvest options: requested `limit` (example below: 200), optional common-term
  count and absolute stopword path. Preserve the existing broad-harvest default
  `--no-default-stopwords`; disclose it. Validate supported flags against the
  resolved executable's local help.

A missing index is not permission to index another directory. Bind its source,
output path, file types/exclusions and write scope first. If index construction
is already authorized, use the resolved command with explicit paths:

```bash
"${yore_cmd[@]}" build --output "$index_dir" "$corpus_root"
```

The documented Yore build defaults cover `md,txt,rst`; use locally supported
`--types`/`--exclude` when the requested corpus needs different inputs. Ask only
if building the missing index or its input/write scope is unresolved. Verify
successful construction and index readability before harvesting.

## Harvest workflow

Create a unique private directory and preserve its identity across steps. With
resolved Bash bindings, for example:

```bash
harvest_dir=$(mktemp -d "${TMPDIR:-/tmp}/yore-vocabulary-harvest.XXXXXXXX")
harvest_json="$harvest_dir/candidates.json"
"${yore_cmd[@]}" vocabulary --index "$index_dir" --format json \
  --limit "$limit" --no-default-stopwords >"$harvest_json" \
  2>"$harvest_dir/stderr.txt"
```

Check command exit status and stderr before consuming stdout. Do not pass a
failed command's partial artifact to filtering. Require a single JSON object
with a `terms` array containing nonempty string `term` values and numeric
`score`/`count` values. Reject duplicate terms. Retain the tool's metadata:
`total` is the candidate count before pagination, `used_default_stopwords` and
`include_stemming` are flags, and `auto_common_terms` is optional when disabled.

For an optional corpus-common exclusion pass, allocate a new run directory and
add `--common-terms "$common_terms"` and, when selected,
`--stopwords "$stopwords_file"` to the same vocabulary invocation. Record the
options separately from the first pass; common-term exclusion can remove domain
terms in small corpora.

After successful JSON validation, an optional plain-list artifact can be made:

```bash
harvest_text="$harvest_dir/candidates.txt"
jq -r '.terms[].term' "$harvest_json" >"$harvest_text"
```

Use the JSON artifact for downstream filtering when terms contain line breaks.
An empty list is a valid outcome: report zero candidates, inspect the selected
index/freshness and filters if unexpected, and do not trigger an empty LLM call.
Supported output formats are `lines`, `json`, and `prompt`; this workflow uses
`json` to retain term metrics and harvest identity.

## Deliverables for the next step

Return the exact JSON path and optional text path, corpus/index paths, resolved
Yore command, selected options, exit/validation outcome, candidate count and
known freshness evidence. Preserve these bindings with the artifact in context
(or a run-local metadata file) so a subsequent filter does not infer its target
repository from the Yore checkout. Keep the artifact available for that handoff;
pass the exact JSON path as `--input`, never a fixed `/tmp` filename or a glob
that could select another run.
