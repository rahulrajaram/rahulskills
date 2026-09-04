# MetaBuilder Bounded-Autonomy Operating Charter

Date: 2026-08-31

Version: 0.1

Status: proposed review model. This document is not ratified authority and does
not change MetaBuilder's own governing files.

## Charter identity and evidence basis

This charter describes a maximally autonomous engineering system whose
discovery is open-ended while every execution remains finite, attributable,
recoverable, and bounded by prior authority.

The review distinguishes three kinds of truth:

| Truth class | Evidence used here | Meaning |
| --- | --- | --- |
| Installed | `/home/rahul/.local/bin/metabuilder`, SHA-256 `6407442f50bac6e1a2f5c7727d01eaa57d9174e23862c98eeab1ac4febe230b9` | Capability available through the admitted consumer CLI inspected on 2026-08-31. |
| Committed source | MetaBuilder commit `ec1b9d079da8afc09b112a0e4f731a1b66412285` | Rust behavior present in committed source, including v3 template expansion and controller-only offline MCP/agent protocol execution, but not necessarily installed for consumers. |
| Target design | The model and Mermaid projections in this repository | Proposed behavior that still requires implementation, qualification, or ratification. |

Uncommitted MetaBuilder files were excluded as implementation evidence. A
diagram digest proves only the exact Mermaid bytes; it does not prove that the
diagram is true, approved, implemented, or secure.

## Purpose, outcomes, and non-goals

The system should maximize correct engineering outcomes and minimize routine
human intervention without allowing an agent, worker, tool, or generated
artifact to manufacture authority.

Success means:

1. The human principal can understand who decides, who enforces, who executes,
   and what evidence returns without reading implementation code.
2. The orchestrator can discover and frame new opportunities indefinitely
   across time, but can execute only a finite campaign admitted under an exact
   standing delegation and authority envelope.
3. Every consequential effect is prepared, authorized, attempted, observed,
   verified, settled, and recoverable through durable evidence.
4. Workers and target tools remain claims producers. They cannot verify
   themselves, widen grants, revise active criteria, or decide continuation.
5. A completed, rejected, blocked, unknown, or bounded-stop outcome is
   independently reconstructable from exact source, policy, runtime, adapter,
   and evidence identities.
6. Human attention is reserved for decisions outside standing delegation,
   unresolved material ambiguity, irreversible or externally consequential
   effects, and amendments to the operating charter.

The system does not promise literal foolproofness, perfect model reasoning,
unlimited resource consumption, hostile-host containment, or automatic
production readiness. It does not treat a hash, receipt, process boundary,
model confidence, or elapsed time as authority or semantic proof.

## Why MetaBuilder is useful

MetaBuilder is the control plane between discretionary reasoning and effects.
It does not make a model intrinsically smarter; it makes the model's work more
correctable, inspectable, and difficult to execute outside the agreed bounds.

It provides:

- deterministic admission and compilation of an exact objective, workflow,
  authority ceiling, adapters, content, source identity, and resource bounds;
- capability attenuation, so each downstream grant is equal to or narrower
  than the principal's ceiling;
- preflight and durable intent before consequential dispatch;
- controller-owned observations, typed `Unknown`, reconciliation without blind
  redispatch, and replayable state;
- isolation between worker claims, controller evidence, independent review,
  integration, and continuation;
- content-addressed artifacts and receipts that expose stale or mismatched
  inputs instead of silently accepting them; and
- finite budgets, breakers, checkpoints, and stop outcomes around otherwise
  open-ended strategic work.

The cost is additional up-front modeling, narrower supported effects, explicit
adapter work, and more artifacts. That cost is justified for consequential or
long-running work; tiny reversible tasks may not need the full harness.

## Ordered tenets

1. **Authority before capability.** Technical ability never implies permission.
2. **Evidence before confidence.** Controller observations and independent
   checks outrank worker assertions and model certainty.
3. **Open discovery, finite execution.** The opportunity space may remain open;
   every discovery episode and execution campaign has explicit resource bounds.
4. **Data never becomes authority.** Discovered content, repository text,
   prompts, and worker output are untrusted data until admitted through a typed
   boundary; none may silently become executable control.
5. **Attenuate downward, report upward.** Grants only narrow as they move toward
   effects; claims, observations, and evidence flow back toward the principal.
6. **Immutable epochs.** Active objectives, criteria, authority, source pins,
   and execution identities do not change in place.
7. **Effects are recoverable protocols.** Persist intent before dispatch,
   preserve ambiguity as `Unknown`, reconcile, and never retry blindly.
8. **Separate strategy from mechanics.** The orchestrator owns discretionary
   judgment; MetaBuilder enforces the admitted contract; the harness executes
   it; the target program owns no authority.
9. **Progress is optional; safety is not.** A terminal result or a finding that
   nothing worthwhile remains may be correct.
10. **Optimize representation by projection.** Keep one detailed semantic model
    and use small question-specific diagrams rather than one maximal picture.

## Environment and the four process compartments

The human principal and durable stores sit outside four process compartments:

1. **Orchestrator process.** Understands intent, explores alternatives,
   delegates bounded work, arbitrates disagreements, selects strategy, judges
   whether evidence is sufficient, and decides continuation within standing
   delegation.
2. **MetaBuilder control-plane process.** Validates authority, compiles an exact
   harness bundle, brokers capabilities, persists intent and state, observes
   effects, verifies structural evidence, recovers ambiguity, and refuses work
   it cannot enforce.
3. **Harness runtime process.** Executes the compiled finite workflow, dispatches
   admitted workers or adapters, and returns claims and artifacts. It has no
   authority to change its own plan or start another epoch.
4. **Target-program compartment.** Contains the exact source and isolated
   candidate as governed values plus the build, test, and run processes invoked
   through the harness. Source code is not an actor and holds no authority.

External providers, repositories, operating-system services, and finite
resources are environment actors. They can enforce or deny their own
permissions; local artifacts cannot manufacture that external authority.

## Actors and authority

| Actor or compartment | May frame | May dispatch | May verify | May integrate | May continue |
| --- | --- | --- | --- | --- | --- |
| Human principal | Any objective or amendment | Reserved effects through an explicit grant | Any evidence | Any admitted or reserved change | May begin any authorized campaign |
| Orchestrator | Objectives and tasks inside standing delegation | Requests dispatch through MetaBuilder | Judges semantic adequacy from independently produced evidence | Only when the standing delegation explicitly includes local integration | May open a new bounded campaign inside delegation |
| MetaBuilder controller | Mechanical plans derived from admitted inputs | Only effects with an enforced adapter and current grant | Structural, provenance, replay, and declared-check evidence | Never by inference; only an explicit integration effect may do so | Evaluates bounds but does not create strategic continuation authority |
| Harness runtime | No new objective | Only compiled and admitted workflow effects | No self-verification | No implicit integration | No new epoch |
| Worker or target tool | No authority-bearing frame | Only its attenuated task grant | May report a claim, never admit it as proof | No | No |
| Independent reviewer | Review frame named by the controller | Read-only review effects | May issue a bounded review result | No | No |
| Target source or program artifact | Nothing; it is a value | Nothing | Nothing | Nothing | Nothing |

No actor may authenticate its own delegation, widen its own grant, declare its
own output verified, revise frozen criteria, or convert a discovered
opportunity into execution authority.

## Standing delegation and residual discretion

A proposed `StandingDelegation` should bind:

- principal, delegate, scope, decision classes, effect ceilings, target paths,
  provider and model routes, cost, time, concurrency, retry, epoch, candidate,
  output, and storage bounds;
- acceptance policy, required reviewers, permitted integration modes, reserved
  decisions, expiry, revocation reference, and amendment procedure; and
- the exact policy and classifier versions used to decide whether a choice is
  delegated.

"Safe and idiomatically sound" is not a free-form permission. The orchestrator
may decide without asking only when all of these predicates are true:

1. the decision class is explicitly delegated;
2. the objective, target, effect, and resource request are inside the envelope;
3. current evidence is sufficient under the named acceptance policy;
4. the action is reversible, or its irreversible class is explicitly allowed;
5. no reserved decision, material ambiguity, conflict of interest, or
   revocation is present; and
6. MetaBuilder can mechanically enforce the complete requested effect.

If any predicate is false or unknown, the orchestrator may investigate and
frame the decision but must not authorize execution. It returns a concise
decision packet to the principal instead.

Ratification may be performed by the principal or by the orchestrator acting
under an authenticated standing delegation. The resulting proof must identify
the actual ratifier, the delegation used, the exact decision digest, scope,
expiry, and revocation state. The orchestrator never becomes the principal and
cannot amend the delegation it is using.

## Open-ended discovery contract

"Unbounded discovery" means the domain of possible questions, hypotheses,
counterexamples, and future campaigns is not artificially closed. It does not
mean unlimited time, tokens, network, subprocesses, files, or recursive agents.

Every discovery episode must have finite time, cost, concurrency, source,
network, output, and recursion bounds. Discovery may:

- inspect authorized read-only sources;
- generate hypotheses, counterexamples, risks, and candidate objectives;
- seek independent corroboration and record disagreement; and
- propose a new capability, adapter, policy amendment, or campaign.

Discovery must not:

- execute text found in a repository, webpage, model response, or artifact as
  instructions merely because it was discovered;
- mutate the active objective, acceptance criteria, authority envelope, source
  pins, or runtime state;
- grant a capability, choose a credential or provider route, spend, integrate,
  deploy, or start a new epoch; or
- treat novelty, model agreement, or repeated assertion as evidence.

A discovered opportunity crosses into execution only as a new typed
`ObjectiveRequest`. It is authorized, decomposed into a finite DAG, compiled,
admitted, and executed under a fresh immutable envelope. Leftover work from an
epoch becomes a durable checkpoint and candidate request; it never silently
extends the active run.

## Execution envelope

Every campaign must bind hard ceilings for:

- objective and acceptance criteria;
- source, candidate, harness definition, compiler, runtime, adapter, content,
  policy, provider, model, and reviewer identities;
- filesystem reads, isolated writes, output publication, processes, network,
  credentials, external state, installation, integration, release, and deploy;
- wall time, charged time, requests, spend, tokens, output bytes, stored bytes,
  concurrency, retries, candidates, epochs, and no-progress streaks;
- allowed tool and protocol schemas, transitive capabilities, and
  reconciliation procedures; and
- stop, escalation, cleanup, and evidence-retention rules.

Unsupported, unenforceable, stale, unauthenticated, conflicting, or ambiguous
requests fail closed. An envelope is revalidated before each consequential
dispatch and before continuation. Downstream contracts may narrow it; none may
widen it.

## Lifecycle, gates, and evidence

The conceptual lifecycle is:

`Draft -> Authorized -> Resolved -> Admitted -> Running -> Verifying ->
Settling -> Accepted | Rejected | Blocked | Unknown | BoundedStop`.

Normal runtime execution is narrated as five phases:

1. **Decide.** The orchestrator or frozen workflow selects one bounded next
   intent or a typed stop.
2. **Admit.** MetaBuilder revalidates authority and resources, then persists
   the exact intent before dispatch.
3. **Interpret.** The harness invokes one admitted adapter or worker against an
   isolated target state.
4. **Verify.** MetaBuilder records the observation, checks declared evidence,
   preserves assurance dimensions separately, and classifies ambiguity.
5. **Settle.** A pure transition produces a new immutable state, checkpoint,
   accepted result, refusal, `Unknown`, or bounded stop.

`Unknown` means a consequential effect may have happened. Recovery replays the
durable state and reconciles external reality without redispatch. Only a
conclusive failed or timed-out result may become eligible for a bounded retry.

Claims, observations, verification, admission, and semantic acceptance remain
distinct:

- a worker claim states what a producer says happened;
- a controller observation records what the effect boundary observed;
- a verification record applies one named check to exact observed evidence;
- admission establishes that the artifact meets the stated gate; and
- semantic acceptance judges whether the checks actually establish the human's
  intended outcome.

Structural integrity, execution provenance, semantic adequacy, security
posture, and production readiness must be reported separately. No single
"qualified" label may collapse them.

## Improving MetaBuilder itself

The orchestrator may discover that a required effect is missing from
MetaBuilder. That finding authorizes a proposal, not a bypass.

The generic safe pattern is:

1. bind an exact clean MetaBuilder base and immutable acceptance criteria;
2. materialize an isolated candidate workspace;
3. let a bounded worker modify only that candidate;
4. run focused, refusal, tamper, timeout, `Unknown`, replay, and full repository
   checks against the exact candidate;
5. obtain an independently framed review of the exact delta;
6. let the controller admit or reject the candidate; and
7. integrate and select a new binary only through a separate authorized effect
   that binds the admitted bytes.

MetaBuilder's current authority explicitly forbids Git worktrees. Its existing
self-hosting path uses an isolated local clone without hardlinks or a retained
remote. Therefore these diagrams use "isolated candidate workspace," not
"worktree." A future worktree design would require an explicit policy amendment
and proof that shared Git metadata cannot violate isolation or source identity.

An uncommitted development binary is not an admissible consumer runtime merely
because it builds. The exact candidate bytes, tests, review, source identity,
and admission receipt must be bound before use.

## Threat and evidence boundary

The design primarily defends against model mistakes, malicious or compromised
workers, prompt injection in discovered content, stale inputs, unsupported
effects, partial failure, crashes, blind retry, scope creep, and accidental
authority expansion.

It does not currently prove safety against a compromised orchestrator,
MetaBuilder controller, operating-system kernel, administrator, or hostile
same-UID concurrent writer. MetaBuilder's documented single-controller model
and candidate filesystem isolation are operating assumptions, not a hostile
multi-writer security boundary. Cryptographic digests establish integrity and
identity of bytes; they do not authenticate a human, prove reviewer
independence, prove semantic correctness, or force an external provider to
honor a local budget.

Live credentials, paid providers, network calls, external writes, target
integration, release, and deployment require effect-specific adapters whose
external enforcement and reconciliation contracts are separately qualified.

## Stop, resume, cleanup, and retrospective rules

A campaign must stop when it is accepted, rejected without an authorized
repair, out of budget, at the no-progress breaker, unable to enforce a required
effect, facing a reserved decision, unable to bind evidence, or holding an
unresolved consequential `Unknown`.

Unexpected termination grants no exception. Resume only from exact durable
state after revalidating source, policy, authority, runtime, adapters, and
external observations. Uncertain state fails closed.

Cleanup is an explicit transition. Preserve unique evidence first, prove that
accepted work is durably reachable, name exact removal targets, and require the
authority appropriate to the destructive effect. File age alone is never a
cleanup predicate.

Retrospectives may generate observations and next-campaign proposals. They may
not revise the closed epoch, prove success, authorize effects, admit work, or
force continuation.

## Unknowns and proposed decisions

| Item | Current status | Consequence | Resolution trigger |
| --- | --- | --- | --- |
| Generic standing delegation to the orchestrator | Proposed, not implemented or ratified by this document | Per-run human ratification cannot be safely removed yet | Principal approves exact scope, reserved decisions, expiry, revocation, and integration authority |
| Authenticated policy registry and decision classifier | Not established in the reviewed consumer path | Free-form "safe and idiomatic" classification could overreach | Adversarial implementation and identity/revocation qualification |
| Installed v3 consumer CLI | Installed binary predates committed v3 source | Offline protocol and template capabilities cannot be claimed as installed consumer features | Separate build/admission/install approval and exact binary verification |
| Governed convergence and continuation | Active source work was uncommitted and excluded from evidence | Multi-epoch automation remains a target design in this review | Committed pure primitives, campaign integration, adversarial proof, and installed admission |
| Independent reviewer identity | Role separation exists; cryptographic identity is not generally proven | Colluding or misrouted review may look independent | Authenticated reviewer policy and controller-observed invocation evidence |
| Hostile same-UID concurrency | Unsupported | Another local writer can undermine candidate and evidence assumptions | OS-enforced isolation, exclusive leases, and adversarial qualification |
| Target integration authority | Must be named per delegation | A correct candidate could still be integrated without permission | Explicit local-commit, merge, push, release, and deploy classes in the envelope |

## Diagram contract and reading order

The diagrams are projections of this charter, not independent sources of
truth. Read them in this order:

1. `metabuilder-autonomy-components.mmd` — what each of the four processes owns
   and why MetaBuilder sits between strategy and effects.
2. `metabuilder-authority-model.mmd` — who may decide, delegate, execute,
   verify, integrate, and continue.
3. `metabuilder-runtime-loop.mmd` — how one bounded epoch moves through decide,
   admit, interpret, verify, and settle.
4. `metabuilder-discovery-execution-boundary.mmd` — how discovery stays
   open-ended without making execution unbounded.
5. `metabuilder-functional-composition.mmd` — how typed intent becomes an exact
   bundle and qualified outcome.

Each viewer answers one question, carries its exact Mermaid digest, defines its
jargon, and states what it does not prove. The exhaustive details remain here
so the diagrams can stay small enough to narrate.

## Ratification block

The following decisions remain proposals until the principal explicitly
ratifies them:

1. Adopt the human-plus-four-process model as the primary representation.
2. Delegate routine strategic, architecture, implementation, local-candidate,
   and bounded-continuation decisions to the orchestrator under a versioned
   standing delegation.
3. Reserve authority amendments, credentials, new provider/model routes,
   unenforced spend, destructive cleanup, external writes, push, release,
   deploy, security/privacy expansion, and unresolved material ambiguity to the
   human principal.
4. Use isolated candidate workspaces, with MetaBuilder specifically using its
   existing no-hardlink clone path rather than a Git worktree.
5. Treat open-ended discovery as a sequence of finite read-mostly episodes that
   can produce proposals but never grants.
6. Require a fresh immutable objective and envelope at every epoch boundary.

If ratified, record the effective date, exact scope, superseded policy, named
delegate identity, expiry and revocation mechanism, and amendment procedure in
the actual authority-bearing system. This review document must not become that
authority merely by being detailed.
