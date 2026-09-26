import assert from 'node:assert/strict'
import { mkdtempSync, writeFileSync, existsSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'

const state = mkdtempSync(join(tmpdir(), 'ow-bridge-test-'))
process.env.OW_CONTINUATION_DIR = state
const { addressedTo, OverwatchContinuation } = await import('../overlays/opencode/plugin/overwatch-continuation.ts')
const item = { schema_version: 1, target_pid: process.pid, target_session: 'ses_owner', cwd: state, label: 'task', exit_code: 0 }

test('only exact process, session, and workspace can receive a completion', () => {
  assert.equal(addressedTo(item, process.pid, 'ses_owner', state), true)
  for (const changed of [
    { target_pid: process.pid + 1 }, { target_session: 'ses_other' },
    { cwd: '/another-project' }, { target_pid: undefined }, { target_session: undefined },
    { exit_code: '0' }, { schema_version: 2 },
  ]) assert.equal(addressedTo({ ...item, ...changed }, process.pid, 'ses_owner', state), false)
})

test('delivery preserves foreign records and does not replay uncertain claims', async () => {
  const received = []
  const client = { session: { promptAsync: async request => { received.push(request); if (request.body.parts[0].text.includes('uncertain-task')) throw Error('unknown delivery'); } } }
  const plugin = await OverwatchContinuation({ client, directory: state })
  await plugin.event({ event: { properties: { sessionID: 'ses_owner' } } })
  writeFileSync(join(state, 'own.json'), JSON.stringify({ ...item, prompt: 'UNTRUSTED CONTROL TEXT' }))
  writeFileSync(join(state, 'foreign.json'), JSON.stringify({ ...item, target_pid: process.pid + 1 }))
  writeFileSync(join(state, 'uncertain.json'), JSON.stringify({ ...item, label: 'uncertain-task' }))
  await new Promise(resolve => setTimeout(resolve, 4500))
  assert.equal(received.length, 2)
  assert.ok(received.every(request => request.path.id === 'ses_owner'))
  assert.ok(received.every(request => !request.body.parts[0].text.includes('UNTRUSTED CONTROL TEXT')))
  assert.ok(existsSync(join(state, 'own.consumed')))
  assert.ok(existsSync(join(state, 'foreign.json')))
  assert.ok(existsSync(join(state, 'uncertain.claimed')))
  rmSync(state, { recursive: true })
})
