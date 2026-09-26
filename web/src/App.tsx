import { Analytics } from '@vercel/analytics/react'
import type { ReactNode } from 'react'
import { ActivityBoard } from './components/ActivityBoard'
import { ArchiveLinks } from './components/ArchiveLinks'
import { Corrections } from './components/Corrections'
import { CoverageStatement } from './components/CoverageStatement'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { FollowLine } from './components/FollowLine'
import { Header } from './components/Header'
import { HeroContent } from './components/Hero'
import { HowThisWorks } from './components/HowThisWorks'
import { IssueArchive } from './components/IssueArchive'
import { IssueHero } from './components/IssueHero'
import { IssueLanes } from './components/IssueLanes'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketByDomain } from './components/MarketByDomain'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { NextEdition } from './components/NextEdition'
import { ProvenanceRail } from './components/ProvenanceRail'
import { RunStatus } from './components/RunStatus'
import { SiteMasthead } from './components/SiteMasthead'
import { SkipLink } from './components/SkipLink'
import { ThesisRunningScore } from './components/ThesisRunningScore'
import { WeThink } from './components/WeThink'
import { WhatChangedTracker } from './components/WhatChangedTracker'
import { WhatMoved } from './components/WhatMoved'
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

/**
 * `/` — what the site is, the run status, the twelve-domain supplier
 * tracker, and the standing reference and depth sections.
 *
 * D-76/autonomy-coverage-plan.md §3, step 1 ("Judged text leaves the live
 * pages"): every judged element that used to sit on this page — the
 * weekly-issue headline strip, "What we now think", the domain stance chips
 * and JUDGED stamps, tracked hypotheses, the standing-thesis pointer at
 * `#read`, and "Watch next" — is gone from this route. `RunStatus`
 * (`#overview`, replacing the old `IssueStrip`) is the first-screen element:
 * an honest statement of whether collection ran and whether it was
 * complete, never a judgment.
 *
 * Step 5 (autonomy-coverage-plan.md §3): the old `MarketPicture` ("the
 * market by domain" section), `PrintGrid` (the scorecard), and the week-36
 * `IssueLanes` that used to sit here are replaced by the twelve-domain
 * tracker — `MarketByDomain`, `WhatChangedTracker`, `CoverageStatement`, and
 * `ArchiveLinks`, built from `data/tracker/{domains,suppliers,events}.ts`.
 * None of the three old components is deleted; they simply have no route
 * rendering them on the front page now, the same as `DomainBoard`'s
 * `TempoSection`. `VendorLensProvider`/`VendorLens` also stop rendering here
 * — both existed only to filter `PrintGrid` and this page's `IssueLanes`,
 * and with both gone the lens has nothing left on this route to filter;
 * their files and the `useVendorLens` hook are untouched, and the issue
 * permalink page (which never mounted the provider) is unaffected.
 *
 * Step 1 fix pass, item 3: the entire Platform-pressure section is gone from
 * this route too, not just its judged "read" column — every row in that
 * table carried a hand-assigned vendor-position label (Holding / Buying in /
 * Outrun / Challengers, i.e. incumbent / challenger / early / platform /
 * absorbed), which describes competitive footing the site no longer states.
 * `PlatformPressure.tsx` itself is untouched and still exported; it simply
 * has no route rendering it now, the same as `DomainBoard`'s `TempoSection`.
 */
function FrontPage() {
  return (
    <>
      <SiteMasthead />
      <RunStatus />
      <MarketByDomain />
      <WhatChangedTracker />
      <CoverageStatement />
      <ArchiveLinks />
      <FollowLine />
      <DomainBoard />

      <details className="depth" id="moved-depth">
        <summary>What moved: tracked prints and capital</summary>
        <WhatMoved />
      </details>
      <details className="depth" id="research-depth">
        <summary>M&amp;A and funding activity</summary>
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
    </>
  )
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
