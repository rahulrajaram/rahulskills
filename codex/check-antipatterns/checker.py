#!/usr/bin/env python3
"""
Real-time anti-pattern checker for active conversations.
Entry point for /check-antipatterns skill.
"""

import json
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

# Command taxonomy: distinguish diagnostic vs action commands
DIAGNOSTIC_COMMANDS = {
    'git status', 'git diff', 'git log',
    'kubectl get', 'kubectl describe', 'kubectl logs', 'kubectl get events',
    'curl', 'docker ps', 'docker images',
    'ls', 'cat', 'head', 'tail',
    'ps aux', 'netstat', 'lsof'
}

ACTION_COMMANDS = {
    'pytest', 'npm test', 'npm run test', 'npx playwright',
    'helm install', 'helm upgrade',
    'kubectl apply', 'kubectl create', 'kubectl delete',
    'docker build', 'docker push',
    'git commit', 'git push',
    'bootstrap', 'deploy', 'make'
}

# Credential patterns to detect in Bash commands
# Note: Use (?:^|[^A-Z_]) to match start or non-letter/underscore before keyword
CREDENTIAL_PATTERNS = [
    r'PASSWORD\s*=',
    r'SECRET\s*=',
    r'API_?KEY\s*=',
    r'TOKEN\s*=',
    r'CREDENTIAL\s*=',
    r'APIKEY\s*=',
    r'SECRET_KEY\s*='
]

# E2E/Integration test patterns
E2E_TEST_PATTERNS = [
    r'pytest.*e2e',
    r'pytest.*integration',
    r'npx\s+playwright',
    r'npm.*test.*e2e',
    r'npm.*test.*integration',
    r'npm\s+run\s+test:e2e',
    r'npm\s+run\s+test:integration'
]


def load_rules() -> Dict:
    """Load universal rules from rules.json."""
    rules_file = Path(__file__).parent / 'rules.json'
    with open(rules_file, 'r') as f:
        return json.load(f)


def load_conversation(filepath: str, lookback: int = 50) -> List[Dict]:
    """Load last N messages from conversation JSONL."""
    messages = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))

    # Return only last N messages for performance
    return messages[-lookback:] if len(messages) > lookback else messages


def extract_bash_commands(messages: List[Dict]) -> List[Tuple[int, str]]:
    """Extract bash commands from messages with their indices."""
    commands = []
    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        content = msg.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue

        for item in content:
            if isinstance(item, dict) and item.get('name') == 'Bash':
                cmd = item.get('input', {}).get('command', '')
                commands.append((i, cmd))

    return commands


def extract_text(content) -> str:
    """Extract text from message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                texts.append(item.get('text', ''))
        return '\n'.join(texts)
    return ''


def is_action_command(cmd: str) -> bool:
    """Check if command is an action (not diagnostic)."""
    cmd_lower = cmd.lower().strip()
    # Check if it starts with any action command
    return any(cmd_lower.startswith(action) for action in ACTION_COMMANDS)


def is_diagnostic_command(cmd: str) -> bool:
    """Check if command is diagnostic."""
    cmd_lower = cmd.lower().strip()
    # Check if it starts with any diagnostic command
    return any(cmd_lower.startswith(diag) for diag in DIAGNOSTIC_COMMANDS)


def check_retry_without_diagnosis(messages: List[Dict]) -> List[Dict]:
    """Detect retry-without-diagnosis pattern for ACTION commands only."""
    warnings = []
    commands = extract_bash_commands(messages)

    # Track ACTION command occurrences (ignore diagnostic commands)
    cmd_occurrences = defaultdict(list)
    for idx, cmd in commands:
        # Only track action commands
        if is_action_command(cmd):
            # Normalize command (first few words) for comparison
            cmd_normalized = ' '.join(cmd.split()[:3])
            cmd_occurrences[cmd_normalized].append((idx, cmd))

    # Find retries of action commands
    for cmd_key, occurrences in cmd_occurrences.items():
        if len(occurrences) < 2:
            continue

        # Check if diagnostic commands ran between retries
        for i in range(len(occurrences) - 1):
            first_idx, first_cmd = occurrences[i]
            second_idx, second_cmd = occurrences[i + 1]

            # Check messages between for diagnostic commands
            diagnostic_found = False
            for msg_idx in range(first_idx + 1, second_idx):
                if msg_idx < len(messages):
                    msg_content = extract_text(messages[msg_idx].get('message', {}).get('content', ''))
                    # Check for diagnostic keywords
                    if any(kw in msg_content.lower() for kw in ['kubectl logs', 'kubectl describe', 'kubectl get events', 'docker logs', 'journalctl', 'cat /var/log']):
                        diagnostic_found = True
                        break

            if not diagnostic_found:
                warnings.append({
                    'type': 'RETRY_WITHOUT_DIAGNOSIS',
                    'severity': 'MEDIUM',
                    'message_range': f"{first_idx}-{second_idx}",
                    'command': first_cmd[:100],
                    'suggestion': "Run diagnostics before retrying: kubectl logs, kubectl describe, kubectl get events"
                })

    return warnings


def check_credential_usage(messages: List[Dict]) -> List[Dict]:
    """Detect credential usage in Bash commands without verification."""
    warnings = []
    commands = extract_bash_commands(messages)

    kubectl_secret_indices = []
    credential_usage = []

    # First pass: Find kubectl get secret commands
    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue
        content = extract_text(msg.get('message', {}).get('content', ''))
        if 'kubectl get secret' in content.lower() or 'kubectl.*secret' in content.lower():
            kubectl_secret_indices.append(i)

    # Second pass: Find credential patterns in Bash commands
    for idx, cmd in commands:
        # Check if command contains credential assignment patterns
        for pattern in CREDENTIAL_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                credential_usage.append((idx, cmd, pattern))
                break

    # For each credential usage, check if kubectl get secret was run nearby
    for usage_idx, cmd, pattern in credential_usage:
        # Check if kubectl get secret was run within 20 messages before
        has_secret_read = any(abs(usage_idx - secret_idx) <= 20 and secret_idx <= usage_idx
                             for secret_idx in kubectl_secret_indices)

        if not has_secret_read:
            # Extract just the credential part for display
            match = re.search(pattern, cmd, re.IGNORECASE)
            cred_snippet = cmd[max(0, match.start()-10):min(len(cmd), match.end()+30)] if match else cmd[:50]

            warnings.append({
                'type': 'CREDENTIAL_ASSUMPTION',
                'severity': 'HIGH',
                'message_range': str(usage_idx),
                'command': f"Found: {cred_snippet}...",
                'suggestion': "Read from K8s secret: kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d"
            })

    return warnings


def check_preflight_missing(messages: List[Dict]) -> List[Dict]:
    """Detect missing preflight checks before integration/e2e tests."""
    warnings = []
    commands = extract_bash_commands(messages)

    test_indices = []
    preflight_indices = []

    # Find E2E/integration test commands
    for idx, cmd in commands:
        # Check if command matches any E2E test pattern
        for pattern in E2E_TEST_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                test_indices.append((idx, cmd))
                break

    # Find preflight check commands
    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        content = extract_text(msg.get('message', {}).get('content', ''))

        # Check for preflight checks
        if any(kw in content.lower() for kw in ['kubectl get pods', 'kubectl get svc', 'docker ps', 'curl', 'health', 'preflight']):
            preflight_indices.append(i)

    # For each test run, check if preflight was done recently
    for test_idx, test_cmd in test_indices:
        # Check if preflight was done within 10 messages before
        has_preflight = any(abs(test_idx - pre_idx) <= 10 and pre_idx < test_idx
                           for pre_idx in preflight_indices)

        if not has_preflight:
            # Extract test type for better error message
            test_type = "E2E test"
            if 'playwright' in test_cmd.lower():
                test_type = "Playwright E2E"
            elif 'integration' in test_cmd.lower():
                test_type = "Integration test"

            warnings.append({
                'type': 'MISSING_PREFLIGHT',
                'severity': 'HIGH',
                'message_range': str(test_idx),
                'command': f"{test_type}: {test_cmd[:60]}...",
                'suggestion': "Run preflight validation: kubectl get pods -A, curl http://localhost:<port>/health"
            })

    return warnings


def check_tool_discovery(messages: List[Dict]) -> List[Dict]:
    """Detect if tools were never discovered."""
    warnings = []

    if len(messages) < 50:
        return warnings  # Too early to warn

    # Check if ever ran tool discovery commands
    discovered = False
    for msg in messages:
        if msg.get('type') != 'assistant':
            continue

        content = extract_text(msg.get('message', {}).get('content', ''))
        if any(kw in content.lower() for kw in ['ls ~/.local/bin', 'ls ./scripts', 'cat tools.md']):
            discovered = True
            break

    if not discovered:
        warnings.append({
            'type': 'TOOL_DISCOVERY_GAP',
            'severity': 'LOW',
            'message_range': f"0-{len(messages)}",
            'command': 'N/A',
            'suggestion': "Check for existing tools: ls ~/.local/bin ~/bin ./scripts/ && cat TOOLS.md"
        })

    return warnings


def identify_good_practices(messages: List[Dict]) -> List[Dict]:
    """Identify positive behaviors."""
    good_practices = []

    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        content = extract_text(msg.get('message', {}).get('content', ''))

        # Good: Reading from K8s secret
        if 'kubectl get secret' in content.lower() and 'base64 -d' in content.lower():
            good_practices.append({
                'type': 'CREDENTIAL_FROM_SECRET',
                'message_idx': i,
                'rule': 1,
                'description': "Used kubectl get secret instead of hardcoding"
            })

        # Good: Diagnostic before retry
        if any(kw in content.lower() for kw in ['kubectl logs', 'kubectl describe', 'kubectl get events']):
            good_practices.append({
                'type': 'DIAGNOSTIC_BEFORE_RETRY',
                'message_idx': i,
                'rule': 2,
                'description': "Ran diagnostic commands to investigate failure"
            })

        # Good: Asking about scope
        if any(kw in content.lower() for kw in ['should i', 'do you want me to', 'this will', 'this expands']):
            good_practices.append({
                'type': 'SCOPE_CONFIRMATION',
                'message_idx': i,
                'rule': 3,
                'description': "Asked user before expanding scope"
            })

    return good_practices


def generate_report(warnings: List[Dict], good_practices: List[Dict], rules: Dict) -> str:
    """Generate human-readable report with severity indicators."""
    lines = []

    lines.append("Analyzing current conversation for anti-patterns...")
    lines.append("")

    # Warnings - grouped by severity
    if warnings:
        # Sort by severity (HIGH first)
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_warnings = sorted(warnings, key=lambda w: severity_order.get(w['severity'], 3))

        lines.append(f"⚠️  WARNINGS ({len(warnings)} found):")
        lines.append("")

        for i, w in enumerate(sorted_warnings, 1):
            # Add severity indicator
            severity_icon = "🔴" if w['severity'] == 'HIGH' else "🟡" if w['severity'] == 'MEDIUM' else "🔵"
            lines.append(f"{i}. {severity_icon} {w['severity']}: {w['type'].replace('_', ' ').title()} (Message {w['message_range']})")
            if w['command'] != 'N/A' and 'Found:' not in w['command']:
                lines.append(f"   - Command: {w['command']}")
            elif 'Found:' in w['command']:
                lines.append(f"   - {w['command']}")
            lines.append(f"   → Suggestion: {w['suggestion']}")
            lines.append("")
    else:
        lines.append("✅ No warnings found!")
        lines.append("")

    # Good Practices
    if good_practices:
        # Deduplicate by type
        unique_practices = {}
        for gp in good_practices:
            if gp['type'] not in unique_practices:
                unique_practices[gp['type']] = gp

        lines.append(f"✅ GOOD PRACTICES ({len(unique_practices)} found):")
        lines.append("")

        for i, gp in enumerate(unique_practices.values(), 1):
            rule = next((r for r in rules['universal_rules'] if r['id'] == gp['rule']), None)
            lines.append(f"{i}. {gp['type'].replace('_', ' ').title()} (Message {gp['message_idx']})")
            lines.append(f"   - {gp['description']}")
            if rule:
                lines.append(f"   ✓ Follows Rule {gp['rule']}: {rule['rule']}")
            lines.append("")

    # Compliance Score
    total_rules = len(rules['universal_rules'])
    violations = len(warnings)
    compliance = int(((total_rules - violations) / total_rules) * 100) if total_rules > 0 else 100

    lines.append("RECOMMENDATIONS:")
    if violations > 0:
        lines.append(f"  - Fix {violations} warning{'s' if violations > 1 else ''} before proceeding")
        lines.append("  - Consider implementing suggested tools")
    else:
        lines.append("  - Keep up the good work!")
    lines.append(f"  - Current compliance: {len(good_practices)} good practices observed")
    lines.append("")
    lines.append(f"📊 COMPLIANCE SCORE: {compliance}% (Target: 95%+)")

    return '\n'.join(lines)


def main(conversation_file: str):
    """Main entry point with differential lookback strategy."""
    print("Loading conversation...")

    # Load full conversation for critical checks
    all_messages = []
    with open(conversation_file, 'r') as f:
        for line in f:
            if line.strip():
                all_messages.append(json.loads(line))

    print(f"Loaded {len(all_messages)} total messages")

    # Use last 50 for recent patterns (retry, preflight)
    recent_messages = all_messages[-50:] if len(all_messages) > 50 else all_messages
    print(f"Analyzing last {len(recent_messages)} messages for recent patterns...")

    rules = load_rules()

    # Run detectors with appropriate lookback
    warnings = []

    # Recent pattern checks (50 messages)
    warnings.extend(check_retry_without_diagnosis(recent_messages))
    warnings.extend(check_preflight_missing(recent_messages))

    # Critical pattern checks (full conversation)
    print("Scanning full conversation for critical patterns (credentials, tools)...")
    warnings.extend(check_credential_usage(all_messages))
    warnings.extend(check_tool_discovery(all_messages))

    # Identify good practices (recent messages)
    good_practices = identify_good_practices(recent_messages)

    # Generate report
    report = generate_report(warnings, good_practices, rules)

    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: checker.py <conversation-file>")
        sys.exit(1)

    main(sys.argv[1])
