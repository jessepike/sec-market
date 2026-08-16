import { ConversationPrompts } from './components/ConversationPrompts'
import { DomainBoard } from './components/DomainBoard'
import { EvidenceDrawer } from './components/EvidenceDrawer'
import { EvidenceLibrary } from './components/EvidenceLibrary'
import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { MarketLayersChart } from './components/MarketLayersChart'
import { MethodologyNote } from './components/MethodologyNote'
import { SignalFeed } from './components/SignalFeed'
import { SummaryCards } from './components/SummaryCards'
import { EvidenceProvider } from './context/EvidenceContext'

function App() {
  return (
    <EvidenceProvider>
      <Header />
      <main className="main-content">
        <Hero />
        <SummaryCards />
        <MarketLayersChart />
        <DomainBoard />
        <SignalFeed />
        <ConversationPrompts />
        <EvidenceLibrary />
      </main>
      <MethodologyNote />
      <EvidenceDrawer />
    </EvidenceProvider>
  )
}

export default App
