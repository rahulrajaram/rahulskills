---
name: speak
description: "Read text out loud using Kokoro TTS. Defaults to reading your last response."
argument-hint: "[optional text]"
---

# Speak

Use Kokoro TTS to read text out loud.

**If text is provided:** read that text. It is whatever follows the
invocation: Claude Code `/speak <text>` (appended as an `ARGUMENTS:` line),
Pi `/skill:speak <text>` (trailing text after the skill block), or Codex
`$speak <text>` (the rest of the request).

**If no text (default):** Read your most recent response from this conversation out loud. Look at the last message you sent to the user and read that text.

Do not speak secrets, credentials, private keys, or large code/data payloads.
Ask before speaking content that may be confidential or surprising in the
user's physical environment. Read [references/kokoro.md](references/kokoro.md)
for backend, audio, and voice details.

Bind `SKILL_DIR` to the absolute directory containing this `SKILL.md` (Claude
Code supplies it as `${CLAUDE_SKILL_DIR}`; elsewhere use the path the skill was
loaded from). Pass text through stdin with a quoted heredoc so it is data, never
shell- or Python-evaluated:

```bash
python3 "<SKILL_DIR>/scripts/speak.py" <<'SPEAK_TEXT_END'
<text to speak>
SPEAK_TEXT_END
```

Substitute the absolute path for `<SKILL_DIR>` and choose a different delimiter
if the text contains a line equal to it. Keep the text concise; strip code
blocks, file paths, and formatting that would not sound natural. If Kokoro or
audio playback is unavailable, report the missing dependency or device and do
not install or reconfigure it implicitly.
