import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { SignalFeed } from './components/SignalFeed'
import { SkipLink } from './components/SkipLink'
import { SummaryCards } from './components/SummaryCards'
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
          <SummaryCards />
          <MarketLayersChart />
          <DomainBoard />
          <SignalFeed />
          <EvidenceLibrary />
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
