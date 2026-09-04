#!/usr/bin/env node
// docs/metabuilder-preparation-trace.mjs
//
// A runnable functional sketch of the MetaBuilder preparation pipeline
// (docs/metabuilder-autonomy-functional-model.md, "Preparation pipeline").
// It visualizes three things the idealized unary chain hides:
//
//   1. FAN-OUT      — authorized, thesis, and ratified are each consumed by
//                     more than one later stage, so the pipeline threads an
//                     accumulating record; it is a dependency graph, not a
//                     unary chain.
//   2. CLAIM FLOW   — skill phases emit claims; the controller verifies them
//                     asynchronously; durable journal appends lag behind the
//                     chain in wall-clock time (potentially out of sync).
//   3. THE GATE     — ratifyDecisionRecord reads a principal or delegated
//                     ratifier decision from the environment (a Reader
//                     dependency), not from the data. Identical request data +
//                     different authority decisions => different outcomes. No
//                     pure function of the data could produce both.
//
// This illustrates the target gate shape. It does not authenticate the
// ratifier or validate a real StandingDelegation; those remain controller
// responsibilities in the proposed operating model.
//
// Run: node docs/metabuilder-preparation-trace.mjs

/* ---------- Result + PrepM (Reader over Except, async) ------------------- */

const Ok = (value) => ({ tag: 'Ok', value });
const Err = (error) => ({ tag: 'Err', error });

// PrepM a = PrepEnv -> Promise<Result a>
//   "Reader"  : every effect takes the environment (principal, services).
//   "Except"  : any stage may fail and short-circuit the chain (Kleisli).
const pure = (value) => async () => Ok(value);
const bindM = (f) => (m) => async (env) => {
  const r = await m(env);
  return r.tag === 'Ok' ? f(r.value)(env) : r;
};
const kleisli = (...arrows) => arrows.reduce((acc, f) => (x) => bindM(f)(acc(x)));

/* ---------- environment: controller, journal, decision service ----------- */

const rand = (min, max) => min + Math.random() * (max - min);
const t0 = performance.now();
const stamp = () => `[t=${String(Math.round(performance.now() - t0)).padStart(4, '0')}ms]`;

const makeEnv = (runTag, principal, ratifier, ratificationAuthority, decision) => {
  let claimSeq = 0;
  const log = (plane, msg) =>
    console.log(`${stamp()} ${runTag} ${plane.padEnd(10)} ${msg}`);
  return {
    principal,
    ratifier,
    ratificationAuthority,
    log,
    nextClaimId: () => `c${String(++claimSeq).padStart(2, '0')}`,
    // Controller verification: asynchronous, variable latency. The chain
    // blocks on the verdict, but the verdict lands whenever it lands.
    verify: async (claim) => {
      await new Promise((r) => setTimeout(r, rand(10, 90)));
      return {
        subject: claim.id,
        verifier: 'controller-1',
        verifiedAt: Math.round(performance.now() - t0),
        value: claim.value, // verified copy of the claimed value
      };
    },
    // Durable journal appends: fire-and-forget from the chain's point of
    // view. They confirm LATER than subsequent chain events — the out-of-sync
    // plane that recovery and replay must reconcile.
    journal: {
      append: async (record) => {
        const lag = rand(80, 320);
        await new Promise((r) => setTimeout(r, lag));
        log('journal', `durable append confirmed for ${record.subject} ` +
          `(lagged ${Math.round(lag)}ms — reconciliation window)`);
      },
    },
    // THE GATE'S INPUT IS NOT IN THE DATA. The decision arrives from the
    // environment, asynchronously, per admitted ratifier. Same request,
    // different authority decision => different pipeline outcome.
    decisionService: async () => {
      await new Promise((r) => setTimeout(r, rand(150, 400))); // human latency
      return decision;
    },
  };
};

/* ---------- skill phase wrapper: execute -> claim -> verify -> flow on --- */

const skillPhase = (phaseId, compute) => (acc) => async (env) => {
  const value = compute(acc); // pure transform over the accumulated record
  const claim = { id: env.nextClaimId(), producer: phaseId, value };
  env.log('chain', `${phaseId} executed; emitted ${claim.id} (CLAIM, unverified)`);
  const record = await env.verify(claim);
  env.log('controller', `verified ${record.subject} -> verified value flows on`);
  env.journal.append(record); // not awaited: journal may lag the chain
  return Ok({ ...acc, [phaseId]: value });
};

/* ---------- the pipeline: each stage reads the whole accumulated record -- */

const authorizeRequest = (request) => async (env) => {
  if (!request.delegationProof && request.requester !== request.principal) {
    return Err({ type: 'DelegationRequired' });
  }
  env.log('chain', 'authorizeRequest: delegation proof checked (authority function)');
  return Ok({
    request,
    authorized: {
      principal: request.principal,
      ratifier: env.ratifier,
      ratificationAuthority: env.ratificationAuthority,
    },
  });
};

const frame = skillPhase('frameGoalsAndConstraints', (acc) => ({
  thesis: `thesis-of(${acc.request.objective})`,
}));
const grill = skillPhase('grillMaterialUnknowns', (acc) => ({
  decisions: `decisions-from(${acc.frameGoalsAndConstraints.thesis})`,
}));

const ratifyDecisionRecord = (acc) => async (env) => {
  env.log('chain', `AUTHORITY GATE ratifyDecisionRecord: reading decision for ` +
    `principal=${env.principal} from ratifier=${env.ratifier} under ` +
    `${env.ratificationAuthority} FROM THE ENVIRONMENT (not from the data)`);
  const decision = await env.decisionService();
  if (decision !== 'approve') {
    env.log('chain', `gate returned '${decision}' -> pipeline refuses`);
    return Err({
      type: 'RatificationRefused',
      principal: env.principal,
      ratifier: env.ratifier,
      authority: env.ratificationAuthority,
    });
  }
  env.log('chain', `gate returned 'approve' for principal=${env.principal} ` +
    `by ratifier=${env.ratifier}`);
  return Ok({
    ...acc,
    ratified: {
      decision: acc.grillMaterialUnknowns.decisions,
      principal: env.principal,
      ratifier: env.ratifier,
      authority: env.ratificationAuthority,
    },
  });
};

const decompose = skillPhase('decomposeObjective', (acc) => ({
  plan: `dag(thesis=${acc.frameGoalsAndConstraints.thesis}, ` +
        `ratified=${JSON.stringify(acc.ratified)})`, // <- FAN-OUT: two earlier values reused
}));

const deriveEnvelope = (acc) => async (env) => {
  env.log('chain', 'deriveAttenuatedEnvelope: attenuates (principal, authorized, ratified)');
  return Ok({
    ...acc,
    authority: `envelope(principal=${env.principal}, ` +
      `ratifier=${env.ratifier}, ceiling<=${acc.authorized.principal})`, // <- FAN-OUT again
  });
};

const assemble = (acc) => async (env) => {
  const prepared = {
    thesis: acc.frameGoalsAndConstraints.thesis,
    decisions: acc.grillMaterialUnknowns.decisions,
    plan: acc.decomposeObjective.plan,
    authority: acc.authority,
  };
  env.log('chain', `PreparedObjective assembled: ${JSON.stringify(prepared)}`);
  return Ok(prepared);
};

const prepareObjective = kleisli(
  authorizeRequest, frame, grill, ratifyDecisionRecord, decompose, deriveEnvelope, assemble
);

/* ---------- dataflow ledger (the fan-out, stated explicitly) ------------- */

const FANOUT = [
  ['authorized', ['frameGoalsAndConstraints', 'deriveAttenuatedEnvelope']],
  ['thesis',     ['grillMaterialUnknowns', 'decomposeObjective']],
  ['ratified',   ['decomposeObjective', 'deriveAttenuatedEnvelope']],
];

/* ---------- run: identical data, different environment decision ---------- */

const REQUEST = Object.freeze({
  requester: 'agent-7',
  principal: 'principal-alice', // SAME principal in every run
  objective: 'bounded-refactor:fp-refine-phase-2',
  delegationProof: { proof: 'valid' },
});

const outcomes = [];

for (const [tag, decision] of [['run-1', 'approve'], ['run-2', 'refuse']]) {
  console.log(`\n=== ${tag} · environment decision '${decision}' · request data byte-identical ===`);
  const env = makeEnv(
    `[${tag}]`,
    REQUEST.principal,
    'orchestrator-1',
    'standing-delegation-1',
    decision,
  );
  const result = await prepareObjective(REQUEST)(env);
  outcomes.push({ decision, digest: JSON.stringify(REQUEST), result });
}

console.log('\n=== FAN-OUT LEDGER (why the chain is a graph, not unary) ===');
for (const [value, consumers] of FANOUT) {
  console.log(`  ${value.padEnd(12)} -> ${consumers.join(', ')}`);
}

console.log('\n=== GATE IS NOT A FUNCTION OF THE DATA ===');
const [a, b] = outcomes;
console.log(`  input digests identical : ${a.digest === b.digest} (byte-identical ObjectiveRequest)`);
console.log(`  run-1 (env: approve)    : ${a.result.tag}`);
console.log(`  run-2 (env: refuse)     : ${b.result.tag} (${JSON.stringify(b.result.error)})`);
console.log('  same data, different outcomes => the deciding input lives in the');
console.log("  environment (the admitted ratifier's live decision), not in ObjectiveRequest.");
