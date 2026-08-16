from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "skills" / "speak" / "scripts" / "speak.py"


def load_module():
    spec = importlib.util.spec_from_file_location("speak_helper", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


class SpeakHelperTests(unittest.TestCase):
    def test_text_is_passed_as_data(self) -> None:
        captured: dict[str, object] = {}
        package = ModuleType("kokoro_voice")
        barge = ModuleType("kokoro_voice.barge")
        tts = ModuleType("kokoro_voice.tts")

        def fake_tts(text: str, *, voice: str):
            captured.update(text=text, voice=voice)
            return b"audio"

        def fake_play(audio, rate: int, *, enable_barge: bool):
            captured.update(audio=audio, rate=rate, enable_barge=enable_barge)

        tts.tts_kokoro = fake_tts
        barge.play_audio_with_barge = fake_play
        modules = {
            "kokoro_voice": package,
            "kokoro_voice.tts": tts,
            "kokoro_voice.barge": barge,
        }
        payload = "quotes: ''' and shell: $(touch /tmp/must-not-exist)"
        with patch.dict(sys.modules, modules), patch.object(sys, "stdin", io.StringIO(payload)):
            result = load_module().main()

        self.assertEqual(result, 0)
        self.assertEqual(
            captured,
            {
                "text": payload,
                "voice": "af_heart",
                "audio": b"audio",
                "rate": 24_000,
                "enable_barge": False,
            },
        )

    def test_empty_input_fails_before_backend_import(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("\n")):
            self.assertEqual(load_module().main(), 2)
