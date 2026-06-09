---
name: system-memory-audit
description: Audit Linux system-wide memory health, swap activity, PSI, kernel tunables, and top consumers. Use for system memory health or tuning; for one named process with longitudinal growth, use memleak-investigate.
argument-hint: ""
---

# System Memory Audit

Produce a read-only, evidence-backed snapshot. High usage, nonzero swap, or a
large process is not by itself evidence of a leak or harmful pressure.

## Routing and safety

- Use this skill for whole-system health, contention, and tunable review.
- Use `memleak-investigate` for a specific process across time.
- The audit is read-only. Restarting/killing processes, changing OOM scores,
  applying `sysctl`, and writing `/etc/sysctl.d` are separate privileged actions
  that require an explicit proposal and user approval.
- Do not install missing tools. Fall back to `/proc` and disclose limitations.

## 1. Establish pressure and activity

```bash
free -h
sed -n '1,30p' /proc/meminfo
vmstat 1 3
cat /proc/pressure/memory 2>/dev/null || true
cat /proc/pressure/io 2>/dev/null || true
```

Report `MemAvailable`, swap used, and `vmstat` swap-in/swap-out rates. PSI
thresholds are workload- and window-dependent; describe sustained `some`/`full`
stall time rather than applying universal warning percentages.

If `deepmetrics` is already installed, it may add context, but its absence is
not an error and does not authorize installation.

## 2. Read tunables without prescribing constants

```bash
for key in overcommit_memory overcommit_ratio swappiness \
  vfs_cache_pressure dirty_ratio dirty_background_ratio min_free_kbytes \
  zone_reclaim_mode; do
  printf '%s=' "$key"
  cat "/proc/sys/vm/$key"
done
cat /proc/sys/kernel/pid_max
```

Compare values with kernel documentation, RAM size, NUMA layout, storage,
allocator/database guidance, and observed workload. Do not label fixed ranges as
universally safe. In particular, low swappiness is not always better,
`overcommit_memory=2` can break workloads, and `min_free_kbytes` must not be set
from a fixed workstation-sized range without kernel/RAM analysis.

## 3. Enumerate actual consumers

Sort by RSS bytes, not `%MEM`, and inspect every readable PID rather than the
first directory entries:

```bash
ps -e -o pid=,rss=,vsz=,comm= --sort=-rss | head -20

for status in /proc/[0-9]*/status; do
  pid=${status#/proc/}; pid=${pid%/status}
  awk -v pid="$pid" '
    /^Name:/ {name=$2}
    /^VmSwap:/ {swap=$2}
    END {if (swap+0 > 0) print swap, pid, name}
  ' "$status" 2>/dev/null
done | sort -rn | head -20

for score in /proc/[0-9]*/oom_score; do
  pid=${score#/proc/}; pid=${pid%/oom_score}
  value=$(cat "$score" 2>/dev/null) || continue
  name=$(cat "/proc/$pid/comm" 2>/dev/null) || name="?"
  printf '%s %s %s\n' "$value" "$pid" "$name"
done | sort -rn | head -20
```

Processes can exit during enumeration and permissions can hide fields. Treat
missing rows as sampling limitations. `oom_score` is a current kernel heuristic,
not a guaranteed kill order.

## 4. Diagnose before recommending

Correlate consumers with active swap I/O, PSI, OOM journal events, cgroup limits,
and workload timing. Separate:

- healthy cache use from reclaim pressure;
- allocated-but-idle swap from current thrashing;
- one large stable process from system-wide contention; and
- host pressure from a cgroup/container limit.

Recommend monitoring or a per-process investigation when a single snapshot is
insufficient. Do not recommend restarting a process solely because it ranks
high by RSS.

## Output contract

Return system facts, pressure evidence, top consumers, tunable context,
limitations, and prioritized recommendations. If changes may help, provide a
read-only proposal containing current value, proposed value, rationale,
workload assumptions, verification, rollback, and whether persistence is
desired. Wait for explicit approval before generating or running an apply script.
