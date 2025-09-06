import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Chip,
  Stack,
  Button,
  IconButton,
  Tooltip,
  Badge,
  Divider,
  LinearProgress,
  Alert,
  Collapse,
  TextField,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
  Fade,
  Zoom
} from '@mui/material'
import {
  FilterList,
  Business,
  ShowChart,
  TrendingUp,
  Assessment,
  Search,
  ExpandMore,
  ExpandLess,
  Info,
  CheckCircle,
  Warning,
  Star,
  StarBorder,
  ViewList,
  ViewModule,
  Refresh,
  Download,
  ArrowUpward,
  ArrowDownward,
  Circle,
  ArrowForward
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

interface Stock {
  code: string
  name: string
  marketCap: number
  per: number
  pbr: number
  roe: number
  debtRatio: number
  sector: string
  price: number
  change: number
  volume: number
  score?: number // 전략 적합도 점수
}

interface FilterStats {
  totalStocks: number
  afterMarketCap: number
  afterFinancial: number
  afterSector: number
  finalCount: number
}

interface InvestmentWorkspaceProps {
  investmentConfig: any
  strategy: any
  onUniverseChange?: (stocks: Stock[]) => void
  onStockSelect?: (stock: Stock) => void
}

const InvestmentWorkspace: React.FC<InvestmentWorkspaceProps> = ({
  investmentConfig,
  strategy,
  onUniverseChange,
  onStockSelect
}) => {
  const [filteredStocks, setFilteredStocks] = useState<Stock[]>([])
  const [filterStats, setFilterStats] = useState<FilterStats>({
    totalStocks: 0,
    afterMarketCap: 0,
    afterFinancial: 0,
    afterSector: 0,
    finalCount: 0
  })
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list')
  const [sortBy, setSortBy] = useState<'marketCap' | 'per' | 'roe' | 'change'>('marketCap')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [expandedPanel, setExpandedPanel] = useState<string | null>('universe')
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  // 투자 유니버스 필터링
  const applyFilters = async () => {
    setLoading(true)
    try {
      // 1. 전체 종목 조회
      let query = supabase
        .from('kw_stock_list')
        .select('*')

      const { data: allStocks, error: listError } = await query
      if (listError) throw listError

      setFilterStats(prev => ({ ...prev, totalStocks: allStocks?.length || 0 }))

      // 2. 시가총액 필터
      if (investmentConfig?.universe?.marketCap) {
        const [min, max] = investmentConfig.universe.marketCap
        query = supabase
          .from('kw_stock_financials')
          .select('*')
          .gte('market_cap', min * 100000000) // 억원 -> 원
          .lte('market_cap', max * 100000000)
      }

      const { data: marketCapFiltered } = await query
      setFilterStats(prev => ({ ...prev, afterMarketCap: marketCapFiltered?.length || 0 }))

      // 3. 재무지표 필터 (PER, PBR, ROE, 부채비율)
      if (investmentConfig?.universe) {
        const { per, pbr, roe, debtRatio } = investmentConfig.universe

        if (per) {
          query = query.gte('per', per[0]).lte('per', per[1])
        }
        if (pbr) {
          query = query.gte('pbr', pbr[0]).lte('pbr', pbr[1])
        }
        if (roe) {
          query = query.gte('roe', roe[0]).lte('roe', roe[1])
        }
        if (debtRatio) {
          query = query.gte('debt_ratio', debtRatio[0]).lte('debt_ratio', debtRatio[1])
        }
      }

      const { data: financialFiltered } = await query
      setFilterStats(prev => ({ ...prev, afterFinancial: financialFiltered?.length || 0 }))

      // 4. 섹터 필터
      let sectorFiltered = financialFiltered
      if (investmentConfig?.sectors) {
        const { include, exclude } = investmentConfig.sectors
        
        if (include?.length > 0) {
          sectorFiltered = financialFiltered?.filter((stock: any) => 
            include.includes(stock.sector)
          ) || null
        }
        
        if (exclude?.length > 0) {
          sectorFiltered = sectorFiltered?.filter((stock: any) => 
            !exclude.includes(stock.sector)
          ) || null
        }
      }

      setFilterStats(prev => ({ 
        ...prev, 
        afterSector: sectorFiltered?.length || 0,
        finalCount: sectorFiltered?.length || 0
      }))

      // 5. 주가 정보 조회 및 병합
      const stockCodes = sectorFiltered?.map((s: any) => s.code) || []
      
      if (stockCodes.length > 0) {
        const { data: priceData } = await supabase
          .from('kw_stock_prices')
          .select('code, close, change_rate, volume')
          .in('code', stockCodes)
          .order('date', { ascending: false })
          .limit(stockCodes.length)

        // 데이터 병합
        const mergedStocks = sectorFiltered?.map((stock: any) => {
          const price = priceData?.find(p => p.code === stock.code)
          return {
            ...stock,
            price: price?.close || 0,
            change: price?.change_rate || 0,
            volume: price?.volume || 0,
            score: calculateStrategyScore(stock, strategy)
          }
        })

        setFilteredStocks(mergedStocks || [])
        if (onUniverseChange) {
          onUniverseChange(mergedStocks || [])
        }
      }

    } catch (error) {
      console.error('Failed to apply filters:', error)
      setFilteredStocks([])
    } finally {
      setLoading(false)
    }
  }

  // 전략 적합도 점수 계산
  const calculateStrategyScore = (stock: any, strategy: any): number => {
    let score = 50 // 기본 점수

    // 전략에 따른 가중치 적용
    if (strategy?.indicators) {
      // RSI 전략이면 변동성 높은 종목 가중
      if (strategy.indicators.some((i: any) => i.id.includes('rsi'))) {
        if (stock.volatility > 20) score += 10
      }
      
      // 이평선 전략이면 추세 강한 종목 가중
      if (strategy.indicators.some((i: any) => i.id.includes('sma'))) {
        if (stock.trend_strength > 0.7) score += 15
      }
    }

    // 재무지표 기반 가산점
    if (stock.roe > 15) score += 10
    if (stock.per < 10 && stock.per > 0) score += 10
    if (stock.debt_ratio < 50) score += 5

    return Math.min(100, Math.max(0, score))
  }

  useEffect(() => {
    if (investmentConfig) {
      applyFilters()
    }
  }, [investmentConfig, strategy])

  // 검색 필터링
  const displayedStocks = filteredStocks
    .filter(stock => 
      stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.code.includes(searchTerm)
    )
    .sort((a, b) => {
      const order = sortOrder === 'asc' ? 1 : -1
      switch (sortBy) {
        case 'marketCap': return (a.marketCap - b.marketCap) * order
        case 'per': return (a.per - b.per) * order
        case 'roe': return (a.roe - b.roe) * order
        case 'change': return (a.change - b.change) * order
        default: return 0
      }
    })

  const toggleFavorite = (code: string) => {
    const newFavorites = new Set(favorites)
    if (favorites.has(code)) {
      newFavorites.delete(code)
    } else {
      newFavorites.add(code)
    }
    setFavorites(newFavorites)
  }

  const formatNumber = (num: number) => {
    if (num >= 1e12) return `${(num / 1e12).toFixed(1)}조`
    if (num >= 1e8) return `${(num / 1e8).toFixed(1)}억`
    if (num >= 1e4) return `${(num / 1e4).toFixed(1)}만`
    return num.toLocaleString()
  }

  return (
    <Box>
      {/* 헤더 - 필터 통계 */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction="row" spacing={3} alignItems="center">
            <Typography variant="h6">
              투자 유니버스
            </Typography>
            
            <Divider orientation="vertical" flexItem />
            
            <Stack direction="row" spacing={2} sx={{ flex: 1 }}>
              <Chip
                icon={<Business />}
                label={`전체: ${filterStats.totalStocks.toLocaleString()}`}
                variant="outlined"
              />
              <ArrowForward fontSize="small" sx={{ alignSelf: 'center' }} />
              <Chip
                icon={<FilterList />}
                label={`시가총액: ${filterStats.afterMarketCap.toLocaleString()}`}
                color={filterStats.afterMarketCap > 0 ? 'primary' : 'default'}
                variant={filterStats.afterMarketCap > 0 ? 'filled' : 'outlined'}
              />
              <ArrowForward fontSize="small" sx={{ alignSelf: 'center' }} />
              <Chip
                icon={<Assessment />}
                label={`재무필터: ${filterStats.afterFinancial.toLocaleString()}`}
                color={filterStats.afterFinancial > 0 ? 'secondary' : 'default'}
                variant={filterStats.afterFinancial > 0 ? 'filled' : 'outlined'}
              />
              <ArrowForward fontSize="small" sx={{ alignSelf: 'center' }} />
              <Chip
                icon={<CheckCircle />}
                label={`최종: ${filterStats.finalCount.toLocaleString()}종목`}
                color="success"
                variant="filled"
              />
            </Stack>

            <Button
              variant="outlined"
              size="small"
              startIcon={<Refresh />}
              onClick={applyFilters}
              disabled={loading}
            >
              새로고침
            </Button>
          </Stack>
        </CardContent>
        {loading && <LinearProgress />}
      </Card>

      {/* 메인 컨테이너 */}
      <Paper sx={{ p: 2 }}>
        {/* 도구 모음 */}
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <TextField
            size="small"
            placeholder="종목명 또는 코드 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ flex: 1, maxWidth: 300 }}
          />

          <ToggleButtonGroup
            size="small"
            value={sortBy}
            exclusive
            onChange={(e, value) => value && setSortBy(value)}
          >
            <ToggleButton value="marketCap">시가총액</ToggleButton>
            <ToggleButton value="per">PER</ToggleButton>
            <ToggleButton value="roe">ROE</ToggleButton>
            <ToggleButton value="change">등락률</ToggleButton>
          </ToggleButtonGroup>

          <IconButton
            size="small"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            {sortOrder === 'asc' ? <ArrowUpward /> : <ArrowDownward />}
          </IconButton>

          <ToggleButtonGroup
            size="small"
            value={viewMode}
            exclusive
            onChange={(e, value) => value && setViewMode(value)}
          >
            <ToggleButton value="list"><ViewList /></ToggleButton>
            <ToggleButton value="grid"><ViewModule /></ToggleButton>
          </ToggleButtonGroup>

          <Tooltip title="Excel 다운로드">
            <IconButton size="small">
              <Download />
            </IconButton>
          </Tooltip>
        </Stack>

        {/* 종목 리스트 */}
        {viewMode === 'list' ? (
          <List sx={{ maxHeight: 600, overflow: 'auto' }}>
            {displayedStocks.map((stock, index) => (
              <Fade in={true} timeout={300 + index * 50} key={stock.code}>
                <ListItem
                  disablePadding
                  secondaryAction={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip
                        size="small"
                        label={`${stock.score || 0}점`}
                        color={(stock.score || 0) > 70 ? 'success' : (stock.score || 0) > 40 ? 'warning' : 'default'}
                      />
                      <IconButton
                        size="small"
                        onClick={() => toggleFavorite(stock.code)}
                      >
                        {favorites.has(stock.code) ? <Star color="warning" /> : <StarBorder />}
                      </IconButton>
                    </Stack>
                  }
                >
                  <ListItemButton onClick={() => onStockSelect && onStockSelect(stock)}>
                    <ListItemText
                      primary={
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="subtitle2">
                            {stock.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {stock.code}
                          </Typography>
                          <Chip
                            size="small"
                            label={stock.sector}
                            variant="outlined"
                          />
                        </Stack>
                      }
                      secondary={
                        <Stack direction="row" spacing={2} sx={{ mt: 0.5 }}>
                          <Typography variant="caption">
                            시총: {formatNumber(stock.marketCap)}
                          </Typography>
                          <Typography variant="caption">
                            PER: {stock.per?.toFixed(1)}
                          </Typography>
                          <Typography variant="caption">
                            PBR: {stock.pbr?.toFixed(1)}
                          </Typography>
                          <Typography variant="caption">
                            ROE: {stock.roe?.toFixed(1)}%
                          </Typography>
                          <Typography
                            variant="caption"
                            color={stock.change > 0 ? 'error.main' : stock.change < 0 ? 'primary.main' : 'textSecondary'}
                          >
                            {stock.change > 0 ? '+' : ''}{stock.change?.toFixed(2)}%
                          </Typography>
                        </Stack>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              </Fade>
            ))}
          </List>
        ) : (
          <Grid container spacing={2} sx={{ maxHeight: 600, overflow: 'auto' }}>
            {displayedStocks.map((stock, index) => (
              <Zoom in={true} timeout={300 + index * 30} key={stock.code}>
                <Grid item xs={12} sm={6} md={4}>
                  <Card
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { boxShadow: 2 },
                      border: favorites.has(stock.code) ? '2px solid' : '1px solid',
                      borderColor: favorites.has(stock.code) ? 'warning.main' : 'divider'
                    }}
                    onClick={() => onStockSelect && onStockSelect(stock)}
                  >
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="start">
                        <Box>
                          <Typography variant="subtitle2">
                            {stock.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {stock.code} • {stock.sector}
                          </Typography>
                        </Box>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleFavorite(stock.code)
                          }}
                        >
                          {favorites.has(stock.code) ? <Star color="warning" /> : <StarBorder />}
                        </IconButton>
                      </Stack>

                      <Divider sx={{ my: 1 }} />

                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">시가총액</Typography>
                          <Typography variant="body2">{formatNumber(stock.marketCap)}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">등락률</Typography>
                          <Typography
                            variant="body2"
                            color={stock.change > 0 ? 'error.main' : 'primary.main'}
                          >
                            {stock.change > 0 ? '+' : ''}{stock.change?.toFixed(2)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">PER</Typography>
                          <Typography variant="body2">{stock.per?.toFixed(1)}</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">PBR</Typography>
                          <Typography variant="body2">{stock.pbr?.toFixed(1)}</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">ROE</Typography>
                          <Typography variant="body2">{stock.roe?.toFixed(1)}%</Typography>
                        </Grid>
                      </Grid>

                      <Box sx={{ mt: 1 }}>
                        <Stack direction="row" spacing={0.5} justifyContent="center">
                          <Chip
                            size="small"
                            label={`적합도 ${stock.score || 0}점`}
                            color={(stock.score || 0) > 70 ? 'success' : (stock.score || 0) > 40 ? 'warning' : 'default'}
                          />
                        </Stack>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Zoom>
            ))}
          </Grid>
        )}

        {/* 결과 없음 */}
        {displayedStocks.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', py: 5 }}>
            <Warning color="action" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" color="textSecondary">
              필터 조건에 맞는 종목이 없습니다
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              필터 조건을 완화하여 다시 시도해보세요
            </Typography>
          </Box>
        )}

        {/* 요약 푸터 */}
        <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Stack direction="row" spacing={3} justifyContent="space-between">
            <Typography variant="body2" color="textSecondary">
              {displayedStocks.length}개 종목 표시 중
              {favorites.size > 0 && ` (즐겨찾기 ${favorites.size}개)`}
            </Typography>
            
            <Stack direction="row" spacing={2}>
              <Chip
                size="small"
                icon={<Circle sx={{ fontSize: 8 }} />}
                label="높은 적합도 (70+)"
                color="success"
                variant="outlined"
              />
              <Chip
                size="small"
                icon={<Circle sx={{ fontSize: 8 }} />}
                label="중간 적합도 (40-70)"
                color="warning"
                variant="outlined"
              />
              <Chip
                size="small"
                icon={<Circle sx={{ fontSize: 8 }} />}
                label="낮은 적합도 (<40)"
                variant="outlined"
              />
            </Stack>
          </Stack>
        </Box>
      </Paper>
    </Box>
  )
}

export default InvestmentWorkspace