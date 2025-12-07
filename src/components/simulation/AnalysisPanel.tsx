
import React, { useState } from 'react';
import {
    Box, Paper, Typography, Tabs, Tab, Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow, Grid
} from '@mui/material';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, BarChart, Bar, Legend
} from 'recharts';
import { BacktestResult } from '../../utils/BacktestEngine';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    primary: '#00D1FF', // Cyan
    secondary: '#7F5AF0', // Purple
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A',
    success: '#2CB67D',
    danger: '#EF4565',
    colors: ['#00D1FF', '#7F5AF0', '#FFBB28', '#FF8042', '#2CB67D']
};

export interface NamedResult {
    id: number;
    name: string;
    result: BacktestResult;
}

interface AnalysisPanelProps {
    results: NamedResult[]; // Array of results for comparison
}

const MetricsTable = ({ results }: { results: NamedResult[] }) => (
    <TableContainer component={Paper} sx={{ bgcolor: 'transparent', boxShadow: 'none', mb: 3 }}>
        <Table size="small">
            <TableHead>
                <TableRow sx={{ '& th': { color: THEME.textDim, borderColor: THEME.border, fontWeight: 'bold' } }}>
                    <TableCell>Metric</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.name}</TableCell>
                    ))}
                </TableRow>
            </TableHead>
            <TableBody>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Initial Balance</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">₩ {r.result.initialBalance.toLocaleString()}</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Final Balance</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ fontWeight: 'bold' }}>₩ {Math.round(r.result.finalBalance).toLocaleString()}</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>CAGR</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.cagr.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Stdev</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.stdev.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Best Year</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.success }}>{r.result.bestYear.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Worst Year</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.danger }}>{r.result.worstYear.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Max Drawdown</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.danger }}>-{r.result.maxDrawdown.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Sharpe Ratio</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.sharpeRatio.toFixed(2)}</TableCell>
                    ))}
                </TableRow>
            </TableBody>
        </Table>
    </TableContainer>
);

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ results }) => {
    const [tab, setTab] = useState(0);

    // Merge Growth Data for Chart
    // Assuming all simulations have same years/length. 
    // We take the first result's years as X-Axis, and map others.
    const chartData = results.length > 0 ? results[0].result.annualReturns.map((point, idx) => {
        const merged: any = { year: point.year };
        results.forEach(r => {
            if (r.result.annualReturns[idx]) {
                merged[`bal_${r.id}`] = r.result.annualReturns[idx].balance;
                merged[`ret_${r.id}`] = r.result.annualReturns[idx].return;
            }
        });
        return merged;
    }) : [];

    return (
        <Paper sx={{ height: '100%', bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ borderBottom: 1, borderColor: THEME.border }}>
                <Tabs
                    value={tab}
                    onChange={(_, v) => setTab(v)}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{
                        '& .MuiTab-root': { color: THEME.textDim, minWidth: 100 },
                        '& .Mui-selected': { color: THEME.primary }
                    }}
                >
                    <Tab label="Summary" />
                    <Tab label="Annual Returns" />
                    <Tab label="Metrics" />
                </Tabs>
            </Box>

            <Box sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
                {tab === 0 && (
                    <Box>
                        <MetricsTable results={results} />
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Portfolio Growth</Typography>
                        <Box sx={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis dataKey="year" stroke={THEME.textDim} />
                                    <YAxis stroke={THEME.textDim} tickFormatter={(val) => `₩${(val / 100000000).toFixed(0)}억`} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                        formatter={(value: number, name: string) => {
                                            // Find portfolio name by parsing 'bal_ID'
                                            // Hacky but works for now
                                            // const id = name.split('_')[1]; 
                                            // return [`₩ ${Math.round(value).toLocaleString()}`, `Portfolio ${id}`]
                                            return [`₩ ${Math.round(value).toLocaleString()}`, 'Balance']
                                        }}
                                    />
                                    <Legend />
                                    {results.map((r, idx) => (
                                        <Line
                                            key={r.id}
                                            type="monotone"
                                            dataKey={`bal_${r.id}`}
                                            stroke={THEME.colors[idx % THEME.colors.length]}
                                            name={r.name}
                                            strokeWidth={2}
                                            dot={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </Box>
                    </Box>
                )}

                {tab === 1 && (
                    <Box>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Annual Returns</Typography>
                        <Box sx={{ height: 400, width: '100%' }}>
                            <ResponsiveContainer>
                                <BarChart data={chartData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis type="number" stroke={THEME.textDim} />
                                    <YAxis dataKey="year" type="category" stroke={THEME.textDim} width={60} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                    />
                                    <Legend />
                                    {results.map((r, idx) => (
                                        <Bar
                                            key={r.id}
                                            dataKey={`ret_${r.id}`}
                                            fill={THEME.colors[idx % THEME.colors.length]}
                                            name={r.name}
                                        />
                                    ))}
                                </BarChart>
                            </ResponsiveContainer>
                        </Box>
                    </Box>
                )}

                {tab === 2 && (
                    <Box>
                        <Typography variant="body2" color={THEME.textDim}>
                            Advanced metrics side-by-side.
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                            <MetricsTable results={results} />
                        </Box>
                    </Box>
                )}
            </Box>
        </Paper>
    );
};

export default AnalysisPanel;
