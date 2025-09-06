import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
  Chip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Badge,
  Alert,
  LinearProgress,
  Drawer,
  Tooltip,
  TextField,
  InputAdornment
} from '@mui/material'
import {
  FilterList,
  Business,
  TrendingUp,
  Assessment,
  ShowChart,
  Visibility,
  VisibilityOff,
  Search,
  Download,
  Refresh,
  Star,
  StarBorder,
  CheckCircle,
  ArrowForward,
  OpenInNew,
  Settings
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { useNavigate } from 'react-router-dom'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

const InvestmentSettingsWithPreview: React.FC = () => {
  const navigate = useNavigate()
  const [currentTab, setCurrentTab] = useState(0)
  const [showPreview, setShowPreview] = useState(true)
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 필터 설정
  const [filters, setFilters] = useState({
    marketCap: [100, 50000],
    per: [5, 25],
    pbr: [0.5, 3],
    roe: [5, 30],
    debtRatio: [0, 100],
    sectors: {
      include: ['IT', '반도체', '2차전지', '바이오'],
      exclude: ['건설', '조선']
    }
  })

  // 필터링 결과
  const [filterResults, setFilterResults] = useState({
    totalCount: 2847,
    afterMarketCap: 1523,
    afterFinancial: 486,
    afterSector: 142,
    stocks: [] as any[]
  })

  // 샘플 데이터 (실제로는 Supabase에서 조회)
  const sampleStocks = [
    { 
      code: '005930', 
      name: '삼성전자', 
      marketCap: 450000, 
      per: 12.5, 
      pbr: 1.2, 
      roe: 8.5, 
      debtRatio: 35,
      sector: 'IT',
      price: 72000,
      change: -1.2,
      volume: 15234567
    },
    { 
      code: '000660', 
      name: 'SK하이닉스', 
      marketCap: 90000, 
      per: 15.2, 
      pbr: 1.8, 
      roe: 12.3, 
      debtRatio: 42,
      sector: '반도체',
      price: 132000,
      change: 2.3,
      volume: 8234567
    },
    { 
      code: '035720', 
      name: '카카오', 
      marketCap: 25000, 
      per: 45.6, 
      pbr: 2.5, 
      roe: 5.2, 
      debtRatio: 18,
      sector: 'IT',
      price: 55000,
      change: 0.5,
      volume: 5234567
    },
    { 
      code: '051910', 
      name: 'LG화학', 
      marketCap: 40000, 
      per: 18.9, 
      pbr: 1.1, 
      roe: 9.8, 
      debtRatio: 55,
      sector: '화학',
      price: 420000,
      change: -0.8,
      volume: 2234567
    },
    { 
      code: '006400', 
      name: '삼성SDI', 
      marketCap: 35000, 
      per: 22.3, 
      pbr: 2.1, 
      roe: 11.5, 
      debtRatio: 28,
      sector: '2차전지',
      price: 680000,
      change: 1.5,
      volume: 1234567
    }
  ]

  // 필터 적용 시뮬레이션
  const applyFilters = async () => {
    setLoading(true)
    
    // 시뮬레이션 딜레이
    setTimeout(() => {
      setFilterResults({
        ...filterResults,
        stocks: sampleStocks.filter(stock => 
          stock.marketCap >= filters.marketCap[0] &&
          stock.marketCap <= filters.marketCap[1] &&
          stock.per >= filters.per[0] &&
          stock.per <= filters.per[1] &&
          stock.pbr >= filters.pbr[0] &&
          stock.pbr <= filters.pbr[1] &&
          stock.roe >= filters.roe[0] &&
          stock.roe <= filters.roe[1] &&
          stock.debtRatio >= filters.debtRatio[0] &&
          stock.debtRatio <= filters.debtRatio[1]
        )
      })
      setLoading(false)
    }, 500)
  }

  useEffect(() => {
    applyFilters()
  }, [filters])

  const formatNumber = (num: number) => {
    if (num >= 10000) return `${(num / 10000).toFixed(1)}조`
    if (num >= 100) return `${(num / 100).toFixed(0)}억`
    return `${num}억`
  }

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 100px)' }}>
      {/* 왼쪽: 투자 설정 영역 */}
      <Box sx={{ flex: showPreview ? '0 0 60%' : 1, transition: 'all 0.3s' }}>
        <Paper sx={{ height: '100%', overflow: 'auto', p: 3 }}>
          {/* 헤더 */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Settings />
              투자 설정
            </Typography>
            
            <Stack direction="row" spacing={2}>
              <Chip 
                icon={<Business />}
                label={`유니버스: ${filterResults.stocks.length}개`}
                color="primary"
              />
              <Button
                variant="outlined"
                startIcon={showPreview ? <VisibilityOff /> : <Visibility />}
                onClick={() => setShowPreview(!showPreview)}
              >
                {showPreview ? '프리뷰 숨기기' : '프리뷰 보기'}
              </Button>
              <Button
                variant="contained"
                startIcon={<ShowChart />}
                onClick={() => navigate('/strategy-builder')}
              >
                전략 구성하기
              </Button>
            </Stack>
          </Box>

          {/* 탭 메뉴 */}
          <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
            <Tab label="투자 유니버스" icon={<FilterList />} iconPosition="start" />
            <Tab label="매매 조건" icon={<TrendingUp />} iconPosition="start" />
            <Tab label="섹터 설정" icon={<Business />} iconPosition="start" />
            <Tab label="리스크 관리" icon={<Assessment />} iconPosition="start" />
          </Tabs>

          <Divider sx={{ my: 2 }} />

          {/* 투자 유니버스 탭 */}
          <TabPanel value={currentTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>시가총액 (억원)</Typography>
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField 
                          label="최소" 
                          value={filters.marketCap[0]}
                          type="number"
                          onChange={(e) => setFilters({
                            ...filters,
                            marketCap: [Number(e.target.value), filters.marketCap[1]]
                          })}
                        />
                        <TextField 
                          label="최대" 
                          value={filters.marketCap[1]}
                          type="number"
                          onChange={(e) => setFilters({
                            ...filters,
                            marketCap: [filters.marketCap[0], Number(e.target.value)]
                          })}
                        />
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>PER (주가수익비율)</Typography>
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField 
                          label="최소" 
                          value={filters.per[0]}
                          type="number"
                          onChange={(e) => setFilters({
                            ...filters,
                            per: [Number(e.target.value), filters.per[1]]
                          })}
                        />
                        <TextField 
                          label="최대" 
                          value={filters.per[1]}
                          type="number"
                          onChange={(e) => setFilters({
                            ...filters,
                            per: [filters.per[0], Number(e.target.value)]
                          })}
                        />
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Alert severity="info">
                  설정을 변경하면 오른쪽 패널에서 실시간으로 필터링 결과를 확인할 수 있습니다.
                </Alert>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 다른 탭들 */}
          <TabPanel value={currentTab} index={1}>
            <Typography>매매 조건 설정</Typography>
          </TabPanel>
          
          <TabPanel value={currentTab} index={2}>
            <Typography>섹터 설정</Typography>
          </TabPanel>
          
          <TabPanel value={currentTab} index={3}>
            <Typography>리스크 관리</Typography>
          </TabPanel>
        </Paper>
      </Box>

      {/* 오른쪽: 실시간 프리뷰 */}
      {showPreview && (
        <Box sx={{ flex: '0 0 40%', borderLeft: '1px solid', borderColor: 'divider' }}>
          <Paper sx={{ height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            {/* 프리뷰 헤더 */}
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Visibility />
                실시간 필터링 결과
              </Typography>
              
              {/* 필터 단계별 결과 */}
              <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                <Chip size="small" label={`전체: ${filterResults.totalCount}`} />
                <ArrowForward fontSize="small" />
                <Chip size="small" label={`시총: ${filterResults.afterMarketCap}`} color="primary" />
                <ArrowForward fontSize="small" />
                <Chip size="small" label={`재무: ${filterResults.afterFinancial}`} color="secondary" />
                <ArrowForward fontSize="small" />
                <Chip size="small" label={`최종: ${filterResults.stocks.length}`} color="success" />
              </Stack>

              {/* 검색 */}
              <TextField
                size="small"
                fullWidth
                placeholder="종목명 또는 코드 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{ mt: 2 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>

            {/* 종목 리스트 */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {loading && <LinearProgress />}
              
              <List>
                {filterResults.stocks
                  .filter(stock => 
                    stock.name.includes(searchTerm) || 
                    stock.code.includes(searchTerm)
                  )
                  .map((stock) => (
                    <ListItem key={stock.code} divider>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">{stock.name}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {stock.code}
                            </Typography>
                            <Chip label={stock.sector} size="small" variant="outlined" />
                          </Box>
                        }
                        secondary={
                          <Grid container spacing={2} sx={{ mt: 0.5 }}>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="textSecondary">
                                시총: {formatNumber(stock.marketCap)}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="textSecondary">
                                PER: {stock.per}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="textSecondary">
                                PBR: {stock.pbr}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="textSecondary">
                                ROE: {stock.roe}%
                              </Typography>
                            </Grid>
                          </Grid>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton size="small">
                          <StarBorder />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
              </List>

              {filterResults.stocks.length === 0 && !loading && (
                <Box sx={{ textAlign: 'center', py: 5 }}>
                  <Typography color="textSecondary">
                    필터 조건에 맞는 종목이 없습니다
                  </Typography>
                </Box>
              )}
            </Box>

            {/* 프리뷰 푸터 */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  size="small"
                  fullWidth
                >
                  Excel 다운로드
                </Button>
                <Button
                  variant="contained"
                  startIcon={<OpenInNew />}
                  size="small"
                  fullWidth
                  onClick={() => {
                    // 필터링된 종목 리스트를 전략빌더로 전달
                    localStorage.setItem('filteredStocks', JSON.stringify(filterResults.stocks))
                    navigate('/strategy-builder')
                  }}
                >
                  전략 적용
                </Button>
              </Stack>
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  )
}

export default InvestmentSettingsWithPreview