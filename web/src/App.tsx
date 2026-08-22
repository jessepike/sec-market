import { Analytics } from '@vercel/analytics/react'
import { ActivityBoard } from './components/ActivityBoard'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { HowThisWorks } from './components/HowThisWorks'
import { Hypotheses } from './components/Hypotheses'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { NextEdition } from './components/NextEdition'
import { PlatformPressure } from './components/PlatformPressure'
import { PrintGrid } from './components/PrintGrid'
import { ProvenanceRail } from './components/ProvenanceRail'
import { SkipLink } from './components/SkipLink'
import { WatchList } from './components/WatchList'
import { WhatMoved } from './components/WhatMoved'
import { EvidenceProvider } from './context/EvidenceProvider'
import { useEvidence } from './context/useEvidence'

function AppShell() {
  const { isOpen } = useEvidence()

  return (
    <>
      <SkipLink />
      <ProvenanceRail />
      <div className="app-shell" inert={isOpen ? true : undefined}>
        <Header />
        <main id="main" className="main-content" tabIndex={-1}>
          <DomainBoard />
          <WhatMoved />
          <PlatformPressure />
          <Hypotheses />
          <PrintGrid />
          <details className="depth" id="research-depth">
            <summary>The market read, domain tempo and M&amp;A activity</summary>
            <Hero />
            <JudgmentBoard />
            <DomainBoard surface="tempo" />
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

function App() {
  return (
    <EvidenceProvider>
      <AppShell />
    </EvidenceProvider>
  )
}

export default App
