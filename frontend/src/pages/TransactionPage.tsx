import { Alert, Box, Button, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { api, errorMessage, type Envelope, type Page } from '../api/client'

type Transaction = {
  txn_ref: string
  gateway_name: string
  owner_display_name: string
  txn_type: string
  status: string
  occurred_at: string
  gross_amount: string
  gross_currency: string
  total_fee: string
  expected_net: string
  settled_amount: string | null
  variance_amount: string | null
  mismatch_code: string | null
}

export function TransactionPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [applied, setApplied] = useState({ from: '', to: '' })
  const [rows, setRows] = useState<Transaction[]>([])
  const [total, setTotal] = useState(0)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let cancelled = false
    const params: Record<string, string | number> = { page, page_size: pageSize }
    if (applied.from) params.occurred_from = applied.from
    if (applied.to) params.occurred_to = applied.to
    api
      .get<Envelope<Page<Transaction>>>('/transactions', { params })
      .then((response) => {
        if (cancelled) return
        setRows(response.data.data.items)
        setTotal(response.data.data.total)
        setMessage('')
      })
      .catch((error: unknown) => {
        if (!cancelled) setMessage(errorMessage(error, 'Could not load transactions'))
      })
    return () => {
      cancelled = true
    }
  }, [page, pageSize, applied])

  return (
    <>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Transaction
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField label="From" type="date" value={from} onChange={(event) => setFrom(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} />
        <TextField label="To" type="date" value={to} onChange={(event) => setTo(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} />
        <Button
          variant="contained"
          onClick={() => {
            setPage(1)
            setApplied({ from, to })
          }}
        >
          Apply
        </Button>
      </Box>
      {message ? <Alert severity="error">{message}</Alert> : null}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Ref</TableCell>
            <TableCell>When</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Gateway</TableCell>
            <TableCell>Owner</TableCell>
            <TableCell>Gross</TableCell>
            <TableCell>Fee</TableCell>
            <TableCell>Expected net</TableCell>
            <TableCell>Settled</TableCell>
            <TableCell>Variance</TableCell>
            <TableCell>Mismatch</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.txn_ref}>
              <TableCell>{row.txn_ref}</TableCell>
              <TableCell>{new Date(row.occurred_at).toLocaleString()}</TableCell>
              <TableCell>{row.txn_type}</TableCell>
              <TableCell>{row.status}</TableCell>
              <TableCell>{row.gateway_name}</TableCell>
              <TableCell>{row.owner_display_name}</TableCell>
              <TableCell>
                {row.gross_amount} {row.gross_currency}
              </TableCell>
              <TableCell>{row.total_fee}</TableCell>
              <TableCell>{row.expected_net}</TableCell>
              <TableCell>{row.settled_amount ?? ''}</TableCell>
              <TableCell>{row.variance_amount ?? ''}</TableCell>
              <TableCell>{row.mismatch_code ?? ''}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={total}
        page={page - 1}
        onPageChange={(_event, next) => setPage(next + 1)}
        rowsPerPage={pageSize}
        onRowsPerPageChange={(event) => {
          setPageSize(Number(event.target.value))
          setPage(1)
        }}
        rowsPerPageOptions={[10, 20, 50]}
      />
    </>
  )
}
