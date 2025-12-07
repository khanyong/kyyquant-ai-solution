
import React from 'react';
import {
    Box, Paper, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Typography, Button, IconButton
} from '@mui/material';
import { Save, DeleteOutline, PieChart as PieIcon } from '@mui/icons-material';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { AssetAllocation } from '../../utils/SimulationEngine';

const THEME = {
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A',
    primary: '#00D1FF',
    secondary: '#7F5AF0',
    panel: '#151921',
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
        <Box sx={{ display: 'flex', gap: 2, height: '100%' }}>
            {/* Left: Table */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
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
                                    <TableCell sx={{ fontWeight: 'bold' }}>{row.asset.id}</TableCell>
                                    <TableCell>{row.asset.name}</TableCell>
                                    <TableCell align="right">
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

                <Box sx={{ mt: 2 }}>
                    <Button
                        variant="outlined"
                        startIcon={<Save />}
                        onClick={onSave}
                        sx={{ color: THEME.primary, borderColor: THEME.primary }}
                    >
                        Save Portfolio
                    </Button>
                </Box>
            </Box>

            {/* Right: Pie Chart */}
            <Paper sx={{ width: 300, bgcolor: 'transparent', boxShadow: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {assets.length > 0 ? (
                    <Box sx={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
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
                                    verticalAlign="bottom"
                                    align="center"
                                    wrapperStyle={{ fontSize: '12px', color: THEME.textDim }}
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
