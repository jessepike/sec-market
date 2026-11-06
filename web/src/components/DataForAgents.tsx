import { dataFiles } from '../data/agentExport'
import { DATA_LICENSE_URL, LAST_UPDATED_DISPLAY } from '../data/meta'

/**
 * `/data/` (D-139): the files programs and AI agents can read, the rules that
 * travel with the data, and the license. The file list comes from
 * src/data/agentExport.ts, the same list llms.txt is built from. Reuses the
 * coverage page's styles; no new CSS.
 */
export function DataForAgents() {
  return (
    <section id="data" className="coverage-page" aria-labelledby="data-heading">
      <h1 id="data-heading">Data for agents</h1>
      <p className="coverage-page__lede">
        Everything on this site is also published as files that programs and AI agents can read. The files are
        rebuilt every time the site is, from the same records the pages show. Data last checked {LAST_UPDATED_DISPLAY}.
      </p>

      <h2 id="data-rules">Rules that come with the data</h2>
      <ul>
        <li>Facts only. The site publishes no stances, rankings, forecasts or interpretation.</li>
        <li>Every figure keeps the period or date it is true for and the source it is cited to. Quote the period with the figure.</li>
        <li>
          &ldquo;Certified&rdquo; means re-derived from the company&rsquo;s own SEC filings. Other figures keep their own
          source and date and are not re-checked automatically.
        </li>
        <li>Corrections are published, never made silently.</li>
      </ul>

      <h2 id="data-files">Files</h2>
      <table className="coverage-table">
        <thead>
          <tr>
            <th scope="col">File</th>
            <th scope="col">Format</th>
            <th scope="col">What it holds</th>
          </tr>
        </thead>
        <tbody>
          {dataFiles.map((file) => (
            <tr key={file.path}>
              <th scope="row" data-label="File"><a href={file.path}>{file.path}</a></th>
              <td data-label="Format">{file.format}</td>
              <td data-label="What it holds">{file.what}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 id="data-markdown">Markdown for agents</h2>
      <p className="coverage-page__note">
        The front page is also published as Markdown at <a href="/index.md">/index.md</a>, and this page at
        <a href="/data/index.md">/data/index.md</a>. Each page points to its Markdown copy in its head and in an HTTP Link header.
      </p>

      <h2 id="data-license">License</h2>
      <p className="coverage-page__note">
        The data and pages are licensed <a href={DATA_LICENSE_URL}>CC BY 4.0</a>. You can reuse them, including
        for AI training, with credit to Security Market Pulse and a link to this site.
      </p>
      <p className="coverage-page__back"><a href="/">Back to the front page</a></p>
    </section>
  )
}
