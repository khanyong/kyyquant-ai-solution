import React from 'react'
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Alert
} from '@mui/material'
import {
    TrendingUp,
    Warning,
    ListAlt
} from '@mui/icons-material'

interface Position {
    stock_code: string
    stock_name: string
    quantity: number
    avg_price: number
    current_price: number
    profit_loss: number
    profit_loss_rate: number
}

interface PortfolioHoldingsTableProps {
    positions: Position[]
    loading?: boolean
}

export default function PortfolioHoldingsTable({ positions, loading }: PortfolioHoldingsTableProps) {
    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('ko-KR').format(value)
    }

    const formatPercent = (value: number) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    }

    const getProfitColor = (value: number) => {
        if (value > 0) return 'error.main'
        if (value < 0) return 'primary.main'
        return 'text.secondary'
    }

    return (
        <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom fontFamily="serif" sx={{ display: 'flex', alignItems: 'center' }}>
                <ListAlt sx={{ mr: 1, color: 'text.primary' }} /> 실시간 보유 종목 현황
            </Typography>

            {positions.length === 0 ? (
                <Alert severity="info">보유 중인 종목이 없습니다.</Alert>
            ) : (
                <TableContainer>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>종목명</TableCell>
                                <TableCell align="right">수량</TableCell>
                                <TableCell align="right">평균단가</TableCell>
                                <TableCell align="right">현재가</TableCell>
                                <TableCell align="right">평가손익</TableCell>
                                <TableCell align="right">수익률</TableCell>
                                <TableCell align="center">비고</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {positions.map((pos) => (
                                <TableRow key={pos.stock_code} hover>
                                    <TableCell>
                                        <Typography variant="body2" fontWeight="bold">
                                            {pos.stock_name}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {pos.stock_code}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">{pos.quantity}주</TableCell>
                                    <TableCell align="right">{formatCurrency(pos.avg_price)}원</TableCell>
                                    <TableCell align="right">{formatCurrency(pos.current_price)}원</TableCell>
                                    <TableCell align="right">
                                        <Typography
                                            variant="body2"
                                            color={getProfitColor(pos.profit_loss)}
                                            fontWeight="bold"
                                        >
                                            {formatCurrency(pos.profit_loss)}원
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography
                                            variant="body2"
                                            color={getProfitColor(pos.profit_loss_rate)}
                                            fontWeight="bold"
                                        >
                                            {formatPercent(pos.profit_loss_rate)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="center">
                                        {pos.profit_loss_rate >= 10 && (
                                            <Chip icon={<TrendingUp sx={{ color: 'text.secondary !important' }} />} label="익절구간" size="small" variant="outlined" sx={{ borderColor: 'text.secondary', color: 'text.secondary', fontWeight: 600 }} />
                                        )}
                                        {pos.profit_loss_rate <= -5 && (
                                            <Chip icon={<Warning sx={{ color: 'text.secondary !important' }} />} label="손절주의" size="small" variant="outlined" sx={{ borderColor: 'text.secondary', color: 'text.secondary', fontWeight: 600 }} />
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Paper>
    )
}
