import { Analytics } from '@vercel/analytics/react'
import type { ReactNode } from 'react'
import { Corrections } from './components/Corrections'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { Header } from './components/Header'
import { HeroContent } from './components/Hero'
import { IssueArchive } from './components/IssueArchive'
import { IssueHero } from './components/IssueHero'
import { IssueLanes } from './components/IssueLanes'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketDesk } from './components/MarketDesk'
import { SiteFooter } from './components/SiteFooter'
import { MethodPage } from './components/MethodPage'
import { SkipLink } from './components/SkipLink'
import { SupplierCoverage } from './components/SupplierCoverage'
import { DataForAgents } from './components/DataForAgents'
import { CompanyPage } from './components/CompanyPage'
import { FundingRounds } from './components/FundingRounds'
import { ThesisRunningScore } from './components/ThesisRunningScore'
import { WeThink } from './components/WeThink'
import { EvidenceProvider } from './context/EvidenceProvider'
import { useEvidence } from './context/useEvidence'
import { issueById } from './data/issues/index'
import { matchRoute } from './data/routes'
import type { Issue } from './data/types'

/**
 * The one-line archive/record notice added by D-76/autonomy-coverage-plan.md
 * §3, step 1 to every page kept as a dated record rather than updated: the
 * issue archive index, each issue permalink, and the standing thesis. It is
 * new wrapper content around a page, never a change to the locked issue data
 * or the thesis argument itself.
 */
function ArchiveNotice({ text }: { text: string }) {
  return <p className="archive-notice">{text}</p>
}

/** October 2026 approved hybrid. Current tracker data powers the dated change log,
 * revenue comparison, event timeline and supplier records. Collection and method
 * remain below the market views; no owner-read placeholder or domain median. */
function FrontPage() {
  return <MarketDesk />
}

/**
 * `/issues/<id>/` — that issue alone, with a link to the standing reference.
 * D-76/autonomy-coverage-plan.md §3, step 1: carries the archive notice
 * above the (unaltered) issue content — signed weekly issues are
 * discontinued, and this page is kept as a dated record.
 */
function IssuePage({ issue }: { issue: Issue }) {
  return (
    <>
      <ArchiveNotice text="Signed weekly issues were discontinued on 25 September 2026. This page is kept unchanged as a dated record." />
      <IssueHero issue={issue} />
      <IssueLanes issue={issue} />
      <WeThink issue={issue} />
      <section className="issue-permalink-links" aria-label="More issues">
        <p>
          <a href="/issues/">Back to the archive</a> · <a href="/">Standing reference</a>
        </p>
      </section>
    </>
  )
}

/**
 * `/thesis/` — the standing home for the founding thesis (SEC-MARKET-FABLE-001
 * T6-16, product-core.md §5): one h1 framing it as one analysis among the
 * site's outputs, then the exact same JudgmentBoard the front page used to
 * carry at `#read`, unchanged. No VendorLensProvider — nothing rendered here
 * (JudgmentBoard, ThesisRunningScore, HeroContent, EvidenceLink) reads the
 * vendor lens; EvidenceLink's drawer comes from EvidenceProvider, which
 * already wraps every route in App() below.
 *
 * D-76/autonomy-coverage-plan.md §3, step 1: carries the archive notice
 * above the (unaltered) thesis argument — this is a dated record, not a
 * standing judgment the site keeps updating.
 */
function ThesisPage() {
  return (
    <>
      <section id="thesis" className="thesis-page" aria-labelledby="thesis-heading">
        <h1 id="thesis-heading">Standing analysis: does security spending lag infrastructure spending?</h1>
        <p className="thesis-page__intro">
          This site began from one question: when spending on computing infrastructure rises, does
          security spending follow, and how long after. This page keeps that analysis and its
          record. It is one analysis among the site&rsquo;s outputs. If you run a security program
          you can skip it; if you plan where security spending goes next, it is for you.
        </p>
        <ArchiveNotice text="This analysis is kept as a dated record and is no longer updated." />
      </section>
      <JudgmentBoard
        leadContent={
          <>
            <ThesisRunningScore />
            <HeroContent />
          </>
        }
      />
      <section className="thesis-page-links" aria-label="More">
        <p className="thesis-page__back">
          <a href="/">Back to the front page</a>
        </p>
      </section>
    </>
  )
}

function RouteContent({ path }: { path: string }) {
  const route = matchRoute(path)

  if (route.kind === 'archive') return <IssueArchive />
  if (route.kind === 'corrections') return <Corrections />
  if (route.kind === 'thesis') return <ThesisPage />
  if (route.kind === 'coverage') return <SupplierCoverage />
  if (route.kind === 'data') return <DataForAgents />
  if (route.kind === 'company' && route.supplierId) return <CompanyPage id={route.supplierId} />
  if (route.kind === 'funding') return <FundingRounds />
  if (route.kind === 'market') return <MarketDesk view="market" />
  if (route.kind === 'method') return <MethodPage />
  if (route.kind === 'issue' && route.issueId && issueById[route.issueId]) {
    return <IssuePage issue={issueById[route.issueId]} />
  }
  return <FrontPage />
}

function AppShell({ path }: { path: string }) {
  const { isOpen } = useEvidence()

  return (
    <>
      <SkipLink />
      <div className="app-shell app-shell--desk" inert={isOpen ? true : undefined}>
        <Header path={path} />
        <main id="main" className="main-content" tabIndex={-1}>
          <RouteContent path={path} />
        </main>
        <SiteFooter />
      </div>
      <EvidenceDrawer />
      {/* Renders null on the server and on the client's first pass; it injects the
          beacon from a useEffect, so it cannot desync prerendered markup. Data only
          flows once Web Analytics is enabled in the Vercel project settings. */}
      <Analytics />
    </>
  )
}

/**
 * `path` selects which of the three routes (front page, archive, issue
 * permalink) to render — see src/data/routes.ts. Defaults to `/` so every
 * existing call site (tests, Storybook-style usage) keeps working unchanged.
 */
function App({ path = '/' }: { path?: string }): ReactNode {
  return (
    <EvidenceProvider>
      <AppShell path={path} />
    </EvidenceProvider>
  )
}

export default App
