#!/usr/bin/env python3
"""
Comprehensive conversation analysis for extracting anti-patterns, tooling gaps, and insights.
"""

import json
import sys
from collections import defaultdict, Counter
from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ConversationStats:
    """Statistics extracted from conversation."""
    total_turns: int = 0
    user_messages: List[str] = field(default_factory=list)
    assistant_messages: List[str] = field(default_factory=list)
    bash_commands: List[Dict[str, Any]] = field(default_factory=list)
    file_reads: List[str] = field(default_factory=list)
    file_writes: List[str] = field(default_factory=list)
    file_edits: List[Dict[str, Any]] = field(default_factory=list)
    grep_searches: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    retries: List[Dict[str, Any]] = field(default_factory=list)
    scope_expansions: List[str] = field(default_factory=list)
    hardcoded_values: List[Dict[str, Any]] = field(default_factory=list)

    # Command patterns
    repeated_commands: Counter = field(default_factory=Counter)
    failed_commands: List[Dict[str, Any]] = field(default_factory=list)

    # Decision points
    assumptions_made: List[str] = field(default_factory=list)
    questions_asked: List[str] = field(default_factory=list)


def load_conversation(filepath: str) -> List[Dict]:
    """Load JSONL conversation file."""
    messages = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    return messages


def extract_text_from_content(content: Any) -> str:
    """Extract text from message content (handles various formats)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif item.get('type') == 'thinking':
                    texts.append(f"[THINKING: {item.get('thinking', '')[:200]}...]")
            elif isinstance(item, str):
                texts.append(item)
        return '\n'.join(texts)
    return str(content)


def analyze_tool_use(message: Dict, stats: ConversationStats):
    """Extract tool usage patterns."""
    content = message.get('message', {}).get('content', [])
    if not isinstance(content, list):
        return

    for item in content:
        if not isinstance(item, dict):
            continue

        tool_name = item.get('name')
        tool_input = item.get('input', {})

        if tool_name == 'Bash':
            cmd = tool_input.get('command', '')
            desc = tool_input.get('description', '')
            stats.bash_commands.append({
                'command': cmd,
                'description': desc,
                'timestamp': message.get('timestamp', '')
            })
            stats.repeated_commands[cmd] += 1

        elif tool_name == 'Read':
            stats.file_reads.append(tool_input.get('file_path', ''))

        elif tool_name == 'Write':
            stats.file_writes.append(tool_input.get('file_path', ''))

        elif tool_name == 'Edit':
            stats.file_edits.append({
                'file': tool_input.get('file_path', ''),
                'old': tool_input.get('old_string', '')[:100],
                'new': tool_input.get('new_string', '')[:100]
            })

        elif tool_name == 'Grep':
            stats.grep_searches.append(tool_input.get('pattern', ''))


def analyze_tool_results(message: Dict, stats: ConversationStats):
    """Analyze tool results for errors and failures."""
    content = message.get('message', {}).get('content', [])
    if not isinstance(content, list):
        return

    for item in content:
        if not isinstance(item, dict):
            continue

        if item.get('type') == 'tool_result':
            result_content = item.get('content', '')
            result_str = str(result_content)

            # Check for errors
            if 'error' in result_str.lower() or 'failed' in result_str.lower():
                stats.errors.append({
                    'tool_use_id': item.get('tool_use_id', ''),
                    'content': result_str[:500],
                    'timestamp': message.get('timestamp', '')
                })


def detect_hardcoded_values(text: str) -> List[Dict[str, str]]:
    """Detect potential hardcoded values (passwords, IPs, secrets)."""
    patterns = []

    # Look for password assignments
    if 'password' in text.lower() and '=' in text:
        for line in text.split('\n'):
            if 'password' in line.lower() and '=' in line:
                patterns.append({
                    'type': 'password',
                    'line': line.strip()[:200]
                })

    # Look for IP addresses being set
    import re
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    if re.search(ip_pattern, text):
        for match in re.finditer(ip_pattern, text):
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            patterns.append({
                'type': 'ip_address',
                'value': match.group(),
                'context': context
            })

    return patterns


def detect_scope_expansion(user_msg: str, assistant_msgs: List[str]) -> List[str]:
    """Detect when assistant expanded scope beyond original request."""
    expansions = []

    # Simple heuristic: if assistant mentions creating/building things not in user request
    original_words = set(user_msg.lower().split())

    expansion_keywords = ['also', 'additionally', 'furthermore', 'we should also',
                          'let me also', 'i will also', 'we need to']

    for msg in assistant_msgs:
        msg_lower = msg.lower()
        for keyword in expansion_keywords:
            if keyword in msg_lower:
                # Extract sentence containing keyword
                sentences = msg.split('.')
                for sent in sentences:
                    if keyword in sent.lower():
                        expansions.append(sent.strip())

    return expansions


def analyze_conversation(filepath: str) -> ConversationStats:
    """Main analysis function."""
    messages = load_conversation(filepath)
    stats = ConversationStats()

    current_user_msg = ""
    current_assistant_msgs = []

    for msg in messages:
        msg_type = msg.get('type')

        if msg_type == 'user':
            # Analyze previous turn if exists
            if current_user_msg and current_assistant_msgs:
                expansions = detect_scope_expansion(current_user_msg, current_assistant_msgs)
                stats.scope_expansions.extend(expansions)

            # Start new turn
            content = msg.get('message', {}).get('content', '')
            current_user_msg = extract_text_from_content(content)
            stats.user_messages.append(current_user_msg)
            current_assistant_msgs = []
            stats.total_turns += 1

        elif msg_type == 'assistant':
            content = msg.get('message', {}).get('content', '')
            text = extract_text_from_content(content)
            current_assistant_msgs.append(text)
            stats.assistant_messages.append(text)

            # Analyze tool use
            analyze_tool_use(msg, stats)
            analyze_tool_results(msg, stats)

            # Check for hardcoded values
            hardcoded = detect_hardcoded_values(text)
            stats.hardcoded_values.extend(hardcoded)

    return stats


def print_anti_patterns(stats: ConversationStats):
    """Print identified anti-patterns."""
    print("=" * 80)
    print("ANTI-PATTERN ANALYSIS")
    print("=" * 80)

    print("\n1. REPEATED COMMANDS (potential tool opportunities)")
    print("-" * 80)
    for cmd, count in stats.repeated_commands.most_common(20):
        if count >= 3:
            print(f"  [{count}x] {cmd[:100]}")

    print("\n2. HARDCODED VALUES DETECTED")
    print("-" * 80)
    for item in stats.hardcoded_values[:20]:
        print(f"  Type: {item['type']}")
        print(f"  Context: {item.get('line', item.get('context', ''))[:150]}")
        print()

    print("\n3. SCOPE EXPANSIONS")
    print("-" * 80)
    for expansion in stats.scope_expansions[:15]:
        print(f"  • {expansion[:200]}")

    print("\n4. ERRORS ENCOUNTERED")
    print("-" * 80)
    for error in stats.errors[:20]:
        print(f"  Timestamp: {error.get('timestamp', 'N/A')}")
        print(f"  Content: {error['content'][:300]}")
        print()


def print_tooling_analysis(stats: ConversationStats):
    """Print tooling gaps and opportunities."""
    print("\n" + "=" * 80)
    print("TOOLING ANALYSIS")
    print("=" * 80)

    print("\n1. FILE OPERATIONS")
    print("-" * 80)
    print(f"  Files Read: {len(stats.file_reads)}")
    print(f"  Files Written: {len(stats.file_writes)}")
    print(f"  Files Edited: {len(stats.file_edits)}")

    print("\n2. COMMAND PATTERNS")
    print("-" * 80)

    # Group similar commands
    kubectl_cmds = [c for c in stats.bash_commands if 'kubectl' in c['command']]
    docker_cmds = [c for c in stats.bash_commands if 'docker' in c['command']]
    pytest_cmds = [c for c in stats.bash_commands if 'pytest' in c['command']]

    print(f"  kubectl commands: {len(kubectl_cmds)}")
    print(f"  docker commands: {len(docker_cmds)}")
    print(f"  pytest commands: {len(pytest_cmds)}")

    print("\n3. GREP SEARCHES (exploration patterns)")
    print("-" * 80)
    for pattern in stats.grep_searches[:15]:
        print(f"  • {pattern}")


def print_summary(stats: ConversationStats):
    """Print overall summary."""
    print("\n" + "=" * 80)
    print("CONVERSATION SUMMARY")
    print("=" * 80)
    print(f"  Total turns: {stats.total_turns}")
    print(f"  User messages: {len(stats.user_messages)}")
    print(f"  Assistant messages: {len(stats.assistant_messages)}")
    print(f"  Bash commands: {len(stats.bash_commands)}")
    print(f"  Errors encountered: {len(stats.errors)}")
    print(f"  Scope expansions detected: {len(stats.scope_expansions)}")
    print(f"  Hardcoded values found: {len(stats.hardcoded_values)}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_conversation.py <conversation.jsonl>")
        sys.exit(1)

    filepath = sys.argv[1]
    stats = analyze_conversation(filepath)

    print_summary(stats)
    print_anti_patterns(stats)
    print_tooling_analysis(stats)
