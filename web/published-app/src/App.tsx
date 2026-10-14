import { Analytics } from '@vercel/analytics/react'
import type { ReactNode } from 'react'
import { ActivityBoard } from './components/ActivityBoard'
import { Corrections } from './components/Corrections'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { FollowLine } from './components/FollowLine'
import { Header } from './components/Header'
import { HeroContent } from './components/Hero'
import { HowThisWorks } from './components/HowThisWorks'
import { Hypotheses } from './components/Hypotheses'
import { IssueArchive } from './components/IssueArchive'
import { IssueHero } from './components/IssueHero'
import { IssueLanes } from './components/IssueLanes'
import { IssueStrip } from './components/IssueStrip'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MarketPicture } from './components/MarketPicture'
import { MethodologyNote } from './components/MethodologyNote'
import { NextEdition } from './components/NextEdition'
import { PlatformPressure } from './components/PlatformPressure'
import { PrintGrid } from './components/PrintGrid'
import { ProvenanceRail } from './components/ProvenanceRail'
import { RefreshStatus } from './RefreshStatus'
import { SiteMasthead } from './components/SiteMasthead'
import { SkipLink } from './components/SkipLink'
import { ThesisPointer } from './components/ThesisPointer'
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
 * `/` — what the site is, this week's read in one strip, then the market
 * picture, then the issue in full, then the standing reference and depth.
 *
 * Order per design-spec v0.3 §3.1, amended by SEC-MARKET-CORE-001 §5: the
 * first screen belongs to the market picture, so the masthead and the issue
 * strip above it are deliberately short. The strip replaced IssueHero here
 * and carries `#overview` forward, so the header's "Issue" link and
 * prerender's front-page section list are unchanged. IssueHero itself is
 * untouched and still renders the issue permalink below.
 *
 * Then: market, we-think, the four lanes, follow, landscape,
 * platforms/vendor-lens-slot/prints (kept together), hypotheses, the thesis
 * pointer (`#read`), then depth sections unchanged.
 *
 * SEC-MARKET-FABLE-001 T6-16 (product-core.md §5): the founding thesis is
 * "one standing analysis on the site, not the site's identity" and moved to
 * its own page, `/thesis/` (see ThesisPage below). `#read` here is now
 * ThesisPointer, a compact pointer to that page, moved to sit after
 * `#hypotheses` — no gate or test asserts front-page section order (the
 * adversarial pass in docs/active/fable-run/consults/adversarial-pass.md
 * confirmed this), so this is a deliberate placement choice, not a
 * constraint. `WeThink` gets `condenseThesis` here so its thesis verdict is
 * also a quiet pointer rather than the full paragraph — see WeThink.tsx.
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
      <SiteMasthead />
      <RefreshStatus />
      <IssueStrip issue={latestIssue} />
      <MarketPicture />
      <WeThink issue={latestIssue} condenseThesis />
      <IssueLanes issue={latestIssue} />
      <FollowLine />
      <DomainBoard />
      <PlatformPressure />
      <VendorLens />
      <PrintGrid />
      <Hypotheses />
      <ThesisPointer />

      <details className="depth" id="moved-depth">
        <summary>What moved: edition delta</summary>
        <WhatMoved />
      </details>
      <details className="depth" id="research-depth">
        <summary>Domain tempo and M&amp;A activity</summary>
        <DomainBoard surface="tempo" />
        <p className="research-depth__note">
          Activity below is the pre-issue window (RoS) — going forward each issue's "New companies
          and funding" and "Acquisitions and consolidation" lanes carry this account.
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

/**
 * `/thesis/` — the standing home for the founding thesis (SEC-MARKET-FABLE-001
 * T6-16, product-core.md §5): one h1 framing it as one analysis among the
 * site's outputs, then the exact same JudgmentBoard the front page used to
 * carry at `#read`, unchanged. No VendorLensProvider — nothing rendered here
 * (JudgmentBoard, ThesisRunningScore, HeroContent, EvidenceLink) reads the
 * vendor lens; EvidenceLink's drawer comes from EvidenceProvider, which
 * already wraps every route in App() below.
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
        <Header path={path} />
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
