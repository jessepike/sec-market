import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import {
  buyingInWording,
  buyingInWordingDecisions,
  platformPressure,
} from '../src/data/platformPressure.ts'

const AI_SECURITY_SENTENCE =
  'AI security absorbed into a platform vendor. Watch whether it survives as a product or becomes a feature.'
const CLOUD_INTO_PLATFORM_SENTENCE =
  'Cloud security absorbed into a platform vendor. Watch whether it survives as a product or becomes a feature.'
const CLOUD_INTO_HYPERSCALER_SENTENCE =
  'Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap.'

describe('buyingInWording (D-75 / SEC-054)', () => {
  it('a hyperscaler acquiring a cloud security company keeps the original sentence, unchanged', () => {
    const decision = buyingInWording('Google', 'Cloud security')
    assert.deepEqual(decision, { text: CLOUD_INTO_HYPERSCALER_SENTENCE, reworded: false, approved: true })
  })

  it('a platform vendor acquiring an AI security company gets the AI-security sentence, reworded', () => {
    const decision = buyingInWording('Palo Alto', 'AI runtime')
    assert.deepEqual(decision, { text: AI_SECURITY_SENTENCE, reworded: true, approved: true })
  })

  it('a platform vendor acquiring a cloud security company gets the same sentence, said of cloud security, reworded', () => {
    const decision = buyingInWording('F5', 'Cloud security')
    assert.deepEqual(decision, { text: CLOUD_INTO_PLATFORM_SENTENCE, reworded: true, approved: true })
  })

  it('leaves a hyperscaler acquiring something other than cloud security alone, unapproved, rather than inventing wording', () => {
    const decision = buyingInWording('Microsoft', 'AI runtime')
    assert.deepEqual(decision, { text: CLOUD_INTO_HYPERSCALER_SENTENCE, reworded: false, approved: false })
  })

  it('leaves a platform vendor acquiring something that is neither AI security nor cloud security alone, unapproved', () => {
    const decision = buyingInWording('Cisco', 'Identity')
    assert.deepEqual(decision, { text: CLOUD_INTO_HYPERSCALER_SENTENCE, reworded: false, approved: false })
  })

  it('treats every name on the documented hyperscaler list as a hyperscaler', () => {
    for (const name of ['Alphabet', 'Google', 'Microsoft', 'Amazon', 'AWS']) {
      assert.equal(buyingInWording(name, 'Cloud security').approved, true)
      assert.equal(buyingInWording(name, 'Cloud security').reworded, false)
    }
  })
})

describe('buyingInWordingDecisions against the real data (SEC-054)', () => {
  it('every non-Identity buying-in row today falls inside one of the three approved cases', () => {
    const decisions = buyingInWordingDecisions()
    assert.ok(decisions.length > 0)
    const unapproved = decisions.filter((decision) => !decision.approved)
    assert.deepEqual(unapproved, [], `rows outside D-75's approved cases: ${JSON.stringify(unapproved)}`)
  })

  it('names Wiz/Google as unchanged and the three Palo Alto/F5 AI-runtime rows as reworded', () => {
    const byId = new Map(buyingInWordingDecisions().map((decision) => [decision.id, decision]))

    const wiz = byId.get('act-wiz-close')
    assert.ok(wiz)
    assert.equal(wiz!.actor, 'Google')
    assert.equal(wiz!.targetGroup, 'Cloud security')
    assert.equal(wiz!.reworded, false)
    assert.equal(wiz!.read, CLOUD_INTO_HYPERSCALER_SENTENCE)

    for (const [id, actor, target] of [
      ['act-protect-ai', 'Palo Alto', 'Protect AI'],
      ['act-calypsoai', 'F5', 'CalypsoAI'],
      ['act-surepath', 'F5', 'SurePath AI'],
    ] as const) {
      const decision = byId.get(id)
      assert.ok(decision, `expected a buying-in decision for ${id}`)
      assert.equal(decision!.actor, actor)
      assert.equal(decision!.target, target)
      assert.equal(decision!.targetGroup, 'AI runtime')
      assert.equal(decision!.reworded, true)
      assert.equal(decision!.read, AI_SECURITY_SENTENCE)
    }
  })
})

describe('platformPressure buying-in rows carry the right per-row judged date', () => {
  it('a reworded row is dated to the 2026-09-21 approval; an unchanged row keeps its original date', () => {
    const rows = platformPressure['buying-in']

    const wiz = rows.find((row) => row.id === 'act-wiz-close')
    assert.ok(wiz)
    assert.equal(wiz!.read, CLOUD_INTO_HYPERSCALER_SENTENCE)
    assert.equal(wiz!.provenance.read.layer, 'judged')
    if (wiz!.provenance.read.layer === 'judged') {
      assert.notEqual(wiz!.provenance.read.judgedOn, '2026-09-21')
    }

    for (const id of ['act-protect-ai', 'act-calypsoai', 'act-surepath']) {
      const row = rows.find((candidate) => candidate.id === id)
      assert.ok(row, `expected a row for ${id}`)
      assert.equal(row!.read, AI_SECURITY_SENTENCE)
      assert.equal(row!.provenance.read.layer, 'judged')
      if (row!.provenance.read.layer === 'judged') {
        assert.equal(row!.provenance.read.judgedOn, '2026-09-21')
      }
    }

    const cyberArk = rows.find((row) => row.id === 'act-cyberark-close')
    assert.ok(cyberArk, 'expected the Identity row (CyberArk) to be untouched')
    assert.match(cyberArk!.read, /platform pillar/)
    assert.equal(cyberArk!.provenance.read.layer, 'judged')
    if (cyberArk!.provenance.read.layer === 'judged') {
      assert.notEqual(cyberArk!.provenance.read.judgedOn, '2026-09-21')
    }
  })
})
