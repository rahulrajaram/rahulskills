#!/usr/bin/env python3
"""
Deep anti-pattern analysis - extracts specific instances of problematic behaviors.
"""

import json
import re
from typing import List, Dict, Tuple

def load_messages(filepath: str) -> List[Dict]:
    """Load JSONL conversation."""
    messages = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    return messages


def extract_text(content) -> str:
    """Extract readable text from message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
        return '\n'.join(texts)
    return ''


def find_credential_antipatterns(messages: List[Dict]) -> List[Dict]:
    """Find instances where credentials were hardcoded or assumed."""
    findings = []

    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        content = extract_text(msg.get('message', {}).get('content', ''))

        # Pattern 1: Hardcoded passwords
        if re.search(r'password\s*=\s*["\'].*["\']', content, re.IGNORECASE):
            findings.append({
                'type': 'HARDCODED_PASSWORD',
                'index': i,
                'timestamp': msg.get('timestamp', ''),
                'evidence': re.findall(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE),
                'context': content[:300]
            })

        # Pattern 2: Using credentials without reading from secrets
        if 'PASSWORD' in content and 'kubectl get secret' not in content:
            if any(keyword in content for keyword in ['export', 'DATA_PLANE_DB_PASSWORD', 'DB_PASSWORD']):
                findings.append({
                    'type': 'ASSUMED_CREDENTIAL',
                    'index': i,
                    'timestamp': msg.get('timestamp', ''),
                    'evidence': 'Used PASSWORD env var without reading from secret',
                    'context': content[:300]
                })

    return findings


# Commands where retries are normal (test-fix-test cycles, status checks)
NORMAL_RETRY_COMMANDS = {
    'pytest', 'python -m pytest', 'npm test', 'npm run test',
    'go test', 'cargo test', 'make test',
    'git status', 'git diff', 'git log',
    'kubectl get', 'kubectl describe', 'docker ps',
    'ls', 'pwd', 'cat', 'head', 'tail',
}


def is_normal_retry_command(cmd: str) -> bool:
    """Check if command is expected to be retried (test cycles, etc.)."""
    cmd_lower = cmd.lower().strip()
    for normal_cmd in NORMAL_RETRY_COMMANDS:
        if cmd_lower.startswith(normal_cmd):
            return True
    return False


def find_retry_without_diagnosis(messages: List[Dict]) -> List[Dict]:
    """Find retry attempts without investigating root cause.

    Excludes normal test-fix-test cycles and status check commands.
    """
    findings = []

    # Track command sequences
    recent_commands = []

    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        # Extract bash commands
        msg_content = msg.get('message', {}).get('content', [])
        if not isinstance(msg_content, list):
            continue

        for item in msg_content:
            if isinstance(item, dict) and item.get('name') == 'Bash':
                cmd = item.get('input', {}).get('command', '')
                recent_commands.append({
                    'cmd': cmd,
                    'index': i,
                    'timestamp': msg.get('timestamp', '')
                })

                # Skip normal retry commands (test cycles, status checks)
                if is_normal_retry_command(cmd):
                    continue

                # Check if this is a retry (same command within last 5 commands)
                if len(recent_commands) >= 2:
                    for prev in recent_commands[-6:-1]:
                        if prev['cmd'] == cmd:
                            # Check if there was diagnosis between attempts
                            checked_logs = False
                            for check_msg in messages[prev['index']:i]:
                                check_content = extract_text(check_msg.get('message', {}).get('content', ''))
                                if any(word in check_content for word in ['kubectl logs', 'kubectl describe', 'kubectl get events', 'error', 'failed', 'traceback']):
                                    checked_logs = True
                                    break

                            if not checked_logs:
                                findings.append({
                                    'type': 'RETRY_WITHOUT_DIAGNOSIS',
                                    'command': cmd[:100],
                                    'first_attempt': prev['index'],
                                    'retry_attempt': i,
                                    'timestamp': msg.get('timestamp', ''),
                                    'evidence': f'Retried command without checking logs/events'
                                })

    return findings


def find_scope_creep(messages: List[Dict]) -> List[Dict]:
    """Find instances where scope expanded beyond original request."""
    findings = []

    # Track user requests and assistant responses
    current_request = None
    current_request_idx = None

    for i, msg in enumerate(messages):
        if msg.get('type') == 'user':
            current_request = extract_text(msg.get('message', {}).get('content', ''))
            current_request_idx = i

        elif msg.get('type') == 'assistant' and current_request:
            content = extract_text(msg.get('message', {}).get('content', ''))

            # Keywords indicating scope expansion
            expansion_indicators = [
                'also create', 'also build', 'also implement', 'also add',
                'we should also', 'let me also', 'additionally',
                'I will also', 'we need to also'
            ]

            for indicator in expansion_indicators:
                if indicator in content.lower():
                    # Extract the sentence
                    sentences = content.split('.')
                    for sent in sentences:
                        if indicator in sent.lower():
                            findings.append({
                                'type': 'SCOPE_EXPANSION',
                                'original_request': current_request[:200],
                                'expansion': sent.strip()[:300],
                                'request_index': current_request_idx,
                                'expansion_index': i,
                                'timestamp': msg.get('timestamp', '')
                            })

    return findings


def find_missing_verification(messages: List[Dict]) -> List[Dict]:
    """Find cases where values were used without verification."""
    findings = []

    for i, msg in enumerate(messages):
        if msg.get('type') != 'assistant':
            continue

        content = extract_text(msg.get('message', {}).get('content', ''))

        # Pattern: Using IP addresses without verifying
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
            if 'docker inspect' not in content and 'kubectl get' not in content:
                # Check if IP is being SET rather than READ
                if any(keyword in content for keyword in ['export', 'PLANE_URL=', '  url:', 'endpoint:']):
                    findings.append({
                        'type': 'UNVERIFIED_IP_USAGE',
                        'evidence': re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content),
                        'index': i,
                        'timestamp': msg.get('timestamp', ''),
                        'context': content[:300]
                    })

        # Pattern: Using service URLs without checking availability
        if re.search(r'http://.*:\d+', content):
            if 'curl' not in content and 'requests.get' not in content and 'await' not in content:
                if 'export' in content or '=' in content:
                    findings.append({
                        'type': 'UNVERIFIED_SERVICE_URL',
                        'evidence': re.findall(r'http://[^\s]+:\d+', content),
                        'index': i,
                        'timestamp': msg.get('timestamp', ''),
                        'context': content[:200]
                    })

    return findings


def extract_conversation_timeline(messages: List[Dict]) -> List[Tuple[str, str, str]]:
    """Extract high-level timeline of conversation."""
    timeline = []

    for msg in messages:
        if msg.get('type') == 'user':
            content = extract_text(msg.get('message', {}).get('content', ''))
            if content.strip():
                timeline.append((
                    msg.get('timestamp', ''),
                    'USER',
                    content[:150]
                ))

    return timeline


def find_tool_opportunities(messages: List[Dict]) -> Dict[str, List]:
    """Find opportunities for custom tools."""
    opportunities = {
        'repeated_sequences': [],
        'manual_checks': [],
        'error_prone_ops': []
    }

    # Track command sequences
    sequences = []
    current_sequence = []

    for msg in messages:
        if msg.get('type') != 'assistant':
            continue

        msg_content = msg.get('message', {}).get('content', [])
        if not isinstance(msg_content, list):
            continue

        cmds = []
        for item in msg_content:
            if isinstance(item, dict) and item.get('name') == 'Bash':
                cmds.append(item.get('input', {}).get('command', ''))

        if cmds:
            current_sequence.extend(cmds)
        else:
            if len(current_sequence) >= 2:
                sequences.append(current_sequence[:])
            current_sequence = []

    # Find repeated sequences
    from collections import Counter
    seq_counter = Counter()
    for seq in sequences:
        if len(seq) >= 2:
            seq_key = ' && '.join(seq)
            if len(seq_key) < 200:
                seq_counter[seq_key] += 1

    for seq, count in seq_counter.most_common(10):
        if count >= 2:
            opportunities['repeated_sequences'].append({
                'sequence': seq,
                'count': count,
                'tool_name': f'myproject-{seq.split()[0].replace("kubectl", "k8s").replace("docker", "docker")}'
            })

    return opportunities


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python deep_analysis.py <conversation.jsonl>")
        sys.exit(1)

    filepath = sys.argv[1]
    messages = load_messages(filepath)

    print("=" * 80)
    print("DEEP ANTI-PATTERN ANALYSIS")
    print("=" * 80)

    # Timeline
    print("\nCONVERSATION TIMELINE (User Requests):")
    print("-" * 80)
    timeline = extract_conversation_timeline(messages)
    for i, (ts, role, content) in enumerate(timeline[:20], 1):
        print(f"{i}. [{ts[11:19]}] {content}")
    print(f"\n... ({len(timeline)} total user messages)")

    # Credential anti-patterns
    print("\n\n1. CREDENTIAL ANTI-PATTERNS:")
    print("-" * 80)
    cred_patterns = find_credential_antipatterns(messages)
    for p in cred_patterns[:10]:
        print(f"\n  Type: {p['type']}")
        print(f"  Timestamp: {p['timestamp']}")
        print(f"  Evidence: {p.get('evidence', 'N/A')}")
        print(f"  Context: {p['context'][:200]}...")

    # Retry without diagnosis
    print("\n\n2. RETRY WITHOUT DIAGNOSIS:")
    print("-" * 80)
    retry_patterns = find_retry_without_diagnosis(messages)
    for p in retry_patterns[:10]:
        print(f"\n  Command: {p['command']}")
        print(f"  First attempt: Message {p['first_attempt']}")
        print(f"  Retry attempt: Message {p['retry_attempt']}")
        print(f"  Evidence: {p['evidence']}")

    # Scope creep
    print("\n\n3. SCOPE EXPANSION INSTANCES:")
    print("-" * 80)
    scope_patterns = find_scope_creep(messages)
    for p in scope_patterns[:10]:
        print(f"\n  Original request: {p['original_request']}")
        print(f"  Expansion: {p['expansion']}")
        print(f"  Timestamp: {p['timestamp']}")

    # Missing verification
    print("\n\n4. MISSING VERIFICATION:")
    print("-" * 80)
    verify_patterns = find_missing_verification(messages)
    for p in verify_patterns[:10]:
        print(f"\n  Type: {p['type']}")
        print(f"  Evidence: {p.get('evidence', 'N/A')}")
        print(f"  Context: {p['context']}")

    # Tool opportunities
    print("\n\n5. TOOL OPPORTUNITIES:")
    print("-" * 80)
    tool_opps = find_tool_opportunities(messages)
    for seq_info in tool_opps['repeated_sequences']:
        print(f"\n  Repeated {seq_info['count']}x: {seq_info['sequence'][:150]}")
        print(f"  → Potential tool: {seq_info['tool_name']}")

    print("\n\n" + "=" * 80)
    print("SUMMARY COUNTS:")
    print("=" * 80)
    print(f"  Credential anti-patterns: {len(cred_patterns)}")
    print(f"  Retry-without-diagnosis: {len(retry_patterns)}")
    print(f"  Scope expansions: {len(scope_patterns)}")
    print(f"  Unverified values: {len(verify_patterns)}")
    print(f"  Repeated sequences: {len(tool_opps['repeated_sequences'])}")
