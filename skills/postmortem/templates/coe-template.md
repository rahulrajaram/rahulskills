# Correction of Error (COE) Report

## Incident: [INCIDENT_TITLE]
**Date:** [YYYY-MM-DD]
**Duration:** [X minutes/hours]
**Severity:** [Critical/High/Medium/Low]
**Affected Systems:** [List affected systems/services]

---

## Executive Summary

[2-3 sentences describing what happened, who was affected, and the business impact]

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
| HH:MM:SS | [First indication of problem] |
| HH:MM:SS | [Detection/Alert triggered] |
| HH:MM:SS | [Investigation started] |
| HH:MM:SS | [Root cause identified] |
| HH:MM:SS | [Mitigation applied] |
| HH:MM:SS | [Service restored] |
| HH:MM:SS | [Post-incident review] |

---

## 5-Whys Analysis

### Problem 1: [Primary Problem Statement]

**Why did [symptom] happen?**
→ [Answer 1]

**Why did [Answer 1] happen?**
→ [Answer 2]

**Why did [Answer 2] happen?**
→ [Answer 3]

**Why did [Answer 3] happen?**
→ [Answer 4]

**Why did [Answer 4] happen?**
→ [Answer 5 - ROOT CAUSE]

### Problem 2: [Secondary Problem Statement] (if applicable)

[Repeat 5-whys structure]

---

## Root Causes

| # | Root Cause | Category |
|---|------------|----------|
| RC1 | [Description] | [Infrastructure/Code/Process/Config/Observability] |
| RC2 | [Description] | [Category] |
| RC3 | [Description] | [Category] |

---

## Impact

| Metric | Value |
|--------|-------|
| Users affected | [N] |
| Failed requests/operations | [N] |
| Data loss | [Yes/No - details if yes] |
| Revenue impact | [$X or N/A] |
| SLA breach | [Yes/No] |
| Customer-reported | [Yes/No] |

---

## Action Items

### Immediate (P0) - Completed
| # | Action | Owner | Status |
|---|--------|-------|--------|
| AI-1 | [Immediate fix applied] | [Name] | ✅ Done |

### Short-term (P1) - This Sprint
| # | Action | Owner | Status |
|---|--------|-------|--------|
| AI-2 | [Preventive measure] | [Name] | TODO |

### Medium-term (P2) - Next Sprint
| # | Action | Owner | Status |
|---|--------|-------|--------|
| AI-3 | [Systemic improvement] | [Name] | TODO |

### Long-term (P3) - Backlog
| # | Action | Owner | Status |
|---|--------|-------|--------|
| AI-4 | [Strategic improvement] | [Name] | TODO |

---

## Lessons Learned

1. **[Lesson Title]** - [Explanation of what we learned and how it applies]

2. **[Lesson Title]** - [Explanation]

3. **[Lesson Title]** - [Explanation]

---

## Appendix

### Files Changed
| Repository | File | Change |
|------------|------|--------|
| [repo] | [path/to/file] | [Brief description] |

### Related Links
- [Link to relevant PR/commit]
- [Link to monitoring dashboard]
- [Link to runbook]

---

**Report Generated:** [YYYY-MM-DDTHH:MM:SSZ]
**Author:** [Name]
**Reviewed By:** [Name or "Pending"]
