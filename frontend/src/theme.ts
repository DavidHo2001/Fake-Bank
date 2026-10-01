import { createTheme } from '@mui/material'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#1a1a1a',
      paper: '#242424',
    },
    primary: { main: '#f4f4f4' },
    text: {
      primary: '#f3f3f3',
      secondary: '#a0a0a0',
    },
    divider: '#333',
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: { color: '#111' },
      },
    },
  },
})
