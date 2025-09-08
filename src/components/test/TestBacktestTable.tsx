import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Button, Alert, Chip, Stack } from '@mui/material';
import { supabase } from '../../lib/supabase';
import { authService } from '../../services/auth';
import { checkBacktestResultsTable, validateTableStructure } from '../../utils/checkBacktestTable';

const TestBacktestTable: React.FC = () => {
  const [tableInfo, setTableInfo] = useState<any>(null);
  const [sampleData, setSampleData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  const checkTable = async () => {
    try {
      setError(null);
      
      // 현재 사용자 확인
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      
      if (!currentUser) {
        setError('로그인이 필요합니다.');
        return;
      }

      // 전체 테이블 구조 확인
      const tableCheckResult = await checkBacktestResultsTable();
      
      if ('error' in tableCheckResult) {
        setError(`테이블 확인 오류: ${tableCheckResult.error}`);
        return;
      }

      // 사용자 데이터 조회
      const { data, error: fetchError } = await supabase
        .from('backtest_results')
        .select('*')
        .eq('user_id', currentUser.id)
        .limit(5)
        .order('created_at', { ascending: false });

      if (fetchError) {
        setError(`테이블 조회 오류: ${fetchError.message}`);
        console.error('Fetch error:', fetchError);
      } else {
        setSampleData(data || []);
        
        // 테이블 구조 검증
        const validation = 'columns' in tableCheckResult && tableCheckResult.columns ? 
          validateTableStructure(tableCheckResult.columns) : 
          { isValid: false, missingColumns: [], extraColumns: [] };
        
        setTableInfo({
          ...tableCheckResult,
          userDataCount: data?.length || 0,
          validation,
          userData: data
        });
      }
    } catch (err: any) {
      setError(`예외 오류: ${err.message}`);
      console.error('Exception:', err);
    }
  };

  // 샘플 데이터 삽입 (테스트용)
  const insertSampleData = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      if (!currentUser) {
        setError('로그인이 필요합니다.');
        return;
      }

      const sampleResult = {
        user_id: currentUser.id,
        strategy_name: `테스트 전략 ${new Date().getTime()}`,
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        initial_capital: 10000000,
        total_return: Math.random() * 30 - 10,
        annual_return: Math.random() * 30 - 10,
        max_drawdown: -(Math.random() * 20),
        win_rate: Math.random() * 100,
        sharpe_ratio: Math.random() * 2,
        total_trades: Math.floor(Math.random() * 100),
        created_at: new Date().toISOString(),
      };

      const { data, error } = await supabase
        .from('backtest_results')
        .insert([sampleResult])
        .select();

      if (error) {
        setError(`데이터 삽입 오류: ${error.message}`);
      } else {
        setError(null);
        alert('샘플 데이터가 추가되었습니다.');
        checkTable(); // 테이블 다시 조회
      }
    } catch (err: any) {
      setError(`삽입 예외: ${err.message}`);
    }
  };

  useEffect(() => {
    checkTable();
  }, []);

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Backtest Results 테이블 테스트
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          현재 사용자: {user ? user.email : '미로그인'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          사용자 ID: {user ? user.id : 'N/A'}
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={checkTable} sx={{ mr: 1 }}>
          테이블 확인
        </Button>
        <Button variant="outlined" onClick={insertSampleData}>
          샘플 데이터 추가
        </Button>
      </Box>

      {tableInfo && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            테이블 정보:
          </Typography>
          
          <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
            <Chip 
              label={`전체 ${tableInfo.totalRows || 0}개 행`} 
              color="primary" 
              variant="outlined" 
            />
            <Chip 
              label={`내 데이터 ${tableInfo.userDataCount || 0}개`} 
              color="success" 
              variant="outlined" 
            />
            <Chip 
              label={`${tableInfo.columns?.length || 0}개 컬럼`} 
              color="info" 
              variant="outlined" 
            />
            {tableInfo.validation?.isValid ? (
              <Chip label="구조 정상" color="success" />
            ) : (
              <Chip label="구조 확인 필요" color="warning" />
            )}
          </Stack>

          {tableInfo.validation && !tableInfo.validation.isValid && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                필수 컬럼 누락: {tableInfo.validation.missingColumns.join(', ') || '없음'}
              </Typography>
            </Alert>
          )}
          
          {tableInfo.columns && tableInfo.columns.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 2 }}>
                컬럼 구조 ({tableInfo.columns.length}개):
              </Typography>
              <Box sx={{ 
                pl: 2, 
                mt: 1,
                maxHeight: 200,
                overflow: 'auto',
                bgcolor: 'background.paper',
                p: 1,
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider'
              }}>
                {tableInfo.columns.map((col: string) => (
                  <Typography key={col} variant="body2" sx={{ fontFamily: 'monospace' }}>
                    • {col}: {tableInfo.columnTypes?.[col] || 'unknown'}
                  </Typography>
                ))}
              </Box>
              
              {tableInfo.validation?.extraColumns && tableInfo.validation.extraColumns.length > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  추가 컬럼: {tableInfo.validation.extraColumns.join(', ')}
                </Typography>
              )}
            </>
          )}
        </Box>
      )}

      {sampleData.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            샘플 데이터 ({sampleData.length}개):
          </Typography>
          <Box sx={{ 
            maxHeight: 300, 
            overflow: 'auto', 
            bgcolor: 'background.paper',
            p: 1,
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider'
          }}>
            <pre style={{ fontSize: '12px', margin: 0 }}>
              {JSON.stringify(sampleData, null, 2)}
            </pre>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default TestBacktestTable;