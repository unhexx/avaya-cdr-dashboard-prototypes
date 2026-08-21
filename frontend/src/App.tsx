import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Header } from './components/Header'
import { DialplanPage } from './pages/DialplanPage'
import { HealthPage } from './pages/HealthPage'
import { LogsPage } from './pages/LogsPage'
import { RecordingsPage } from './pages/RecordingsPage'

function Home() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-primary mb-2">Aquarius CDR Dashboard Prototypes</h1>
      <p className="text-muted-foreground mb-8">Четыре UI-прототипа для анализа Avaya CDR под брендом Aquarius.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to="/classic" className="p-6 border rounded-lg hover:border-primary transition-colors bg-card">
          <h2 className="text-xl font-semibold mb-1">1. Classic Advanced Table</h2>
          <p className="text-sm text-muted-foreground">Плотный табличный вид с advanced filters, виртуализацией и экспортом</p>
        </Link>
        <Link to="/analytics" className="p-6 border rounded-lg hover:border-primary transition-colors bg-card">
          <h2 className="text-xl font-semibold mb-1">2. Analytics Dashboard</h2>
          <p className="text-sm text-muted-foreground">KPI-карточки, графики и drill-down в таблицу</p>
        </Link>
        <Link to="/contact-center" className="p-6 border rounded-lg hover:border-primary transition-colors bg-card">
          <h2 className="text-xl font-semibold mb-1">3. Contact Center Focus</h2>
          <p className="text-sm text-muted-foreground">VDN, агенты, SLA, heatmap для супервизоров</p>
        </Link>
        <Link to="/modern" className="p-6 border rounded-lg hover:border-primary transition-colors bg-card">
          <h2 className="text-xl font-semibold mb-1">4. Modern Cards + Timeline</h2>
          <p className="text-sm text-muted-foreground">Карточки звонков, timeline, mobile-friendly</p>
        </Link>
      </div>
    </div>
  )
}

function Placeholder({ title }: { title: string }) {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold text-primary mb-2">{title}</h1>
      <p className="text-muted-foreground">В разработке... См. PROJECT_SPECIFICATION.md</p>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background text-foreground">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/classic" element={<Placeholder title="Prototype 1: Classic Advanced Table" />} />
            <Route path="/analytics" element={<Placeholder title="Prototype 2: Analytics Dashboard" />} />
            <Route path="/contact-center" element={<Placeholder title="Prototype 3: Contact Center Focus" />} />
            <Route path="/modern" element={<Placeholder title="Prototype 4: Modern Cards + Timeline" />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/dialplan" element={<DialplanPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/recordings" element={<RecordingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
