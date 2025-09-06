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
  Chip,
  Stack,
  Button,
  Divider,
  LinearProgress,
  Alert,
  TextField,
  InputAdornment,
  IconButton,
  Badge,
  Collapse
} from '@mui/material'
import {
  FilterList,
  Business,
  TrendingUp,
  Search,
  Refresh,
  ExpandLess,
  ExpandMore,
  CheckCircle,
  Warning,
  ArrowForward,
  ArrowDownward,
  Visibility,
  VisibilityOff
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

const TradingSettingsWithUniverse: React.FC = () => {
  const [showUniverse, setShowUniverse] = useState(true)
  const [investmentConfig, setInvestmentConfig] = useState<any>(null)
  const [filteredStocks, setFilteredStocks] = useState<any[]>([])
  const [filterStats, setFilterStats] = useState({
    total: 0,
    afterMarketCap: 0,
    afterFinancial: 0,
    afterSector: 0,
    final: 0
  })
  const [isCalculating, setIsCalculating] = useState(false)
  const [showStockList, setShowStockList] = useState(false)
  const [appliedFilters, setAppliedFilters] = useState({
    valuation: false,
    financial: false,
    sector: false
  })
  const [currentFilterValues, setCurrentFilterValues] = useState<any>({
    valuation: null,
    financial: null,
    sector: null
  })
  const [filterProgress, setFilterProgress] = useState({
    valuation: 0,
    financial: 0,
    sector: 0
  })
  const [dataStatus, setDataStatus] = useState<'loading' | 'ready' | 'error' | 'no-data'>('loading')
  const [allStocks, setAllStocks] = useState<any[]>([])
  const [cumulativeFilteredStocks, setCumulativeFilteredStocks] = useState<any[]>([])
  const [dataFreshness, setDataFreshness] = useState<{
    lastUpdate: string
    daysOld: number
    totalStocks: number
    freshStocks: number
  } | null>(null)

  // 종목 데이터 로드
  useEffect(() => {
    loadStockData()
  }, [])

  const loadStockData = async () => {
    setDataStatus('loading')
    try {
      // 1. 먼저 전체 개수 확인
      const { count: totalCount } = await supabase
        .from('kw_financial_snapshot')
        .select('*', { count: 'exact', head: true })
      
      const finalTotalCount = totalCount || 0
      console.log('전체 종목 수:', finalTotalCount)
      
      // 2. 페이지네이션으로 모든 데이터 로드
      let allData: any[] = []
      let offset = 0
      const pageSize = 1000
      
      while (offset < finalTotalCount) {
        const { data: pageData, error: pageError } = await supabase
          .from('kw_financial_snapshot')
          .select('*')
          .order('snapshot_date', { ascending: false })
          .range(offset, offset + pageSize - 1)
        
        if (pageError) throw pageError
        
        if (!pageData || pageData.length === 0) break
        
        allData = [...allData, ...pageData]
        offset += pageSize
        
        // 최대 10페이지까지만 (10000개)
        if (offset >= 10000) break
      }
      
      console.log(`로드된 데이터: ${allData.length}개`)
      
      if (allData.length === 0) {
        setDataStatus('no-data')
        setFilterStats(prev => ({ ...prev, total: 0 }))
        return
      }
      
      // 3. 가장 최신 스냅샷만 필터링
      const latestByStock: any = {}
      allData.forEach(item => {
        if (!latestByStock[item.stock_code] || 
            item.snapshot_date > latestByStock[item.stock_code].snapshot_date) {
          latestByStock[item.stock_code] = item
        }
      })
      
      const uniqueStocks = Object.values(latestByStock)
      console.log(`유니크한 종목: ${uniqueStocks.length}개`)
      
      setAllStocks(uniqueStocks)
      
      // 4. 데이터 신선도 정보 설정
      setDataFreshness({
        lastUpdate: new Date().toISOString(),
        daysOld: 0,
        totalStocks: finalTotalCount,
        freshStocks: uniqueStocks.length
      })
      
      // 5. filterStats 초기화 - total은 전체 종목 수를 유지
      setFilterStats(prev => ({ 
        ...prev, 
        total: finalTotalCount  // 전체 종목 수로 설정
      }))
      
      // 3. 수집 로그 조회
      const { data: logData } = await supabase
        .from('kw_collection_log')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)
      
      if (logData && logData.length > 0) {
        const lastCollection = logData[0]
        console.log('최근 수집 정보:', lastCollection)
      }
      
      setDataStatus('ready')
      
    } catch (error) {
      console.error('데이터 로드 실패:', error)
      setDataStatus('error')
      // 오류 시 샘플 데이터 사용
      setFilterStats(prev => ({ ...prev, total: 2847 }))
    }
  }

  // localStorage에서 투자 설정 불러오기
  useEffect(() => {
    const loadConfig = () => {
      const saved = localStorage.getItem('investmentConfig')
      if (saved) {
        setInvestmentConfig(JSON.parse(saved))
      }
    }

    loadConfig()
    // localStorage 변경 감지
    window.addEventListener('storage', loadConfig)
    return () => window.removeEventListener('storage', loadConfig)
  }, [])

  // 필터 적용 이벤트 리스너
  useEffect(() => {
    const handleApplyFilter = (event: CustomEvent) => {
      const { filterType, filters } = event.detail
      handleFilterApplication(filterType, filters)
    }
    
    window.addEventListener('applyFilter', handleApplyFilter as EventListener)
    return () => {
      window.removeEventListener('applyFilter', handleApplyFilter as EventListener)
    }
  }, [filterStats])

  // 필터링 통계 계산 (실제 데이터 필터링)
  const calculateFilteringStats = async (universe: any) => {
    setIsCalculating(true)
    
    // 실제 데이터 필터링
    setTimeout(async () => {
      const total = dataFreshness?.totalStocks || filterStats.total || 0  // 실제 전체 종목 수 사용 (변경하지 않음)
      let remaining = total
      
      // 실제로 필터링된 데이터 수 계산
      if (allStocks.length > 0) {
        let filteredStocks = [...allStocks]
        
        // 시가총액 필터
        if (universe.marketCap) {
          const [min, max] = universe.marketCap
          const beforeCount = filteredStocks.length
          filteredStocks = filteredStocks.filter(stock => {
            const marketCapBillion = (stock.market_cap || 0) / 100000000
            return marketCapBillion >= min && marketCapBillion <= max
          })
          console.log(`시가총액 필터: ${beforeCount} → ${filteredStocks.length}`)
        }
        
        const afterMarketCap = filteredStocks.length
        
        // PER 필터
        if (universe.per) {
          const [min, max] = universe.per
          const beforeCount = filteredStocks.length
          filteredStocks = filteredStocks.filter(stock => {
            if (!stock.per || stock.per <= 0) return false
            return stock.per >= min && stock.per <= max
          })
          console.log(`PER 필터: ${beforeCount} → ${filteredStocks.length}`)
        }
        
        // PBR 필터
        if (universe.pbr) {
          const [min, max] = universe.pbr
          const beforeCount = filteredStocks.length
          filteredStocks = filteredStocks.filter(stock => {
            if (!stock.pbr || stock.pbr <= 0) return false
            return stock.pbr >= min && stock.pbr <= max
          })
          console.log(`PBR 필터: ${beforeCount} → ${filteredStocks.length}`)
        }
        
        // ROE 필터
        if (universe.roe) {
          const [min, max] = universe.roe
          const beforeCount = filteredStocks.length
          filteredStocks = filteredStocks.filter(stock => {
            if (stock.roe === null || stock.roe === undefined) return false
            return stock.roe >= min && stock.roe <= max
          })
          console.log(`ROE 필터: ${beforeCount} → ${filteredStocks.length}`)
        }
        
        const afterFinancial = filteredStocks.length
        const afterSector = filteredStocks.length  // 섹터 필터는 나중에 구현
        
        setFilterStats({
          total,
          afterMarketCap,
          afterFinancial,
          afterSector,
          final: filteredStocks.length
        })
        
        setFilteredStocks(filteredStocks)
        updateSampleStocks(universe, filteredStocks.length)
        setIsCalculating(false)
        return
      }
      
      // 시가총액 필터
      if (universe.marketCap) {
        const [min, max] = universe.marketCap
        // 시가총액 범위에 따른 대략적인 필터링
        const ratio = Math.min((max - min) / 10000, 1) * 0.7
        remaining = Math.floor(remaining * ratio)
      }
      const afterMarketCap = remaining
      
      // 재무지표 필터 (PER, PBR, ROE, ROA 등)
      let financialFilterRatio = 1
      if (universe.per) {
        const [min, max] = universe.per
        financialFilterRatio *= Math.min((max - min) / 50, 1)
      }
      if (universe.pbr) {
        const [min, max] = universe.pbr
        financialFilterRatio *= Math.min((max - min) / 5, 1)
      }
      if (universe.roe) {
        const [min, max] = universe.roe
        financialFilterRatio *= Math.min((max - min) / 50, 1)
      }
      if (universe.roa) {
        const [min, max] = universe.roa
        financialFilterRatio *= Math.min((max - min) / 30, 1)
      }
      if (universe.debtRatio) {
        const [min, max] = universe.debtRatio
        financialFilterRatio *= Math.min((max - min) / 200, 1)
      }
      if (universe.currentRatio) {
        const [min, max] = universe.currentRatio
        financialFilterRatio *= Math.min((max - min) / 300, 1)
      }
      
      remaining = Math.floor(afterMarketCap * financialFilterRatio * 0.5)
      const afterFinancial = remaining
      
      // 섹터 필터
      if (universe.sectors && universe.sectors.length > 0) {
        // 전체 24개 섹터 중 선택된 섹터 비율
        const sectorRatio = universe.sectors.length / 24
        remaining = Math.floor(afterFinancial * sectorRatio)
      }
      const afterSector = remaining
      
      setFilterStats({
        total,
        afterMarketCap,
        afterFinancial,
        afterSector,
        final: afterSector
      })
      
      // 샘플 종목 업데이트
      updateSampleStocks(universe, afterSector)
      setIsCalculating(false)
    }, 500) // 0.5초 딜레이로 계산 중 효과
  }

  // 필터 적용 처리
  const handleFilterApplication = (filterType: string, filters: any) => {
    setIsCalculating(true)
    setFilterProgress((prev: any) => ({ ...prev, [filterType]: 0 }))
    
    // 프로그레스 애니메이션
    const progressInterval = setInterval(() => {
      setFilterProgress((prev: any) => {
        const newProgress = { ...prev }
        if (newProgress[filterType] < 100) {
          newProgress[filterType] += 10
        } else {
          clearInterval(progressInterval)
        }
        return newProgress
      })
    }, 50)
    
    setTimeout(() => {
      // 전체 종목 수는 dataFreshness에서 가져온 값을 유지
      const total = dataFreshness?.totalStocks || filterStats.total || 0
      
      // 기존 통계를 유지하면서 새로운 필터만 업데이트
      let newStats = { ...filterStats, total }  // 기존 통계 유지
      
      // 필터링 시작점 결정 - 이미 필터링된 데이터가 있으면 그것을 사용
      let stocksToFilter = cumulativeFilteredStocks.length > 0 && appliedFilters.valuation ? 
                           [...cumulativeFilteredStocks] : [...allStocks]
      let filteredData = [...stocksToFilter]
      let currentCount = stocksToFilter.length
      
      // 1. 가치평가 필터 (새로 적용하는 경우에만)
      if (filterType === 'valuation') {
        const valuationFilters = filters
        
        // 필터 값 저장
        setCurrentFilterValues((prev: any) => ({ ...prev, valuation: valuationFilters }))
        
        // 전체 데이터에서 시작
        filteredData = [...allStocks]
        
        if (allStocks.length > 0 && valuationFilters) {
          // 실제 데이터 필터링
          filteredData = filteredData.filter(stock => {
            // 시가총액 필터 (억원 단위)
            if (valuationFilters?.marketCap) {
              const [min, max] = valuationFilters.marketCap
              const marketCapBillion = (stock.market_cap || 0) / 100000000
              if (marketCapBillion < min || marketCapBillion > max) return false
            }
            // PER 필터
            if (valuationFilters?.per) {
              const [min, max] = valuationFilters.per
              if (!stock.per || stock.per < min || stock.per > max) return false
            }
            // PBR 필터
            if (valuationFilters?.pbr) {
              const [min, max] = valuationFilters.pbr
              if (!stock.pbr || stock.pbr < min || stock.pbr > max) return false
            }
            return true
          })
          newStats.afterMarketCap = filteredData.length
          currentCount = filteredData.length
        } else {
          // 시뮬레이션
          if (valuationFilters?.marketCap) {
            const [min, max] = valuationFilters.marketCap
            const ratio = Math.min((max - min) / 10000, 1) * 0.8
            currentCount = Math.floor(total * ratio)
          }
          newStats.afterMarketCap = currentCount
        }
        
        setAppliedFilters(prev => ({ ...prev, valuation: true }))
      } else if (appliedFilters.valuation && filterType !== 'valuation') {
        // 가치평가 필터가 이미 적용된 상태면 그 결과를 유지
        // newStats.afterMarketCap는 이미 유지되고 있음
      }
      
      // 2. 재무지표 필터 (가치평가 필터 결과에 적용)
      if (filterType === 'financial') {
        const financialFilters = filters
        
        // 필터 값 저장
        setCurrentFilterValues((prev: any) => ({ ...prev, financial: financialFilters }))
        
        // 가치평가 필터가 적용되어 있으면 먼저 가치평가 필터를 다시 적용
        if (appliedFilters.valuation && currentFilterValues.valuation) {
          // 저장된 가치평가 필터 값으로 재적용
          const valuationFilters = currentFilterValues.valuation
          filteredData = [...allStocks]
          
          if (allStocks.length > 0 && valuationFilters) {
            filteredData = filteredData.filter(stock => {
              if (valuationFilters?.marketCap) {
                const [min, max] = valuationFilters.marketCap
                const marketCapBillion = (stock.market_cap || 0) / 100000000
                if (marketCapBillion < min || marketCapBillion > max) return false
              }
              if (valuationFilters?.per) {
                const [min, max] = valuationFilters.per
                if (!stock.per || stock.per < min || stock.per > max) return false
              }
              if (valuationFilters?.pbr) {
                const [min, max] = valuationFilters.pbr
                if (!stock.pbr || stock.pbr < min || stock.pbr > max) return false
              }
              return true
            })
            // 가치평가 필터 결과 유지
            newStats.afterMarketCap = filteredData.length
          }
        } else {
          // 가치평가 필터가 없으면 전체에서 시작
          filteredData = [...allStocks]
        }
        
        // 재무지표 필터 적용
        if (filteredData.length > 0 && financialFilters) {
          filteredData = filteredData.filter(stock => {
            if (financialFilters?.roe) {
              const [min, max] = financialFilters.roe
              if (stock.roe === undefined || stock.roe === null) return false
              if (stock.roe < min || stock.roe > max) return false
            }
            if (financialFilters?.debtRatio) {
              const [min, max] = financialFilters.debtRatio
              if (stock.debt_ratio !== undefined && (stock.debt_ratio < min || stock.debt_ratio > max)) return false
            }
            return true
          })
          newStats.afterFinancial = filteredData.length
          currentCount = filteredData.length
        } else {
          // 시뮬레이션
          let financialRatio = 1
          if (financialFilters?.roe) {
            const [min, max] = financialFilters.roe
            financialRatio *= Math.min((max - min) / 40, 1)
          }
          if (financialFilters?.debtRatio) {
            const [min, max] = financialFilters.debtRatio
            financialRatio *= Math.min((max - min) / 100, 1)
          }
          const baseCount = appliedFilters.valuation ? newStats.afterMarketCap : total
          currentCount = Math.floor(baseCount * financialRatio * 0.6)
          newStats.afterFinancial = currentCount
        }
        
        setAppliedFilters(prev => ({ ...prev, financial: true }))
      } else if (appliedFilters.financial && filterType !== 'financial') {
        // 재무지표 필터가 이미 적용된 상태면 그 결과를 유지
        // newStats.afterFinancial는 이미 유지되고 있음
      }
      
      // 3. 섹터 필터 (재무지표 필터 결과에 적용)
      if (filterType === 'sector') {
        const sectorFilters = filters
        
        // 이전 필터가 적용되어 있으면 그 결과에서 시작
        if ((appliedFilters.financial || appliedFilters.valuation) && cumulativeFilteredStocks.length > 0) {
          filteredData = [...cumulativeFilteredStocks]
        } else {
          filteredData = [...allStocks]
        }
        
        if (filteredData.length > 0 && sectorFilters?.sectors) {
          // 실제 데이터 필터링
          filteredData = filteredData.filter(stock => {
            if (sectorFilters.sectors && sectorFilters.sectors.length > 0) {
              return sectorFilters.sectors.includes(stock.sector)
            }
            return true
          })
          newStats.afterSector = filteredData.length
          currentCount = filteredData.length
        } else if (sectorFilters?.sectors && sectorFilters.sectors.length > 0) {
          // 시뮬레이션
          const sectorRatio = sectorFilters.sectors.length / 24
          // 이전 필터 결과에서 계속
          const prevCount = appliedFilters.financial ? newStats.afterFinancial : 
                           appliedFilters.valuation ? newStats.afterMarketCap : total
          currentCount = Math.floor(prevCount * sectorRatio)
          newStats.afterSector = currentCount
        }
        
        setAppliedFilters(prev => ({ ...prev, sector: true }))
      } else if (appliedFilters.sector && filterType !== 'sector') {
        // 섹터 필터가 이미 적용된 상태면 그 결과를 유지
        // newStats.afterSector는 이미 유지되고 있음
      }
      
      // 최종 결과 설정
      // 현재 적용된 모든 필터를 고려한 최종 카운트
      if (appliedFilters.sector || filterType === 'sector') {
        newStats.final = newStats.afterSector || currentCount
      } else if (appliedFilters.financial || filterType === 'financial') {
        newStats.final = newStats.afterFinancial || currentCount
      } else if (appliedFilters.valuation || filterType === 'valuation') {
        newStats.final = newStats.afterMarketCap || currentCount
      } else {
        newStats.final = currentCount
      }
      
      setFilterStats(newStats)
      setFilteredStocks(filteredData.slice(0, 10))  // UI에 표시할 샘플 종목
      setCumulativeFilteredStocks(filteredData)  // 전체 필터링된 종목 저장
      
      // 샘플 종목 업데이트
      updateSampleStocks(investmentConfig?.universe || {}, currentCount)
      setIsCalculating(false)
      clearInterval(progressInterval)
      setFilterProgress(prev => ({ ...prev, [filterType]: 100 }))
    }, 1000)
  }
  
  // 샘플 종목 업데이트
  const updateSampleStocks = (universe: any, count: number) => {
    // 필터 조건에 맞는 샘플 종목 생성
    const samples = sampleStocks.filter(stock => {
      // 시가총액 체크
      if (universe.marketCap) {
        const [min, max] = universe.marketCap
        if (stock.marketCap < min || stock.marketCap > max) return false
      }
      // PER 체크
      if (universe.per) {
        const [min, max] = universe.per
        if (stock.per < min || stock.per > max) return false
      }
      // 섹터 체크
      if (universe.sectors && universe.sectors.length > 0) {
        if (!universe.sectors.includes(stock.sector)) return false
      }
      return true
    })
    
    setFilteredStocks(samples)
  }

  // 샘플 종목 데이터 (실제로는 InvestmentWorkspace에서 관리)
  const sampleStocks = [
    { code: '005930', name: '삼성전자', marketCap: 4500000, per: 12.5, pbr: 1.2, roe: 8.5, sector: 'IT', change: -1.2 },
    { code: '000660', name: 'SK하이닉스', marketCap: 900000, per: 15.2, pbr: 1.8, roe: 12.3, sector: '반도체', change: 2.3 },
    { code: '035720', name: '카카오', marketCap: 250000, per: 45.6, pbr: 2.5, roe: 5.2, sector: 'IT', change: 0.5 },
    { code: '051910', name: 'LG화학', marketCap: 400000, per: 18.9, pbr: 1.1, roe: 9.8, sector: '화학', change: -0.8 },
    { code: '006400', name: '삼성SDI', marketCap: 350000, per: 22.3, pbr: 2.1, roe: 11.5, sector: '2차전지', change: 1.5 }
  ]

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      {/* 왼쪽: 기존 투자 설정 */}
      <Box sx={{ flex: showUniverse ? '0 0 65%' : '1', transition: 'all 0.3s' }}>
        <Paper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList />
              투자 설정
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={showUniverse ? <VisibilityOff /> : <Visibility />}
              onClick={() => setShowUniverse(!showUniverse)}
            >
              {showUniverse ? '유니버스 숨기기' : '유니버스 보기'}
            </Button>
          </Box>
          <Box sx={{ p: 2 }}>
            <TradingSettingsSimplified />
          </Box>
        </Paper>
      </Box>

      {/* 오른쪽: 필터링된 투자 유니버스 */}
      {showUniverse && (
        <Box sx={{ flex: '0 0 35%', display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* 필터 통계 카드 */}
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Business />
                투자 유니버스
                <Badge badgeContent={filterStats.final} color="primary" max={9999}>
                  <Box />
                </Badge>
              </Typography>
              <Stack direction="row" spacing={1}>
                {dataStatus === 'no-data' && (
                  <Button
                    size="small"
                    variant="outlined"
                    color="warning"
                    onClick={() => {
                      // 데이터 다운로드 페이지나 가이드로 이동
                      alert('키움 API를 통해 데이터를 다운로드해야 합니다.\n백엔드 서버에서 download_all_fundamentals.py를 실행하세요.')
                    }}
                  >
                    데이터 다운로드
                  </Button>
                )}
                {(appliedFilters.valuation || appliedFilters.financial || appliedFilters.sector) && (
                  <Button
                    size="small"
                    variant="outlined"
                    color="secondary"
                    onClick={() => {
                      // 모든 필터 초기화
                      setAppliedFilters({ valuation: false, financial: false, sector: false })
                      setCurrentFilterValues({ valuation: null, financial: null, sector: null })
                      setFilterStats({
                        total: dataFreshness?.totalStocks || 0,
                        afterMarketCap: 0,
                        afterFinancial: 0,
                        afterSector: 0,
                        final: 0
                      })
                      setCumulativeFilteredStocks([])
                      setFilteredStocks([])
                      setFilterProgress({ valuation: 0, financial: 0, sector: 0 })
                    }}
                  >
                    필터 초기화
                  </Button>
                )}
                <IconButton 
                  size="small"
                  onClick={() => {
                    loadStockData()
                  }}
                  disabled={isCalculating || dataStatus === 'loading'}
                >
                  <Refresh fontSize="small" />
                </IconButton>
              </Stack>
            </Box>
            
            {/* 데이터 상태 표시 */}
            {dataStatus === 'loading' && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress />
                <Typography variant="caption">데이터 로딩 중...</Typography>
              </Box>
            )}
            {dataStatus === 'no-data' && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  종목 데이터가 없습니다. 키움 API를 통해 데이터를 먼저 다운로드하세요.
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  백엔드 실행: python backend/api/kiwoom_fundamental.py --all
                </Typography>
              </Alert>
            )}
            {dataStatus === 'error' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                데이터베이스 연결 실패. 샘플 데이터를 사용합니다.
              </Alert>
            )}
            {dataStatus === 'ready' && (
              <Box>
                <Alert severity="success" sx={{ mt: 2 }}>
                  {dataFreshness.totalStocks}개 종목 데이터 준비 완료
                </Alert>
                {dataFreshness && (
                  <Paper sx={{ mt: 2, p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      📊 데이터 정보
                    </Typography>
                    <Stack spacing={1}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption">최종 업데이트:</Typography>
                        <Typography variant="caption" fontWeight="bold">
                          {dataFreshness.lastUpdate} ({dataFreshness.daysOld}일 전)
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption">전체 종목:</Typography>
                        <Typography variant="caption">{dataFreshness.totalStocks}개</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption">최신 데이터:</Typography>
                        <Typography variant="caption" color={
                          dataFreshness.freshStocks > dataFreshness.totalStocks * 0.8 
                            ? 'success.main' 
                            : dataFreshness.freshStocks > dataFreshness.totalStocks * 0.5
                            ? 'warning.main'
                            : 'error.main'
                        }>
                          {dataFreshness.freshStocks}개 ({Math.round((dataFreshness.freshStocks / dataFreshness.totalStocks) * 100)}%)
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(dataFreshness.freshStocks / dataFreshness.totalStocks) * 100}
                        color={
                          dataFreshness.freshStocks > dataFreshness.totalStocks * 0.8 
                            ? 'success' 
                            : dataFreshness.freshStocks > dataFreshness.totalStocks * 0.5
                            ? 'warning'
                            : 'error'
                        }
                        sx={{ mt: 1, height: 6, borderRadius: 1 }}
                      />
                      {dataFreshness.daysOld > 7 && (
                        <Alert severity="warning" sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            데이터가 오래되었습니다. 새로 수집하는 것을 권장합니다.
                          </Typography>
                        </Alert>
                      )}
                    </Stack>
                  </Paper>
                )}
              </Box>
            )}
            
            {/* 시각적 필터링 흐름 */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FilterList fontSize="small" />
                필터링 흐름
              </Typography>
              
              {/* 전체 종목 */}
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 2, 
                  mb: 2, 
                  bgcolor: 'primary.dark',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <Typography variant="h4" color="primary.contrastText">
                  {filterStats.total.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="primary.contrastText">
                  전체 종목
                </Typography>
              </Paper>
              
              {/* 가치평가 필터 */}
              <Box sx={{ position: 'relative', mb: 2 }}>
                <ArrowDownward sx={{ position: 'absolute', left: '50%', top: -20, transform: 'translateX(-50%)', color: 'text.secondary' }} />
                <Paper 
                  elevation={appliedFilters.valuation ? 2 : 0}
                  sx={{ 
                    p: 2,
                    bgcolor: appliedFilters.valuation ? 'primary.main' : 'grey.800',
                    transition: 'all 0.3s',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  {filterProgress.valuation > 0 && filterProgress.valuation < 100 && (
                    <LinearProgress 
                      variant="determinate" 
                      value={filterProgress.valuation}
                      sx={{ position: 'absolute', top: 0, left: 0, right: 0 }}
                    />
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2" color={appliedFilters.valuation ? "primary.contrastText" : "text.secondary"}>
                        가치평가 필터
                      </Typography>
                      <Typography variant="h5" color={appliedFilters.valuation ? "primary.contrastText" : "text.primary"}>
                        {filterStats.afterMarketCap > 0 ? filterStats.afterMarketCap.toLocaleString() : '-'}
                      </Typography>
                    </Box>
                    {appliedFilters.valuation && (
                      <CheckCircle color="success" />
                    )}
                  </Box>
                  {filterStats.afterMarketCap > 0 && (
                    <Typography variant="caption" color={appliedFilters.valuation ? "primary.contrastText" : "text.secondary"}>
                      {Math.round((filterStats.afterMarketCap / filterStats.total) * 100)}% 통과
                    </Typography>
                  )}
                </Paper>
              </Box>
              
              {/* 재무 필터 */}
              <Box sx={{ position: 'relative', mb: 2 }}>
                <ArrowDownward sx={{ position: 'absolute', left: '50%', top: -20, transform: 'translateX(-50%)', color: 'text.secondary' }} />
                <Paper 
                  elevation={appliedFilters.financial ? 2 : 0}
                  sx={{ 
                    p: 2,
                    bgcolor: appliedFilters.financial ? 'secondary.main' : 'grey.800',
                    transition: 'all 0.3s',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  {filterProgress.financial > 0 && filterProgress.financial < 100 && (
                    <LinearProgress 
                      variant="determinate" 
                      value={filterProgress.financial}
                      sx={{ position: 'absolute', top: 0, left: 0, right: 0 }}
                    />
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2" color={appliedFilters.financial ? "secondary.contrastText" : "text.secondary"}>
                        재무지표 필터
                      </Typography>
                      <Typography variant="h5" color={appliedFilters.financial ? "secondary.contrastText" : "text.primary"}>
                        {filterStats.afterFinancial > 0 ? filterStats.afterFinancial.toLocaleString() : '-'}
                      </Typography>
                    </Box>
                    {appliedFilters.financial && (
                      <CheckCircle color="success" />
                    )}
                  </Box>
                  {filterStats.afterFinancial > 0 && filterStats.afterMarketCap > 0 && (
                    <Typography variant="caption" color={appliedFilters.financial ? "secondary.contrastText" : "text.secondary"}>
                      {Math.round((filterStats.afterFinancial / filterStats.afterMarketCap) * 100)}% 통과
                    </Typography>
                  )}
                </Paper>
              </Box>
              
              {/* 섹터 필터 */}
              <Box sx={{ position: 'relative', mb: 2 }}>
                <ArrowDownward sx={{ position: 'absolute', left: '50%', top: -20, transform: 'translateX(-50%)', color: 'text.secondary' }} />
                <Paper 
                  elevation={appliedFilters.sector ? 2 : 0}
                  sx={{ 
                    p: 2,
                    bgcolor: appliedFilters.sector ? 'info.main' : 'grey.800',
                    transition: 'all 0.3s',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  {filterProgress.sector > 0 && filterProgress.sector < 100 && (
                    <LinearProgress 
                      variant="determinate" 
                      value={filterProgress.sector}
                      sx={{ position: 'absolute', top: 0, left: 0, right: 0 }}
                    />
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2" color={appliedFilters.sector ? "info.contrastText" : "text.secondary"}>
                        섹터 필터
                      </Typography>
                      <Typography variant="h5" color={appliedFilters.sector ? "info.contrastText" : "text.primary"}>
                        {filterStats.afterSector > 0 ? filterStats.afterSector.toLocaleString() : '-'}
                      </Typography>
                    </Box>
                    {appliedFilters.sector && (
                      <CheckCircle color="success" />
                    )}
                  </Box>
                  {filterStats.afterSector > 0 && filterStats.afterFinancial > 0 && (
                    <Typography variant="caption" color={appliedFilters.sector ? "info.contrastText" : "text.secondary"}>
                      {Math.round((filterStats.afterSector / filterStats.afterFinancial) * 100)}% 통과
                    </Typography>
                  )}
                </Paper>
              </Box>
              
              {/* 최종 결과 */}
              <Paper 
                elevation={3}
                sx={{ 
                  p: 2,
                  bgcolor: filterStats.final > 0 ? 'success.main' : 'grey.900',
                  border: '2px solid',
                  borderColor: filterStats.final > 0 ? 'success.light' : 'grey.700'
                }}
              >
                <Typography variant="h3" color={filterStats.final > 0 ? "success.contrastText" : "text.primary"}>
                  {filterStats.final.toLocaleString()}
                </Typography>
                <Typography variant="body2" color={filterStats.final > 0 ? "success.contrastText" : "text.secondary"}>
                  최종 투자 유니버스
                </Typography>
                {filterStats.final > 0 && (
                  <Button
                    variant="contained"
                    size="small"
                    sx={{ mt: 2, bgcolor: 'white', color: 'success.main' }}
                    onClick={() => setShowStockList(!showStockList)}
                    startIcon={showStockList ? <VisibilityOff /> : <Visibility />}
                  >
                    {showStockList ? '리스트 숨기기' : '리스트 보기'}
                  </Button>
                )}
              </Paper>
            </Box>

            {/* 필터 요약 */}
            {investmentConfig && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="textSecondary">적용된 필터:</Typography>
                <Stack spacing={1} sx={{ mt: 1 }}>
                  <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                    {investmentConfig.universe?.marketCap && (
                      <Chip 
                        label={`시총: ${investmentConfig.universe.marketCap[0]}~${investmentConfig.universe.marketCap[1]}억`} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                    {investmentConfig.universe?.per && (
                      <Chip 
                        label={`PER: ${investmentConfig.universe.per[0]}~${investmentConfig.universe.per[1]}`} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                    {investmentConfig.universe?.pbr && (
                      <Chip 
                        label={`PBR: ${investmentConfig.universe.pbr[0]}~${investmentConfig.universe.pbr[1]}`} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                    {investmentConfig.universe?.roe && (
                      <Chip 
                        label={`ROE: ${investmentConfig.universe.roe[0]}~${investmentConfig.universe.roe[1]}%`} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                  </Stack>
                  <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                    {investmentConfig.universe?.debtRatio && (
                      <Chip 
                        label={`부채비율: ${investmentConfig.universe.debtRatio[0]}~${investmentConfig.universe.debtRatio[1]}%`} 
                        size="small" 
                        variant="outlined"
                        color="secondary"
                      />
                    )}
                    {investmentConfig.universe?.currentRatio && (
                      <Chip 
                        label={`유동비율: ${investmentConfig.universe.currentRatio[0]}~${investmentConfig.universe.currentRatio[1]}%`} 
                        size="small" 
                        variant="outlined"
                        color="secondary"
                      />
                    )}
                    {investmentConfig.universe?.sectors?.length > 0 && (
                      <Chip 
                        label={`섹터: ${investmentConfig.universe.sectors.length}개`} 
                        size="small" 
                        variant="outlined" 
                        color="primary"
                      />
                    )}
                  </Stack>
                </Stack>
              </Box>
            )}
          </Paper>

          {/* 종목 리스트 */}
          <Collapse in={showStockList}>
            <Paper sx={{ mt: 2 }}>
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <TextField
                  size="small"
                  fullWidth
                  placeholder="종목 검색..."
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton size="small">
                          <Refresh />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />
              </Box>

              <Box sx={{ p: 1 }}>
                {filteredStocks.length === 0 && !isCalculating ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Warning color="action" sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="body1" color="text.secondary">
                    현재 필터 조건에 맞는 종목이 없습니다
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    필터 조건을 완화해보세요
                  </Typography>
                </Box>
              ) : (
                <>
                  <List dense>
                    {(filteredStocks.length > 0 ? filteredStocks : sampleStocks).map((stock) => (
                  <ListItem key={stock.code} divider>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="subtitle2">{stock.name}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {stock.code}
                            </Typography>
                          </Stack>
                          <Chip 
                            label={stock.sector} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Grid container spacing={1} sx={{ mt: 0.5 }}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="textSecondary">
                              시총: {(stock.marketCap / 10000).toFixed(0)}조
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography 
                              variant="caption" 
                              color={stock.change > 0 ? 'error.main' : stock.change < 0 ? 'primary.main' : 'textSecondary'}
                            >
                              {stock.change > 0 ? '+' : ''}{stock.change}%
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="textSecondary">
                              PER: {stock.per}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="textSecondary">
                              PBR: {stock.pbr}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="textSecondary">
                              ROE: {stock.roe}%
                            </Typography>
                          </Grid>
                        </Grid>
                      }
                    />
                  </ListItem>
                ))}
              </List>

                  {/* 더 많은 종목 표시 */}
                  {filterStats.final > filteredStocks.length && (
                    <Box sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        + {filterStats.final - filteredStocks.length}개 종목 더 보기
                      </Typography>
                    </Box>
                  )}
                </>
              )}
              </Box>

              {/* 액션 버튼 */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="caption">
                  필터링된 {filterStats.final}개 종목이 전략 빌더에서 사용됩니다.
                  전략 빌더에서 매수/매도 조건을 설정하세요.
                </Typography>
              </Alert>
              <Stack direction="row" spacing={1}>
                <Button variant="outlined" size="small" fullWidth>
                  Excel 다운로드
                </Button>
                <Button 
                  variant="contained" 
                  size="small" 
                  fullWidth 
                  startIcon={<TrendingUp />}
                  onClick={() => {
                    // Navigate to Strategy Builder tab
                    const event = new CustomEvent('navigateToStrategyBuilder', { 
                      detail: { universe: filteredStocks } 
                    })
                    window.dispatchEvent(event)
                  }}
                >
                  전략 빌더로 이동
                </Button>
              </Stack>
            </Box>
          </Paper>
          </Collapse>
        </Box>
      )}
    </Box>
  )
}

export default TradingSettingsWithUniverse