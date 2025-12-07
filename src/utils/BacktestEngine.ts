
import { AssetAllocation } from './SimulationEngine';

export interface BacktestResult {
    initialBalance: number;
    finalBalance: number;
    cagr: number;
    stdev: number;
    bestYear: number;
    worstYear: number;
    maxDrawdown: number;
    sharpeRatio: number;
    sortinoRatio: number;
    annualReturns: { year: number; return: number; balance: number }[];
    monthlyReturns: number[]; // For Sortino calculation
}

// Helper: Calculate Standard Deviation
const calculateStdDev = (data: number[]) => {
    const mean = data.reduce((a, b) => a + b, 0) / data.length;
    const variance = data.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / data.length;
    return Math.sqrt(variance);
};

// Helper: Calculate Max Drawdown
const calculateMaxDrawdown = (balances: number[]) => {
    let maxPeak = balances[0];
    let maxDrawdown = 0;

    for (const balance of balances) {
        if (balance > maxPeak) {
            maxPeak = balance;
        }
        const drawdown = (maxPeak - balance) / maxPeak;
        if (drawdown > maxDrawdown) {
            maxDrawdown = drawdown;
        }
    }
    return maxDrawdown * 100; // Percentage
};

export const runBacktest = (
    allocations: AssetAllocation[],
    initialCapital: number,
    years: number = 20,
    monthlyContribution: number = 0,
    rebalanceResults: boolean = true
): BacktestResult => {
    // 1. Calculate Portfolio Composite Stats (Weighted Average)
    const totalAllocated = allocations.reduce((sum, a) => sum + a.amount, 0);
    // If no assets, return safe defaults
    if (totalAllocated === 0 || initialCapital === 0) {
        return {
            initialBalance: initialCapital,
            finalBalance: initialCapital,
            cagr: 0,
            stdev: 0,
            bestYear: 0,
            worstYear: 0,
            maxDrawdown: 0,
            sharpeRatio: 0,
            sortinoRatio: 0,
            annualReturns: [],
            monthlyReturns: []
        };
    }

    let weightedMeanReturn = 0;
    let weightedStdDev = 0;

    allocations.forEach(alloc => {
        const weight = alloc.amount / totalAllocated;
        // Asset Expected Return is in %, convert to decimal
        weightedMeanReturn += (alloc.asset.expectedReturn / 100) * weight;
        // Simplified risk assumption: weighted average of volatility (ignoring covariance for now)
        weightedStdDev += ((alloc.asset.volatility || 0) / 100) * weight;
    });

    // 2. Simulate Year-by-Year (Deterministic + slight random noise for "Scenario")
    // Note: For a "Backtest" view in a planner without real history, we typically show "Expected Path"
    // OR we simulate one median path. 
    // To match PortfolioVisualizer's "Historical" feel, we might want to generate a sequence 
    // that statistically matches the portfolio's properties.

    // However, strictly speaking, a "Backtest" requires historical data. 
    // Since we are simulating, we will generate a "Representative Path" using the Gaussian distribution.
    // To keep it stable for the UI (so it doesn't jump every render), we can use a seeded random or 
    // just a fixed projection for the "Expected" line, and noise for others.

    // For this feature, let's generate a "Likely Scenario" (Mean return applied).
    // To make it look "Real" like the screenshot, we will simply apply the Mean Return for now,
    // as true random generation is visually confusing if it changes.
    // BUT, the screenshot shows "Best Year" and "Worst Year", which implies variability.
    // So we MUST generate a sequence of returns that varies.

    const annualReturns: { year: number; return: number; balance: number }[] = [];
    const monthlyReturns: number[] = [];

    let currentBalance = initialCapital;
    let peakBalance = initialCapital;

    // Generate distinct annual returns using a fixed pattern to ensure stability across renders if desired,
    // or just pure random. Pure random is better for 'Monte Carlo', but for 'Backtest' 
    // we essentially need "Projected Performance".
    // Let's create a pseudo-random sequence for 30 years to create a "Chart" that looks realistic.

    for (let i = 1; i <= years; i++) {
        // Generate a random return based on Normal Distribution (Box-Muller transform)
        const u1 = Math.random();
        const u2 = Math.random();
        const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);

        // Annual Return %
        const randomReturn = weightedMeanReturn + (weightedStdDev * z);
        const annualReturnPercent = randomReturn;

        const startBalance = currentBalance;

        // Apply return
        const profit = startBalance * annualReturnPercent;
        currentBalance += profit;

        // Apply Contribution
        currentBalance += (monthlyContribution * 12);

        annualReturns.push({
            year: 2024 + i,
            return: annualReturnPercent * 100,
            balance: currentBalance
        });

        // Generate ~12 fake monthly returns for stats
        for (let m = 0; m < 12; m++) {
            monthlyReturns.push(randomReturn / 12); // Simplified
        }
    }

    // 3. Calculate Metrics
    const finalBalance = currentBalance;
    const cagr = (Math.pow(finalBalance / initialCapital, 1 / years) - 1) * 100;

    const returnValues = annualReturns.map(y => y.return);
    const bestYear = Math.max(...returnValues);
    const worstYear = Math.min(...returnValues);
    const stdev = calculateStdDev(returnValues);

    const riskFreeRate = 2.0; // 2% Assumption
    const sharpeRatio = (cagr - riskFreeRate) / stdev;

    // Sortino: Downside Deviation
    const negativeReturns = returnValues.filter(r => r < 0);
    const downsideDev = negativeReturns.length > 0 ? calculateStdDev(negativeReturns) : 1; // Avoid div/0
    const sortinoRatio = (cagr - riskFreeRate) / downsideDev;

    const maxDrawdown = calculateMaxDrawdown(annualReturns.map(a => a.balance));

    return {
        initialBalance: initialCapital,
        finalBalance,
        cagr,
        stdev,
        bestYear,
        worstYear,
        maxDrawdown,
        sharpeRatio,
        sortinoRatio,
        annualReturns,
        monthlyReturns
    };
};
