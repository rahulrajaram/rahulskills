---
name: speak
description: "Read text out loud using Kokoro TTS. Defaults to reading your last response."
argument-hint: "[optional text]"
---

# Speak

Use Kokoro TTS to read text out loud.

**If arguments are provided:** Read "$ARGUMENTS"

**If no arguments (default):** Read your most recent response from this conversation out loud. Look at the last message you sent to the user and read that text.

Do not speak secrets, credentials, private keys, or large code/data payloads.
Ask before speaking content that may be confidential or surprising in the
user's physical environment. Read [references/kokoro.md](references/kokoro.md)
for backend, audio, and voice details.

Pass text through stdin so it is data, never interpolated Python code:

```bash
printf '%s' "$TEXT_TO_SPEAK" | python3 "$SKILL_DIR/scripts/speak.py"
```

Set `TEXT_TO_SPEAK` from the arguments or the last response without shell
evaluation. Keep it concise; strip code blocks, file paths, and formatting that
would not sound natural. If Kokoro or audio playback is unavailable, report the
missing dependency or device and do not install or reconfigure it implicitly.
