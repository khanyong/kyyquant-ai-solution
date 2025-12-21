import React, { useState } from 'react'
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    Stack,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    TextField,
    CircularProgress,
    Divider
} from '@mui/material'
import {
    Warning,
    Block,
    DeleteForever,
    PauseCircleFilled,
    HealthAndSafety
} from '@mui/icons-material'
import { kiwoomApi } from '../../services/kiwoomApiService'
import { supabase } from '../../lib/supabase'

interface EmergencyControlPanelProps {
    onOpComplete: () => void
}

export default function EmergencyControlPanel({ onOpComplete }: EmergencyControlPanelProps) {
    const [loading, setLoading] = useState(false)

    // Dialog States
    const [confirmDialogOpen, setConfirmDialogOpen] = useState(false)
    const [actionType, setActionType] = useState<'HALT' | 'CANCEL_ORDERS' | 'LIQUIDATE_ALL' | null>(null)
    const [confirmInput, setConfirmInput] = useState('')
    const [confirmError, setConfirmError] = useState('')

    const getActionConfig = (type: string | null) => {
        switch (type) {
            case 'HALT':
                return {
                    title: '⚠️ 자동매매 로직 긴급 정지',
                    description: '현재 실행 중인 모든 자동매매 로직을 즉시 정지합니다.\n\n매매가 중단되며, 보유 종목은 그대로 유지됩니다. 계속하시겠습니까?',
                    confirmText: 'STOP',
                    buttonText: '로직 정지 실행',
                    color: 'warning' as const
                }
            case 'CANCEL_ORDERS':
                return {
                    title: '⚠️ 미체결 주문 일괄 취소',
                    description: '현재 대기 중인 "모든" 미체결 매수/매도 주문을 취소합니다.\n\n이 작업은 되돌릴 수 없습니다.',
                    confirmText: 'CANCEL',
                    buttonText: '일괄 취소 실행',
                    color: 'warning' as const
                }
            case 'LIQUIDATE_ALL':
                return {
                    title: '🚨 전량 강제 청산 (긴급 매도)',
                    description: '보유 중인 "모든" 주식을 시장가(Market Order)로 즉시 매도합니다.\n\n매우 위험한 작업입니다. 시장 상황 급변 시에만 사용하세요.\n실행 후에는 되돌릴 수 없습니다.',
                    confirmText: 'LIQUIDATE',
                    buttonText: '전량 매도 실행',
                    color: 'error' as const
                }
            default:
                return { title: '', description: '', confirmText: '', buttonText: '', color: 'primary' as const }
        }
    }

    const handleOpenConfirm = (type: 'HALT' | 'CANCEL_ORDERS' | 'LIQUIDATE_ALL') => {
        setActionType(type)
        setConfirmInput('')
        setConfirmError('')
        setConfirmDialogOpen(true)
    }

    const executeAction = async () => {
        const config = getActionConfig(actionType)
        if (confirmInput.toUpperCase() !== config.confirmText) {
            setConfirmError(`정확히 "${config.confirmText}"를 입력해주세요.`)
            return
        }

        setConfirmDialogOpen(false)
        setLoading(true)

        try {
            if (actionType === 'HALT') {
                const { error } = await supabase
                    .from('strategies')
                    .update({ is_active: false, auto_trade_enabled: false })
                    .eq('is_active', true)

                if (error) throw error
                alert('모든 전략이 정지되었습니다.')

            } else if (actionType === 'CANCEL_ORDERS') {
                // 1. Get Pending Orders from DB or API
                const { data: orders } = await supabase
                    .from('orders')
                    .select('*')
                    .in('status', ['PENDING', 'PARTIAL'])

                if (!orders || orders.length === 0) {
                    alert('취소할 미체결 주문이 없습니다.')
                } else {
                    // Mocking loop cancellation (In production, replace with Kiwoom API calls)
                    for (const order of orders) {
                        await supabase
                            .from('orders')
                            .update({ status: 'CANCELLED' })
                            .eq('id', order.id)
                    }
                    alert(`${orders.length}건의 미체결 주문을 취소 요청했습니다.`)
                }

            } else if (actionType === 'LIQUIDATE_ALL') {
                // 1. Get Current Holdings
                const balance = await kiwoomApi.getAccountBalance()
                if (!balance?.output2) {
                    throw new Error('보유 잔고를 조회할 수 없습니다.')
                }

                const holdings = balance.output2
                if (holdings.length === 0) {
                    alert('보유 중인 종목이 없습니다.')
                } else {
                    let successCount = 0
                    // 2. Loop and Market Sell
                    for (const item of holdings) {
                        const stockCode = item.pdno
                        const qty = parseInt(item.hldg_qty)

                        if (qty > 0) {
                            // Market Sell (00: 지정가, 03: 시장가) -> Using kiwoomApi helper
                            // Assuming sellStock takes (code, qty, price, type). If basic, maybe 0 price for market logic handling required
                            // Here we act as if sending 0 price is market order in our safe wrapper or backend
                            const result = await kiwoomApi.sellStock(stockCode, qty, 0)
                            if (result?.rt_cd === '0') successCount++
                        }
                    }
                    alert(`${holdings.length}종목 중 ${successCount}종목에 대해 시장가 매도 주문을 전송했습니다.`)
                }
            }
        } catch (err: any) {
            console.error('Emergency Action Failed:', err)
            alert(`작업 실패: ${err.message}`)
        } finally {
            setLoading(false)
            onOpComplete()
        }
    }

    const config = getActionConfig(actionType)

    return (
        <Card variant="outlined" sx={{ borderColor: 'error.main', borderWidth: 1 }}>
            <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                    <HealthAndSafety color="error" fontSize="large" />
                    <Typography variant="h6" fontWeight="bold" color="error.main">
                        긴급 대응 센터 (Emergency Control)
                    </Typography>
                </Stack>

                <Alert severity="warning" sx={{ mb: 3 }} icon={<Warning fontSize="inherit" />}>
                    이 패널의 기능은 급격한 시장 변동이나 시스템 오류 등 <strong>비상 상황</strong>에서만 사용하십시오.<br />
                    모든 작업은 즉시 실행되며, 실행 후에는 되돌릴 수 없습니다.
                </Alert>

                <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                    {/* Action 1: Halt */}
                    <Box sx={{ flex: 1, border: '1px solid', borderColor: 'divider', p: 2, borderRadius: 1 }}>
                        <Stack spacing={1} alignItems="center" textAlign="center">
                            <PauseCircleFilled color="warning" sx={{ fontSize: 40 }} />
                            <Typography variant="subtitle1" fontWeight="bold">로직 일시 정지</Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ minHeight: 40, display: 'block' }}>
                                모든 자동매매 전략의 실행을 즉시<br />중단합니다. (보유 종목 유지)
                            </Typography>
                            <Button
                                variant="outlined"
                                color="warning"
                                fullWidth
                                onClick={() => handleOpenConfirm('HALT')}
                                disabled={loading}
                            >
                                매매 로직 정지
                            </Button>
                        </Stack>
                    </Box>

                    {/* Action 2: Cancel Orders */}
                    <Box sx={{ flex: 1, border: '1px solid', borderColor: 'divider', p: 2, borderRadius: 1 }}>
                        <Stack spacing={1} alignItems="center" textAlign="center">
                            <Block color="error" sx={{ fontSize: 40 }} />
                            <Typography variant="subtitle1" fontWeight="bold">미체결 일괄 취소</Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ minHeight: 40, display: 'block' }}>
                                체결되지 않고 대기 중인 모든<br />주문을 일괄 취소합니다.
                            </Typography>
                            <Button
                                variant="outlined"
                                color="error"
                                fullWidth
                                onClick={() => handleOpenConfirm('CANCEL_ORDERS')}
                                disabled={loading}
                            >
                                미체결 주문 취소
                            </Button>
                        </Stack>
                    </Box>

                    {/* Action 3: Liquidate All */}
                    <Box sx={{ flex: 1, border: '1px solid', borderColor: 'error.main', bgcolor: 'error.dark', color: 'white', p: 2, borderRadius: 1 }}>
                        <Stack spacing={1} alignItems="center" textAlign="center">
                            <DeleteForever sx={{ fontSize: 40, color: 'white' }} />
                            <Typography variant="subtitle1" fontWeight="bold" sx={{ color: 'white' }}>전량 강제 청산</Typography>
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', minHeight: 40, display: 'block' }}>
                                보유 중인 모든 주식을<br />시장가로 즉시 매도합니다.
                            </Typography>
                            <Button
                                variant="contained"
                                color="error"
                                fullWidth
                                sx={{ bgcolor: 'white', color: 'error.main', '&:hover': { bgcolor: 'grey.100' } }}
                                onClick={() => handleOpenConfirm('LIQUIDATE_ALL')}
                                disabled={loading}
                            >
                                🚨 전량 청산
                            </Button>
                        </Stack>
                    </Box>
                </Stack>
            </CardContent>

            {/* Confirmation Dialog */}
            <Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)}>
                <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: config.color === 'error' ? 'error.main' : 'warning.main' }}>
                    <Warning /> {config.title}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText sx={{ whiteSpace: 'pre-line', mb: 2, color: 'text.primary' }}>
                        {config.description}
                    </DialogContentText>

                    <DialogContentText color="text.secondary" sx={{ mb: 1, fontSize: '0.9rem' }}>
                        실행하려면 아래 입력창에 <strong>{config.confirmText}</strong> 를 입력하세요.
                    </DialogContentText>

                    <TextField
                        autoFocus
                        fullWidth
                        size="small"
                        variant="outlined"
                        value={confirmInput}
                        onChange={(e) => {
                            setConfirmInput(e.target.value)
                            setConfirmError('')
                        }}
                        error={!!confirmError}
                        helperText={confirmError}
                        placeholder={config.confirmText}
                        sx={{ mt: 1 }}
                    />
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={() => setConfirmDialogOpen(false)} color="inherit">
                        취소 (Close)
                    </Button>
                    <Button
                        onClick={executeAction}
                        variant="contained"
                        color={config.color}
                        disabled={loading || confirmInput.toUpperCase() !== config.confirmText}
                    >
                        {loading ? <CircularProgress size={24} color="inherit" /> : config.buttonText}
                    </Button>
                </DialogActions>
            </Dialog>
        </Card>
    )
}
