import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stack,
  FormControl,
  InputLabel,
  OutlinedInput,
  InputAdornment,
  Alert,
  Typography,
  Box
} from '@mui/material'
import { supabase } from '../../lib/supabase'

interface EditStrategyDialogProps {
  open: boolean
  strategyId: string | null
  strategyName: string
  currentAllocatedCapital: number
  currentAllocatedPercent: number
  onClose: () => void
  onSuccess: () => void
}

export default function EditStrategyDialog({
  open,
  strategyId,
  strategyName,
  currentAllocatedCapital,
  currentAllocatedPercent,
  onClose,
  onSuccess
}: EditStrategyDialogProps) {
  const [allocatedCapital, setAllocatedCapital] = useState<number>(0)
  const [allocatedPercent, setAllocatedPercent] = useState<number>(0)
  const [accountBalance, setAccountBalance] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (open) {
      setAllocatedCapital(currentAllocatedCapital)
      setAllocatedPercent(currentAllocatedPercent)
      setError('')
      loadAccountBalance()
    }
  }, [open, currentAllocatedCapital, currentAllocatedPercent])

  const loadAccountBalance = async () => {
    try {
      const { data, error } = await supabase
        .from('kw_account_balance')
        .select('deposit')
        .order('updated_at', { ascending: false })
        .limit(1)
        .single()

      if (error) {
        console.error('계좌 잔고 조회 실패:', error)
        return
      }

      if (data) {
        setAccountBalance(data.deposit)
      }
    } catch (error) {
      console.error('계좌 잔고 조회 오류:', error)
    }
  }

  const handleSave = async () => {
    if (!strategyId) {
      setError('전략 ID가 없습니다.')
      return
    }

    if (allocatedPercent <= 0) {
      setError('할당 비율을 입력해주세요 (0보다 커야 합니다)')
      return
    }

    try {
      setLoading(true)
      setError('')

      const { error: updateError } = await supabase
        .from('strategies')
        .update({
          allocated_capital: allocatedCapital || 0,
          allocated_percent: allocatedPercent || 0
        })
        .eq('id', strategyId)

      if (updateError) throw updateError

      // 성공
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('전략 수정 실패:', error)
      setError(`전략 수정 실패: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6" fontWeight="bold">
          ⚙️ 전략 수정
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Stack spacing={3}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              전략명
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {strategyName}
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              💰 자금 할당 수정
            </Typography>

            <Stack spacing={2}>
              {accountBalance > 0 && (
                <Alert severity="info">
                  현재 예수금: <strong>{accountBalance.toLocaleString()}원</strong>
                </Alert>
              )}

              <Stack direction="row" spacing={2}>
                <FormControl fullWidth>
                  <InputLabel>할당 비율 (%)</InputLabel>
                  <OutlinedInput
                    type="number"
                    value={allocatedPercent}
                    onChange={(e) => {
                      const percent = parseFloat(e.target.value) || 0
                      setAllocatedPercent(percent)
                      // 자동으로 할당 금액 계산
                      if (accountBalance > 0) {
                        setAllocatedCapital(Math.round(accountBalance * percent / 100))
                      }
                    }}
                    label="할당 비율 (%)"
                    endAdornment={<InputAdornment position="end">%</InputAdornment>}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>할당 금액 (원)</InputLabel>
                  <OutlinedInput
                    type="number"
                    value={allocatedCapital}
                    onChange={(e) => {
                      const capital = parseFloat(e.target.value) || 0
                      setAllocatedCapital(capital)
                      // 역계산: 금액 입력 시 비율 자동 계산
                      if (accountBalance > 0) {
                        setAllocatedPercent(Math.round(capital / accountBalance * 100 * 100) / 100)
                      }
                    }}
                    label="할당 금액 (원)"
                    endAdornment={<InputAdornment position="end">원</InputAdornment>}
                  />
                </FormControl>
              </Stack>

              {allocatedPercent > 0 && (
                <Typography variant="caption" color="text.secondary">
                  💡 {allocatedPercent}% = {allocatedCapital.toLocaleString()}원
                </Typography>
              )}
            </Stack>
          </Box>
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          취소
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={loading || allocatedPercent <= 0}
        >
          {loading ? '저장 중...' : '저장'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
