---
name: yore-vocabulary-llm-filter
description: "Classify harvested Yore terms for Whisper vocabulary using a selected gptengage backend, validate strict JSON, and present a human-gated merge preview."
argument-hint: "[--input FILE] [--scope global|local] [--backend claude|codex|gemini] [--dry-run]"
---

# Yore Vocabulary LLM Filter

Turn candidates from `yore-vocabulary-harvest` into a curated recommendation.
This skill makes an external LLM call. Classification is non-deterministic and
never authorizes repository or home-directory writes by itself.

## Inputs and routing

- `--input` is required unless exactly one freshly generated harvest artifact is
  already in context. Accept a JSON candidate payload or one term per line.
- `--backend` selects an installed gptengage backend; do not silently substitute
  another backend.
- `--scope local` proposes a repository-local vocabulary target already defined
  by the project. `--scope global` proposes `$HOME/.whisper/vocabulary.txt`.
  If the local target is not documented, ask rather than inventing one.
- `--dry-run` may call the LLM and print validated recommendations, but creates
  no proposal files and never merges.

Require `gptengage` and `jq`; report missing commands without installing them.
Review input for secrets or private corpus content before sending it externally.

## Classification contract

Build one prompt containing all of the following, followed by the complete
candidate payload:

- Whisper transcription accuracy is the objective.
- Keep terms whose phonemes are likely to become the wrong word/nonsense.
- Drop ordinary English and compounds whose spacing/casing an LLM consumer can
  recover.
- Mark truncated/index noise as `artifact` and genuine uncertainty as `review`.
- Allowed verdicts: `keep`, `drop`, `review`, `artifact`.
- Allowed categories: `acronym`, `project-name`, `proper-noun`, `jargon`,
  `phonetically-clear`, `compound-clear`, `stemming-artifact`, `other`.
- Return strict JSON only as
  `{"terms":[{"term":string,"verdict":enum,"category":enum,"reason":string}]}`.

Invoke with arguments, not shell-evaluated content. A safe shape is:

```bash
prompt_file=$(mktemp)
result_file=$(mktemp)
# Write the full contract and candidate payload to "$prompt_file" using the
# runtime's safe file-edit mechanism, then:
gptengage invoke <backend> "$(cat "$prompt_file")" >"$result_file"
jq -e '
  type == "object" and (.terms | type == "array") and
  all(.terms[];
    (.term | type == "string") and
    (.reason | type == "string") and
    (["keep","drop","review","artifact"] | index(.verdict)) != null and
    (["acronym","project-name","proper-noun","jargon","phonetically-clear",
      "compound-clear","stemming-artifact","other"] | index(.category)) != null)
' "$result_file" >/dev/null
```

Never recover JSON with `sed` or accept markdown-fenced/partial output. On
failure, retain no repository/home writes, report the validation error, and
retry only after diagnosing truncation, backend failure, or prompt size.

## Review and gated writes

Render every validated term as a review table plus bucket counts. In dry-run
mode, stop there. Otherwise, ask whether to write local proposal bucket files;
name the exact paths first and use collision-safe temporary files.

Merging is a second approval boundary. Show the selected target and exact diff,
including user overrides, then wait for explicit approval. Use an atomic replace
in the target directory, preserve existing lines, sort/deduplicate, and retain a
rollback copy or the original content until verification succeeds. `review` and
`artifact` terms are never merged automatically.

## Output contract

Return backend, input, scope, validation status, counts, full review table,
proposed target, whether proposal files were written, whether merge approval is
pending, and the exact diff/rollback path after an approved merge.
