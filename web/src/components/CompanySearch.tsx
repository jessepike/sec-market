import { useRef, useState } from 'react'
import { searchCompanies } from '../data/tracker/search'
import { shortSupplierName } from '../data/tracker/names'
import { trackerSuppliers } from '../data/tracker/suppliers'
import { CompanyRequest } from './CompanyRequest'

export function CompanySearch({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [query, setQuery] = useState('')
  const input = useRef<HTMLInputElement>(null)
  const results = searchCompanies(trackerSuppliers, query)
  const searching = query.trim().length > 0
  return <div className="desk-company-search">
    <search aria-label="Company search">
    <label className="desk-company-search__label" htmlFor="company-search">Search for a company</label>
    <div className="desk-company-search__field">
      <input ref={input} id="company-search" type="search" value={query} placeholder="Company name, ticker or alias"
        aria-describedby="company-search-help" aria-controls="company-search-results"
        onChange={event => setQuery(event.target.value)} />
      {query && <button type="button" onClick={() => { setQuery(''); input.current?.focus() }}>Clear search</button>}
    </div>
    <p id="company-search-help" className="desk-note desk-company-search__help">Search the {trackerSuppliers.length} tracked companies and business segments. Select a result for facts, dated events and sources.</p>
    <div id="company-search-results">
      <p className="desk-note" role="status">{searching ? `${results.length} matching ${results.length === 1 ? 'record' : 'records'}.` : ''}</p>
      {searching && (results.length ? <ul>{results.map(supplier => <li key={supplier.id}>
        <button className="desk-supplier-link" type="button" title={supplier.name} onClick={() => openSupplier(supplier.id)}>
          {shortSupplierName(supplier.name)}{supplier.ticker && <> <span className="desk-company-search__ticker">{supplier.ticker}</span></>}
        </button>
      </li>)}</ul> : <p className="desk-note">No tracked company matches “{query.trim()}”. Try another name or ticker, or clear the search. The roster does not cover every security company.</p>)}
    </div>
    </search>
    <CompanyRequest />
  </div>
}
