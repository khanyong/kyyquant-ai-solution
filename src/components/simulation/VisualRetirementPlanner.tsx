
import React, { useState } from 'react';
import { Box, Paper, Button, Typography } from '@mui/material';

import IPCSidebar from './IPCSidebar';
import IPCHome from './IPCHome';
import PortfolioBacktest from './tools/PortfolioBacktest';
import MonteCarloTool from './tools/MonteCarloTool';
import FactorAnalysisTool from './tools/FactorAnalysisTool';
import OptimizationTool from './tools/OptimizationTool';
import ISAPage from './tools/ISAPage';
import PensionPage from './tools/PensionPage';
// import BankingMockup from './tools/BankingMockup'; // Deprecated
import CashAssets from './tools/CashAssets';
import DebtManagement from './tools/DebtManagement';
import RealEstate from './tools/RealEstate';
import OtherAssets from './tools/OtherAssets';
import CashFlowAnalysis from './tools/CashFlowAnalysis';
import InsuranceAnalysis from './tools/InsuranceAnalysis';
import LifeGoalPlanning from './tools/LifeGoalPlanning';
import SettingsPage from './tools/SettingsPage';
import MarketGuidePage from './tools/MarketGuidePage';
import { Portfolio, SimulationParams } from './types';


const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    border: 'var(--ipc-border)'
};

const VisualRetirementPlanner: React.FC = () => {
    // --- Navigation State ---
    const [activeTool, setActiveTool] = useState('dashboard');

    // --- Global Portfolio State (Lifted Up) ---
    const [portfolios, setPortfolios] = useState<Portfolio[]>([
        { id: 1, name: 'Portfolio 1', allocations: [] }
    ]);
    const [activePortfolioId, setActivePortfolioId] = useState(1);

    // --- Global Simulation Params (Lifted Up) ---
    const [simParams, setSimParams] = useState<SimulationParams>({
        totalCapital: 100000000,
        simYears: 20,
        monthlyContribution: 1000000,
        rebalanceFreq: 'Annually',
        benchmark: 'SPY'
    });

    // Helper: Identify active portfolio
    const activePortfolio = portfolios.find(p => p.id === activePortfolioId) || portfolios[0];

    // --- Render: IPC Shell ---
    return (
        <Box sx={{ display: 'flex', height: '100%', bgcolor: THEME.bg, color: THEME.text }}>
            {/* Sidebar */}
            <IPCSidebar activeTool={activeTool} setActiveTool={setActiveTool} />

            {/* Main Content Area */}
            <Box sx={{ flex: 1, height: '100%', overflow: 'hidden', p: 0 }}>
                {activeTool === 'dashboard' && <IPCHome setActiveTool={setActiveTool} />}

                {activeTool === 'backtest' && (
                    <PortfolioBacktest
                        portfolios={portfolios}
                        setPortfolios={setPortfolios}
                        activePortfolioId={activePortfolioId}
                        setActivePortfolioId={setActivePortfolioId}
                        params={simParams}
                        setParams={setSimParams}
                    />
                )}

                {activeTool === 'montecarlo' && (
                    <MonteCarloTool
                        activePortfolio={activePortfolio}
                        params={simParams}
                    />
                )}



                {activeTool === 'factor' && <FactorAnalysisTool activePortfolio={activePortfolio} />}
                {activeTool === 'allocation' && <OptimizationTool activePortfolio={activePortfolio} />}

                {/* Investment Pages */}
                {activeTool === 'isa' && <ISAPage />}
                {activeTool === 'pension' && <PensionPage />}
                {activeTool === 'market_guide' && <MarketGuidePage />}

                {/* Asset & Liability Management */}
                {activeTool === 'cash_assets' && <CashAssets />}
                {activeTool === 'real_estate' && <RealEstate />}
                {activeTool === 'other_assets' && <OtherAssets />}
                {activeTool === 'debt_mgmt' && <DebtManagement />}

                {/* Life & Risk Planning */}
                {activeTool === 'cashflow' && <CashFlowAnalysis />}
                {activeTool === 'insurance' && <InsuranceAnalysis />}
                {activeTool === 'goals' && <LifeGoalPlanning />}

                {/* Settings */}
                {activeTool === 'settings' && <SettingsPage />}

                {!['dashboard', 'backtest', 'montecarlo', 'factor', 'allocation', 'isa', 'pension', 'market_guide', 'cash_assets', 'real_estate', 'other_assets', 'debt_mgmt', 'cashflow', 'insurance', 'goals', 'settings'].includes(activeTool) && (
                    <Box sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94A1B2' }}>
                        <Typography variant="h4" fontWeight="bold" sx={{ mb: 2 }}>{activeTool.toUpperCase()}</Typography>
                        <Typography variant="body1">This module is currently under development.</Typography>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default VisualRetirementPlanner;

