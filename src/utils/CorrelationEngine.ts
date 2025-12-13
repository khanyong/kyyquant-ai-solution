import { AssetProfile, AssetAllocation } from './SimulationEngine';

// 1. Hardcoded Correlation Priors (Category vs Category)
// Range: -1.0 to 1.0
const CATEGORY_CORRELATIONS: Record<string, Record<string, number>> = {
    'US Stock': { 'US Stock': 1.0, 'KR Stock': 0.7, 'Bond': -0.2, 'Crypto': 0.4, 'Cash': 0.0, 'Raw Materials': 0.3 },
    'KR Stock': { 'US Stock': 0.7, 'KR Stock': 1.0, 'Bond': -0.1, 'Crypto': 0.3, 'Cash': 0.0, 'Raw Materials': 0.4 },
    'Bond': { 'US Stock': -0.2, 'KR Stock': -0.1, 'Bond': 1.0, 'Crypto': -0.1, 'Cash': 0.1, 'Raw Materials': -0.3 },
    'Crypto': { 'US Stock': 0.4, 'KR Stock': 0.3, 'Bond': -0.1, 'Crypto': 1.0, 'Cash': 0.0, 'Raw Materials': 0.2 },
    'Cash': { 'US Stock': 0.0, 'KR Stock': 0.0, 'Bond': 0.1, 'Crypto': 0.0, 'Cash': 1.0, 'Raw Materials': 0.0 },
    'Raw Materials': { 'US Stock': 0.3, 'KR Stock': 0.4, 'Bond': -0.3, 'Crypto': 0.2, 'Cash': 0.0, 'Raw Materials': 1.0 },
};

// Helper to get prior
const getPriorCorrelation = (cat1: string, cat2: string): number => {
    if (cat1 === cat2) return 1.0;
    const fromMap = CATEGORY_CORRELATIONS[cat1]?.[cat2] ?? CATEGORY_CORRELATIONS[cat2]?.[cat1];
    return fromMap ?? 0.3; // Default moderate correlation
};

// 2. Generate Synthetic Time Series (Geometric Brownian Motion with correlated noise)
// Simplified: We generate independent series first, then mix them based on correlation.
// Actually for this demo, calculating "Theoretical Correlation" is better than random simulation noise.
// We will return the Correlation Matrix directly based on the assets.

export interface CorrelationMatrix {
    assets: string[];
    matrix: number[][]; // N x N matrix
}

export const calculateCorrelationMatrix = (allocations: AssetAllocation[]): CorrelationMatrix => {
    const assets = allocations.map(a => a.asset.name);
    const n = assets.length;
    const matrix: number[][] = Array(n).fill(0).map(() => Array(n).fill(0));

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            if (i === j) {
                matrix[i][j] = 1.0;
            } else {
                const asset1 = allocations[i].asset;
                const asset2 = allocations[j].asset;

                // Get Base Correlation from Category
                let correlation = getPriorCorrelation(asset1.category, asset2.category);

                // Adjust for Risk Level (Higher risk assets tend to correlate more in tail events, but here we just add noise)
                // If same asset ID (should cover i==j, but good safety)
                if (asset1.id === asset2.id) correlation = 1.0;

                matrix[i][j] = correlation;
            }
        }
    }

    return { assets, matrix };
};

export const interpretCorrelation = (val: number): string => {
    if (val > 0.8) return 'Very High';
    if (val > 0.5) return 'High';
    if (val > 0.2) return 'Low';
    if (val > -0.2) return 'Uncorrelated';
    return 'Inverse';
};
