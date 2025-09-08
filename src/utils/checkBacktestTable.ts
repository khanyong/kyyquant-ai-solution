import { supabase } from '../lib/supabase';

export async function checkBacktestResultsTable() {
  console.log('=== Checking backtest_results table ===');
  
  try {
    // 1. 테이블 구조 확인 (첫 번째 행만 가져와서 컬럼 확인)
    const { data: sampleData, error: sampleError } = await supabase
      .from('backtest_results')
      .select('*')
      .limit(1);
    
    if (sampleError) {
      console.error('Error fetching sample:', sampleError);
      return { error: sampleError };
    }
    
    // 2. 전체 데이터 개수 확인
    const { count, error: countError } = await supabase
      .from('backtest_results')
      .select('*', { count: 'exact', head: true });
    
    if (countError) {
      console.error('Error counting rows:', countError);
    }
    
    // 3. 컬럼 정보 추출
    let columns: string[] = [];
    let columnTypes: Record<string, string> = {};
    
    if (sampleData && sampleData.length > 0) {
      columns = Object.keys(sampleData[0]);
      for (const col of columns) {
        const value = sampleData[0][col];
        columnTypes[col] = value === null ? 'null' : typeof value;
      }
    }
    
    // 4. 최근 데이터 5개 확인
    const { data: recentData, error: recentError } = await supabase
      .from('backtest_results')
      .select('id, strategy_name, created_at, total_return, win_rate, total_trades')
      .order('created_at', { ascending: false })
      .limit(5);
    
    if (recentError) {
      console.error('Error fetching recent data:', recentError);
    }
    
    const result = {
      tableExists: !sampleError,
      totalRows: count || 0,
      columns: columns,
      columnTypes: columnTypes,
      sampleRow: sampleData?.[0] || null,
      recentData: recentData || [],
    };
    
    console.log('Table Check Result:', result);
    return result;
    
  } catch (error) {
    console.error('Exception in checkBacktestResultsTable:', error);
    return { error };
  }
}

// 테이블에 필요한 컬럼이 있는지 확인
export function validateTableStructure(columns: string[]): {
  isValid: boolean;
  missingColumns: string[];
  extraColumns: string[];
  optionalColumns: string[];
} {
  const requiredColumns = [
    'id',
    'user_id',
    'start_date',
    'end_date',
    'initial_capital',
    'final_capital',
    'total_return',
    'max_drawdown',
    'total_trades',
    'profitable_trades',
    'created_at'
  ];
  
  const optionalColumns = [
    'strategy_id',
    'strategy_name',
    'test_period_start',
    'test_period_end',
    'sharpe_ratio',
    'win_rate',
    'winning_trades',
    'losing_trades',
    'avg_profit',
    'avg_loss',
    'profit_factor',
    'recovery_factor',
    'results_data',
    'trade_details',
    'daily_returns',
    'updated_at'
  ];
  
  const allKnownColumns = [...requiredColumns, ...optionalColumns];
  
  const missingColumns = requiredColumns.filter(col => !columns.includes(col));
  const extraColumns = columns.filter(col => !allKnownColumns.includes(col));
  const presentOptionalColumns = optionalColumns.filter(col => columns.includes(col));
  
  return {
    isValid: missingColumns.length === 0,
    missingColumns,
    extraColumns,
    optionalColumns: presentOptionalColumns
  };
}