// Core interfaces for the simulation engine

export type AccountType = 'general' | 'pension' | 'irp';

export interface AssetProfile {
    id: string;
    name: string;
    category: 'equity' | 'bond' | 'derivative' | 'structured';
    riskLevel: 1 | 2 | 3 | 4 | 5; // 1 = Safe, 5 = High Risk
    expectedReturn: number; // Annual %
    dividendYield: number; // Annual %
    isTaxEfficient: boolean; // e.g., foreign ETFs better in Pension
    allowedAccounts: AccountType[];
    // Educational content
    description?: string;
    pros?: string[];
    cons?: string[];
    maxDrawdown?: number;
    volatility?: number; // Annualized Standard Deviation (%)
    // Seeking Alpha Style Analysis
    quantScore?: number; // 1.0 - 5.0 (Strong Sell to Strong Buy)
    factorGrades?: {
        valuation: string;
        growth: string;
        profitability: string;
        momentum: string;
        revisions: string;
    };
    dividendStats?: {
        payoutRatio: number; // %
        growthRate5Y: number; // %
        growthStreak: number; // Years
        yieldTTM: number; // %
    };
    // Portfolio Visualizer Data
}

export interface AssetAllocation {
    asset: AssetProfile;
    amount: number;
    purchaseDate?: string;
}

export interface MonteCarloResult {
    percentiles: {
        p10: number[]; // Worst case (10th percentile)
        p50: number[]; // Base case (Median)
        p90: number[]; // Best case (90th percentile)
    };
    metrics: {
        cagr: number;
        sharpeRatio: number;
        mdd: number;
        bestYear: number;
        worstYear: number;
    };
    years: number[];
}

export const runMonteCarloSimulation = (
    allocations: AssetAllocation[],
    initialCapital: number,
    years: number = 20,
    simulations: number = 1000
): MonteCarloResult => {
    // 1. Calculate Portfolio Composite Stats
    let totalExpectedReturn = 0;
    let totalVolatility = 0;

    // Simplification: We assume correlation = 1 for worst case, but ideally we'd need a correlation matrix.
    // For this 'Expert System' MVP, we'll use a weighted average volatility adjusted by a diversification benefit factor.
    // If >2 assets, reduce volatility by 15% to simulate diversification (simple heuristic).

    let totalWeight = 0;
    let allocationsCount = allocations.length;

    allocations.forEach(a => {
        const weight = a.amount / initialCapital;
        totalExpectedReturn += (a.asset.expectedReturn / 100) * weight;
        totalVolatility += ((a.asset.volatility || 15) / 100) * weight; // Default 15% if missing
        totalWeight += weight;
    });

    if (totalWeight === 0) {
        return {
            percentiles: { p10: [], p50: [], p90: [] },
            metrics: { cagr: 0, sharpeRatio: 0, mdd: 0, bestYear: 0, worstYear: 0 },
            years: []
        };
    }

    // Adjust for cash drag if not 100% invested (assuming cash return = 2%)
    const cashWeight = 1 - totalWeight;
    if (cashWeight > 0) {
        totalExpectedReturn += 0.02 * cashWeight; // 2% risk-free rate
        // Cash has 0 allocation to volatility
    }

    // Diversification Bonus
    if (allocationsCount > 2) {
        totalVolatility *= 0.85;
    }

    // 2. Run Monte Carlo Loop
    const results: number[][] = [];

    for (let sim = 0; sim < simulations; sim++) {
        let currentWealth = initialCapital;
        const path: number[] = [initialCapital];

        for (let y = 1; y <= years; y++) {
            // Random Normal Distribution (Box-Muller transform)
            const u1 = Math.random();
            const u2 = Math.random();
            const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);

            // Return = Mean + Volatility * Z
            // Geometric Brownian Motion approximation: exp((mu - 0.5*sigma^2) + sigma*Z)
            const periodicReturn = Math.exp((totalExpectedReturn - 0.5 * Math.pow(totalVolatility, 2)) + totalVolatility * z);

            currentWealth *= periodicReturn;
            path.push(currentWealth);
        }
        results.push(path);
    }

    // 3. Extract Percentiles per Year
    const p10Path: number[] = [];
    const p50Path: number[] = [];
    const p90Path: number[] = [];

    for (let y = 0; y <= years; y++) {
        const yearValues = results.map(r => r[y]).sort((a, b) => a - b);
        p10Path.push(yearValues[Math.floor(simulations * 0.1)]);
        p50Path.push(yearValues[Math.floor(simulations * 0.5)]);
        p90Path.push(yearValues[Math.floor(simulations * 0.9)]);
    }

    // 4. Calculate Risk Metrics (from Median Path for generic stats)
    const finalValue = p50Path[years];
    const cagr = Math.pow(finalValue / initialCapital, 1 / years) - 1;
    const stdDev = totalVolatility; // simplified
    const sharpe = (cagr - 0.035) / stdDev; // Assuming 3.5% Risk Free Rate

    // Estimate MDD (Max Drawdown) roughly from the p10 path's worst drop
    // (A true MDD needs analysis of every path, but this is a decent proxy)
    let peak = p10Path[0];
    let maxDrawdown = 0;
    for (const val of p10Path) {
        if (val > peak) peak = val;
        const dd = (peak - val) / peak;
        if (dd > maxDrawdown) maxDrawdown = dd;
    }

    return {
        percentiles: {
            p10: p10Path,
            p50: p50Path,
            p90: p90Path
        },
        metrics: {
            cagr: cagr * 100,
            sharpeRatio: sharpe,
            mdd: maxDrawdown * 100,
            bestYear: (Math.exp(totalExpectedReturn + totalVolatility * 2) - 1) * 100, // +2 Sigma
            worstYear: (Math.exp(totalExpectedReturn - totalVolatility * 2) - 1) * 100  // -2 Sigma
        },
        years: Array.from({ length: years + 1 }, (_, i) => i + new Date().getFullYear())
    };
};

// Simple Simulation Results (Mock)
export const calculatePortfolioStats = (allocations: AssetAllocation[]) => {
    let totalAmount = 0;
    let weightedReturn = 0;
    let weightedYield = 0;
    let expectedAnnualDividend = 0;

    allocations.forEach(item => {
        totalAmount += item.amount;
        weightedReturn += item.asset.expectedReturn * item.amount;
        weightedYield += item.asset.dividendYield * item.amount;
        expectedAnnualDividend += item.amount * (item.asset.dividendYield / 100);
    });

    return {
        totalAmount,
        avgReturn: totalAmount > 0 ? weightedReturn / totalAmount : 0,
        avgYield: totalAmount > 0 ? weightedYield / totalAmount : 0,
        annualDividend: expectedAnnualDividend,
        monthlyDividend: expectedAnnualDividend / 12
    };
};

export const runSimpleBacktest = (allocations: AssetAllocation[], years: number = 10) => {
    // Very simple compound interest projection for now
    // Future: Use actual historical data from `asset.id`
    const stats = calculatePortfolioStats(allocations);
    const startAmount = stats.totalAmount;
    const history = [];

    let currentAmount = startAmount;
    for (let i = 0; i <= years; i++) {
        history.push({
            year: i,
            amount: Math.round(currentAmount)
        });
        currentAmount = currentAmount * (1 + stats.avgReturn / 100);
    }
    return history;
};

export interface UserPersona {
    currentAge: number;
    retirementAge: number;
    lifeExpectancy: number;
    currentIncome: number;
    targetMonthlySpend: number;
    existingSocialSecurity: boolean; // National Pension
}

export interface SimulationResult {
    monthlyIncome: number[]; // Array of monthly income for each year
    totalWealth: number[]; // Array of total wealth for each year
    taxPaid: number;
    healthInsurancePremium: number;
    isBankrupt: boolean;
}

// Placeholder function
export const calculateRetirementPlan = (
    accounts: any[],
    persona: UserPersona
): SimulationResult => {
    // TODO: Implement complex logic
    return {
        monthlyIncome: [],
        totalWealth: [],
        taxPaid: 0,
        healthInsurancePremium: 0,
        isBankrupt: false
    };
};
