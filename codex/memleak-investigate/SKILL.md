---
name: memleak-investigate
description: Investigate memory leaks in any Linux process using /proc, eBPF (bpftrace/bcc), and system tools. Use when user says "memory leak", "memleak", "OOM", "RSS growing", "swap full", or asks to investigate why a process is using too much memory.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, WebSearch
---

# Memory Leak Investigator

Systematic investigation of memory leaks in Linux processes using layered analysis — from lightweight `/proc` inspection through eBPF deep tracing.

## When to Use

- Process RSS/VSZ growing over time
- System swap filling up or OOM kills
- User reports a specific process using too much memory
- Post-incident investigation of memory exhaustion

## Usage

`/memleak-investigate [PID or process-name]`

## Arguments

- `PID` or `process-name` (optional): Target process. If omitted, ask the user or identify the top memory consumer.

## Investigation Phases

Work through phases in order. Each phase is progressively more invasive. **Always complete Phase 1 before proceeding.** Ask the user before running anything that requires `sudo` or could disturb the process (gdb attach, eBPF probes).

---

### Phase 1: Triage (no sudo, no attach, safe)

Goal: Establish baseline facts. Is this actually a leak, or just high but stable usage?

#### 1a. Process identity and basic stats

```bash
# Basic process info
ps -p <PID> -o pid,comm,rss,vsz,etime,pcpu,pmem --no-headers

# Detailed memory breakdown from /proc
grep -E '^(Name|State|Vm|Rss|Threads|Hugetlb)' /proc/<PID>/status
```

**Record these values:**
| Metric | Value | What it means |
|--------|-------|---------------|
| VmRSS | | Physical memory in use |
| VmHWM | | Peak RSS ever reached (proves past growth) |
| VmSize | | Virtual address space |
| VmSwap | | Amount swapped out |
| VmData | | Heap + data segments |
| RssAnon | | Anonymous (heap) portion of RSS |
| RssFile | | File-backed (mmap/shared libs) portion |
| Threads | | Thread count (high = possible thread leak) |

**Key diagnostic:** If `VmHWM >> VmRSS`, the process has already leaked and been partially swapped. If `VmHWM ≈ VmRSS`, it's still growing.

#### 1b. System-wide memory context

```bash
free -h
# Check if swap is filling up — swap pressure is often the real symptom
```

#### 1c. What kind of memory is growing?

```bash
# Top memory regions by size (identifies heap vs GPU vs mmap vs shared libs)
awk '/^[0-9a-f]/ {
    split($1, a, "-");
    size = strtonum("0x" a[2]) - strtonum("0x" a[1]);
    if (size > 10485760) {
        path = $6; if (path == "") path = "(anonymous)";
        printf "%10.1f MB  %s  %s\n", size/1048576, $2, path
    }
}' /proc/<PID>/maps | sort -rn | head -30
```

**Interpret the output:**
| Dominant region | Likely cause |
|-----------------|--------------|
| `[heap]` growing | malloc leak (most common) |
| Many anonymous `rw-p` regions | mmap leak or thread stack leak |
| `/dev/nvidia*` or `/dev/dri/*` growing | GPU memory leak |
| Shared library sizes growing | Unlikely — probably red herring |
| File-backed regions growing | mmap file leak |

#### 1d. What allocator is in use?

```bash
# Check loaded libraries
grep -iE 'jemalloc|tcmalloc|mimalloc' /proc/<PID>/maps
# If nothing matches, it's glibc malloc
```

This matters because:
- **glibc malloc**: fragmentation-prone, `malloc_stats()` available via gdb
- **jemalloc**: has built-in profiling (`MALLOC_CONF=prof:true`), `malloc_stats_print()`
- **tcmalloc**: has heap profiler (`HEAPPROFILE` env var)

#### 1e. Binary analysis (what is this thing?)

```bash
file /proc/<PID>/exe
# Check language, whether stripped, etc.

# For the actual binary path:
readelf -n /proc/<PID>/exe 2>/dev/null | grep -A2 "Build ID"

# What libraries does it use? (hints at framework/language)
ldd /proc/<PID>/exe 2>/dev/null | head -20
```

#### 1f. RSS trend over time (the proof)

Run for at least 2 minutes to establish whether RSS is actually growing:

```bash
# Poll every 10 seconds, record to CSV
for i in $(seq 1 12); do
    rss=$(awk '/VmRSS/ {print $2}' /proc/<PID>/status)
    echo "$(date -Iseconds),$rss"
    sleep 10
done
```

**Decision point after Phase 1:**
- RSS stable → Not a leak. May be high-but-stable usage (investigate startup allocation, config, caching)
- RSS growing slowly → Confirmed leak. Proceed to Phase 2
- RSS growing fast → Confirmed leak, may need urgent action (Phase 2 + consider restart)
- Mostly in swap, VmHWM very high → Already leaked significantly. Capture data now before restart

---

### Phase 2: Deeper /proc analysis (no sudo, no attach)

Goal: Narrow down the leak to a specific memory type and quantify growth rate.

#### 2a. File descriptor leak check

```bash
# Count open file descriptors
ls /proc/<PID>/fd 2>/dev/null | wc -l

# Types of open fds
ls -la /proc/<PID>/fd 2>/dev/null | awk '{print $NF}' | sed 's/.*\///' | sort | uniq -c | sort -rn | head -20
```

Growing fd count → file/socket leak (different problem from memory leak, but often co-occurring).

#### 2b. Thread count trend

```bash
# Current thread count
ls /proc/<PID>/task | wc -l

# Monitor for growth
for i in $(seq 1 6); do
    echo "$(date -Iseconds) threads=$(ls /proc/<PID>/task | wc -l)"
    sleep 10
done
```

Growing thread count → thread leak (each thread consumes ~8 MB stack by default).

#### 2c. Page fault rate

```bash
# From /proc/PID/stat: field 10 = minor faults, field 12 = major faults
awk '{print "minor_faults="$10, "major_faults="$12}' /proc/<PID>/stat
sleep 10
awk '{print "minor_faults="$10, "major_faults="$12}' /proc/<PID>/stat
```

High major fault rate → process is thrashing (accessing swapped-out memory). High minor fault rate → actively allocating new pages.

#### 2d. Detailed per-region breakdown (smaps)

```bash
# Requires sudo on some systems, try without first
# Summarize: which regions contribute most RSS?
awk '/^[0-9a-f]/ {region=$0} /^Rss:/ {rss=$2; if (rss > 1024) print rss " kB  " region}' /proc/<PID>/smaps 2>/dev/null | sort -rn | head -20
```

#### 2e. Network socket count (for processes with network activity)

```bash
# Count network connections — growing count may indicate connection leak
cat /proc/<PID>/net/sockstat 2>/dev/null
```

#### 2f. GPU memory (if applicable)

```bash
# NVIDIA
nvidia-smi --query-compute-apps=pid,used_memory --format=csv 2>/dev/null | grep <PID>

# Or check maps for GPU regions
grep -c '/dev/nvidia\|/dev/dri' /proc/<PID>/maps 2>/dev/null
```

---

### Phase 3: Allocator stats (requires gdb attach — ask user first)

Goal: Get internal allocator statistics. **Attaching gdb briefly pauses the process.**

#### 3a. glibc malloc_info

```bash
# Writes XML to a file inside the target process
gdb -batch \
  -ex 'set $fd = (int)open("/tmp/malloc-info-<PID>.xml", 578, 420)' \
  -ex 'set $fp = (void*)fdopen($fd, "w")' \
  -ex 'call (int)malloc_info(0, $fp)' \
  -ex 'call (int)fflush($fp)' \
  -ex 'call (int)fclose($fp)' \
  -p <PID>
cat /tmp/malloc-info-<PID>.xml
```

The XML output shows per-arena allocation counts, sizes, and free chunk bins. Look for:
- `<total type="rest" count="N" size="HUGE">` — large amount of allocated-but-not-freed memory
- Many arenas with high `mprotect` counts — thread arena fragmentation

#### 3b. jemalloc stats (if jemalloc detected in Phase 1d)

```bash
gdb -batch -ex 'call (void)malloc_stats_print(0, 0, "")' -p <PID>
```

#### 3c. Process core dump (for heap inspection — large and slow)

```bash
# WARNING: creates a file as large as the process RSS
gcore -o /tmp/core-<PID> <PID>
```

Only do this if the other phases haven't identified the source and you need to inspect actual heap contents.

---

### Phase 4: eBPF tracing (requires sudo — ask user first)

Goal: Identify exact allocation call sites and leaked objects. **Non-invasive to the target process** (kernel-level tracing, no attach/pause).

#### 4a. Allocation rate and size distribution

```bash
sudo bpftrace -e '
  uprobe:/usr/lib/x86_64-linux-gnu/libc.so.6:malloc /pid == <PID>/ {
    @alloc_count++;
    @size_hist = hist(arg0);
  }
  uprobe:/usr/lib/x86_64-linux-gnu/libc.so.6:free /pid == <PID> && arg0 != 0/ {
    @free_count++;
  }
  interval:s:5 {
    $net = @alloc_count - @free_count;
    printf("[%ds] malloc=%d free=%d net=%d\n",
           elapsed/1000000000, @alloc_count, @free_count, $net);
    @alloc_count = 0; @free_count = 0;
  }
  END { print(@size_hist); }
' -c 'sleep 30'
```

**Interpret:** If `net` is consistently positive, allocations are outpacing frees — confirmed leak at the allocator level. The histogram shows which size class dominates.

#### 4b. Identify leaking call sites with memleak-bpfcc

```bash
# Top 10 unfreed allocation sites, sampled over 30 seconds, reporting every 5s
sudo memleak-bpfcc -p <PID> -o 30 5 -T 10
```

If the binary is stripped (no symbols), this reports raw offsets. If symbols are available, it reports function names and stack traces.

**Key output to capture:**
- The top call site address/offset
- Its allocation count and total bytes
- Whether counts grow between report intervals (= actively leaking)

#### 4c. Idle vs. active comparison

This is critical for determining the trigger. Run allocation monitoring (4a) during two distinct phases:

1. **5 minutes idle** — process running but no user interaction
2. **5 minutes active** — actively using the application

Compare the `net` allocation rate:
- **Rate constant in both** → timer/render loop leak
- **Rate higher when active** → event-driven leak (input handling, command processing, etc.)
- **Rate only when active** → specific user action triggers it
- **Rate only when idle** → background task / polling loop

#### 4d. Capture leaked allocation content

If you know the leaking size class from 4a/4b, peek at what's being allocated:

```bash
sudo bpftrace -e '
  uprobe:/usr/lib/x86_64-linux-gnu/libc.so.6:malloc /pid == <PID> && arg0 >= <MIN_SIZE> && arg0 <= <MAX_SIZE>/ {
    @pending = 1;
    @sz = arg0;
  }
  uretprobe:/usr/lib/x86_64-linux-gnu/libc.so.6:malloc /pid == <PID> && @pending == 1/ {
    @pending = 0;
    if (retval != 0) {
      @sample_count++;
      if (@sample_count % 100 == 0) {
        printf("alloc #%d size=%d addr=%p\n", @sample_count, @sz, retval);
        printf("  bytes: "); print(buf(retval, 64));
        printf("  string: %s\n", str(retval, 64));
      }
    }
  }
' -c 'sleep 15'
```

**Interpret content:**
- Readable strings → string buffer leak (log messages, command history, etc.)
- Binary with recognizable patterns → struct/object leak (correlate with source code)
- All zeros → freshly allocated, content written later — try sampling with a delay
- Repeated patterns → likely rendering commands or event objects

#### 4e. Track brk/mmap syscalls (heap expansion events)

```bash
sudo bpftrace -e '
  tracepoint:syscalls:sys_enter_brk /pid == <PID>/ {
    printf("brk(%p)\n", args.brk);
    @brk_count++;
  }
  tracepoint:syscalls:sys_enter_mmap /pid == <PID>/ {
    @mmap_count++;
    @mmap_sizes = hist(args.len);
  }
  interval:s:10 {
    printf("[%ds] brk=%d mmap=%d\n", elapsed/1000000000, @brk_count, @mmap_count);
    @brk_count = 0; @mmap_count = 0;
  }
' -c 'sleep 60'
```

Frequent `brk()` calls = heap is being extended. Frequent `mmap()` = large allocations or thread stacks being created.

---

### Phase 5: Correlate and conclude

#### 5a. Build the evidence chain

Assemble findings into a coherent narrative:

1. **What is growing?** (heap, anonymous mmap, GPU, threads, fds?)
2. **How fast?** (KB/s, GB/day — use RSS trend data)
3. **Where in the code?** (call site from memleak, or behavioral fingerprint)
4. **What's being leaked?** (allocation size, content if captured)
5. **When does it happen?** (idle vs active, constant vs bursty)
6. **What can we rule out?** (GPU? fragmentation? user-triggered?)

#### 5b. Search for known issues

Before writing up, check if this is already known:
- Search GitHub issues for the project
- Search for the process name + "memory leak" + OS
- Check changelogs for recent memory-related fixes

#### 5c. Write up findings

For a bug report, lead with:
1. **Behavioral description** — what's happening, reproduction steps, leak rate
2. **Environmental info** — OS, version, hardware
3. **Measured data** — RSS trend, allocation rates
4. **Analysis** — what type of memory, what's ruled out

Put raw technical data (offsets, memory maps, /proc dumps) in a collapsible section — most readers won't need it, but it's there for whoever does.

**Redact before sharing:**
- Home directory paths (`/home/username/`)
- Hostnames, IP addresses
- Socket paths containing usernames
- Process-specific `/proc` paths (use `<PID>` placeholder)

---

## What We Might Miss (Limitations)

Be honest about what each technique can and cannot tell you:

| Technique | Can tell you | Cannot tell you |
|-----------|-------------|-----------------|
| `/proc/PID/status` | Current memory sizes, peak RSS | What's in the memory, why it grew |
| RSS trend monitoring | Growth rate, whether it's stable or growing | What code is responsible |
| `/proc/PID/maps` | Which regions are large, heap vs GPU vs mmap | What's inside those regions |
| `memleak-bpfcc` | Which call sites don't free (with offsets) | Function names if binary is stripped |
| `bpftrace` malloc/free | Allocation rate, size distribution | Which specific allocations leak vs. churn |
| Idle vs active comparison | Whether interaction triggers the leak | Exactly which interaction |
| Allocation content peek | Data type hints (strings, structs) | Full object semantics without symbols |

**Common pitfalls:**
- Measuring only during idle and claiming "not user-triggered" — you must compare both
- Confusing high allocation *rate* with a *leak* — high churn with matching frees is not a leak
- Assuming the largest allocation size class is the leak — it might be the most-churned-but-freed class
- Reporting raw binary offsets as if they're universally meaningful — they're build-specific

## Output

Generate a report containing:
1. Summary of findings (1 paragraph)
2. Evidence table (metrics collected)
3. Leak characterization (type, rate, trigger)
4. Ruled-out causes
5. Recommended action (file bug, restart periodically, upgrade, configure allocator, etc.)

Save to: `~/memleak-report-<process-name>-<date>.md`
