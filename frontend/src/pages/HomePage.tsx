import { Box, Typography } from '@mui/material'
import logo from '../assets/DavidBank.png'
import homeMock from './homeMock.json'

const cardSx = {
  border: '1px solid #333',
  borderRadius: 3,
  p: 2.5,
  bgcolor: '#242424',
}

export function HomePage() {
  const users = homeMock.usersByMonth
  const latest = users[users.length - 1]
  const first = users[0]
  const growth = Math.round(((latest.users - first.users) / first.users) * 100)

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '300px 1fr' },
        gap: 3,
        alignItems: 'start',
      }}
    >
      <Box
        sx={{
          bgcolor: '#111',
          border: '1px solid #333',
          borderRadius: 3,
          minHeight: { md: 520 },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2,
        }}
      >
        <Box component="img" src={logo} alt="David Bank" sx={{ width: '100%', display: 'block' }} />
      </Box>

      <Box>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          David Bank
        </Typography>
        <Typography sx={{ mt: 1, maxWidth: 640, color: 'text.secondary' }}>
          David Bank is a demo merchant bank. It shows how a payment gateway prices a charge — percent
          fee, fixed fee, minimum fee, FX markup — and where the expected net differs from the settled
          amount.
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mt: 3 }}>
          <Box sx={cardSx}>
            <Typography variant="overline" color="text.secondary">
              Active users
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, lineHeight: 1.1 }}>
              {latest.users.toLocaleString()}
            </Typography>
            <Typography variant="body2" sx={{ color: '#3dd68c', mb: 2 }}>
              +{growth}% since {first.month}
            </Typography>
            <UserChart points={users} />
          </Box>

          <Box sx={cardSx}>
            <Typography variant="overline" color="text.secondary">
              Service fee vs other banks
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Illustrative percent fee. Live rates stay on Fee Schedule.
            </Typography>
            <FeeChart rows={homeMock.serviceFeeCompare} />
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

function UserChart({ points }: { points: { month: string; users: number }[] }) {
  const width = 320
  const height = 150
  const max = Math.max(...points.map((point) => point.users))
  const min = Math.min(...points.map((point) => point.users))
  const span = max - min || 1
  const coords = points.map((point, index) => {
    const x = 12 + (index / (points.length - 1)) * (width - 24)
    const y = 16 + (1 - (point.users - min) / span) * (height - 48)
    return { ...point, x, y }
  })
  const line = coords.map((point) => `${point.x},${point.y}`).join(' ')
  const area = `${coords[0].x},${height - 22} ${line} ${coords[coords.length - 1].x},${height - 22}`

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="Users by month">
      <polygon points={area} fill="#fff" opacity="0.12" />
      <polyline points={line} fill="none" stroke="#fff" strokeWidth="2.5" />
      {coords.map((point) => (
        <g key={point.month}>
          <circle cx={point.x} cy={point.y} r="3.5" fill="#fff" />
          <text x={point.x} y={height - 6} textAnchor="middle" fontSize="11" fill="#9a9a9a">
            {point.month}
          </text>
        </g>
      ))}
    </svg>
  )
}

function FeeChart({ rows }: { rows: { bank: string; percentFee: number }[] }) {
  const max = Math.max(...rows.map((row) => row.percentFee))

  return (
    <Box sx={{ display: 'grid', gap: 1.5 }}>
      {rows.map((row) => {
        const ours = row.bank === 'David Bank'
        return (
          <Box key={row.bank}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2" sx={{ fontWeight: ours ? 700 : 500 }}>
                {row.bank}
              </Typography>
              <Typography variant="body2">{row.percentFee.toFixed(1)}%</Typography>
            </Box>
            <Box sx={{ height: 8, bgcolor: '#333', borderRadius: 99 }}>
              <Box
                sx={{
                  width: `${(row.percentFee / max) * 100}%`,
                  height: '100%',
                  borderRadius: 99,
                  bgcolor: ours ? '#f4f4f4' : '#666',
                }}
              />
            </Box>
          </Box>
        )
      })}
    </Box>
  )
}
