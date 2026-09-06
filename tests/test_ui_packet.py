"""Focused contract checks for the UI prompt packet generator."""

import importlib.util
from argparse import Namespace
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "skills/tui-web-design-orchestrator/scripts/design_prompt_packet.py"
SPEC = importlib.util.spec_from_file_location("design_prompt_packet", SCRIPT)
generator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(generator)


def args(**overrides):
    values = dict(mode="web-app", brief="Review deployment health", audience="release managers",
                  constraints=["must work over SSH"], style="Dense and calm", tech="",
                  name="", component=[], output="json", outfile="")
    values.update(overrides)
    return Namespace(**values)


def test_packet_derives_components_and_preserves_constraints():
    packet = generator.build_packet(args())
    assert packet["constraints"] == ["must work over SSH"]
    assert packet["component_map"] == []
    assert "Feature cards" not in packet["implementation_prompt"]
    assert "must work over SSH" in packet["implementation_prompt"]


def test_explicit_components_are_retained_without_extra_preset_panels():
    packet = generator.build_packet(args(component=["Health timeline"]))
    assert packet["component_map"] == ["Health timeline"]
    assert list(packet["component_state_matrix"]) == ["Health timeline"]
