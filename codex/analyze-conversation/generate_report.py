#!/usr/bin/env python3
"""
Generates comprehensive retrospective report from conversation analysis.
Entry point for /analyze-conversation skill.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Import from analyzer and patterns modules
sys.path.insert(0, os.path.dirname(__file__))
from analyzer import analyze_conversation
from patterns import (
    find_credential_antipatterns,
    find_retry_without_diagnosis,
    find_scope_creep,
    find_missing_verification,
    find_tool_opportunities,
    extract_conversation_timeline,
    load_messages
)


def find_conversation_file(conversation_id=None):
    """Find conversation JSONL file."""
    if conversation_id:
        # Search in .claude/projects/
        projects_dir = Path.home() / '.claude' / 'projects'
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                conv_file = project_dir / f'{conversation_id}.jsonl'
                if conv_file.exists():
                    return str(conv_file)
        raise FileNotFoundError(f"Conversation {conversation_id} not found")
    else:
        # Use current conversation (most recent JSONL in current project)
        # This would need to be determined by the skill runner
        raise ValueError("No conversation ID provided - current conversation detection not yet implemented")


# Commands that are normal development patterns - don't suggest tools for these
NORMAL_DEV_COMMANDS = {
    'git status',
    'git diff',
    'git log',
    'git add',
    'git commit',
    'ls',
    'pwd',
    'cd',
    'cat',
    'echo',
}

# Command prefixes that are normal test-fix-test cycles
NORMAL_TEST_COMMANDS = {
    'pytest',
    'python -m pytest',
    'npm test',
    'npm run test',
    'go test',
    'cargo test',
}


def is_normal_dev_command(cmd: str) -> bool:
    """Check if command is a normal development pattern."""
    cmd_lower = cmd.lower().strip()

    # Check exact matches
    for normal_cmd in NORMAL_DEV_COMMANDS:
        if cmd_lower.startswith(normal_cmd):
            return True

    # Check test commands
    for test_cmd in NORMAL_TEST_COMMANDS:
        if cmd_lower.startswith(test_cmd):
            return True

    return False


def check_project_context(conversation_file: str) -> dict:
    """Check what tools/docs already exist in the project."""
    context = {
        'has_project_cli': False,
        'has_tools_doc': False,
        'has_claude_md': False,
        'has_operations_md': False,
        'existing_tools': [],
    }

    # Try to find project root from conversation file path
    # e.g., ~/.claude/projects/<project-slug>/...
    # maps to ~/Documents/myproject/
    conv_path = Path(conversation_file)
    project_dir_name = conv_path.parent.name  # e.g., <project-slug>

    if project_dir_name.startswith('-'):
        # Convert back to path: <project-slug> -> ~/Documents/myproject
        project_path = Path('/' + project_dir_name[1:].replace('-', '/'))

        # Check for common documentation files
        if (project_path / 'CLAUDE.md').exists():
            context['has_claude_md'] = True
        if (project_path / 'OPERATIONS.md').exists():
            context['has_operations_md'] = True
        if (project_path / 'TOOLS.md').exists():
            context['has_tools_doc'] = True

        # Check for project CLI
        for subdir in ['myproject_cp', '.']:
            scripts_dir = project_path / subdir / 'scripts'
            if scripts_dir.exists():
                context['has_project_cli'] = True
                break

        # Check for bin/myproject or similar
        for pattern in ['bin/myproject', 'scripts/myproject', '.local/bin/myproject']:
            if (project_path / pattern).exists() or (Path.home() / pattern).exists():
                context['has_project_cli'] = True
                break

    return context


def generate_markdown_report(conversation_file: str, output_dir: str = None) -> str:
    """Generate comprehensive markdown report."""

    # Create output directory
    if output_dir is None:
        output_dir = Path.home() / '.claude' / 'retrospectives'
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract conversation ID from filename
    conv_id = Path(conversation_file).stem

    # Run analysis
    print(f"Analyzing conversation: {conv_id}...")
    stats = analyze_conversation(conversation_file)
    messages = load_messages(conversation_file)

    # Check project context for existing tools/docs
    project_context = check_project_context(conversation_file)

    # Extract detailed patterns
    print("Extracting anti-patterns...")
    cred_patterns = find_credential_antipatterns(messages)
    retry_patterns = find_retry_without_diagnosis(messages)
    scope_patterns = find_scope_creep(messages)
    verify_patterns = find_missing_verification(messages)
    tool_opps = find_tool_opportunities(messages)
    timeline = extract_conversation_timeline(messages)

    # Generate report
    report_lines = []

    # Header
    report_lines.append(f"# Conversation Retrospective: {conv_id}")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Conversation File:** `{conversation_file}`")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append("### Top Anti-Patterns Found")
    report_lines.append("")
    report_lines.append(f"1. **Retry-Without-Diagnosis**: {len(retry_patterns)} instances")
    report_lines.append(f"2. **Credential Assumptions**: {len(cred_patterns)} instances")
    report_lines.append(f"3. **Scope Expansions**: {len(scope_patterns)} instances")
    report_lines.append(f"4. **Unverified Values**: {len(verify_patterns)} instances")
    report_lines.append(f"5. **Tool Discovery Gaps**: {len(stats.file_writes)} scripts written (potential duplicates)")
    report_lines.append("")

    report_lines.append("### Top Tool Opportunities")
    report_lines.append("")
    tool_opp_count = 0
    for cmd, count in stats.repeated_commands.most_common(10):
        if count >= 3 and not is_normal_dev_command(cmd):
            tool_opp_count += 1
            tool_name = f"myproject-{cmd.split()[0] if cmd.split() else 'cmd'}"
            report_lines.append(f"{tool_opp_count}. **Repeated {count}x**: `{cmd[:80]}...` → Tool: `{tool_name}`")
            if tool_opp_count >= 5:
                break
    if tool_opp_count == 0:
        report_lines.append("- None identified (repeated commands are normal dev patterns)")
    report_lines.append("")

    report_lines.append("### Top Universal Rules Violated")
    report_lines.append("")
    if len(retry_patterns) > 0:
        report_lines.append(f"- **Rule 2** (diagnose before retry): {len(retry_patterns)} violations")
    if len(cred_patterns) > 0:
        report_lines.append(f"- **Rule 1** (never hardcode creds): {len(cred_patterns)} violations")
    if len(scope_patterns) > 0:
        report_lines.append(f"- **Rule 3** (ask before scope expansion): {len(scope_patterns)} violations")
    if len(verify_patterns) > 0:
        report_lines.append(f"- **Rule 6** (verify external values): {len(verify_patterns)} violations")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Conversation Summary
    report_lines.append("## Conversation Summary")
    report_lines.append("")
    report_lines.append(f"- **Total Turns**: {stats.total_turns}")
    report_lines.append(f"- **User Messages**: {len(stats.user_messages)}")
    report_lines.append(f"- **Assistant Messages**: {len(stats.assistant_messages)}")
    report_lines.append(f"- **Bash Commands**: {len(stats.bash_commands)}")
    report_lines.append(f"- **Files Read**: {len(stats.file_reads)}")
    report_lines.append(f"- **Files Written**: {len(stats.file_writes)}")
    report_lines.append(f"- **Files Edited**: {len(stats.file_edits)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Anti-Patterns Found
    report_lines.append("## Anti-Patterns Found")
    report_lines.append("")

    # Retry-without-diagnosis
    if retry_patterns:
        report_lines.append("### 1. Retry-Without-Diagnosis")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(retry_patterns)} instances")
        report_lines.append("")
        report_lines.append("**What Happened**: Commands were retried without checking logs/events between attempts.")
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(retry_patterns[:5], 1):
            report_lines.append(f"{i}. Command: `{p['command']}`")
            report_lines.append(f"   - First attempt: Message {p['first_attempt']}")
            report_lines.append(f"   - Retry attempt: Message {p['retry_attempt']}")
            report_lines.append(f"   - Issue: {p['evidence']}")
        report_lines.append("")
        report_lines.append("**Fix**: Always run diagnostics before retry:")
        report_lines.append("```bash")
        report_lines.append("# Before retrying, check:")
        report_lines.append("kubectl logs <resource>")
        report_lines.append("kubectl describe <resource>")
        report_lines.append("kubectl get events --sort-by='.lastTimestamp'")
        report_lines.append("```")
        report_lines.append("")

    # Credential anti-patterns
    if cred_patterns:
        report_lines.append("### 2. Credential Assumptions")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(cred_patterns)} instances")
        report_lines.append("")
        report_lines.append("**What Happened**: Passwords/secrets used without reading from K8s secrets.")
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(cred_patterns[:3], 1):
            report_lines.append(f"{i}. Type: {p['type']}")
            report_lines.append(f"   - Evidence: {p.get('evidence', 'N/A')}")
            report_lines.append(f"   - Context: {p['context'][:150]}...")
        report_lines.append("")
        report_lines.append("**Fix**: Always read from K8s secrets:")
        report_lines.append("```bash")
        report_lines.append("kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d")
        report_lines.append("# Or use: myproject-creds get <secret> --namespace <ns>")
        report_lines.append("```")
        report_lines.append("")

    # Scope creep
    if scope_patterns:
        report_lines.append("### 3. Scope Expansions")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(scope_patterns)} instances")
        report_lines.append("")
        report_lines.append("**What Happened**: Task scope expanded beyond original request without asking user.")
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(scope_patterns[:3], 1):
            report_lines.append(f"{i}. Original request: {p['original_request']}")
            report_lines.append(f"   - Expansion: {p['expansion']}")
        report_lines.append("")
        report_lines.append("**Fix**: Stop and ask before expanding scope:")
        report_lines.append("> \"Encountered blocker: [X]. This is outside the original task scope. Should I:")
        report_lines.append("> a) Fix it now (expands scope)")
        report_lines.append("> b) Document it and continue")
        report_lines.append("> c) Stop here\"")
        report_lines.append("")

    # Unverified values
    if verify_patterns:
        report_lines.append("### 4. Unverified External Values")
        report_lines.append("")
        report_lines.append(f"**Found**: {len(verify_patterns)} instances")
        report_lines.append("")
        report_lines.append("**What Happened**: IP addresses or URLs used without verification.")
        report_lines.append("")
        report_lines.append("**Examples**:")
        for i, p in enumerate(verify_patterns[:3], 1):
            report_lines.append(f"{i}. Type: {p['type']}")
            report_lines.append(f"   - Value: {p.get('evidence', 'N/A')}")
            report_lines.append(f"   - Context: {p['context'][:100]}...")
        report_lines.append("")
        report_lines.append("**Fix**: Always verify external values:")
        report_lines.append("```bash")
        report_lines.append("# For cluster IPs:")
        report_lines.append("docker inspect <container> | jq -r '.[0].NetworkSettings.Networks.kind.IPAddress'")
        report_lines.append("# For service URLs:")
        report_lines.append("kubectl get svc <name> -o jsonpath='{.status.loadBalancer.ingress[0].ip}'")
        report_lines.append("```")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Tool Opportunities
    report_lines.append("## Tool Opportunities")
    report_lines.append("")
    report_lines.append("Commands repeated 3+ times that may benefit from automation:")
    report_lines.append("")

    actionable_tool_opps = []
    for cmd, count in stats.repeated_commands.most_common(10):
        if count >= 3 and not is_normal_dev_command(cmd):
            tool_name = f"myproject-{cmd.split()[0]}" if cmd.split() else "myproject-cmd"
            report_lines.append(f"- **{count}x**: `{cmd[:80]}` → Tool: `{tool_name}`")
            actionable_tool_opps.append((cmd, count))

    if not actionable_tool_opps:
        report_lines.append("- None identified (all repeated commands are normal dev patterns like git, pytest)")
        report_lines.append("")
        report_lines.append("**Note**: Commands like `git status`, `pytest`, etc. are expected to repeat")
        report_lines.append("during normal development and don't indicate tooling gaps.")

    report_lines.append("")
    report_lines.append("**Repeated Command Sequences**:")
    if tool_opps['repeated_sequences']:
        for seq_info in tool_opps['repeated_sequences']:
            report_lines.append(f"- **{seq_info['count']}x**: `{seq_info['sequence'][:100]}`")
            report_lines.append(f"  → Potential tool: `{seq_info['tool_name']}`")
    else:
        report_lines.append("- None found (single commands only)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")

    high_priority_items = []
    medium_priority_items = []

    # HIGH priority - based on actual findings
    if len(retry_patterns) >= 5:
        high_priority_items.append(
            "**Implement `myproject-diag`** - Automated diagnostics before retry\n"
            f"   - Would have prevented: {len(retry_patterns)} retry-without-diagnosis instances"
        )
    if len(cred_patterns) > 0:
        high_priority_items.append(
            "**Implement `myproject-creds`** - Safe credential retrieval\n"
            f"   - Would have prevented: {len(cred_patterns)} credential anti-patterns"
        )
    if len(stats.bash_commands) > 100 and len(stats.errors) > 10:
        high_priority_items.append(
            "**Implement `myproject-preflight`** - Pre-test validation\n"
            "   - Would have prevented: Failed test runs due to environment issues"
        )

    # MEDIUM priority - context-aware (only suggest if not already present)
    if not project_context['has_tools_doc'] and not project_context['has_claude_md']:
        medium_priority_items.append(
            "**Create `TOOLS.md` or `CLAUDE.md`** - Document available tools for discoverability"
        )

    if not project_context['has_project_cli'] and actionable_tool_opps:
        medium_priority_items.append(
            "**Consider unified CLI** - Consolidate repeated command patterns into tools"
        )

    if len(scope_patterns) > 3:
        medium_priority_items.append(
            "**Update workflow** - Add explicit scope confirmation checkpoints"
        )

    report_lines.append("### Priority 1 (HIGH) - Immediate Action")
    report_lines.append("")
    if high_priority_items:
        for i, item in enumerate(high_priority_items, 1):
            report_lines.append(f"{i}. {item}")
    else:
        report_lines.append("- None identified - conversation followed good practices")
    report_lines.append("")

    report_lines.append("### Priority 2 (MEDIUM) - Short-Term")
    report_lines.append("")
    if medium_priority_items:
        for i, item in enumerate(medium_priority_items, 1):
            report_lines.append(f"{i}. {item}")
    else:
        report_lines.append("- None identified - project already has good tooling/documentation")
    report_lines.append("")

    report_lines.append("### Priority 3 (LOW) - Long-Term")
    report_lines.append("")
    report_lines.append("1. **Add telemetry** - Track anti-pattern occurrences over time")
    report_lines.append("2. **Build metrics dashboard** - Visualize improvement trends")
    report_lines.append("3. **Continuous learning loop** - Feed learnings back into `/check-antipatterns`")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Success Metrics
    report_lines.append("## Success Metrics")
    report_lines.append("")
    report_lines.append("| Metric | Current | Target |")
    report_lines.append("|--------|---------|--------|")
    report_lines.append(f"| Retry-without-diagnosis | {len(retry_patterns)} | 0 |")
    report_lines.append(f"| Hardcoded credentials | {len(cred_patterns)} | 0 |")
    report_lines.append(f"| Scope expansions without asking | {len(scope_patterns)} | 0 |")
    report_lines.append(f"| Unverified values | {len(verify_patterns)} | 0 |")
    report_lines.append(f"| Manual command sequences | {len(stats.bash_commands)} | <50 (with tooling) |")
    report_lines.append("")

    # Calculate compliance score
    total_violations = len(retry_patterns) + len(cred_patterns) + len(scope_patterns) + len(verify_patterns)
    total_opportunities = total_violations + 15  # 15 universal rules
    compliance_score = int(((total_opportunities - total_violations) / total_opportunities) * 100) if total_opportunities > 0 else 100

    report_lines.append(f"**Compliance Score**: {compliance_score}% (Target: 95%+)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Footer
    report_lines.append(f"*Report generated by `/analyze-conversation` skill*")
    report_lines.append(f"*For real-time anti-pattern detection, use `/check-antipatterns`*")

    # Write report
    report_file = output_dir / f"{conv_id}_retrospective.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"\n✅ Report generated: {report_file}")
    return str(report_file)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <conversation-file>")
        print("   or: generate_report.py --id <conversation-id>")
        sys.exit(1)

    if sys.argv[1] == '--id':
        if len(sys.argv) < 3:
            print("Error: Conversation ID required")
            sys.exit(1)
        conversation_file = find_conversation_file(sys.argv[2])
    else:
        conversation_file = sys.argv[1]

    output_file = generate_markdown_report(conversation_file)
    print(f"\nRetrospective analysis complete!")
    print(f"Report: {output_file}")
