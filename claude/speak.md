---
allowed-tools: Bash(python3:*)
argument-hint: [optional text]
description: Read text out loud using Kokoro TTS. Defaults to reading your last response.
---

Use Kokoro TTS to read text out loud.

**If arguments are provided:** Read "$ARGUMENTS"

**If no arguments (default):** Read your most recent response from this conversation out loud. Look at the last message you sent to the user and read that text.

Run this Python code with the appropriate text:

```bash
python3 -c "
from kokoro_voice.tts import tts_kokoro
from kokoro_voice.barge import play_audio_with_barge

text = '''TEXT_TO_SPEAK'''

print(f'Speaking: {text[:100]}...' if len(text) > 100 else f'Speaking: {text}')
audio = tts_kokoro(text, voice='af_heart')
if audio is not None:
    play_audio_with_barge(audio, 24000, enable_barge=False)
    print('Done.')
"
```

Replace TEXT_TO_SPEAK with either the provided arguments or your last response text. Keep the text concise - strip any code blocks, file paths, or formatting that wouldn't sound natural when spoken.
