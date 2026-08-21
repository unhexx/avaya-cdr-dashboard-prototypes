import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Header } from './components/Header'
import { I18nProvider } from './i18n'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { ClassicPage } from './pages/ClassicPage'
import { ContactCenterPage } from './pages/ContactCenterPage'
import { DialplanPage } from './pages/DialplanPage'
import { HealthPage } from './pages/HealthPage'
import { LogsPage } from './pages/LogsPage'
import { ModernPage } from './pages/ModernPage'
import { RecordingsPage } from './pages/RecordingsPage'

function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <main>
            <Routes>
              {/* Четыре UI-оболочки CDR (ADR 0010 + алиасы Header) */}
              <Route path="/" element={<ClassicPage />} />
              <Route path="/classic" element={<ClassicPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/contact-center" element={<ContactCenterPage />} />
              <Route path="/cc" element={<ContactCenterPage />} />
              <Route path="/modern" element={<ModernPage />} />
              <Route path="/cards" element={<ModernPage />} />
              {/* Ops */}
              <Route path="/health" element={<HealthPage />} />
              <Route path="/dialplan" element={<DialplanPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/recordings" element={<RecordingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </I18nProvider>
  )
}

export default App
