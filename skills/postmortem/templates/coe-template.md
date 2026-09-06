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
| [Time or unknown] | [Supported cause identified, if observed] |
| [Time or unknown] | [Mitigation applied, if observed] |
| [Time or unknown] | [Service restored, if observed] |
| HH:MM:SS | [Post-incident review] |

---

## 5-Whys Analysis

### Problem 1: [Primary Problem Statement]

**Why did [symptom] happen?**
→ [Supported explanation, evidence source, or explicit unknown]

[Continue or branch only while evidence supports a useful causal link. No fixed
number of whys and no required process cause. Distinguish hypotheses from causes.]

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

### Immediate (P0) - Proposed or observed status
| # | Action | Owner | Status |
|---|--------|-------|--------|
| AI-1 | [Proposed action or observed mitigation] | [Name] | [Planned/Unknown; Done only with execution evidence] |

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
