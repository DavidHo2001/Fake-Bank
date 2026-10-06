import axios from 'axios'
import { getAccessToken, notifyUnauthorized } from '../auth/session'

export const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401 && getAccessToken()) {
      notifyUnauthorized()
    }
    return Promise.reject(error)
  },
)

export type Envelope<T> = {
  status: 'success' | 'error'
  data: T
}

export type Page<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
}

export function errorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.data?.message
    if (typeof message === 'string') {
      return message
    }
  }
  return fallback
}
