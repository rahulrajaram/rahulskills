# Kokoro Backend

Use `kokoro_voice.tts.tts_kokoro` to synthesize text and
`kokoro_voice.barge.play_audio_with_barge` to play 24 kHz audio.

Available voices include `af_heart` (default), `af_bella`, `af_nicole`,
`am_adam`, and `am_michael`.

```python
from kokoro_voice.tts import tts_kokoro
from kokoro_voice.barge import play_audio_with_barge

audio = tts_kokoro(text, voice="af_heart")
if audio is not None:
    play_audio_with_barge(audio, 24000, enable_barge=False)
```
