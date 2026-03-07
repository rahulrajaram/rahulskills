#!/usr/bin/env python3
"""Generate a structured TUI/web design prompt packet from a plain-language brief."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

MODE_PRESETS = {
    "web-page": {
        "default_tech": "HTML/CSS/JS or React",
        "primary_tasks": [
            "Understand value proposition within 5 seconds",
            "Find trust signals and key proof points",
            "Complete primary call-to-action",
        ],
        "information_architecture": [
            "Hero (problem, value, CTA)",
            "Evidence (social proof, metrics, logos, testimonials)",
            "Feature/benefit sections",
            "Pricing or offer clarity",
            "FAQ and final CTA",
        ],
        "components": [
            "Top navigation",
            "Hero block",
            "Feature cards",
            "Testimonial/proof block",
            "FAQ accordion",
            "Footer with utility links",
        ],
        "interactions": [
            "Clear primary/secondary CTA hierarchy",
            "Progressive disclosure for detail-heavy content",
            "Focus-visible behavior for keyboard users",
            "Reduced motion alternative for animated transitions",
        ],
    },
    "web-app": {
        "default_tech": "React + component library",
        "primary_tasks": [
            "Complete recurring workflows quickly",
            "Locate data and actions with low cognitive load",
            "Recover from errors without losing progress",
        ],
        "information_architecture": [
            "Global nav (top or side)",
            "Module-level page structure",
            "List/detail or dashboard drilldown flows",
            "Search/filter/sort entry points",
            "Settings/help/account utility zone",
        ],
        "components": [
            "Global navigation",
            "Command/search bar",
            "Data table or card grid",
            "Form controls and inline validation",
            "Modal or drawer for secondary tasks",
            "Notification/toast system",
        ],
        "interactions": [
            "Persisted filtering/sorting state",
            "Batch actions where repetitive work exists",
            "Undo where destructive actions are present",
            "Clear loading/empty/error transitions",
        ],
    },
    "tui-dashboard": {
        "default_tech": "Textual (Python) or Bubble Tea (Go)",
        "primary_tasks": [
            "Scan system status fast",
            "Triaging issues without mouse input",
            "Jump between list and detail context quickly",
        ],
        "information_architecture": [
            "Top status/header line",
            "Primary list/table pane",
            "Detail pane with key actions",
            "Contextual footer shortcuts",
            "Event/log strip for immediate feedback",
        ],
        "components": [
            "Split panes",
            "Selectable table/list",
            "Status badges",
            "Inline action bar",
            "Command palette or quick-jump",
            "Toast/status line + event log",
        ],
        "interactions": [
            "Keyboard map: arrows/jk, enter, esc, /, ?, g/G",
            "80-column and 120-column layout behavior",
            "No-color fallback semantics",
            "Safe confirmation for destructive actions",
        ],
    },
    "tui-wizard": {
        "default_tech": "Textual (Python), Ink (Node), or TUIs in Rust/Go",
        "primary_tasks": [
            "Guide user through a risky multi-step task",
            "Prevent invalid submissions early",
            "Offer clear recovery/abort paths",
        ],
        "information_architecture": [
            "Intro and prerequisites",
            "Step-by-step form screens",
            "Inline validation and error hints",
            "Review and confirm screen",
            "Result summary with next actions",
        ],
        "components": [
            "Step progress indicator",
            "Form fields with validation hints",
            "Selection lists and toggles",
            "Confirmation dialog or inline confirm",
            "Result screen with logs",
            "Abort/retry controls",
        ],
        "interactions": [
            "Next/back/abort shortcuts",
            "Field-level validation timing",
            "Resume behavior on interruption",
            "Explicit confirmation checkpoint before apply",
        ],
    },
}

COMMON_STATES = [
    "default",
    "hover/focus",
    "active",
    "disabled",
    "error",
    "empty",
    "loading",
    "success",
]

WEB_A11Y = [
    "Meet WCAG contrast expectations for text and UI controls",
    "Provide visible keyboard focus and logical tab order",
    "Use semantic landmarks and heading hierarchy",
    "Respect reduced-motion preferences",
]

TUI_A11Y = [
    "Enable complete keyboard-only operation",
    "Do not rely only on color for status semantics",
    "Provide concise help screen with key bindings",
    "Offer low-density fallback for narrow terminals",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a structured TUI/web design prompt packet."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=sorted(MODE_PRESETS.keys()),
        help="Design mode preset.",
    )
    parser.add_argument("--brief", required=True, help="Plain-language design brief.")
    parser.add_argument("--audience", default="general users")
    parser.add_argument(
        "--constraints",
        action="append",
        default=[],
        help="Constraint text. Repeat for multiple constraints.",
    )
    parser.add_argument(
        "--style",
        default="Clear hierarchy, strong readability, purposeful visual personality.",
    )
    parser.add_argument(
        "--tech",
        default="",
        help="Preferred implementation stack (defaults by mode).",
    )
    parser.add_argument("--name", default="", help="Optional project name.")
    parser.add_argument(
        "--output",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument("--outfile", default="", help="Write output to file path.")
    return parser.parse_args()


def normalize_constraints(raw_constraints: list[str]) -> list[str]:
    constraints: list[str] = []
    for item in raw_constraints:
        for chunk in item.split(","):
            text = chunk.strip()
            if text:
                constraints.append(text)
    return constraints


def infer_project_name(explicit_name: str, brief: str) -> str:
    if explicit_name.strip():
        return explicit_name.strip()
    words = re.findall(r"[A-Za-z0-9]+", brief)
    if not words:
        return "Untitled UI"
    return " ".join(words[:6]).title()


def build_assumptions(mode: str, audience: str, constraints: list[str], tech: str) -> list[str]:
    assumptions = []
    if audience == "general users":
        assumptions.append("Audience details were not provided; using a broad default audience.")
    if not constraints:
        assumptions.append("No hard constraints were provided; favoring practical defaults.")
    if not tech:
        assumptions.append(
            f"Tech stack not specified; defaulting to {MODE_PRESETS[mode]['default_tech']}."
        )
    if mode.startswith("tui"):
        assumptions.append("Assuming keyboard-only usage and remote-terminal compatibility.")
    else:
        assumptions.append("Assuming modern evergreen browser support.")
    return assumptions


def build_packet(args: argparse.Namespace) -> dict:
    mode_data = MODE_PRESETS[args.mode]
    constraints = normalize_constraints(args.constraints)
    tech = args.tech.strip() or mode_data["default_tech"]
    project_name = infer_project_name(args.name, args.brief)
    assumptions = build_assumptions(args.mode, args.audience, constraints, args.tech.strip())

    a11y_checks = list(TUI_A11Y if args.mode.startswith("tui") else WEB_A11Y)

    component_state_matrix = {
        component: list(COMMON_STATES)
        for component in mode_data["components"]
    }

    implementation_prompt = build_implementation_prompt(
        mode=args.mode,
        project_name=project_name,
        brief=args.brief,
        audience=args.audience,
        style=args.style,
        tech=tech,
        primary_tasks=mode_data["primary_tasks"],
        constraints=constraints,
        components=mode_data["components"],
        interactions=mode_data["interactions"],
    )

    review_prompt = build_review_prompt(
        mode=args.mode,
        project_name=project_name,
        brief=args.brief,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "meta": {
            "generated_at_utc": timestamp,
            "project_name": project_name,
            "mode": args.mode,
            "tech": tech,
        },
        "brief": args.brief,
        "audience": args.audience,
        "style_direction": args.style,
        "assumptions": assumptions,
        "constraints": constraints,
        "north_star": (
            f"Design a {args.mode.replace('-', ' ')} that helps {args.audience} "
            f"achieve the goal: {args.brief}"
        ),
        "primary_tasks": mode_data["primary_tasks"],
        "information_architecture": mode_data["information_architecture"],
        "component_map": mode_data["components"],
        "interaction_model": mode_data["interactions"],
        "component_state_matrix": component_state_matrix,
        "accessibility_checks": a11y_checks,
        "implementation_prompt": implementation_prompt,
        "review_prompt": review_prompt,
    }


def build_implementation_prompt(
    mode: str,
    project_name: str,
    brief: str,
    audience: str,
    style: str,
    tech: str,
    primary_tasks: list[str],
    constraints: list[str],
    components: list[str],
    interactions: list[str],
) -> str:
    constraint_lines = "\n".join(f"- {c}" for c in constraints) if constraints else "- Use sensible defaults and document assumptions."
    task_lines = "\n".join(f"- {task}" for task in primary_tasks)
    component_lines = "\n".join(f"- {component}" for component in components)
    interaction_lines = "\n".join(f"- {item}" for item in interactions)

    mode_specific = ""
    if mode.startswith("tui"):
        mode_specific = (
            "\nTUI-specific requirements:\n"
            "- Provide a complete keyboard map and help screen.\n"
            "- Define behavior for 80-column and 120-column terminal widths.\n"
            "- Include monochrome fallback semantics (no color dependence)."
        )
    else:
        mode_specific = (
            "\nWeb-specific requirements:\n"
            "- Define responsive behavior for mobile, tablet, and desktop.\n"
            "- Use semantic design tokens for color, spacing, and type.\n"
            "- Include focus-visible and reduced-motion treatment."
        )

    return (
        f"Design and implement a {mode} named '{project_name}'.\n\n"
        f"Brief:\n{brief}\n\n"
        f"Audience:\n- {audience}\n\n"
        f"Style direction:\n- {style}\n\n"
        f"Primary tasks:\n{task_lines}\n\n"
        f"Constraints:\n{constraint_lines}\n\n"
        f"Required components:\n{component_lines}\n\n"
        f"Interaction expectations:\n{interaction_lines}"
        f"{mode_specific}\n\n"
        "Deliver output in this order:\n"
        "1. Concise design spec\n"
        "2. Component/state matrix\n"
        "3. File-by-file implementation plan\n"
        "4. Test checklist"
    )


def build_review_prompt(mode: str, project_name: str, brief: str) -> str:
    return (
        f"Review the proposed {mode} design for '{project_name}'.\n"
        f"Original brief: {brief}\n\n"
        "Prioritize findings by severity:\n"
        "1. Usability and flow risks\n"
        "2. Accessibility gaps\n"
        "3. Missing states (empty/loading/error/success)\n"
        "4. Inconsistent component behavior\n"
        "5. Ambiguous implementation details\n\n"
        "Return concrete fixes for each finding."
    )


def to_markdown(packet: dict) -> str:
    def section(title: str, body: str) -> str:
        return f"## {title}\n\n{body}".strip()

    def bullets(items: list[str]) -> str:
        if not items:
            return "- None"
        return "\n".join(f"- {item}" for item in items)

    lines = []
    lines.append(f"# Design Prompt Packet: {packet['meta']['project_name']}")
    lines.append("")
    lines.append(section("Meta", bullets([
        f"Generated: {packet['meta']['generated_at_utc']}",
        f"Mode: {packet['meta']['mode']}",
        f"Tech: {packet['meta']['tech']}",
    ])))
    lines.append("")
    lines.append(section("Brief", packet["brief"]))
    lines.append("")
    lines.append(section("Audience", packet["audience"]))
    lines.append("")
    lines.append(section("Style Direction", packet["style_direction"]))
    lines.append("")
    lines.append(section("Assumptions", bullets(packet["assumptions"])))
    lines.append("")
    lines.append(section("Constraints", bullets(packet["constraints"])))
    lines.append("")
    lines.append(section("North Star", packet["north_star"]))
    lines.append("")
    lines.append(section("Primary Tasks", bullets(packet["primary_tasks"])))
    lines.append("")
    lines.append(section("Information Architecture", bullets(packet["information_architecture"])))
    lines.append("")
    lines.append(section("Component Map", bullets(packet["component_map"])))
    lines.append("")
    lines.append(section("Interaction Model", bullets(packet["interaction_model"])))
    lines.append("")

    state_lines = []
    for component, states in packet["component_state_matrix"].items():
        state_lines.append(f"- {component}: {', '.join(states)}")
    lines.append(section("Component State Matrix", "\n".join(state_lines)))
    lines.append("")

    lines.append(section("Accessibility Checks", bullets(packet["accessibility_checks"])))
    lines.append("")
    lines.append(section("Implementation Prompt", f"```text\n{packet['implementation_prompt']}\n```"))
    lines.append("")
    lines.append(section("Review Prompt", f"```text\n{packet['review_prompt']}\n```"))

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    args = parse_args()
    packet = build_packet(args)

    if args.output == "json":
        out = json.dumps(packet, indent=2)
    else:
        out = to_markdown(packet)

    if args.outfile:
        path = Path(args.outfile)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
