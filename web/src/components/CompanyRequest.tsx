import { useRef, useState, type FormEvent } from 'react'

// Sends a typed company name to a private review list (ops/timer/api/request.js).
// No email address is shown. Nothing is published from a request.
export const REQUEST_ENDPOINT = 'https://market-pipeline-timer.vercel.app/api/request'

type State = 'idle' | 'sending' | 'sent' | 'invalid' | 'failed'
const MESSAGES: Record<State, string> = {
  idle: '',
  sending: 'Sending…',
  sent: 'Thanks. The name is on the review list.',
  invalid: 'Enter a company name of 2 to 60 letters or numbers, without links.',
  failed: 'The request did not go through. Try again later.',
}

export function CompanyRequest() {
  const [name, setName] = useState('')
  const [state, setState] = useState<State>('idle')
  const opened = useRef(0)
  const honeypot = useRef<HTMLInputElement>(null)
  async function submit(event: FormEvent) {
    event.preventDefault()
    if (state === 'sending') return
    setState('sending')
    try {
      const response = await fetch(REQUEST_ENDPOINT, { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ name, website: honeypot.current?.value ?? '', elapsed: Date.now() - opened.current }) })
      if (response.ok) { setState('sent'); setName('') } else setState(response.status === 400 ? 'invalid' : 'failed')
    } catch { setState('failed') }
  }
  return <details className="desk-company-request" onToggle={event => { if ((event.target as HTMLDetailsElement).open && !opened.current) opened.current = Date.now() }}>
    <summary>Want a company tracked?</summary>
    <form onSubmit={submit}>
      <label htmlFor="company-request">Company name</label>
      <div className="desk-company-search__field">
        <input id="company-request" name="company" placeholder="Company name" value={name} required minLength={2} maxLength={60} autoComplete="off"
          aria-describedby="company-request-help company-request-status" onChange={event => { setName(event.target.value); if (state !== 'sending') setState('idle') }} />
        <button type="submit" disabled={state === 'sending'}>Send</button>
      </div>
      <div className="desk-company-request__trap" aria-hidden="true">
        <label htmlFor="company-request-website">Leave this empty</label>
        <input ref={honeypot} id="company-request-website" name="website" tabIndex={-1} autoComplete="off" />
      </div>
      <p id="company-request-help" className="desk-note">Requests go to a private review list. A company appears here only after it is added and passes every check.</p>
      <p id="company-request-status" className="desk-note" role="status">{MESSAGES[state]}</p>
    </form>
  </details>
}
