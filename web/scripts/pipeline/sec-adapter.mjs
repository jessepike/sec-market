// Parse archived SEC bytes with the existing producer and a separate verifier.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { buildSupplierRecord } from '../../src/data/edgarLogic.ts'
import { edgarRegistry } from '../../src/data/edgarRegistry.ts'
import { dollars, growthText, verifyHistory, verifyRevenuePeriod, verifyIdentity, verifySecEvents, TRACKED_ITEMS, TRACKED_FORMS } from '../sec-verify/independent.mjs'

const input = JSON.parse(readFileSync(0, 'utf8'))
const reg = edgarRegistry.find(r => r.id === input.supplierId)
if (!reg) throw new Error('SEC supplier is outside approved registry')
const source = input.documents[0]
if (String(source.cik).padStart(10, '0') !== reg.cik) throw new Error('SEC CIK differs from source contract')
const fact = (predicate, value) => ({ supplierId: reg.id, predicate, value,
  factId: createHash('sha256').update(JSON.stringify([reg.id, predicate, value])).digest('hex'), assurance: 'sec_rederived' })

if (input.kind === 'sec_facts') {
  const record = buildSupplierRecord(reg.id, reg.name, reg.cik, source, reg.revenueConcepts)
  const period = figure => ({ value: dollars(figure.quarter.value),
    priorYearValue: figure.priorYearQuarter ? dollars(figure.priorYearQuarter.value) : undefined,
    yoyGrowth: figure.growth !== null && !figure.flags.length ? growthText(figure.growth) : '',
    period: `Quarter ended ${figure.quarter.periodEnd}${figure.quarter.derived ? ' (derived from annual less preceding quarters)' : ''}`,
    periodEnd: figure.quarter.periodEnd, releaseDate: figure.quarter.filedDate })
  const checks = [verifyHistory(source, reg.revenueConcepts, record.quarters),
    verifyRevenuePeriod(source, reg.revenueConcepts, period(record.latest), { requireReleaseDate: true })]
  if (record.prior) checks.push(verifyRevenuePeriod(source, reg.revenueConcepts, period(record.prior), { requireReleaseDate: false }))
  if (checks.some(c => !c.ok)) throw new Error(checks.filter(c => !c.ok).map(c => c.reason).join('; '))
  console.log(JSON.stringify({ facts: [fact('sec_revenue_snapshot', record)], checks }))
} else {
  const recent = source.filings.recent
  const seen = new Set(recent.accessionNumber)
  for (const archive of input.documents.slice(1)) {
    for (let i = 0; i < archive.accessionNumber.length; i++) {
      if (seen.has(archive.accessionNumber[i])) continue
      seen.add(archive.accessionNumber[i])
      for (const key of Object.keys(recent)) recent[key].push(archive[key]?.[i] ?? '')
    }
  }
  const windowEnd = input.windowEnd, windowStart = new Date(Date.parse(windowEnd+'T00:00:00Z') - 365*86400000).toISOString().slice(0,10)
  const identity = { name: source.name, ticker: reg.ticker, kind: 'public' }
  const checks = [verifyIdentity(source, identity, Date.parse(windowEnd+'T23:59:59Z'))]
  const events = []
  for (let i = 0; i < recent.form.length; i++) {
    const form = recent.form[i], date = recent.filingDate[i], accession = recent.accessionNumber[i]
    if (date < windowStart || date > windowEnd) continue
    const needs = form === '8-K' ? (recent.items[i] ?? '').split(',').map(c=>c.trim()).filter(c=>c in TRACKED_ITEMS).map(c=>[c,TRACKED_ITEMS[c][0]])
      : form in TRACKED_FORMS ? [[form,TRACKED_FORMS[form][0]]] : []
    for (const [code,type] of needs) {
      const primary = recent.primaryDocument[i]
      if (!/^[A-Za-z0-9_.-]+$/.test(primary) || !/^\d{10}-\d{2}-\d{6}$/.test(accession)) throw new Error('Invalid SEC filing path')
      events.push({ id: `EV-filing-${reg.id}-${accession}-${code.replace('.','-')}`, supplierId:reg.id,date,type,form,item:code,
        accessions:[accession],evidenceDates:[date],url:`https://www.sec.gov/Archives/edgar/data/${Number(reg.cik)}/${accession.replaceAll('-','')}/${primary}`,
        text:`Form ${form}${form==='8-K'?` (Item ${code})`:''}, filed ${date}.` })
    }
  }
  checks.push(verifySecEvents(source, events, events, windowStart, windowEnd, windowEnd))
  if (checks.some(c=>!c.ok)) throw new Error(checks.filter(c=>!c.ok).map(c=>c.reason).join('; '))
  console.log(JSON.stringify({facts:[fact('sec_identity',identity),fact('sec_events_snapshot',events)],checks}))
}
