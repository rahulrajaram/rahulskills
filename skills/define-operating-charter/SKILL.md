---
name: define-operating-charter
description: Define and ratify a durable operating charter for a long-running agentic system by separating goals, tenets, environment, actors, authority, delegation, constraints, unknowns, evidence, lifecycle, recovery, success, and stop conditions. Use when the user wants to establish how an orchestrator, supervisor, harness, or worker system should operate before autonomous execution, or asks to define an execution envelope or operating charter.
---

# Define Operating Charter

Turn an ambitious or ambiguous autonomous objective into an explicit charter
that can safely govern execution across sessions. The charter is an authority
and decision model, not merely a project plan.

## Inputs, scope, and interaction

Start with the requested system, existing policy/charter, named decision owners,
known resources, and explicit grants. Bind role names and paths to actual project
actors and mechanisms; a controller role in a draft does not prove a controller
exists. Reuse still-valid decisions and ratification evidence rather than
restarting the interview.

This skill produces a charter or amendment; it does not automatically build or
activate a supervisor, execute campaigns, install capabilities, or change grants.
Relevant investigation and provisional drafting may proceed within existing
permissions before ratification. Finish the concrete draft/options before asking
for a missing owner decision, and hold only dependent policy activation or effects.
Ordinary method choices do not require owner approval.

Do not infer ratification from silence, a speculative model response, a digest,
or a completed template. Defaults are proposals and cannot override the user's
goal or existing authority. Preserve approval records for unchanged decisions;
changed actors, effect scope, bounds, or reserved decisions require the applicable
owner's amendment. Do not require new approval merely for reusing a valid charter.

## Core distinctions

Keep these concepts separate throughout:

- **Goal**: an outcome the system should achieve.
- **Tenet**: a durable principle used when several valid choices remain.
- **Constraint**: a hard boundary the system may not cross.
- **Preference**: a desired default that may yield to a harder concern.
- **Unknown**: a fact whose truth has not been established.
- **Assumption**: a temporary proposition used to make progress.
- **Actor**: a human, process, model, service, or program with a role.
- **Authority**: permission to authorize an effect.
- **Capability**: technical ability to produce an effect.
- **Delegation**: authority one actor may exercise on another's behalf.
- **Evidence**: durable proof that an event, state, or outcome occurred.
- **Gate**: a predicate that must be satisfied before a transition.
- **Stop condition**: a state where execution must cease or return authority.
- **Recovery condition**: evidence required to resume after interruption or
  failure.

Never infer authority from identity, capability, convenience, or prior action.

## Workflow

1. Summarize the proposed operating system and objective in plain language.
2. Inventory confirmed facts separately from interpretations and unknowns.
3. Identify all actors and assign each an explicit role:
   - owner or principal,
   - strategic delegate,
   - supervisor or control-plane program,
   - implementation workers,
   - independent reviewers or verifiers,
   - external providers and finite resources.
4. Define the authority graph. For every material effect, state who may:
   frame it, dispatch it, implement it, verify it, integrate it, remove its
   artifacts, retry it, expand it, or approve an exception.
5. State the goals, supporting goals, non-goals, and measurable success
   criteria.
6. State tenets in priority order. Make conflicts resolvable; avoid slogans
   that do not guide a choice.
7. State hard constraints and invariants before operational preferences.
8. Define the execution envelope:
   - allowed resources, providers, models, tools, paths, and repositories;
   - cost, time, concurrency, retry, repair, epoch, and storage bounds;
   - permitted source, Git, network, deployment, and publication effects;
   - which effects require a fresh human decision.
9. Define the lifecycle as observable states and transitions. Include normal
   progress, review, acceptance, integration, cleanup, blocked states,
   unexpected termination, recovery, and completion.
10. Bind gates to evidence. Self-asserted strings, elapsed time, file age, or
    an actor's confidence are not proof unless the charter explicitly makes
    them authoritative and explains why that is safe.
11. Define residual discretion: decisions a delegate may make without asking,
    decisions it may frame but not authorize, and decisions reserved to the
    owner.
12. Define retrospective behavior: who judges whether work truly remains,
    what evidence supports that judgment, and who may create a new bounded
    objective after a stop.
13. Maintain an ambiguity register. Ask focused questions only for unresolved
    items that would change authority, safety, public behavior, irreversible
    scope, or the execution model. Make conservative assumptions for routine
    implementation detail and label them.
14. Present the prepared draft or changed decisions for explicit ratification
    where not already covered by valid owner approval. After ratification,
    record its version, effective scope, superseded policy, and amendment
    process.

## Long-running autonomy rules

- Prefer a durable programmatic supervisor for repeated mechanics; keep the
  strategic delegate responsible for framing, audit, gates, recovery, and
  discretionary judgment.
- Do not describe a finite campaign as literally endless. Model indefinite
  progress as repeated bounded campaigns with explicit review and relaunch
  decisions.
- Unexpected termination does not grant permission to skip gates. Recover
  from durable evidence, classify uncertain state fail-closed, and resume only
  from a valid transition.
- A terminal result may be correct. The delegate should review the evidence
  and open new scope only when a real improvement opportunity exists.
- Cleanup is a lifecycle transition, not an age-based sweep. Preserve unique
  evidence before destructive removal and prove that accepted work is durably
  integrated or otherwise reachable.
- Fallback resources remain fallbacks. State the exact condition that permits
  their use and preserve evidence of that condition.

## Output contract

Produce a compact but complete charter with these sections:

1. **Charter identity** — name, version, status, effective scope.
2. **Purpose and outcomes** — goals, non-goals, success measures.
3. **Tenets** — ordered decision principles.
4. **Environment** — repositories, programs, providers, resources, and
   relevant current state.
5. **Actors and authority** — role and delegation matrix.
6. **Execution envelope** — allowed and prohibited actions, bounds, fallback
   rules, and human gates.
7. **Lifecycle and evidence** — states, transitions, gates, receipts, cleanup,
   recovery, and reconciliation.
8. **Unknowns and assumptions** — with owner, consequence, and resolution
   trigger.
9. **Stop, resume, and retrospective rules** — including unexpected death and
   new-scope creation.
10. **Risks and mitigations** — especially authority confusion, evidence loss,
    uncontrolled resource growth, and false completion.
11. **Ratification block** — exact decisions being confirmed, effective date,
    superseded rules, and amendment procedure.

Use a table only for mappings such as actor-to-authority or state-to-gate.
Report draft versus ratified status, actual approval provenance, unresolved
decisions, and what was verified. List a missing receipt/controller as missing;
never generate fictional execution evidence to complete the charter.
Use normative language precisely: **must**, **must not**, **may**, and
**should** should have distinct force.

## Ratification discipline

Before execution under a new or amended charter begins, verify existing or new
owner confirmation for every applicable decision that changes:

- the actor with authority over living product behavior;
- permitted model/provider routes and fallback conditions;
- destructive artifact or branch disposition;
- push, deploy, publish, spending, secrets, or external side effects;
- hard campaign bounds or human decision gates;
- the scope of delegated architectural discretion.

Do not turn a draft into effective policy merely because it is detailed. Mark
unratified sections as proposals. Once ratified, preserve the charter as a
versioned durable artifact and require amendments to name what they replace.

When the chartered system will run as a MetaBuilder harness, the ratified
charter is the authoritative input for the harness brief's actors and
authority boundaries; `metabuilder-harness-design` restates rather than
re-decides them.

## Quality check

Before returning, verify that:

- every actor has a bounded role and no capability silently became authority;
- every destructive transition has preservation and verification predicates;
- every fallback has a precise trigger;
- every stop has a recovery or escalation rule;
- indefinite operation is built from bounded, auditable cycles;
- unknowns are not disguised as facts;
- success and "nothing remains" are independently reviewable;
- the ratification block is specific enough to execute without reinterpretation.
