---
name: kokoro-tts
description: Read Claude's responses out loud using Kokoro TTS. Use when user says "read that", "speak it", "say it out loud", or requests audio output.
allowed-tools: Bash
---

# Kokoro TTS Reader

Read text out loud using the Kokoro TTS system in this project.

## When to Use

- User says "read that out loud" or "speak it"
- User asks you to say something audibly
- User wants text-to-speech output

## How to Use

Run Python to synthesize and play audio:

```python
from kokoro_voice.tts import tts_kokoro
from kokoro_voice.barge import play_audio_with_barge

text = "YOUR TEXT HERE"
audio = tts_kokoro(text, voice='af_heart')
if audio is not None:
    play_audio_with_barge(audio, 24000, enable_barge=False)
```

## Available Voices

- `af_heart` (default, female)
- `af_bella`
- `af_nicole`
- `am_adam` (male)
- `am_michael`

## Example

User: "What's the weather like? Read it out loud."
You: Generate response, then run the TTS code with your response text.
