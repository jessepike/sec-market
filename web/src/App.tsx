import { Analytics } from '@vercel/analytics/react'
import type { ReactNode } from 'react'
import { ActivityBoard } from './components/ActivityBoard'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { Header } from './components/Header'
import { HeroContent } from './components/Hero'
import { HowThisWorks } from './components/HowThisWorks'
import { Hypotheses } from './components/Hypotheses'
import { IssueArchive } from './components/IssueArchive'
import { IssueHero } from './components/IssueHero'
import { IssueLanes } from './components/IssueLanes'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { NextEdition } from './components/NextEdition'
import { PlatformPressure } from './components/PlatformPressure'
import { PrintGrid } from './components/PrintGrid'
import { ProvenanceRail } from './components/ProvenanceRail'
import { SkipLink } from './components/SkipLink'
import { ThesisRunningScore } from './components/ThesisRunningScore'
import { VendorLens } from './components/VendorLens'
import { WatchList } from './components/WatchList'
import { WeThink } from './components/WeThink'
import { WhatMoved } from './components/WhatMoved'
import { EvidenceProvider } from './context/EvidenceProvider'
import { useEvidence } from './context/useEvidence'
import { VendorLensProvider } from './context/VendorLensProvider'
import { issueById, latestIssue } from './data/issues/index'
import { matchRoute } from './data/routes'
import type { Issue } from './data/types'

/**
 * `/` — this week's issue, then the standing reference, then depth.
 *
 * Wrapped in VendorLensProvider (SEC-031): IssueLanes and PrintGrid, both
 * inside, read the lens state to filter; VendorLens is the control. Scoped
 * to this page on purpose — the issue permalink page has no lens control, so
 * it never mounts the provider, and its IssueLanes renders unfiltered via
 * useVendorLens()'s inactive fallback.
 */
function FrontPage() {
  return (
    <VendorLensProvider>
      <IssueHero issue={latestIssue} />
      <IssueLanes issue={latestIssue} />
      <WeThink issue={latestIssue} />

      <JudgmentBoard
        leadContent={
          <>
            <ThesisRunningScore />
            <HeroContent />
          </>
        }
      />
      <DomainBoard />
      <PlatformPressure />
      <Hypotheses />
      <VendorLens />
      <PrintGrid />

      <details className="depth" id="moved-depth">
        <summary>What moved: edition delta</summary>
        <WhatMoved />
      </details>
      <details className="depth" id="research-depth">
        <summary>Domain tempo and M&amp;A activity</summary>
        <DomainBoard surface="tempo" />
        <p className="research-depth__note">
          Activity below is the pre-issue window (RoS) — going forward each issue's Formation and
          Absorption lanes carry this account.
        </p>
        <ActivityBoard />
      </details>
      <details className="depth" id="layers">
        <summary>Market layers</summary>
        <MarketLayersChart />
      </details>
      <details className="depth" id="watch">
        <summary>Watch next</summary>
        <WatchList />
      </details>
      <details className="depth" id="method">
        <summary>How this is built</summary>
        <HowThisWorks />
      </details>
      <details className="depth" id="research">
        <summary>Research &amp; evidence</summary>
        <EvidenceLibrary />
      </details>
      <MethodologyNote />
      <NextEdition />
    </VendorLensProvider>
  )
}

/** `/issues/<id>/` — that issue alone, with a link to the standing reference. */
function IssuePage({ issue }: { issue: Issue }) {
  return (
    <>
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

function RouteContent({ path }: { path: string }) {
  const route = matchRoute(path)

  if (route.kind === 'archive') return <IssueArchive />
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
      <ProvenanceRail />
      <div className="app-shell" inert={isOpen ? true : undefined}>
        <Header />
        <main id="main" className="main-content" tabIndex={-1}>
          <RouteContent path={path} />
        </main>
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
