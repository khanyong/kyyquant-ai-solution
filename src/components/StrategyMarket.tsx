
import React, { useState, useEffect } from 'react'
import {
    Box,
    Typography,
    Grid,
    Paper,
    Chip,
    Button,
    Tab,
    Tabs,
    TextField,
    InputAdornment,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Stack,
    CircularProgress,
    Alert,
    Snackbar,
    Tooltip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton
} from '@mui/material'
import {
    Search,
    CorporateFare,
    ShowChart,
    PieChart,
    FilterList,
    Download,
    Refresh,
    ContentCopy,
    EmojiEvents, // for ranking trophy
    TrendingUp,
    TrendingDown,
    Close,
    History
} from '@mui/icons-material'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip as ChartTooltip,
    Legend,
    Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import strategyService, { Strategy } from '../services/strategyService'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    ChartTooltip,
    Legend,
    Filler
)

interface MarketStrategy extends Strategy {
    rank: number
}

const StrategyMarket: React.FC = () => {
    const [tabValue, setTabValue] = useState(1) // Default to List view for now
    const [strategies, setStrategies] = useState<MarketStrategy[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [searchQuery, setSearchQuery] = useState('')
    const [copyingId, setCopyingId] = useState<string | null>(null)
    const [selectedStrategy, setSelectedStrategy] = useState<MarketStrategy | null>(null)
    const [notification, setNotification] = useState<{ message: string, type: 'success' | 'error' } | null>(null)

    // Korean Market Colors (Adapted for Light Theme)
    const THEME = {
        bg: '#FFFFFF',
        panel: '#FFFFFF',
        text: '#121212',
        textDim: '#757575',
        border: '#121212',
        hairline: '#E0E0E0',
        accent: '#C5A065', // Journalistic Gold
        success: '#D32F2F', // Red for profit in KR market
        danger: '#1976D2', // Blue for loss in KR market
        info: '#1976D2'
    }

    const fetchStrategies = async () => {
        setLoading(true)
        try {
            const data = await strategyService.getMarketStrategies()
            const strategiesWithRank = data.map((s, index) => ({ ...s, rank: index + 1 }))
            setStrategies(strategiesWithRank)
        } catch (err) {
            console.error(err)
            setError('전략 목록을 불러오는데 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchStrategies()
    }, [])

    const handleCopyStrategy = async (strategy: Strategy) => {
        if (!confirm(`'${strategy.name}' 전략을 내 전략으로 복사하시겠습니까?`)) return

        setCopyingId(strategy.id)
        try {
            const result = await strategyService.copyStrategy(strategy.id)
            if (result) {
                setNotification({ message: '전략이 성공적으로 복사되었습니다.', type: 'success' })
            } else {
                setNotification({ message: '전략 복사에 실패했습니다.', type: 'error' })
            }
        } catch (err) {
            setNotification({ message: '오류가 발생했습니다.', type: 'error' })
        } finally {
            setCopyingId(null)
        }
    }

    // Filter strategies based on search query
    const filteredStrategies = strategies.filter(s =>
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.profiles?.name || '').toLowerCase().includes(searchQuery.toLowerCase())
    )

    // Mock chart data generation (can be replaced with actual history later)
    const generateAreaChartData = (isProfit: boolean) => ({
        labels: Array.from({ length: 30 }, (_, i) => i),
        datasets: [
            {
                data: Array.from({ length: 30 }, () => 100 + Math.random() * 20 - (isProfit ? 5 : 15)),
                borderColor: isProfit ? THEME.success : THEME.danger,
                backgroundColor: isProfit ? 'rgba(211, 47, 47, 0.1)' : 'rgba(25, 118, 210, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 0,
                fill: true
            }
        ]
    })

    const getRankBadge = (rank: number) => {
        if (rank === 1) return <EmojiEvents sx={{ color: '#FFD700' }} /> // Gold
        if (rank === 2) return <EmojiEvents sx={{ color: '#C0C0C0' }} /> // Silver
        if (rank === 3) return <EmojiEvents sx={{ color: '#CD7F32' }} /> // Bronze
        return <Typography variant="body2" sx={{ fontWeight: 'bold', color: THEME.textDim }}>{rank}</Typography>
    }

    return (
        <Box sx={{ color: THEME.text, bgcolor: '#FFFFFF', minHeight: '100vh', p: 3 }}>

            {/* Notification */}
            <Snackbar
                open={!!notification}
                autoHideDuration={6000}
                onClose={() => setNotification(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={() => setNotification(null)} severity={notification?.type || 'info'} sx={{ width: '100%' }}>
                    {notification?.message}
                </Alert>
            </Snackbar>

            {/* Header */}
            <Box sx={{ mb: 4, borderBottom: `1px solid ${THEME.border}`, pb: 2 }}>
                <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                    <CorporateFare sx={{ fontSize: 32, color: THEME.text }} />
                    <Typography variant="h4" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>
                        Expert Strategy Market
                    </Typography>
                </Stack>
                <Typography variant="body1" sx={{ color: THEME.textDim, fontFamily: '"Playfair Display", serif', fontStyle: 'italic' }}>
                    Top Performing Strategies & Rankings
                </Typography>
            </Box>

            {/* Filter Bar */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, border: `1px solid ${THEME.hairline}`, borderRadius: 0, bgcolor: THEME.panel }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item>
                        <FilterList sx={{ color: THEME.text }} />
                    </Grid>
                    <Grid item xs>
                        <TextField
                            fullWidth
                            size="small"
                            placeholder="Search Strategy or Author..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            sx={{ bgcolor: 'white', '& .MuiOutlinedInput-root': { borderRadius: 0 } }}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><Search sx={{ color: THEME.textDim }} /></InputAdornment>
                            }}
                        />
                    </Grid>
                    <Grid item>
                        <Button
                            startIcon={<Refresh />}
                            onClick={fetchStrategies}
                            disabled={loading}
                            sx={{ color: THEME.text, borderColor: THEME.text }}
                        >
                            Refresh
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {/* Tabs */}
            <Box sx={{ borderBottom: `1px solid ${THEME.border}`, mb: 2 }}>
                <Tabs
                    value={tabValue}
                    onChange={(e, v) => setTabValue(v)}
                    textColor="secondary"
                    indicatorColor="secondary"
                    sx={{
                        '& .MuiTab-root': { fontFamily: '"Playfair Display", serif', fontWeight: 'bold', fontSize: '1rem', color: THEME.textDim },
                        '& .Mui-selected': { color: `${THEME.text} !important` },
                        '& .MuiTabs-indicator': { backgroundColor: THEME.text, height: 3 }
                    }}
                >
                    <Tab label="Dashboard" icon={<ShowChart sx={{ fontSize: 18, mr: 1 }} />} iconPosition="start" />
                    <Tab label="Strategy List" icon={<CorporateFare sx={{ fontSize: 18, mr: 1 }} />} iconPosition="start" />
                </Tabs>
            </Box>

            {/* Content */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                    <CircularProgress sx={{ color: THEME.accent }} />
                </Box>
            ) : error ? (
                <Alert severity="error">{error}</Alert>
            ) : (
                <>
                    {/* Dashboard View (Placeholder) */}
                    {tabValue === 0 && (
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={8}>
                                <Paper elevation={0} sx={{ p: 3, border: `1px solid ${THEME.border}`, borderRadius: 0, height: 400 }}>
                                    <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2, borderBottom: `1px solid ${THEME.hairline}`, pb: 1 }}>
                                        <ShowChart sx={{ color: THEME.text }} />
                                        <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700 }}>Benchmark Analysis</Typography>
                                    </Stack>
                                    <Box sx={{ height: 320, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Typography color="text.secondary">Market Overview Chart (Coming Soon)</Typography>
                                    </Box>
                                </Paper>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <Paper elevation={0} sx={{ p: 3, border: `1px solid ${THEME.border}`, borderRadius: 0, height: 400 }}>
                                    <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2, borderBottom: `1px solid ${THEME.hairline}`, pb: 1 }}>
                                        <PieChart sx={{ color: THEME.text }} />
                                        <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700 }}>Sector Distribution</Typography>
                                    </Stack>
                                    <Box sx={{ height: 320, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Typography color="text.secondary">Sector Analysis (Coming Soon)</Typography>
                                    </Box>
                                </Paper>
                            </Grid>
                        </Grid>
                    )}

                    {/* Table View (Strategy List) */}
                    {tabValue === 1 && (
                        <TableContainer component={Paper} elevation={0} sx={{ border: `1px solid ${THEME.border}`, borderRadius: 0 }}>
                            <Table sx={{ minWidth: 650 }} aria-label="strategy table">
                                <TableHead sx={{ bgcolor: THEME.panel }}>
                                    <TableRow sx={{ borderBottom: `2px solid ${THEME.text}` }}>
                                        <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text, width: '5%' }}>Rank</TableCell>
                                        <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Strategy</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Source</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Return</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>MDD</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Stats</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Trend</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {filteredStrategies.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={8} align="center" sx={{ py: 3 }}>
                                                검색 결과가 없습니다.
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        filteredStrategies.flatMap((row, index) => {
                                            // Determine data availability
                                            const hasLiveActivity = (row.total_trades || 0) > 0 || (row.total_profit || 0) !== 0
                                            const backtestReturn = row.backtest_metrics?.avg_return || row.backtest_metrics?.best_return
                                            const backtestCount = row.backtest_count || 0
                                            const hasBacktest = backtestReturn !== undefined

                                            const rowsToRender = []

                                            // 1. Live/Mock Row
                                            if (hasLiveActivity || !hasBacktest) {
                                                rowsToRender.push({ ...row, _displaySource: 'MOCK', _keySuffix: 'mock' })
                                            }

                                            // 2. Backtest Row (Only if valid backtest data exists)
                                            if (hasBacktest) {
                                                // If we ALREADY added a MOCK row, this is the second row.
                                                // If we didn't (because !hasLiveProfit), this is the first/only row.
                                                // BUT, the logic above: if (!hasBacktest) we force MOCK. 
                                                // So if hasBacktest is true, we adding a BT row.
                                                // If we ALSO have hasLiveProfit, we have two rows.

                                                // Wait, if hasLiveProfit is FALSE, and hasBacktest is TRUE:
                                                // Block 1 runs? No (false || false).
                                                // Block 2 runs? Yes.
                                                // Correct.

                                                // If hasLiveProfit is TRUE, and hasBacktest is TRUE:
                                                // Block 1 runs.
                                                // Block 2 runs.
                                                // Two rows. Correct.

                                                rowsToRender.push({ ...row, _displaySource: 'BACKTEST', _keySuffix: 'bt' })
                                            }

                                            return rowsToRender.map((renderRow) => {
                                                const displaySource = renderRow._displaySource as 'MOCK' | 'BACKTEST'

                                                let displayReturn = 0
                                                let mdd = renderRow.backtest_metrics?.mdd || 0
                                                let trades = renderRow.total_trades || renderRow.backtest_metrics?.total_trades || 0

                                                // Period String Logic
                                                let periodString = '-'
                                                if (renderRow.backtest_metrics?.start_date && renderRow.backtest_metrics?.end_date) {
                                                    const start = new Date(renderRow.backtest_metrics.start_date)
                                                    const end = new Date(renderRow.backtest_metrics.end_date)
                                                    const diffTime = Math.abs(end.getTime() - start.getTime())
                                                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
                                                    periodString = `${diffDays} Days`
                                                }

                                                // Determine Return Value
                                                if (displaySource === 'BACKTEST') {
                                                    displayReturn = backtestReturn || 0
                                                } else {
                                                    if (renderRow.allocated_capital && renderRow.allocated_capital > 0) {
                                                        displayReturn = ((renderRow.total_profit || 0) / renderRow.allocated_capital) * 100
                                                    } else {
                                                        displayReturn = 0
                                                    }
                                                }

                                                const isProfit = (displaySource === 'MOCK' ? (renderRow.total_profit || 0) : displayReturn) >= 0

                                                return (
                                                    <TableRow
                                                        key={`${renderRow.id}-${renderRow._keySuffix}`}
                                                        sx={{ '&:hover': { bgcolor: '#F5F5F5' }, borderBottom: `1px solid ${THEME.hairline}` }}
                                                    >
                                                        {/* Rank */}
                                                        <TableCell align="center">
                                                            {getRankBadge(renderRow.rank)}
                                                        </TableCell>

                                                        {/* Strategy Info */}
                                                        <TableCell onClick={() => setSelectedStrategy(renderRow)} sx={{ cursor: 'pointer' }}>
                                                            <Box>
                                                                <Typography sx={{ fontWeight: 600, color: THEME.text }}>{renderRow.name}</Typography>
                                                                <Tooltip title={renderRow.description || (renderRow.profiles?.name ? `Created by ${renderRow.profiles.name}` : '')}>
                                                                    <Typography variant="caption" sx={{
                                                                        color: THEME.textDim,
                                                                        display: '-webkit-box',
                                                                        overflow: 'hidden',
                                                                        WebkitBoxOrient: 'vertical',
                                                                        WebkitLineClamp: 1,
                                                                        maxWidth: 200,
                                                                    }}>
                                                                        {renderRow.profiles?.name ? `by ${renderRow.profiles.name}` : ''}
                                                                        {renderRow.description ? ` | ${renderRow.description}` : ''}
                                                                    </Typography>
                                                                </Tooltip>
                                                                {/* Display Universes Tags */}
                                                                {renderRow.universes && renderRow.universes.length > 0 && (
                                                                    <Stack direction="row" spacing={0.5} sx={{ mt: 0.5, flexWrap: 'wrap', gap: 0.5 }}>
                                                                        {renderRow.universes.slice(0, 3).map((u, i) => (
                                                                            <Chip
                                                                                key={i}
                                                                                label={u.name}
                                                                                size="small"
                                                                                sx={{
                                                                                    fontSize: '0.6rem',
                                                                                    height: 18,
                                                                                    bgcolor: '#F5F5F5',
                                                                                    color: THEME.textDim,
                                                                                    border: `1px solid ${THEME.hairline}`
                                                                                }}
                                                                            />
                                                                        ))}
                                                                        {renderRow.universes.length > 3 && (
                                                                            <Typography variant="caption" sx={{ color: THEME.textDim, fontSize: '0.6rem', alignSelf: 'center' }}>
                                                                                +{renderRow.universes.length - 3}
                                                                            </Typography>
                                                                        )}
                                                                    </Stack>
                                                                )}
                                                            </Box>
                                                        </TableCell>

                                                        {/* Source Badge */}
                                                        <TableCell align="center">
                                                            <Chip
                                                                label={displaySource}
                                                                size="small"
                                                                onClick={() => setSelectedStrategy(renderRow)}
                                                                sx={{
                                                                    fontSize: '0.65rem',
                                                                    height: 20,
                                                                    fontWeight: 'bold',
                                                                    color: displaySource === 'MOCK' ? '#fff' : THEME.text,
                                                                    bgcolor: displaySource === 'MOCK' ? THEME.info : '#E0E0E0',
                                                                    cursor: 'pointer'
                                                                }}
                                                            />
                                                        </TableCell>

                                                        {/* Return */}
                                                        <TableCell align="right">
                                                            <Box>
                                                                <Typography sx={{ color: isProfit ? THEME.success : THEME.danger, fontWeight: 700 }}>
                                                                    {displaySource === 'MOCK'
                                                                        ? `${(renderRow.total_profit || 0).toLocaleString()} ₩`
                                                                        : `${displayReturn.toFixed(1)}%`
                                                                    }
                                                                </Typography>
                                                                {displaySource === 'MOCK' && hasBacktest && (
                                                                    <Typography variant="caption" sx={{ display: 'block', color: THEME.textDim, fontSize: '0.7rem' }}>
                                                                        (BT: {backtestReturn?.toFixed(1)}%)
                                                                    </Typography>
                                                                )}
                                                            </Box>
                                                        </TableCell>

                                                        {/* MDD */}
                                                        <TableCell align="right" sx={{ color: THEME.danger }}>
                                                            {displaySource === 'BACKTEST' ? (mdd ? `-${mdd.toFixed(1)}%` : '-') : '-'}
                                                        </TableCell>

                                                        {/* Stats (Trades / Period) */}
                                                        <TableCell align="center">
                                                            <Stack alignItems="center" spacing={0}>
                                                                <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
                                                                    {displaySource === 'BACKTEST'
                                                                        ? (backtestCount > 0 ? `${backtestCount} Runs` : `${trades} Trades`)
                                                                        : `${trades} Trades`
                                                                    }
                                                                </Typography>
                                                                <Typography variant="caption" sx={{ color: THEME.textDim, fontSize: '0.7rem' }}>
                                                                    {displaySource === 'BACKTEST'
                                                                        ? (backtestCount > 0 ? 'Avg Return' : periodString)
                                                                        : 'Live'}
                                                                </Typography>
                                                            </Stack>
                                                        </TableCell>

                                                        {/* Trend (Mini Chart) */}
                                                        <TableCell align="center">
                                                            <Box sx={{ width: 100, height: 30, display: 'inline-block' }}>
                                                                <Line
                                                                    data={generateAreaChartData(isProfit)}
                                                                    options={{
                                                                        responsive: true,
                                                                        maintainAspectRatio: false,
                                                                        plugins: { legend: { display: false }, tooltip: { enabled: false } },
                                                                        scales: { x: { display: false }, y: { display: false } },
                                                                        elements: { point: { radius: 0 }, line: { borderWidth: 1 } }
                                                                    }}
                                                                />
                                                            </Box>
                                                        </TableCell>

                                                        {/* Action Button */}
                                                        <TableCell align="center">
                                                            <Button
                                                                variant="outlined"
                                                                size="small"
                                                                startIcon={copyingId === renderRow.id ? <CircularProgress size={16} /> : <ContentCopy />}
                                                                onClick={(e) => { e.stopPropagation(); handleCopyStrategy(renderRow); }}
                                                                disabled={!!copyingId}
                                                                sx={{
                                                                    color: THEME.text,
                                                                    borderColor: THEME.hairline,
                                                                    borderRadius: 0,
                                                                    '&:hover': { borderColor: THEME.text, bgcolor: 'rgba(0,0,0,0.05)' }
                                                                }}
                                                            >
                                                                Get
                                                            </Button>
                                                        </TableCell>
                                                    </TableRow>
                                                )
                                            })
                                        })
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </>
            )}
            <Dialog
                open={!!selectedStrategy}
                onClose={() => setSelectedStrategy(null)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle sx={{ m: 0, p: 2 }}>
                    {selectedStrategy?.name} - Performance History
                    <IconButton
                        aria-label="close"
                        onClick={() => setSelectedStrategy(null)}
                        sx={{
                            position: 'absolute',
                            right: 8,
                            top: 8,
                            color: (theme) => theme.palette.grey[500],
                        }}
                    >
                        <Close />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers>
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Strategy Description</Typography>
                        <Typography variant="body2" color="text.secondary">
                            {selectedStrategy?.description || "No description provided."}
                        </Typography>
                    </Box>

                    {selectedStrategy?.universes && selectedStrategy.universes.length > 0 && (
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Investment Universe</Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                                {selectedStrategy.universes.map((u, idx) => (
                                    <Chip
                                        key={idx}
                                        label={u.name}
                                        size="medium"
                                        icon={<FilterList sx={{ fontSize: '1rem !important' }} />}
                                        sx={{ mb: 1 }}
                                    />
                                ))}
                            </Stack>
                        </Box>
                    )}

                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>Backtest History</Typography>
                    <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #eee' }}>
                        <Table size="small">
                            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                                <TableRow>
                                    <TableCell>Run Date</TableCell>
                                    <TableCell>Test Period</TableCell>
                                    <TableCell align="right">Return</TableCell>
                                    <TableCell align="right">Win Rate</TableCell>
                                    <TableCell align="right">MDD</TableCell>
                                    <TableCell align="right">Sharpe</TableCell>
                                    <TableCell align="right">Trades</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {selectedStrategy?.backtest_history?.map((bt: any, idx: number) => (
                                    <TableRow key={bt.id || idx}>
                                        <TableCell>{new Date(bt.created_at || Date.now()).toLocaleDateString()}</TableCell>
                                        <TableCell>
                                            {bt.start_date && bt.end_date ? (
                                                <Box>
                                                    <Typography variant="caption" display="block" sx={{ fontSize: '0.75rem', lineHeight: 1.2 }}>
                                                        {new Date(bt.start_date).toLocaleDateString()} ~
                                                    </Typography>
                                                    <Typography variant="caption" display="block" sx={{ fontSize: '0.75rem', lineHeight: 1.2 }}>
                                                        {new Date(bt.end_date).toLocaleDateString()}
                                                    </Typography>
                                                </Box>
                                            ) : (
                                                <Typography variant="caption" color="text.secondary">-</Typography>
                                            )}
                                        </TableCell>
                                        <TableCell align="right" sx={{ color: (bt.total_return_rate || 0) >= 0 ? THEME.success : THEME.danger, fontWeight: 600 }}>
                                            {(bt.total_return_rate || 0).toFixed(2)}%
                                        </TableCell>
                                        <TableCell align="right">{(bt.win_rate || 0).toFixed(1)}%</TableCell>
                                        <TableCell align="right" sx={{ color: THEME.danger }}>{bt.max_drawdown ? `${bt.max_drawdown.toFixed(1)}%` : '-'}</TableCell>
                                        <TableCell align="right">{bt.sharpe_ratio ? bt.sharpe_ratio.toFixed(2) : '-'}</TableCell>
                                        <TableCell align="right">{bt.total_trades}</TableCell>
                                    </TableRow>
                                ))}
                                {(!selectedStrategy?.backtest_history || selectedStrategy.backtest_history.length === 0) && (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center">No backtest history available.</TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </DialogContent>
            </Dialog>
        </Box>
    )
}

export default StrategyMarket
