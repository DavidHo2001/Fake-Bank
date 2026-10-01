export type Session = {
  accessToken: string
  displayName: string
  email: string
  role: string
}

const KEY = 'david-bank-session'

export function loadSession(): Session | null {
  const raw = localStorage.getItem(KEY)
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw) as Session
  } catch {
    return null
  }
}

export function saveSession(session: Session): void {
  localStorage.setItem(KEY, JSON.stringify(session))
}

export function clearSession(): void {
  localStorage.removeItem(KEY)
}
