
import { AssetAllocation } from '../../utils/SimulationEngine';

export interface Portfolio {
    id: number;
    name: string;
    allocations: AssetAllocation[];
}

export interface SimulationParams {
    totalCapital: number;
    simYears: number;
    monthlyContribution: number;
    rebalanceFreq: string;
    benchmark: string;
}
