import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button,
  CircularProgress
} from '@mui/material';
import { supabase } from '../lib/supabase';

export default function TestInvestmentUniverse() {
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(0);
  const [data, setData] = useState<any[]>([]);

  const testLoad = async () => {
    setLoading(true);
    console.log('=== 테스트 시작 ===');
    
    try {
      // 첫 번째 페이지 테스트
      console.log('첫 번째 페이지 로딩...');
      const { data: firstPage, error: error1, count: totalCount } = await supabase
        .from('kw_financial_snapshot')
        .select('*', { count: 'exact' })
        .range(0, 999);
      
      if (error1) {
        console.error('에러:', error1);
        return;
      }
      
      console.log(`첫 페이지: ${firstPage?.length}개, 전체: ${totalCount}개`);
      setData(firstPage || []);
      setCount(totalCount || 0);
      
      // 두 번째 페이지 테스트
      if (totalCount && totalCount > 1000) {
        console.log('두 번째 페이지 로딩...');
        const { data: secondPage, error: error2 } = await supabase
          .from('kw_financial_snapshot')
          .select('*')
          .range(1000, 1999);
        
        if (error2) {
          console.error('두 번째 페이지 에러:', error2);
        } else {
          console.log(`두 번째 페이지: ${secondPage?.length}개`);
          setData(prev => [...prev, ...(secondPage || [])]);
        }
      }
      
      // 세 번째 페이지 테스트
      if (totalCount && totalCount > 2000) {
        console.log('세 번째 페이지 로딩...');
        const { data: thirdPage, error: error3 } = await supabase
          .from('kw_financial_snapshot')
          .select('*')
          .range(2000, 2999);
        
        if (error3) {
          console.error('세 번째 페이지 에러:', error3);
        } else {
          console.log(`세 번째 페이지: ${thirdPage?.length}개`);
          setData(prev => [...prev, ...(thirdPage || [])]);
        }
      }
      
      // 네 번째 페이지 테스트
      if (totalCount && totalCount > 3000) {
        console.log('네 번째 페이지 로딩...');
        const { data: fourthPage, error: error4 } = await supabase
          .from('kw_financial_snapshot')
          .select('*')
          .range(3000, 3999);
        
        if (error4) {
          console.error('네 번째 페이지 에러:', error4);
        } else {
          console.log(`네 번째 페이지: ${fourthPage?.length}개`);
          setData(prev => [...prev, ...(fourthPage || [])]);
        }
      }
      
    } catch (error) {
      console.error('전체 에러:', error);
    } finally {
      setLoading(false);
      console.log('=== 테스트 완료 ===');
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Supabase 페이지네이션 테스트
      </Typography>
      
      <Box sx={{ my: 2 }}>
        <Button 
          variant="contained" 
          onClick={testLoad}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : '데이터 로드 테스트'}
        </Button>
      </Box>
      
      <Box>
        <Typography>전체 개수: {count}</Typography>
        <Typography>로드된 개수: {data.length}</Typography>
      </Box>
      
      {data.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">샘플 데이터 (상위 5개):</Typography>
          {data.slice(0, 5).map((item, idx) => (
            <Typography key={idx}>
              {item.stock_code} - {item.stock_name} - 시가총액: {Number(item.market_cap)?.toLocaleString()}
            </Typography>
          ))}
        </Box>
      )}
    </Paper>
  );
}