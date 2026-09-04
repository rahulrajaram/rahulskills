# Four Standalone Startup Concepts

## Purpose

These concepts begin with four thin technical layers. Each layer supports a
separate product and company. None depends on combining the four project
families into one platform.

| Product | Origin asset | Initial buyer | First commercial wedge |
|---|---|---|---|
| FleetYield | DeepMetrics | AI infrastructure operator | Find recoverable GPU capacity and prevent avoidable job failures. |
| CodeProof | Cultivar, Yore, Wyrd | Application security leader | Turn a vulnerability advisory into verified exposure and test evidence. |
| Option Foundry | GPTEngage, Contrapuntal, Grilling | Corporate strategy leader | Generate and challenge a portfolio of strategic options. |
| Agent Clearinghouse | GPTQueue | Enterprise platform or security leader | Give cross-runtime agent messages identity, policy, and traceability. |

The names are working labels, not final brands.

## 1. FleetYield

### Product

FleetYield is a shadow optimizer for AI compute fleets.

It observes Linux hosts, accelerators, processes, and workloads. It then finds
waste, failure precursors, and unsafe resource pressure. Operators receive a
ranked set of actions with supporting evidence and estimated operational
effect.

The product does not replace a scheduler or metrics system. It advises the
operators who manage those systems.

### Buyer and problem

The initial buyer is the head of AI infrastructure at a GPU cloud, enterprise
AI platform, or high-performance computing environment.

The buyer needs to answer questions such as:

- Which jobs are overprovisioned?
- Which nodes should be diagnosed or quarantined?
- Where is usable accelerator capacity stranded?
- Which resource constraint caused a failed or slow job?
- Would resizing or rescheduling improve throughput?

The product should tie every recommendation to one economic measure. Useful
measures include recovered accelerator-hours, avoided failed-job hours, and
diagnosis time.

### Product workflow

```text
Collect fleet metrics → Detect an opportunity or risk → Explain the cause
                      → Recommend an action → Observe the result
```

DeepMetrics supplies the low-overhead host and process evidence. Standard
sources such as NVIDIA DCGM, Prometheus, Kubernetes, or Slurm can add workload
and accelerator context.

NVIDIA DCGM already provides GPU telemetry and diagnostics. NVIDIA Run:ai
already manages workload scheduling and GPU allocation. FleetYield should
interpret signals across those systems and measure the result of each
recommendation. See
[NVIDIA DCGM](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)
and [NVIDIA Run:ai](https://docs.nvidia.com/run-ai/index.html).

### Six-week wedge

Run FleetYield in read-only mode on one cluster.

1. Ingest DeepMetrics and existing accelerator metrics.
2. Identify underused allocations and recurring job failures.
3. Produce a daily ranked opportunity report.
4. Estimate the capacity or failure cost attached to each finding.
5. Record which recommendations operators accept.
6. Compare expected and observed results.

### Proprietary learning loop

The defensible dataset links workload signatures to operator actions and
measured outcomes. Over time, the product learns which recommendations work
for each workload, scheduler, and hardware topology.

### Cofounder

Find a former GPU-cloud, HPC, or AI-infrastructure operator. The cofounder must
secure production telemetry and design partners. Access matters more than
adding another generalist engineer.

### Main risk

The product may look like another observability dashboard. Avoid this by
selling measured capacity recovery and failure prevention, not metric volume.

## 2. CodeProof

### Product

CodeProof is a vulnerability-to-verification engine for large code estates.

An operator supplies a vulnerability advisory, dependency change, or planned
migration. CodeProof identifies the affected systems, determines likely
reachability, finds owners, and produces a verification plan. The final output
is an evidence packet, not a list of search results.

### Buyer and problem

The initial buyer is an application security or platform engineering leader
responsible for many repositories and services.

The buyer needs to know:

- Which repositories contain the affected component?
- Which deployed systems can reach the vulnerable path?
- Which teams own those systems?
- What will break after an upgrade or patch?
- Which integration tests would demonstrate a safe remediation?
- Which findings can be dismissed with evidence?

### Product workflow

```text
Ingest advisory or change → Map affected code and documentation
                          → Rank reachable exposure → Design verification
                          → Track remediation evidence
```

Cultivar supplies structural code indexes and call relationships. Yore
retrieves relevant documentation and repository context. Wyrd reranks and
deduplicates large result sets.

### Six-week wedge

Start with one vulnerability workflow and two supported languages.

1. Connect to a GitHub organization or local repository estate.
2. Accept a CVE or security advisory as input.
3. Find the affected dependencies, call paths, and owners.
4. Separate direct evidence from inferred exposure.
5. Generate an integration-test plan or reproducer.
6. Export a remediation packet for the security ticket.

### Proprietary learning loop

Track which findings teams confirm, dismiss, patch, or test. Link each finding
to later regressions and escaped incidents. This outcome history improves
reachability ranking, ownership resolution, and test recommendations.

### Market boundary

Sourcegraph already provides enterprise code search, code insights, and
agentic changes across large repository sets. CodeProof should compete on
exposure evidence and verification, not generic code understanding. See
[Sourcegraph](https://sourcegraph.com/docs/getting-started) and
[Agentic Batch Changes](https://sourcegraph.com/docs/agentic-batch-changes).

### Cofounder

Find an application security, software supply-chain, or enterprise developer
tools leader. The cofounder should understand security budgets and have access
to large engineering organizations.

### Main risk

CVE detection is crowded. A useful wedge must prove practical reachability,
remediation impact, and test coverage better than existing scanners.

## 3. Option Foundry

### Product

Option Foundry creates and tests strategic options for enterprises.

A company supplies its capabilities, constraints, customer evidence, and
strategic question. The product generates distinct paths, challenges each
path, and returns a portfolio of options with assumptions and experiments.

This is a portfolio system, not a brainstorming chatbot.

### Buyer and problem

The initial buyer is a corporate strategy, innovation, R&D portfolio, or
internal venture leader.

The buyer needs to:

- Find opportunities outside the current planning consensus.
- Compare options built from different assumptions.
- Expose weak evidence before committing capital.
- Turn speculative ideas into small tests.
- Preserve rejected options and revisit them when conditions change.
- Learn which teams and models make calibrated forecasts.

### Product workflow

```text
Frame the decision → Generate divergent options → Debate and grill each option
                   → Design falsification tests → Track outcomes
```

GPTEngage generates a broad option tree. Contrapuntal compares competing
positions. Grilling exposes assumptions, dependencies, and missing evidence.

### Six-week wedge

Deliver a service-supported strategy sprint.

1. Select one live portfolio or market-entry question.
2. Ingest a bounded set of company materials and constraints.
3. Generate a diverse option set.
4. Run adversarial review against each option.
5. Produce a ranked portfolio with evidence gaps and stop criteria.
6. Convert the leading options into small experiments.

### Proprietary learning loop

Track each option from generation through selection, experiment, funding, and
outcome. The resulting dataset can reveal which assumptions, methods, and
participants produce useful options for a specific enterprise.

### Cofounder

Find a former corporate strategy or innovation leader with executive access.
A strategy consultancy partner could also provide distribution and a
repeatable delivery process.

### Main risk

Idea generation is easy to copy and difficult to budget. Sell better portfolio
decisions and faster falsification. Do not sell the number of ideas produced.

## 4. Agent Clearinghouse

### Product

Agent Clearinghouse is an identity-bound message broker for enterprise agents.

It gives every cross-agent handoff a verified sender, delegated scope, trace
parent, expiry, and policy decision. It also records delivery, failure,
approval, and downstream action.

The product works across agent runtimes. It does not require customers to
replace their orchestration frameworks.

### Buyer and problem

The initial buyer is an enterprise platform or security team running several
agents across different frameworks and business systems.

The buyer needs to answer:

- Which agent requested this action?
- On whose authority did it act?
- What context and permissions crossed the handoff?
- Which agents and tools participated in the result?
- Can the organization revoke an agent or delegated capability?
- Can auditors reconstruct the full chain of action?

### Product workflow

```text
Register agent → Issue or map workload identity → Send signed envelope
               → Enforce policy → Propagate trace → Record outcome
```

GPTQueue supplies bounded inboxes, discovery, delivery, tracing, and
cross-agent communication. Enterprise identity should remain authoritative.
The clearinghouse maps that identity into messages and policy decisions.

### Six-week wedge

Build an agent mailroom for two or three common runtimes.

1. Register agents and map them to workload identities.
2. Wrap each message in a signed, expiring envelope.
3. Propagate one trace across agent and tool boundaries.
4. Block an unauthorized or over-scoped handoff.
5. Display the complete interaction and approval chain.
6. Export an audit receipt for one business action.

### Proprietary learning loop

The product learns from message topology, policy decisions, failed handoffs,
revocations, and incident investigations. That history can improve default
policies and expose unsafe communication patterns.

### Market boundary

NIST is examining agent identity, authorization, auditing, and
non-repudiation. This provides a useful design and buyer reference. See the
[NIST concept paper](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd).

### Cofounder

Find an identity, access management, or product security leader. The
cofounder should understand enterprise trust architecture and security sales.

### Main risk

Agent standards and platform controls are changing quickly. Stay
framework-neutral and focus on cross-runtime trust, communication, and audit.

## Portfolio comparison

| Product | Strongest advantage | Hardest dependency | Primary risk |
|---|---|---|---|
| FleetYield | Direct link to expensive compute utilization | Production cluster telemetry | Becoming another dashboard |
| CodeProof | Deterministic code and evidence pipeline | Large private code estates | Crowded security market |
| Option Foundry | Structured divergence and adversarial review | Executive distribution | Being treated as a generic AI feature |
| Agent Clearinghouse | Cross-runtime communication and traceability | Enterprise identity integration | Standards and platform competition |

FleetYield has the largest operational upside and the hardest data-access
problem. CodeProof offers the clearest technical demonstration. Option Foundry
depends most on the cofounder's distribution. Agent Clearinghouse fits an
emerging security category but faces the greatest standards risk.
