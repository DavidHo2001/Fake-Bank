import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import LogoutIcon from '@mui/icons-material/Logout'
import { AppBar, Box, Button, IconButton, Toolbar, Typography } from '@mui/material'
import { Link as RouterLink, Outlet, useNavigate } from 'react-router-dom'
import logo from '../assets/DavidBank-Icon.png'
import { clearSession, loadSession } from '../auth/session'

export function AppShell() {
  const navigate = useNavigate()
  const session = loadSession()

  function logout() {
    clearSession()
    navigate('/')
  }

  return (
    <>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: '#121212', borderBottom: '1px solid #2c2c2c' }}>
        <Toolbar sx={{ minHeight: 80 }}>
          <IconButton
            component={RouterLink}
            to="/home"
            edge="start"
            aria-label="Home"
            sx={{ p: 0, mr: 2, width: 72, height: 72, overflow: 'hidden', position: 'relative' }}
          >
            <Box
              component="img"
              src={logo}
              alt="David Bank"
              sx={{ position: 'absolute', width: 259, height: 144, maxWidth: 'none', left: -93, top: -22 }}
            />
          </IconButton>
          <Button component={RouterLink} to="/fee-schedules" color="inherit">
            Fee Schedule
          </Button>
          <Button component={RouterLink} to="/transactions" color="inherit">
            Transaction
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <AccountCircleIcon />
          <Typography sx={{ mx: 1 }}>{session?.displayName}</Typography>
          <IconButton color="inherit" aria-label="Logout" onClick={logout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ p: 3 }}>
        <Outlet />
      </Box>
    </>
  )
}
