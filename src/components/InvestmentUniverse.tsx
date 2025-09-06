import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Slider, 
  Grid, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress
} from '@mui/material';
import { supabase } from '../lib/supabase';

interface StockData {
  id: number;
  stock_code: string;
  stock_name: string;
  market: string;
  market_cap: number;
  current_price: number;
  per: number;
  pbr: number;
  roe: number;
  high_52w: number;
  low_52w: number;
}

interface FilterCriteria {
  marketCap: [number, number];
  per: [number, number];
  pbr: [number, number];
  roe: [number, number];
  market: string;
  searchTerm: string;
}

export default function InvestmentUniverse() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  const [filters, setFilters] = useState<FilterCriteria>({
    marketCap: [0, 10000000], // 0 ~ 10조원
    per: [0, 100],
    pbr: [0, 10],
    roe: [-50, 50],
    market: 'ALL',
    searchTerm: ''
  });

  // 데이터 로드 (페이지네이션으로 전체 데이터 가져오기)
  useEffect(() => {
    loadStockData();
  }, []);

  const loadStockData = async () => {
    try {
      setLoading(true);
      let allData: StockData[] = [];
      let offset = 0;
      const pageSize = 1000;
      let pageCount = 0;
      
      console.log('데이터 로딩 시작...');
      
      // 페이지네이션으로 모든 데이터 가져오기
      while (true) {
        console.log(`페이지 ${pageCount + 1} 로딩 중... (offset: ${offset})`);
        
        const { data, error, count } = await supabase
          .from('kw_financial_snapshot')
          .select('*', { count: 'exact' })
          .order('market_cap', { ascending: false, nullsLast: true })
          .range(offset, offset + pageSize - 1);

        if (error) {
          console.error('Supabase 에러:', error);
          throw error;
        }
        
        console.log(`페이지 ${pageCount + 1}: ${data?.length || 0}개 데이터 받음, 전체: ${count}개`);
        
        if (!data || data.length === 0) {
          console.log('더 이상 데이터가 없음');
          break;
        }
        
        // 데이터 타입 변환 (문자열을 숫자로)
        const convertedData = data.map(item => ({
          ...item,
          market_cap: Number(item.market_cap) || 0,
          current_price: Number(item.current_price) || 0,
          per: Number(item.per) || 0,
          pbr: Number(item.pbr) || 0,
          roe: Number(item.roe) || 0,
          high_52w: Number(item.high_52w) || 0,
          low_52w: Number(item.low_52w) || 0,
        }));
        
        allData = [...allData, ...convertedData];
        pageCount++;
        
        // 마지막 페이지인지 확인
        if (data.length < pageSize) {
          console.log('마지막 페이지 도달');
          break;
        }
        
        offset += pageSize;
        
        // 너무 많은 페이지 방지 (최대 10페이지)
        if (pageCount >= 10) {
          console.log('최대 페이지 수 도달');
          break;
        }
      }
      
      console.log(`✅ 총 ${allData.length}개 종목 로드 완료`);
      setStocks(allData);
    } catch (error) {
      console.error('Error loading stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  // 필터링된 데이터
  const filteredStocks = useMemo(() => {
    return stocks.filter(stock => {
      // 시가총액 필터
      if (stock.market_cap > 0) {
        const marketCapBillion = stock.market_cap / 100000000; // 억원 단위
        if (marketCapBillion < filters.marketCap[0] || 
            marketCapBillion > filters.marketCap[1]) return false;
      }
      
      // PER 필터 (0보다 큰 경우만 필터 적용)
      if (stock.per > 0 && (stock.per < filters.per[0] || 
          stock.per > filters.per[1])) return false;
      
      // PBR 필터 (0보다 큰 경우만 필터 적용)
      if (stock.pbr > 0 && (stock.pbr < filters.pbr[0] || 
          stock.pbr > filters.pbr[1])) return false;
      
      // ROE 필터 (0이 아닌 경우만 필터 적용)
      if (stock.roe !== 0 && (stock.roe < filters.roe[0] || 
          stock.roe > filters.roe[1])) return false;
      
      // 시장 필터
      if (filters.market !== 'ALL' && stock.market !== filters.market) return false;
      
      // 검색어 필터
      if (filters.searchTerm && 
          !stock.stock_name?.toLowerCase().includes(filters.searchTerm.toLowerCase()) &&
          !stock.stock_code?.includes(filters.searchTerm)) return false;
      
      return true;
    });
  }, [stocks, filters]);

  const handleFilterChange = (key: keyof FilterCriteria, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(0); // 필터 변경시 첫 페이지로
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}조`;
    if (num >= 10000) return `${(num / 10000).toFixed(1)}억`;
    return `${num.toFixed(0)}백만`;
  };

  const formatPrice = (price: number): string => {
    return price?.toLocaleString() || '-';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        투자 유니버스 설정
      </Typography>
      
      {/* 필터 섹션 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          필터 설정
        </Typography>
        
        <Grid container spacing={3}>
          {/* 시가총액 필터 */}
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>
              시가총액: {formatNumber(filters.marketCap[0])} ~ {formatNumber(filters.marketCap[1])}
            </Typography>
            <Slider
              value={filters.marketCap}
              onChange={(_, value) => handleFilterChange('marketCap', value)}
              valueLabelDisplay="auto"
              min={0}
              max={10000000}
              step={10000}
              valueLabelFormat={formatNumber}
              marks={[
                { value: 0, label: '0' },
                { value: 100000, label: '1000억' },
                { value: 1000000, label: '1조' },
                { value: 10000000, label: '10조' }
              ]}
            />
          </Grid>

          {/* PER 필터 */}
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>
              PER: {filters.per[0]} ~ {filters.per[1]}
            </Typography>
            <Slider
              value={filters.per}
              onChange={(_, value) => handleFilterChange('per', value)}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              step={1}
            />
          </Grid>

          {/* PBR 필터 */}
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>
              PBR: {filters.pbr[0]} ~ {filters.pbr[1]}
            </Typography>
            <Slider
              value={filters.pbr}
              onChange={(_, value) => handleFilterChange('pbr', value)}
              valueLabelDisplay="auto"
              min={0}
              max={10}
              step={0.1}
            />
          </Grid>

          {/* ROE 필터 */}
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>
              ROE: {filters.roe[0]}% ~ {filters.roe[1]}%
            </Typography>
            <Slider
              value={filters.roe}
              onChange={(_, value) => handleFilterChange('roe', value)}
              valueLabelDisplay="auto"
              min={-50}
              max={50}
              step={1}
            />
          </Grid>

          {/* 시장 선택 */}
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>시장</InputLabel>
              <Select
                value={filters.market}
                label="시장"
                onChange={(e) => handleFilterChange('market', e.target.value)}
              >
                <MenuItem value="ALL">전체</MenuItem>
                <MenuItem value="KOSPI">KOSPI</MenuItem>
                <MenuItem value="KOSDAQ">KOSDAQ</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* 검색 */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="종목명/코드 검색"
              value={filters.searchTerm}
              onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
            />
          </Grid>

          {/* 결과 요약 */}
          <Grid item xs={12} md={4}>
            <Box display="flex" alignItems="center" height="100%">
              <Chip 
                label={`${filteredStocks.length}개 종목`}
                color="primary"
                sx={{ fontSize: '1.1rem', py: 2.5 }}
              />
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* 결과 테이블 */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>코드</TableCell>
                <TableCell>종목명</TableCell>
                <TableCell>시장</TableCell>
                <TableCell align="right">현재가</TableCell>
                <TableCell align="right">시가총액</TableCell>
                <TableCell align="right">PER</TableCell>
                <TableCell align="right">PBR</TableCell>
                <TableCell align="right">ROE(%)</TableCell>
                <TableCell align="right">52주 최고/최저</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredStocks
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((stock) => (
                  <TableRow key={stock.id}>
                    <TableCell>{stock.stock_code}</TableCell>
                    <TableCell>{stock.stock_name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={stock.market} 
                        size="small"
                        color={stock.market === 'KOSPI' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell align="right">{formatPrice(stock.current_price)}</TableCell>
                    <TableCell align="right">
                      {stock.market_cap > 0 ? formatNumber(stock.market_cap / 100000000) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {stock.per > 0 ? stock.per.toFixed(2) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {stock.pbr > 0 ? stock.pbr.toFixed(2) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {stock.roe !== 0 ? stock.roe.toFixed(1) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      <Box>
                        <Typography variant="caption" color="error">
                          {formatPrice(stock.high_52w)}
                        </Typography>
                        <br />
                        <Typography variant="caption" color="primary">
                          {formatPrice(stock.low_52w)}
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={filteredStocks.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          labelRowsPerPage="페이지당 행 수:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} / 전체 ${count}개`
          }
        />
      </Paper>
    </Box>
  );
}