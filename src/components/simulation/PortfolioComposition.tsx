
import React from 'react';
import {
    Box, Paper, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Typography, Button, IconButton
} from '@mui/material';
import { Save, DeleteOutline, PieChart as PieIcon } from '@mui/icons-material';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { AssetAllocation } from '../../utils/SimulationEngine';

const THEME = {
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    border: 'var(--ipc-border)',
    primary: 'var(--ipc-primary)',
    secondary: 'var(--ipc-secondary)',
    panel: 'var(--ipc-bg-panel)',
    chartColors: ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
};

interface PortfolioCompositionProps {
    assets: AssetAllocation[];
    totalValue: number;
    onRemove: (id: string) => void;
    onSave: () => void;
}

const PortfolioComposition: React.FC<PortfolioCompositionProps> = ({
    assets, totalValue, onRemove, onSave
}) => {
    // Prepare Data for Pie Chart
    const pieData = assets.map(a => ({
        name: a.asset.name,
        value: a.amount,
        ticker: a.asset.id
    }));

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
            {/* Top: Table */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <TableContainer component={Paper} sx={{ bgcolor: 'transparent', boxShadow: 'none', flex: 1, overflowY: 'auto' }}>
                    <Table size="small" stickyHeader>
                        <TableHead>
                            <TableRow sx={{ '& th': { bgcolor: THEME.panel, color: THEME.textDim, fontWeight: 'bold', borderBottom: '1px solid ' + THEME.border } }}>
                                <TableCell>Ticker</TableCell>
                                <TableCell>Name</TableCell>
                                <TableCell align="right">Allocation</TableCell>
                                <TableCell align="center">Action</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {assets.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={4} align="center" sx={{ color: THEME.textDim, py: 4, borderBottom: '1px solid ' + THEME.border }}>
                                        No assets. Drag & Drop to add.
                                    </TableCell>
                                </TableRow>
                            )}
                            {assets.map((row) => (
                                <TableRow key={row.asset.id} sx={{ '& td': { color: THEME.text, borderBottom: '1px solid ' + THEME.border } }}>
                                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>{row.asset.id}</TableCell>
                                    <TableCell sx={{ fontSize: '0.8rem' }}>{row.asset.name}</TableCell>
                                    <TableCell align="right" sx={{ fontSize: '0.8rem' }}>
                                        {((row.amount / totalValue) * 100).toFixed(2)}%
                                    </TableCell>
                                    <TableCell align="center">
                                        <IconButton size="small" onClick={() => onRemove(row.asset.id)} sx={{ color: '#ef4444' }}>
                                            <DeleteOutline fontSize="small" />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>

                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="outlined"
                        startIcon={<Save />}
                        onClick={onSave}
                        size="small"
                        sx={{ color: THEME.primary, borderColor: THEME.primary }}
                    >
                        Save
                    </Button>
                </Box>
            </Box>

            {/* Bottom: Pie Chart */}
            <Paper sx={{ height: 250, bgcolor: 'transparent', boxShadow: 'none', borderTop: '1px solid ' + THEME.border, pt: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {assets.length > 0 ? (
                    <Box sx={{ width: '100%', height: '100%' }}>
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={50}
                                    outerRadius={70}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={THEME.chartColors[index % THEME.chartColors.length]} />
                                    ))}
                                </Pie>
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: THEME.panel, border: '1px solid ' + THEME.border }}
                                    itemStyle={{ color: THEME.text }}
                                    formatter={(value: number) => `${((value / totalValue) * 100).toFixed(1)}%`}
                                />
                                <Legend
                                    layout="vertical"
                                    verticalAlign="middle"
                                    align="right"
                                    wrapperStyle={{ fontSize: '11px', color: THEME.textDim }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </Box>
                ) : (
                    <Box sx={{ textAlign: 'center', color: THEME.textDim }}>
                        <PieIcon sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />
                        <Typography variant="body2">No Data</Typography>
                    </Box>
                )}
            </Paper>
        </Box>
    );
};

export default PortfolioComposition;
