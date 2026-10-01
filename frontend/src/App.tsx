import { Navigate, Route, Routes } from 'react-router-dom'
import { loadSession } from './auth/session'
import { AppShell } from './layout/AppShell'
import { FeeSchedulePage } from './pages/FeeSchedulePage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { TransactionPage } from './pages/TransactionPage'

function RequireAuth() {
  if (!loadSession()) {
    return <Navigate to="/" replace />
  }
  return <AppShell />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/home" element={<HomePage />} />
        <Route path="/fee-schedules" element={<FeeSchedulePage />} />
        <Route path="/transactions" element={<TransactionPage />} />
      </Route>
    </Routes>
  )
}
