// Accuracy gate for machine-written filed-event text (D-103). Every filed
// event's text is built by a script, so every one is checked before it can
// publish. filing-events.ts drops a quote that fails and keeps only the plain
// filing label; the data tests fail the refresh run if any published text
// fails, so a bad line is held instead of going live.

const LABEL = /^(Form 8-K \(Item \d\.\d{2}\)|Form [A-Z0-9 -]+) reporting [^.]+, filed \d{4}-\d{2}-\d{2}\.$/
const QUOTED = /^(.*?) The filing describes it as: “(.+)”( …)?$/

/** Problems with a filing excerpt; empty when it may be quoted. */
export function quoteProblems(quote) {
  const problems = []
  if (quote.length < 80) problems.push('quote is shorter than 80 characters')
  if (quote.length > 460) problems.push('quote is longer than 460 characters')
  if (!/^[A-Z‘($0-9]/.test(quote)) problems.push('quote does not start a sentence')
  if (/incorporated (?:herein )?by reference/i.test(quote)) problems.push('quote is reference boilerplate')
  if (/^Item\s*\d\.\d{2}/i.test(quote) || /Direct Financial Obligation|Off-Balance Sheet Arrangement/.test(quote)) problems.push('quote contains an item title')
  if (!/\d/.test(quote)) problems.push('quote states no date or amount')
  if (/[“”]/.test(quote)) problems.push('quote contains unconverted inner double quotes')
  if (/&[#a-z0-9]+;|<\/?[a-z]/i.test(quote)) problems.push('quote contains HTML')
  if (/\s{2,}/.test(quote) || [...quote].some(c => c.charCodeAt(0) < 32)) problems.push('quote contains stray whitespace or control characters')
  return problems
}

/** Problems with a published filed-event text; empty when it is well formed. */
export function eventTextProblems(text) {
  const m = QUOTED.exec(text)
  const label = m ? m[1] : text
  const problems = LABEL.test(label) ? [] : [`label is not in the standard form: "${label.slice(0, 80)}"`]
  if (m) problems.push(...quoteProblems(m[2]))
  return problems
}
