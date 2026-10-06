import { Alert, Box, Button, TextField, Typography } from '@mui/material'
import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import logo from '../assets/DavidBank.png'
import { api, errorMessage, type Envelope } from '../api/client'
import { useSession } from '../auth/session'

type LoginData = {
  access_token: string
  token_type: string
  user_dto: {
    email: string
    display_name: string
    role: string
  }
}

export function LoginPage() {
  const navigate = useNavigate()
  const { session, saveSession } = useSession()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  if (session) {
    return <Navigate to="/home" replace />
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setMessage('')
    try {
      const response = await api.post<Envelope<LoginData>>('/auth/login', { email, password })
      const user = response.data.data.user_dto
      saveSession({
        accessToken: response.data.data.access_token,
        displayName: user.display_name,
        email: user.email,
        role: user.role,
      })
      navigate('/home')
    } catch (error) {
      setMessage(errorMessage(error, 'Login failed'))
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: 'radial-gradient(ellipse at top, #2c2c2c 0%, #141414 55%)',
      }}
    >
      <Box
        component="form"
        onSubmit={submit}
        sx={{
          width: { xs: '92%', sm: 420 },
          p: 4,
          borderRadius: 3,
          border: '1px solid #3a3a3a',
          bgcolor: 'rgba(28,28,28,0.92)',
          boxShadow: '0 30px 80px rgba(0,0,0,0.45)',
          display: 'grid',
          justifyItems: 'center',
          gap: 2,
        }}
      >
        <Box component="img" src={logo} alt="David Bank" sx={{ width: 220, display: 'block' }} />
        <Typography variant="overline" sx={{ letterSpacing: 4, color: 'text.secondary' }}>
          Sign in
        </Typography>
        {message ? (
          <Alert severity="error" sx={{ width: '100%' }}>
            {message}
          </Alert>
        ) : null}
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          fullWidth
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          fullWidth
        />
        <Button type="submit" variant="contained" fullWidth size="large" sx={{ mt: 1 }}>
          Enter
        </Button>
      </Box>
    </Box>
  )
}
