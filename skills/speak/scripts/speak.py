#!/usr/bin/env python3
"""Speak UTF-8 text received through stdin without evaluating it as code."""

from __future__ import annotations

import sys


def main() -> int:
    text = sys.stdin.read().strip()
    if not text:
        print("No text to speak.", file=sys.stderr)
        return 2

    try:
        from kokoro_voice.barge import play_audio_with_barge
        from kokoro_voice.tts import tts_kokoro
    except ImportError as error:
        print(f"Kokoro TTS dependency unavailable: {error}", file=sys.stderr)
        return 3

    preview = f"{text[:100]}..." if len(text) > 100 else text
    print(f"Speaking: {preview}")
    audio = tts_kokoro(text, voice="af_heart")
    if audio is None:
        print("Kokoro TTS did not produce audio.", file=sys.stderr)
        return 4
    play_audio_with_barge(audio, 24_000, enable_barge=False)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
