import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

export type Session = {
  accessToken: string
  displayName: string
  email: string
  role: string
}

type AuthContextValue = {
  session: Session | null
  saveSession: (session: Session) => void
  clearSession: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)
const STORAGE_KEY = 'david-bank-session'

function readStoredSession(): Session | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as Session
  } catch {
    return null
  }
}

const initialSession = readStoredSession()
let accessToken: string | null = initialSession?.accessToken ?? null
let onUnauthorized: (() => void) | null = null

function persist(next: Session | null) {
  accessToken = next?.accessToken ?? null
  if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  else localStorage.removeItem(STORAGE_KEY)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(initialSession)

  const saveSession = useCallback((next: Session) => {
    persist(next)
    setSession(next)
  }, [])

  const clearSession = useCallback(() => {
    persist(null)
    setSession(null)
  }, [])

  useEffect(() => {
    onUnauthorized = () => {
      persist(null)
      setSession(null)
      if (window.location.pathname !== '/') {
        window.location.assign('/')
      }
    }
    return () => {
      onUnauthorized = null
    }
  }, [])

  return <AuthContext.Provider value={{ session, saveSession, clearSession }}>{children}</AuthContext.Provider>
}

export function useSession(): AuthContextValue {
  const value = useContext(AuthContext)
  if (!value) {
    throw new Error('useSession must be used within AuthProvider')
  }
  return value
}

export function getAccessToken(): string | null {
  return accessToken
}

export function notifyUnauthorized(): void {
  onUnauthorized?.()
}
