---
name: memleak-investigate
description: Investigate longitudinal memory growth in a specific Linux process using /proc and, with approval, attach/tracing tools. For whole-system OOM, swap, or tuning without a target process, use system-memory-audit first.
argument-hint: "[PID or process-name]"
---

# Memory Leak Investigator

Determine whether one process retains memory over time and narrow the likely
source. High RSS, peak RSS, swap use, or allocation churn alone does not prove a
leak.

## Preconditions and safety

Resolve a process name to an exact PID and verify `/proc/<PID>/exe`, command
line, start time, owner, and container/cgroup before sampling. If multiple PIDs
match, ask which one. If the process exits or PID identity changes, stop rather
than merging samples from different processes.

Start read-only. Ask before `sudo`, gdb/gcore attaches, eBPF uprobes, signals,
restarts, or workload generation. Do not install missing tools. Containers,
hidepid, ptrace policy, stripped binaries, allocator choice, and short-lived
processes can limit evidence; report the limitation and fallback.

## 1. Establish a comparable longitudinal baseline

```bash
ps -p <PID> -o pid=,lstart=,etime=,rss=,vsz=,pcpu=,pmem=,comm=
grep -E '^(Name|State|VmRSS|VmHWM|VmSize|VmSwap|VmData|RssAnon|RssFile|Threads):' \
  /proc/<PID>/status
cat /proc/<PID>/cgroup
```

Sample at a cadence appropriate to the suspected growth while recording workload
phase. Two minutes is a starting point, not a universal proof window:

```bash
for i in $(seq 1 12); do
  test -r /proc/<PID>/status || { echo "process exited" >&2; break; }
  awk -v at="$(date -Iseconds)" '
    /^VmRSS:/ {rss=$2} /^RssAnon:/ {anon=$2} /^RssFile:/ {file=$2}
    /^VmSwap:/ {swap=$2} /^Threads:/ {threads=$2}
    END {print at "," rss "," anon "," file "," swap "," threads}
  ' /proc/<PID>/status
  sleep 10
done
```

`VmHWM` is a historical peak, not evidence that past growth leaked or swapped.
Repeated RSS/anonymous growth under comparable load suggests retention but can
still be cache growth, allocator fragmentation, or delayed reclamation.

## 2. Classify the growth

Use `/proc/<PID>/smaps_rollup` when readable, then `smaps`/`maps` for region
detail. Compare anonymous, file-backed, shared, swap, thread count, and file
descriptor count over time. Avoid summing virtual map extents as if they were
resident memory.

```bash
cat /proc/<PID>/smaps_rollup 2>/dev/null
find /proc/<PID>/fd -mindepth 1 -maxdepth 1 2>/dev/null | wc -l
find /proc/<PID>/task -mindepth 1 -maxdepth 1 2>/dev/null | wc -l
grep -iE 'jemalloc|tcmalloc|mimalloc' /proc/<PID>/maps 2>/dev/null
```

`/proc/<PID>/net/*` represents the process network namespace, not per-PID socket
ownership. If socket ownership matters, use an already-installed ownership-aware
tool such as `ss -np` and disclose permission gaps.

## 3. Choose one deeper method

Only after baseline evidence supports unexplained retention:

- Prefer allocator-native profiling enabled at process start when supported
  (jemalloc/tcmalloc/mimalloc). State when restart/configuration is required.
- With explicit approval, use `memleak-bpfcc -p <PID>` for outstanding sampled
  allocation stacks. Validate libc/allocator probe coverage and symbol quality.
- With explicit approval, briefly attach gdb for allocator statistics. Attaches
  can pause or destabilize the target; do not write files inside the target
  process without confirming paths and disk capacity.
- Create a core dump only with approval after estimating RSS-sized disk use and
  reviewing sensitive-data exposure.

Do not use a naive `malloc_count - free_count` bpftrace program as leak proof:
call counts are not bytes, realloc/failures/interposed allocators alter semantics,
and global pending-return state is concurrency-unsafe. Do not sample allocation
contents unless the user explicitly accepts the privacy risk.

## 4. Correlate and verify

Compare idle and active phases only when the user can supply a reproducible,
safe workload. Correlate retained bytes/stacks with source and build identity.
After a candidate fix or mitigation, repeat the same workload and sampling
window; a lower one-off RSS value is not sufficient verification.

Internet issue search is optional and requires browsing authorization under the
active environment policy. Prefer exact version/build and upstream primary
sources; do not substitute similar reports for local evidence.

## Output contract

Return:

1. target identity, environment, and sampling window;
2. a timestamped evidence table and growth rate with uncertainty;
3. classification: stable, inconclusive, suspected retention, or traced leak;
4. alternatives considered (cache, fragmentation, mmap, threads, descriptors,
   GPU/cgroup pressure) and what is actually ruled out;
5. recommended next diagnostic or mitigation, with approval needs; and
6. exact verification needed to close the finding.

Do not write a report file unless the user requests one. Before sharing raw
artifacts, redact secrets, home paths, hostnames, IPs, and private socket paths.
