import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { escapeHtmlAttr } from '../src/data/htmlEscape.ts'

describe('escapeHtmlAttr', () => {
  it('escapes & < > " \' in that order, without double-escaping its own output', () => {
    assert.equal(escapeHtmlAttr('&'), '&amp;')
    assert.equal(escapeHtmlAttr('<'), '&lt;')
    assert.equal(escapeHtmlAttr('>'), '&gt;')
    assert.equal(escapeHtmlAttr('"'), '&quot;')
    assert.equal(escapeHtmlAttr("'"), '&#39;')
  })

  it('escapes a value that would otherwise close an attribute early', () => {
    const attack = `"><script>alert(1)</script>`
    const escaped = escapeHtmlAttr(attack)
    assert.equal(escaped, '&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;')
    assert.ok(!escaped.includes('"'))
    assert.ok(!escaped.includes('<'))
    assert.ok(!escaped.includes('>'))
  })

  it('leaves plain text untouched', () => {
    assert.equal(
      escapeHtmlAttr('Record earnings meet thin VC and quiet M&A this week.'.replace('&', 'and')),
      'Record earnings meet thin VC and quiet MandA this week.',
    )
    assert.equal(escapeHtmlAttr('Issue 2026-w36 · Security Market Pulse'), 'Issue 2026-w36 · Security Market Pulse')
  })

  it('round-trips a realistic issue read containing an ampersand and quotes', () => {
    const read = `M&A stays quiet as CrowdStrike's "record" quarter meets a <thin> VC week.`
    const escaped = escapeHtmlAttr(read)
    assert.equal(
      escaped,
      'M&amp;A stays quiet as CrowdStrike&#39;s &quot;record&quot; quarter meets a &lt;thin&gt; VC week.',
    )
  })
})
