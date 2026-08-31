# MetaBuilder Autonomy Functional Model

Date: 2026-08-30

Status: proposed semantic model for review. It does not describe a currently
implemented callable-skill ABI.

## Purpose

This model separates five constructs that the mixed architectural overview
places in similar boxes:

1. **Actors** own authority, submit requests, execute work, or verify results.
2. **Artifacts** are immutable typed values passed between functions.
3. **Callable phases** transform typed inputs into claims or results.
4. **Runtime components** interpret effects and persist controller observations.
5. **Rules** constrain composition, execution, evidence, recovery, and stopping.

The three focused Mermaid projections are views of this model:

- `metabuilder-functional-composition.mmd` shows functions and typed values.
- `metabuilder-authority-model.mmd` shows actors and authority-bearing artifacts.
- `metabuilder-runtime-loop.mmd` shows pure transitions and effect interpretation.

`metabuilder-autonomy-components.mmd` remains a mixed architectural inventory.
It is not the primary explanation of function composition.

## Visual type system

Shape communicates construct kind. Border color communicates implementation
status. Border weight communicates architectural importance.

| Construct | Mermaid shape | Meaning |
| --- | --- | --- |
| Actor | Stadium | Person, agent, controller, operator, approver, or verifier |
| Callable phase | Rectangle | Function-like transformation with a declared contract |
| Artifact | Parallelogram in the functional view; cylinder in the authority and runtime views | Immutable typed value, claim, observation, lock, or record |
| Runtime component | Subroutine | Compiler, broker, runner, interpreter, or durable store |
| Decision | Diamond | Pure branch over an explicit value |
| Rule | Yellow note | Standing invariant or evidence boundary |

Status colors:

- Blue: established or currently supported.
- Green: missing or proposed.
- Orange: current but requiring material improvement.
- Red: refused, deprecated, redundant, or consolidation candidate.

## Actors

~~~haskell
type ActorId = OpaqueId
type PrincipalId = ActorId
type RequesterId = ActorId
type OperatorId = ActorId
type WorkerId = ActorId
type VerifierId = ActorId
~~~

The requester sends an objective. The principal owns the authority ceiling and
the meaning of success. They are often the same human, but need not be.

~~~haskell
type ObjectiveRequest =
  { submittedBy     : RequesterId
  , principal       : PrincipalId
  , objective       : BoundedObjective
  , delegationProof : Optional DelegationProof
  }
~~~

If `submittedBy /= principal`, admission requires a valid delegation proof.
An agent cannot appoint itself principal merely by submitting the request.

## Typed values

~~~haskell
type BoundedObjective =
  { desiredOutcome : OutcomeDefinition
  , constraints    : Set Constraint
  , acceptance     : Set AcceptanceCheck
  , stopRules      : Set StopRule
  , resourceBounds : ResourceBounds
  }

type PreparedObjective =
  { thesis    : ProductThesis
  , decisions : DecisionRecord
  , plan      : ExecutionDag
  , authority : AuthorityEnvelopeRef
  }

type AuthorityEnvelopeRef =
  { principal       : PrincipalId
  , allowedEffects  : Set EffectGrant
  , resourceCeiling : ResourceBounds
  , expiresAt       : Optional Instant
  , revocationRef   : RevocationRef
  , ratification    : RatificationProof
  }
~~~

The authority envelope is an input to composition. A contract, recipe, worker,
or runtime component may attenuate it, but may never widen it.

## Callable skill phases

`SKILL.md` remains human guidance. A phase becomes callable only when it has
both a contract and an execution binding.

~~~haskell
type SkillContract input output =
  { phaseId            : PhaseId
  , semanticVersion    : Version
  , inputType          : TypeId
  , outputType         : TypeId
  , requiredOperations : Set ScopedOperation
  , resourceBounds     : ResourceBounds
  , failureTypes       : Set FailureType
  , recoveryPolicy     : RecoveryPolicy
  , normativeGuidance  : Set GuidanceReference
  }

type ExecutionBinding input output =
  input -> Task (Result SkillFailure (Claim output))

type CallablePhase input output =
  { contract : SkillContract input output
  , binding  : ExecutionBinding input output
  }
~~~

A scoped operation carries its own recovery semantics:

~~~haskell
type ScopedOperation =
  { kind        : EffectKind
  , target      : EffectTarget
  , mode        : EffectMode
  , bounds      : OperationBounds
  , adapter     : AdapterId
  , idempotency : IdempotencyRule
  , reconcile   : ReconciliationProcedure
  }
~~~

## Preparation pipeline

These names correspond to existing skills, but the callable bindings are
proposed.

~~~haskell
prepareObjective
  : ObjectiveRequest
  -> Task (Result PreparationError PreparedObjective)

prepareObjective request = do
  authorized <- authorizeRequest request

  thesis    <- frameGoalsAndConstraints authorized
  decisions <- grillMaterialUnknowns thesis
  ratified  <- principalRatify request.principal decisions
  plan      <- decomposeObjective thesis ratified
  authority <- deriveAttenuatedEnvelope
    request.principal
    authorized
    ratified

  pure PreparedObjective
    { thesis
    , decisions
    , plan
    , authority
    }
~~~

`prepareObjective` is a composition boundary, not a single callable phase.
Its internal chain is exactly:

ObjectiveRequest -> authorizeRequest -> frame-goals-constraints ->
ProductThesis -> grilling -> DecisionRecord -> principalRatify ->
objective-to-dag-decomposition -> ExecutionDag -> deriveAttenuatedEnvelope ->
PreparedObjective.

Each skill phase returns a claim; the controller verifies it independently
before the value flows on as evidence. Ratification is a human authority gate:
the principal, not a skill, accepts or refuses the decisions record. The
attenuated envelope is derived from the ratified ceiling and may never widen it.

The same chain can be sketched as a left-to-right pipeline over typed values:

~~~haskell
prepareObjective
  =   authorizeRequest
  >>> frameGoalsAndConstraints
  >>> grillMaterialUnknowns
  >>> principalRatify
  >>> decomposeObjective
  >>> deriveAttenuatedEnvelope

-- equivalently, right to left:

prepareObjective
  =   deriveAttenuatedEnvelope
  .   decomposeObjective
  .   principalRatify
  .   grillMaterialUnknowns
  .   frameGoalsAndConstraints
  .   authorizeRequest

-- (conceptual phase order; see the qualifications below)
~~~

This sketch is a conceptual phase order, not a type- or dataflow-equivalent
formulation of the `do` block above. It is idealized in five ways:

1. Each skill edge is really `execute -> Claim -> controllerVerify -> verified
   value`; claims never flow directly into the next phase's input.
2. The dataflow has fan-out: `authorized`, `thesis`, and `ratified` are each
   consumed more than once, so the faithful form is a small dependency graph,
   not a unary chain. `decomposeObjective` consumes the thesis together with
   the ratified decisions.
3. Each arrow is really Kleisli composition `>=>` — over a composed effect such
   as `ExceptT PreparationError Task`, since raw `Task (Result e a)` alone does
   not provide short-circuiting `do` notation — and stage failures inject into
   the common `PreparationError`.
4. `principalRatify` and `deriveAttenuatedEnvelope` are not free functions of
   the data alone: both are anchored to `request.principal`, exposed as an
   explicit argument or reader environment rather than silent closure.
5. The gate is an effectful authority interaction, not a pure function: refusal,
   timeout, identity verification, and revocation are explicit outcomes.

## Composition and compilation

~~~haskell
type RecipeSpec =
  { requiredRoles        : Set RoleRequirement
  , alternatives         : Map RoleId (NonEmpty PhaseId)
  , multiplicity         : Map RoleId Cardinality
  , completenessChecks   : Set CompletenessPredicate
  , runtimeProfile       : RuntimeProfileId
  }

type CompositionInputs =
  { recipe    : RecipeSpec
  , catalog   : ContractCatalog
  , authority : AuthorityEnvelopeRef
  }

resolve
  : CompositionInputs
  -> Result CompositionError ResolvedGraph

resolve inputs =
  inputs.recipe
    |> bindRequiredRoles inputs.catalog
    >>= checkNominalPortTypes
    >>= checkProducerConsumerVariance
    >>= checkExecutionBindingsExist
    >>= checkOperationsWithin inputs.authority
    >>= checkResourceBoundsEnforceable
    >>= checkRecoveryCompleteness
~~~

Digests identify exact artifacts. They do not define compatibility.

~~~haskell
createResolutionLock
  : ResolvedGraph
  -> ResolutionLock

compileHarness
  : ResolutionLock
  -> Result CompileError HarnessBundle

buildHarness inputs = do
  graph  <- resolve inputs
  lock   <- pure (createResolutionLock graph)
  bundle <- compileHarness lock
  admitBundle bundle lock
~~~

`update-module` performs a new build-time resolution and produces a new module.
It does not mutate an active run. Live revision is a separate operation that
requires quiescence, preserved historical pins, and fresh qualification.

## Claims, observations, and evidence

A worker or adapter produces a claim. The controller records observations.
Only a verifier operating over observations produces a verification record.

~~~haskell
type Claim value =
  { producer : WorkerId
  , value    : value
  , context  : ClaimContext
  }

type Observation =
  { intent       : IntentId
  , adapter      : AdapterId
  , rawOutcome   : RawOutcome
  , observedAt   : Instant
  }

type VerificationRecord value =
  { subjectDigest   : Digest
  , checkIdentity   : CheckId
  , adapterIdentity : AdapterId
  , observationRef  : ObservationId
  , result          : Result VerificationFailure value
  , verifier        : VerifierId
  }
~~~

A skill may declare evidence requirements. It may not declare its own output
to be controller evidence.

## Runtime reducer and effect interpreter

The controller separates pure planning from effect interpretation:

~~~haskell
nextIntent
  : RunState
  -> NextStep

transition
  : RunState
  -> RunEvent
  -> Result StopReason RunState

interpret
  : AuthorityEnvelopeRef
  -> Intent
  -> Task Observation
~~~

~~~haskell
runLoop bundle authority state =
  case nextIntent state of
    Stop reason ->
      Finished reason state

    Execute intent -> do
      admitted    <- brokerAdmit authority intent
      observation <- interpret authority admitted
      event       <- verifyAndClassify observation

      case transition state event of
        Error reason ->
          Finished reason state

        Ok nextState ->
          runLoop bundle authority nextState
~~~

`EffectOutcomeUnknown` means a consequential effect may have happened. The
controller reconciles it from persisted intent and observation state. It never
blindly redispatches the effect.

## Composition-conformance kernel

The smallest credible first slice uses two deterministic bindings:

~~~haskell
produceTaskSpec
  : BoundedObjective
  -> Result ProduceError TaskSpec

validateTaskSpec
  : TaskSpec
  -> Result ValidationError ValidationReport
~~~

This slice proves resolution, typed transfer, denial, timeout, legal recovery,
identity invalidation, reconciliation, and replay. It does not execute
`autonomy-loop` or `autonomous-execution-contract` semantics.

## Complete bounded autonomous harness

The first milestone that merits that name must support:

~~~haskell
autonomousEngineeringLoop
  : AuthorizedObjective
  -> HarnessBundle
  -> Task FinalOutcome

autonomousEngineeringLoop objective bundle = do
  task       <- selectNextBoundedTask objective
  claim      <- dispatchGovernedAgent task
  candidate  <- observeCandidateChanges claim
  testRecord <- runAndVerifyTests candidate
  review     <- obtainIndependentReview candidate
  admission  <- decideAdmission testRecord review

  case admission of
    Accepted checkpoint ->
      continueWithinBounds objective checkpoint

    Rejected reason ->
      recoverOrStop reason

    OutcomeUnknown reconciliation ->
      reconcileWithoutRedispatch reconciliation
~~~

It requires isolated candidate writes, hard route and resource ceilings,
controller-observed changes and tests, independent review, finite continuation,
durable checkpoints, interruption recovery, and explicit stop conditions.

It does not require push, deploy, unrestricted network, credentials, or
unbounded self-improvement.

## Non-negotiable invariants

1. The requester and principal are separate fields even when their values match.
2. No actor, contract, recipe, or worker may self-grant authority.
3. Composition may only attenuate the ratified authority envelope.
4. Every callable phase has a concrete execution binding.
5. Worker output is a claim, not controller evidence.
6. Effects are admitted before execution and observed afterward.
7. Ambiguous consequential effects are reconciled without blind redispatch.
8. Build-time module updates never silently revise an active run.
9. Historical locks and evidence remain pinned and reproducible.
10. Continuation is finite and bounded by explicit acceptance and breaker rules.
