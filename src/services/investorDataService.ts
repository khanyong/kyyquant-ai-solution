import { supabase } from './supabase';

export interface InvestorData {
  date: string;
  individual_buy: number;
  individual_sell: number;
  individual_net: number;
  foreign_buy: number;
  foreign_sell: number;
  foreign_net: number;
  institution_buy: number;
  institution_sell: number;
  institution_net: number;
  program_buy: number;
  program_sell: number;
  program_net: number;
}

export interface InvestorTrend {
  investor_type: string;
  trend: 'accumulating' | 'distributing' | 'neutral';
  net_amount: number;
  percentage: number;
}

class InvestorDataService {
  async getRecentInvestorData(days: number = 20): Promise<InvestorData[]> {
    try {
      const { data, error } = await supabase
        .from('kw_investor_data')
        .select('*')
        .order('date', { ascending: false })
        .limit(days);

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching investor data:', error);
      return [];
    }
  }

  async getInvestorTrends(): Promise<InvestorTrend[]> {
    try {
      const data = await this.getRecentInvestorData(20);
      
      if (data.length === 0) return [];

      const trends: InvestorTrend[] = [];
      
      // Calculate trends for each investor type
      const investorTypes = [
        { key: 'individual', label: '개인' },
        { key: 'foreign', label: '외국인' },
        { key: 'institution', label: '기관' },
        { key: 'program', label: '프로그램' }
      ];

      for (const type of investorTypes) {
        const netKey = `${type.key}_net` as keyof InvestorData;
        const totalNet = data.reduce((sum, d) => sum + (d[netKey] as number || 0), 0);
        const avgNet = totalNet / data.length;
        
        let trend: 'accumulating' | 'distributing' | 'neutral' = 'neutral';
        if (avgNet > 1000000000) trend = 'accumulating';
        else if (avgNet < -1000000000) trend = 'distributing';

        trends.push({
          investor_type: type.label,
          trend,
          net_amount: totalNet,
          percentage: 0 // Calculate percentage if needed
        });
      }

      return trends;
    } catch (error) {
      console.error('Error calculating investor trends:', error);
      return [];
    }
  }

  async getInvestorDataByDateRange(startDate: string, endDate: string): Promise<InvestorData[]> {
    try {
      const { data, error } = await supabase
        .from('kw_investor_data')
        .select('*')
        .gte('date', startDate)
        .lte('date', endDate)
        .order('date', { ascending: true });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching investor data by date range:', error);
      return [];
    }
  }

  formatAmount(amount: number): string {
    const billion = 1000000000;
    const million = 1000000;
    
    if (Math.abs(amount) >= billion) {
      return `${(amount / billion).toFixed(1)}억`;
    } else if (Math.abs(amount) >= million) {
      return `${(amount / million).toFixed(0)}백만`;
    }
    return amount.toLocaleString();
  }

  getNetFlowColor(amount: number): string {
    if (amount > 0) return 'success';
    if (amount < 0) return 'error';
    return 'default';
  }
}

export const investorDataService = new InvestorDataService();