import { ActivityBoard } from './components/ActivityBoard'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { HowThisWorks } from './components/HowThisWorks'
import { JudgmentBoard } from './components/JudgmentBoard'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { PrintGrid } from './components/PrintGrid'
import { SkipLink } from './components/SkipLink'
import { WatchList } from './components/WatchList'
import { EvidenceProvider } from './context/EvidenceProvider'
import { useEvidence } from './context/useEvidence'

function AppShell() {
  const { isOpen } = useEvidence()

  return (
    <>
      <SkipLink />
      <div className="app-shell" inert={isOpen ? true : undefined}>
        <Header />
        <main id="main" className="main-content" tabIndex={-1}>
          <Hero />
          <JudgmentBoard />
          <PrintGrid />
          <DomainBoard />
          <ActivityBoard />
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
        </main>
        <MethodologyNote />
      </div>
      <EvidenceDrawer />
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
