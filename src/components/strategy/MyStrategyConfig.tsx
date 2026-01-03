import React, { useState, useEffect } from 'react'
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stack,
    Typography,
    InputAdornment,
    Switch,
    FormControlLabel,
    Alert,
    Box,
    CircularProgress,
    OutlinedInput
} from '@mui/material'
import { Settings, Save } from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { Strategy } from '../../services/strategyService'

interface MyStrategyConfigProps {
    open: boolean
    onClose: () => void
    strategy: Strategy | null
    onSave: () => void
}

const MyStrategyConfig: React.FC<MyStrategyConfigProps> = ({
    open,
    onClose,
    strategy,
    onSave
}) => {
    const [loading, setLoading] = useState(false)
    const [universes, setUniverses] = useState<{ id: string; name: string }[]>([])
    const [selectedUniverseId, setSelectedUniverseId] = useState<string>('')
    const [allocatedCapital, setAllocatedCapital] = useState<number>(0)
    const [allocatedPercent, setAllocatedPercent] = useState<number>(0)
    const [accountBalance, setAccountBalance] = useState<number>(0)
    const [isActive, setIsActive] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (open && strategy) {
            loadUniverses()
            loadStrategyDetails()
            loadAccountBalance()
        }
    }, [open, strategy])

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

    const loadUniverses = async () => {
        try {
            const { data, error } = await supabase
                .from('kw_investment_filters')
                .select('id, name')
                .eq('is_active', true)
                .order('created_at', { ascending: false })

            if (error) throw error
            setUniverses(data || [])
        } catch (err) {
            console.error('Failed to load universes:', err)
        }
    }

    const loadStrategyDetails = async () => {
        if (!strategy) return
        setLoading(true)
        try {
            // 1. Load Strategy Settings
            setAllocatedCapital(strategy.allocated_capital || 0)
            setAllocatedPercent(strategy.allocated_percent || 0)
            setIsActive(strategy.is_active)

            // 2. Load Linked Universe
            const { data, error } = await supabase
                .from('strategy_universes')
                .select('investment_filter_id')
                .eq('strategy_id', strategy.id)
                .eq('is_active', true)
                .single()

            if (error && error.code !== 'PGRST116') { // PGRST116: no rows result
                console.error('Error fetching universe link:', error)
            }

            if (data) {
                setSelectedUniverseId(data.investment_filter_id)
            } else {
                setSelectedUniverseId('')
            }
        } catch (err) {
            console.error('Failed to load strategy details:', err)
            setError('설정 정보를 불러오는데 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        if (!strategy) return
        setLoading(true)
        setError(null)

        if (allocatedPercent < 0 || allocatedPercent > 100) {
            setError('할당 비율은 0~100 사이여야 합니다.')
            setLoading(false)
            return
        }

        try {
            // 1. Update Strategy (Capital & Active Status)
            const { error: updateError } = await supabase
                .from('strategies')
                .update({
                    allocated_capital: allocatedCapital,
                    allocated_percent: allocatedPercent,
                    is_active: isActive,
                    updated_at: new Date().toISOString()
                })
                .eq('id', strategy.id)

            if (updateError) throw updateError

            // 2. Update Universe Link (Upsert logic)
            if (selectedUniverseId) {
                // First, deactivate any existing links
                await supabase
                    .from('strategy_universes')
                    .update({ is_active: false })
                    .eq('strategy_id', strategy.id)

                // Then insert/activate the new one
                const { error: linkError } = await supabase
                    .from('strategy_universes')
                    .upsert({
                        strategy_id: strategy.id,
                        investment_filter_id: selectedUniverseId,
                        is_active: true
                    }, { onConflict: 'strategy_id, investment_filter_id' })

                if (linkError) throw linkError
            }

            onSave()
            onClose()
        } catch (err) {
            console.error('Save failed:', err)
            setError('설정 저장에 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Settings />
                전략 설정 ({strategy?.name})
            </DialogTitle>

            <DialogContent>
                {loading && !universes.length ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <Stack spacing={3} sx={{ mt: 1 }}>
                        {error && <Alert severity="error">{error}</Alert>}

                        {/* 1. Universe Selection */}
                        <FormControl fullWidth>
                            <InputLabel>투자 유니버스 (종목 필터)</InputLabel>
                            <Select
                                value={selectedUniverseId}
                                label="투자 유니버스 (종목 필터)"
                                onChange={(e) => setSelectedUniverseId(e.target.value)}
                            >
                                <MenuItem value="">
                                    <em>선택 안함 (전체 종목 대상 - 위험)</em>
                                </MenuItem>
                                {universes.map((u) => (
                                    <MenuItem key={u.id} value={u.id}>
                                        {u.name}
                                    </MenuItem>
                                ))}
                            </Select>
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                * 유니버스 빌더에서 저장한 필터 목록입니다.
                            </Typography>
                        </FormControl>

                        {/* 2. Capital Allocation */}
                        <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                            <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                                💰 자금 할당 설정
                            </Typography>

                            {accountBalance > 0 && (
                                <Alert severity="info" sx={{ mb: 2, py: 0 }}>
                                    현재 예수금: {accountBalance.toLocaleString()}원
                                </Alert>
                            )}

                            <Stack spacing={2}>
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
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                * 이 전략에 할당할 최대 금액입니다. 비율을 조정하면 금액이 자동 계산됩니다.
                            </Typography>
                        </Box>

                        {/* 3. Activation Switch */}
                        <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={isActive}
                                        onChange={(e) => setIsActive(e.target.checked)}
                                        color="success"
                                        disabled={allocatedCapital <= 0}
                                    />
                                }
                                label={
                                    <Typography fontWeight="bold">
                                        전략 활성화 (Active)
                                    </Typography>
                                }
                            />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, ml: 4 }}>
                                {allocatedCapital <= 0
                                    ? "자금을 할당해야 활성화할 수 있습니다."
                                    : "활성화하면 자동매매 시스템이 주기적으로 신호를 체크하고 주문을 실행합니다."}
                            </Typography>
                        </Box>
                    </Stack>
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>취소</Button>
                <Button
                    onClick={handleSave}
                    variant="contained"
                    startIcon={<Save />}
                    disabled={loading || (isActive && allocatedCapital <= 0)}
                >
                    저장
                </Button>
            </DialogActions>
        </Dialog>
    )
}

export default MyStrategyConfig
