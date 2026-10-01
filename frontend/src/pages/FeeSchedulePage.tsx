import { Alert, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { api, errorMessage, type Envelope, type Page } from '../api/client'

type FeeSchedule = {
  gateway_name: string
  version_code: string
  txn_type: string
  effective_from: string
  effective_to: string | null
  settlement_currency: string
  percent_rate: string
  fixed_fee: string
  min_fee: string
  fx_markup_bps: number
  failed_attempt_fee: string
  refund_returns_percent_fee: boolean
}

export function FeeSchedulePage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [rows, setRows] = useState<FeeSchedule[]>([])
  const [total, setTotal] = useState(0)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let cancelled = false
    api
      .get<Envelope<Page<FeeSchedule>>>('/fee-schedules', { params: { page, page_size: pageSize } })
      .then((response) => {
        if (cancelled) return
        setRows(response.data.data.items)
        setTotal(response.data.data.total)
        setMessage('')
      })
      .catch((error: unknown) => {
        if (!cancelled) setMessage(errorMessage(error, 'Could not load fee schedules'))
      })
    return () => {
      cancelled = true
    }
  }, [page, pageSize])

  return (
    <>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Fee Schedule
      </Typography>
      {message ? <Alert severity="error">{message}</Alert> : null}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Gateway</TableCell>
            <TableCell>Version</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>From</TableCell>
            <TableCell>To</TableCell>
            <TableCell>Currency</TableCell>
            <TableCell>Percent</TableCell>
            <TableCell>Fixed</TableCell>
            <TableCell>Min</TableCell>
            <TableCell>FX bps</TableCell>
            <TableCell>Failed fee</TableCell>
            <TableCell>Refund returns %</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={`${row.gateway_name}-${row.version_code}-${row.txn_type}`}>
              <TableCell>{row.gateway_name}</TableCell>
              <TableCell>{row.version_code}</TableCell>
              <TableCell>{row.txn_type}</TableCell>
              <TableCell>{row.effective_from}</TableCell>
              <TableCell>{row.effective_to ?? ''}</TableCell>
              <TableCell>{row.settlement_currency}</TableCell>
              <TableCell>{row.percent_rate}</TableCell>
              <TableCell>{row.fixed_fee}</TableCell>
              <TableCell>{row.min_fee}</TableCell>
              <TableCell>{row.fx_markup_bps}</TableCell>
              <TableCell>{row.failed_attempt_fee}</TableCell>
              <TableCell>{row.refund_returns_percent_fee ? 'yes' : 'no'}</TableCell>
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
