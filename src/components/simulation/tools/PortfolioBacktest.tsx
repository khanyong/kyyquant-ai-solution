
import React, { useState } from 'react';
import {
    Box, Grid, Paper, Typography, Button, IconButton,
    TextField, InputAdornment, Tabs, Tab, Divider
} from '@mui/material';
import {
    Search, AddCircleOutline, PlayArrow, PieChart
} from '@mui/icons-material';

import AssetSelector from '../AssetSelector';
import AssetDetailDialog from '../AssetDetailDialog';
import AllocationDialog from '../AllocationDialog';
import { AssetProfile, AssetAllocation, calculatePortfolioStats, formatLargeNumber } from '../../../utils/SimulationEngine';
import { runBacktest } from '../../../utils/BacktestEngine';
import PortfolioSettings from '../PortfolioSettings';
import AnalysisPanel, { NamedResult } from '../AnalysisPanel';
import PortfolioComposition from '../PortfolioComposition';
import { Portfolio, SimulationParams } from '../types';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    primary: '#00D1FF',
    secondary: '#7F5AF0',
    success: '#2CB67D',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A'
};

interface PortfolioBacktestProps {
    portfolios: Portfolio[];
    setPortfolios: (p: Portfolio[]) => void;
    activePortfolioId: number;
    setActivePortfolioId: (id: number) => void;
    params: SimulationParams;
    setParams: (p: SimulationParams) => void;
}

const PortfolioBacktest: React.FC<PortfolioBacktestProps> = ({
    portfolios, setPortfolios, activePortfolioId, setActivePortfolioId,
    params, setParams
}) => {
    // Helpers
    const activePortfolio = portfolios.find(p => p.id === activePortfolioId) || portfolios[0];
    const updateActiveAllocations = (newAllocations: AssetAllocation[]) => {
        setPortfolios(portfolios.map(p =>
            p.id === activePortfolioId ? { ...p, allocations: newAllocations } : p
        ));
    };

    // --- State: Dialogs ---
    const [detailOpen, setDetailOpen] = useState(false);
    const [selectedAssetForDetail, setSelectedAssetForDetail] = useState<AssetProfile | null>(null);
    const [allocationOpen, setAllocationOpen] = useState(false);
    const [pendingAsset, setPendingAsset] = useState<AssetProfile | null>(null);

    // Derived Stats
    const portfolioStats = calculatePortfolioStats(activePortfolio.allocations);
    const remainingCash = params.totalCapital - portfolioStats.totalAmount;

    // --- Logic: Backtest ---
    const comparisonResults: NamedResult[] = portfolios.map(p => ({
        id: p.id,
        name: p.name,
        result: runBacktest(
            p.allocations,
            params.totalCapital,
            params.simYears,
            params.monthlyContribution,
            params.rebalanceFreq !== 'No Rebalancing'
        )
    }));

    // --- Handlers ---
    const handleDropRequest = (asset: AssetProfile) => {
        setPendingAsset(asset);
        setAllocationOpen(true);
    };

    const handleAllocationConfirm = (amount: number) => {
        if (!pendingAsset) return;
        const newAlloc: AssetAllocation = {
            asset: pendingAsset,
            amount,
            purchaseDate: new Date().toISOString()
        };
        updateActiveAllocations([...activePortfolio.allocations, newAlloc]);
        setAllocationOpen(false);
    };

    const handleRemoveAsset = (id: string) => {
        updateActiveAllocations(activePortfolio.allocations.filter(a => a.asset.id !== id));
    };

    const handleAddPortfolio = () => {
        const newId = Math.max(...portfolios.map(p => p.id)) + 1;
        setPortfolios([...portfolios, { id: newId, name: `Portfolio ${newId}`, allocations: [] }]);
        setActivePortfolioId(newId);
    };

    const updateParam = (key: keyof SimulationParams, value: any) => {
        setParams({ ...params, [key]: value });
    };

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header / Stats Overlay */}
            <Paper sx={{ mb: 2, p: 2, bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                <Grid container spacing={4} alignItems="center">
                    <Grid item xs={3}>
                        <Typography variant="h5" fontWeight="bold" sx={{ color: THEME.text }}>Backtest Portfolio</Typography>
                    </Grid>
                    <Grid item xs={9}>
                        <Box sx={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>Total Capital</Typography>
                                <Typography variant="h6" fontWeight="bold">{formatLargeNumber(params.totalCapital)}</Typography>
                            </Box>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>Expected Return</Typography>
                                <Typography variant="h6" fontWeight="bold" color={THEME.primary}>{portfolioStats.avgReturn.toFixed(2)}%</Typography>
                            </Box>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>Remaining Cash</Typography>
                                <Typography variant="h6" fontWeight="bold" color={remainingCash < 0 ? '#ef4444' : THEME.text}>
                                    {((remainingCash / params.totalCapital) * 100).toFixed(1)}%
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>

            <Grid container spacing={2} sx={{ flex: 1, overflow: 'hidden' }}>
                {/* 1. Asset Library */}
                <Grid item xs={12} md={3} sx={{ height: '100%' }}>
                    <Paper sx={{ height: '100%', bgcolor: THEME.panel, border: '1px solid ' + THEME.border, display: 'flex', flexDirection: 'column' }}>
                        <Box sx={{ p: 1.5, borderBottom: '1px solid ' + THEME.border }}>
                            <TextField
                                fullWidth
                                placeholder="Search..."
                                size="small"
                                InputProps={{
                                    startAdornment: <InputAdornment position="start"><Search sx={{ color: THEME.textDim }} /></InputAdornment>,
                                    sx: { color: THEME.text, bgcolor: THEME.bg }
                                }}
                            />
                        </Box>
                        <Box sx={{ flex: 1, overflowY: 'auto', p: 1 }}>
                            <AssetSelector
                                onDragStart={(e, asset) => e.dataTransfer.setData('application/json', JSON.stringify(asset))}
                                onAssetClick={(asset) => { setSelectedAssetForDetail(asset); setDetailOpen(true); }}
                                darkTheme={true}
                            />
                        </Box>
                    </Paper>
                </Grid>

                {/* 2. Construction */}
                <Grid item xs={12} md={5} sx={{ height: '100%' }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2 }}>
                        <PortfolioSettings
                            years={params.simYears} setYears={(v) => updateParam('simYears', v)}
                            monthlyContribution={params.monthlyContribution} setMonthlyContribution={(v) => updateParam('monthlyContribution', v)}
                            rebalanceFreq={params.rebalanceFreq} setRebalanceFreq={(v) => updateParam('rebalanceFreq', v)}
                            benchmark={params.benchmark} setBenchmark={(v) => updateParam('benchmark', v)}
                        />

                        <Paper sx={{ flex: 1, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, display: 'flex', flexDirection: 'column' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', borderBottom: '1px solid ' + THEME.border, pr: 1 }}>
                                <Tabs
                                    value={activePortfolioId}
                                    onChange={(_, v) => setActivePortfolioId(v)}
                                    variant="scrollable" scrollButtons="auto"
                                    sx={{ flex: 1, '& .MuiTab-root': { color: THEME.textDim, minWidth: 80 }, '& .Mui-selected': { color: THEME.primary } }}
                                >
                                    {portfolios.map(p => <Tab key={p.id} label={p.name} value={p.id} />)}
                                </Tabs>
                                <IconButton size="small" onClick={handleAddPortfolio} sx={{ color: THEME.success }}><AddCircleOutline /></IconButton>
                            </Box>

                            <Box
                                sx={{ flex: 1, p: 2, overflowY: 'auto' }}
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={(e) => handleDropRequest(JSON.parse(e.dataTransfer.getData('application/json')))}
                            >
                                <PortfolioComposition
                                    assets={activePortfolio.allocations}
                                    totalValue={params.totalCapital}
                                    onRemove={handleRemoveAsset}
                                    onSave={() => alert('Saved')}
                                />
                            </Box>
                        </Paper>
                    </Box>
                </Grid>

                {/* 3. Analysis */}
                <Grid item xs={12} md={4} sx={{ height: '100%' }}>
                    <AnalysisPanel results={comparisonResults} />
                </Grid>
            </Grid>

            {/* Dialogs */}
            <AssetDetailDialog open={detailOpen} onClose={() => setDetailOpen(false)} asset={selectedAssetForDetail} />
            <AllocationDialog
                open={allocationOpen} onClose={() => setAllocationOpen(false)}
                onConfirm={handleAllocationConfirm} asset={pendingAsset} remainingCash={remainingCash}
            />
        </Box>
    );
};

export default PortfolioBacktest;

