
import React, { useState } from 'react'
import {
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    Stack,
    Chip,
    Button,
    Avatar,
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
    Paper,
    Divider,
    MenuItem,
    Select
} from '@mui/material'
import {
    Search,
    Verified,
    FilterList,
    Download,
    Refresh,
    ShowChart,
    PieChart,
    CorporateFare
} from '@mui/icons-material'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

const StrategyMarket: React.FC = () => {
    const [tabValue, setTabValue] = useState(0)

    // Korean Market Colors (Adapted for Light Theme)
    // Editorial Theme
    const THEME = {
        bg: '#FFFFFF',
        panel: '#FFFFFF',
        text: '#121212',
        textDim: '#757575',
        border: '#121212',
        hairline: '#E0E0E0',
        accent: '#C5A065', // Journalistic Gold
        success: '#121212', // Black for financial positive (or keeping red/blue for market data but muted)
        danger: '#D32F2F', // Brick Red
        info: '#1976D2'   // Corporate Blue
    }

    // Chart Colors (Editorial)
    const COLOR_UP = '#D32F2F' // Brick Red
    const COLOR_DOWN = '#1976D2' // Corporate Blue

    // Mock Data for Area Chart
    const generateAreaChartData = (isProfit: boolean) => ({
        labels: Array.from({ length: 30 }, (_, i) => i),
        datasets: [
            {
                data: Array.from({ length: 30 }, () => 100 + Math.random() * 20 - (isProfit ? 5 : 15)),
                borderColor: isProfit ? COLOR_UP : COLOR_DOWN,
                backgroundColor: isProfit ? 'rgba(211, 47, 47, 0.1)' : 'rgba(25, 118, 210, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 0,
                fill: true
            }
        ]
    })

    // Mock Strategies
    const strategies = [
        {
            id: 1,
            rank: 1,
            title: 'Global Macro Alpha',
            author: 'QuantMaster',
            year: 2023,
            category: 'Multi-Asset',
            cagr: 32.5,
            mdd: 8.4,
            aum: '52억',
            location: '서울(Seoul)',
            isVerified: true,
            description: '거시경제 지표 기반의 멀티에셋 전략'
        },
        {
            id: 2,
            rank: 2,
            title: 'Neutral Equity Arb',
            author: 'DeltaOne',
            year: 2022,
            category: 'Market Neutral',
            cagr: 12.8,
            mdd: 2.1,
            aum: '125억',
            location: '부산(Busan)',
            isVerified: true,
            description: '가격 비효율성을 포착하는 차익거래'
        },
        {
            id: 3,
            rank: 3,
            title: 'KOSPI200 Enhanced',
            author: 'IndexPlus',
            year: 2021,
            category: 'Equity Long',
            cagr: 15.2,
            mdd: 18.5,
            aum: '8.5억',
            location: '판교(Pangyo)',
            isVerified: true,
            description: '코스피200 추종 및 알파 전략'
        },
        {
            id: 4,
            rank: 4,
            title: 'Clean Energy Rotation',
            author: 'GreenFund',
            year: 2024,
            category: 'Sector',
            cagr: -5.4,
            mdd: 22.1,
            aum: '3.2억',
            location: '여의도(Yeouido)',
            isVerified: false,
            description: '신재생 에너지 섹터 로테이션'
        },
        {
            id: 5,
            rank: 5,
            title: 'Volatility Short',
            author: 'VixTrader',
            year: 2023,
            category: 'Derivatives',
            cagr: 45.2,
            mdd: 45.5,
            aum: '1.2억',
            location: '강남(Gangnam)',
            isVerified: false,
            description: 'VIX 선물을 이용한 변동성 매도'
        }
    ]

    return (
        <Box sx={{ color: THEME.text, bgcolor: '#FFFFFF', minHeight: '100vh', p: 3 }}>

            {/* Title Header - Masthead Style */}
            <Box sx={{ mb: 4, borderBottom: `1px solid ${THEME.border}`, pb: 2 }}>
                <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                    <CorporateFare sx={{ fontSize: 32, color: THEME.text }} />
                    <Typography variant="h4" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>
                        Expert Strategy Market
                    </Typography>
                </Stack>
                <Typography variant="body1" sx={{ color: THEME.textDim, fontFamily: '"Playfair Display", serif', fontStyle: 'italic' }}>
                    Professional Marketplace Analysis & Tracking
                </Typography>
            </Box>

            {/* Summary Cards (Pastel Style) */}
            {/* Summary Cards (Editorial Style) */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* 1. Total Strategies */}
                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, borderTop: `4px solid ${THEME.text}`, borderLeft: `1px solid ${THEME.hairline}`, borderRight: `1px solid ${THEME.hairline}`, borderBottom: `1px solid ${THEME.hairline}`, borderRadius: 0, height: '100%' }}>
                        <Typography variant="body2" sx={{ color: THEME.textDim, fontWeight: 600, mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>Total Strategies</Typography>
                        <Typography variant="h4" sx={{ color: THEME.text, fontWeight: 700, fontFamily: '"Playfair Display", serif' }}>34,415</Typography>
                    </Paper>
                </Grid>
                {/* 2. Avg Return (Gold Accent) */}
                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, borderTop: `4px solid ${THEME.accent}`, borderLeft: `1px solid ${THEME.hairline}`, borderRight: `1px solid ${THEME.hairline}`, borderBottom: `1px solid ${THEME.hairline}`, borderRadius: 0, height: '100%' }}>
                        <Typography variant="body2" sx={{ color: THEME.textDim, fontWeight: 600, mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>Avg Return (YTD)</Typography>
                        <Stack direction="row" alignItems="baseline" spacing={1}>
                            <Typography variant="h4" sx={{ color: THEME.accent, fontWeight: 700, fontFamily: '"Playfair Display", serif' }}>+12.4%</Typography>
                        </Stack>
                    </Paper>
                </Grid>
                {/* 3. AUM */}
                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, borderTop: `4px solid ${THEME.text}`, borderLeft: `1px solid ${THEME.hairline}`, borderRight: `1px solid ${THEME.hairline}`, borderBottom: `1px solid ${THEME.hairline}`, borderRadius: 0, height: '100%' }}>
                        <Typography variant="body2" sx={{ color: THEME.textDim, fontWeight: 600, mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>Total AUM</Typography>
                        <Typography variant="h4" sx={{ color: THEME.text, fontWeight: 700, fontFamily: '"Playfair Display", serif' }}>1,437 <span style={{ fontSize: '1rem', color: THEME.textDim }}>Billion KRW</span></Typography>
                    </Paper>
                </Grid>
                {/* 4. Top Sector */}
                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, borderTop: `4px solid ${THEME.text}`, borderLeft: `1px solid ${THEME.hairline}`, borderRight: `1px solid ${THEME.hairline}`, borderBottom: `1px solid ${THEME.hairline}`, borderRadius: 0, height: '100%' }}>
                        <Typography variant="body2" sx={{ color: THEME.textDim, fontWeight: 600, mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>Dominant Sector</Typography>
                        <Typography variant="h4" sx={{ color: THEME.text, fontWeight: 700, fontFamily: '"Playfair Display", serif' }}>Tech <span style={{ fontSize: '1rem', color: THEME.textDim }}>IT/Semi</span></Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Filter Bar */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, border: `1px solid ${THEME.hairline}`, borderRadius: 0, bgcolor: THEME.panel }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item>
                        <FilterList sx={{ color: THEME.text }} />
                    </Grid>
                    <Grid item xs={2}>
                        <Select fullWidth size="small" defaultValue="all" sx={{ bgcolor: 'white', borderRadius: 0, border: `1px solid ${THEME.hairline}` }}>
                            <MenuItem value="all">Global (All)</MenuItem>
                            <MenuItem value="kr">South Korea</MenuItem>
                            <MenuItem value="us">United States</MenuItem>
                        </Select>
                    </Grid>
                    <Grid item xs={2}>
                        <Select fullWidth size="small" defaultValue="all" sx={{ bgcolor: 'white', borderRadius: 0, border: `1px solid ${THEME.hairline}` }}>
                            <MenuItem value="all">All Sectors</MenuItem>
                            <MenuItem value="tech">Technology</MenuItem>
                            <MenuItem value="finance">Finance</MenuItem>
                        </Select>
                    </Grid>
                    <Grid item xs>
                        <TextField
                            fullWidth
                            size="small"
                            placeholder="Search Strategy..."
                            sx={{ bgcolor: 'white', '& .MuiOutlinedInput-root': { borderRadius: 0 } }}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><Search sx={{ color: THEME.textDim }} /></InputAdornment>
                            }}
                        />
                    </Grid>
                </Grid>
            </Paper>

            {/* Main Content Area */}
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

            {/* Dashboard View (Top Performer chart from previous design, restyled) */}
            {tabValue === 0 && (
                <Grid container spacing={3}>
                    <Grid item xs={12} md={8}>
                        <Paper elevation={0} sx={{ p: 3, border: `1px solid ${THEME.border}`, borderRadius: 0, height: 400 }}>
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2, borderBottom: `1px solid ${THEME.hairline}`, pb: 1 }}>
                                <ShowChart sx={{ color: THEME.text }} />
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700 }}>Benchmark Analysis (YoY)</Typography>
                            </Stack>
                            <Box sx={{ height: 320, width: '100%' }}>
                                <Line
                                    data={generateAreaChartData(true)}
                                    options={{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: { legend: { display: false } },
                                        scales: {
                                            x: { grid: { display: false } },
                                            y: { grid: { color: '#f0f0f0' }, border: { display: false } }
                                        },
                                        elements: { line: { tension: 0.4 } }
                                    }}
                                />
                            </Box>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Paper elevation={0} sx={{ p: 3, border: `1px solid ${THEME.border}`, borderRadius: 0, height: 400 }}>
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2, borderBottom: `1px solid ${THEME.hairline}`, pb: 1 }}>
                                <PieChart sx={{ color: THEME.text }} />
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700 }}>Sector Distribution</Typography>
                            </Stack>
                            {/* Placeholder for Pie Chart content */}
                            <Stack spacing={2} sx={{ mt: 4 }}>
                                {['IT/Semi (45%)', 'Finance (25%)', 'Healthcare (15%)', 'Consumer (10%)', 'Others (5%)'].map((item, idx) => (
                                    <Box key={idx}>
                                        <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                                            <Typography variant="body2">{item.split('(')[0]}</Typography>
                                            <Typography variant="body2" fontWeight={600}>{item.split('(')[1].replace(')', '')}</Typography>
                                        </Stack>
                                        <Box sx={{ width: '100%', height: 4, bgcolor: '#eee', borderRadius: 0 }}>
                                            <Box sx={{ width: item.split('(')[1].replace(')', ''), height: '100%', bgcolor: [THEME.text, THEME.textDim, '#9E9E9E', '#BDBDBD', '#E0E0E0'][idx], borderRadius: 0 }} />
                                        </Box>
                                    </Box>
                                ))}
                            </Stack>
                        </Paper>
                    </Grid>
                </Grid>
            )}

            {/* Table View */}
            {tabValue === 1 && (
                <TableContainer component={Paper} elevation={0} sx={{ border: `1px solid ${THEME.border}`, borderRadius: 0 }}>
                    <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', borderBottom: `1px solid ${THEME.hairline}` }}>
                        <Button startIcon={<Refresh />} size="small" sx={{ mr: 1, color: THEME.text }}>Refresh</Button>
                        <Button startIcon={<Download />} variant="outlined" size="small" sx={{ color: THEME.text, borderColor: THEME.text, borderRadius: 0 }}>Export CSV</Button>
                    </Box>
                    <Table sx={{ minWidth: 650 }} aria-label="strategy table">
                        <TableHead sx={{ bgcolor: THEME.panel }}>
                            <TableRow sx={{ borderBottom: `2px solid ${THEME.text}` }}>
                                <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>ID</TableCell>
                                <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Strategy Name</TableCell>
                                <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Year</TableCell>
                                <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Firm / Location</TableCell>
                                <TableCell sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>Category</TableCell>
                                <TableCell align="right" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>CAGR</TableCell>
                                <TableCell align="right" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>MDD</TableCell>
                                <TableCell align="center" sx={{ fontWeight: 700, fontFamily: '"Playfair Display", serif', color: THEME.text }}>30-Day Trend</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {strategies.map((row) => (
                                <TableRow
                                    key={row.id}
                                    sx={{ '&:hover': { bgcolor: '#F5F5F5' }, borderBottom: `1px solid ${THEME.hairline}` }}
                                >
                                    <TableCell component="th" scope="row" sx={{ color: THEME.textDim, fontFamily: '"Playfair Display", serif' }}>
                                        #{row.id.toString().padStart(3, '0')}
                                    </TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: THEME.text }}>
                                        {row.title}
                                    </TableCell>
                                    <TableCell sx={{ color: THEME.textDim }}>{row.year}</TableCell>
                                    <TableCell sx={{ color: THEME.textDim }}>{row.location}</TableCell>
                                    <TableCell>
                                        <Chip label={row.category} size="small" variant="outlined" sx={{ color: THEME.textDim, borderColor: THEME.hairline, borderRadius: 0 }} />
                                    </TableCell>
                                    <TableCell align="right" sx={{ color: row.cagr >= 0 ? THEME.success : THEME.danger, fontWeight: 700 }}>
                                        {row.cagr >= 0 ? '+' : ''}{row.cagr}%
                                    </TableCell>
                                    <TableCell align="right" sx={{ color: THEME.textDim }}>
                                        {row.mdd}%
                                    </TableCell>
                                    <TableCell align="center">
                                        <Box sx={{ width: 100, height: 30, display: 'inline-block' }}>
                                            <Line
                                                data={generateAreaChartData(row.cagr >= 0)}
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
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Box>
    )
}

export default StrategyMarket
