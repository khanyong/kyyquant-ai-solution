import React, { useState, useEffect } from 'react'
import { investorDataService } from '../services/investorDataService'
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
  Collapse,
  Slider,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  ToggleButton,
  ToggleButtonGroup,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Tooltip,
  Fab,
  CircularProgress
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
  VisibilityOff,
  Assessment,
  AccountBalance,
  Category,
  Speed,
  Tune,
  BookmarkBorder,
  Bookmark,
  AutoAwesome,
  Timeline,
  LocalFireDepartment,
  Diamond,
  Savings,
  ViewModule,
  BubbleChart,
  ShowChart,
  LocalAtm,
  Security,
  Save as SaveIcon,
  Folder,
  Groups
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import SaveFilterDialog from './SaveFilterDialog'
import LoadFilterDialog from './LoadFilterDialog'
import InvestorTrendFilter from './InvestorTrendFilter'

const TradingSettingsWithUniverse: React.FC = () => {
  const [showUniverse, setShowUniverse] = useState(true)
  const [investmentConfig, setInvestmentConfig] = useState<any>(null)
  const [filteredStocks, setFilteredStocks] = useState<any[]>([])
  const [filterStats, setFilterStats] = useState({
    total: 0,
    afterMarketCap: 0,
    afterFinancial: 0,
    afterSector: 0,
    afterInvestor: 0,
    final: 0
  })
  const [isCalculating, setIsCalculating] = useState(false)
  const [showStockList, setShowStockList] = useState(false)
  const [appliedFilters, setAppliedFilters] = useState({
    valuation: false,
    financial: false,
    sector: false,
    investor: false
  })
  const [currentFilterValues, setCurrentFilterValues] = useState<any>({
    valuation: null,
    financial: null,
    sector: null,
    investor: null
  })
  const [filterProgress, setFilterProgress] = useState({
    valuation: 0,
    financial: 0,
    sector: 0,
    investor: 0
  })
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [loadDialogOpen, setLoadDialogOpen] = useState(false)
  const [dataStatus, setDataStatus] = useState<'loading' | 'ready' | 'error' | 'no-data'>('loading')
  const [allStocks, setAllStocks] = useState<any[]>([])
  const [cumulativeFilteredStocks, setCumulativeFilteredStocks] = useState<any[]>([])
  const [dataFreshness, setDataFreshness] = useState<{
    lastUpdate: string
    daysOld: number
    totalStocks: number
    freshStocks: number
  } | null>(null)
  
  // 필터 설정 상태
  const [valuationFilters, setValuationFilters] = useState({
    marketCap: [100, 50000],  // 억원
    per: [0, 50],
    pbr: [0, 10],
    pcr: [0, 30],  // Price to Cash Flow Ratio
    psr: [0, 5],   // Price to Sales Ratio  
    peg: [0, 3],   // PEG Ratio
    eps: [-1000, 10000],  // 주당순이익 (원)
    bps: [0, 100000],     // 주당순자산 (원)
    currentPrice: [1000, 100000],  // 현재가 (원)
    priceToHigh52w: [50, 100],     // 52주 최고가 대비 (%)
    volume: [100, 10000],           // 거래량 (천주)
    foreignRatio: [0, 50]          // 외국인 보유비율 (%)
  })
  
  const [financialFilters, setFinancialFilters] = useState({
    roe: [-20, 50],  // %
    roa: [0, 20],  // %
    debtRatio: [0, 200],  // %
    currentRatio: [100, 300],  // 유동비율 %
    quickRatio: [50, 200],  // 당좌비율 %
    operatingMargin: [-20, 50],  // 영업이익률 %
    netMargin: [0, 30],  // 순이익률 %
    revenueGrowth: [-10, 50],  // 매출성장률 %
    profitGrowth: [-10, 50],  // 이익성장률 %
    equityGrowth: [0, 30],  // 자본성장률 %
    dividendYield: [0, 10],  // 배당수익률 %
    dividendPayout: [0, 50]  // 배당성향 %
  })
  
  const [sectorFilters, setSectorFilters] = useState({
    sectors: [] as string[]
  })
  
  const [investorFilters, setInvestorFilters] = useState({
    foreignHoldingRatio: [0, 100],
    institutionHoldingRatio: [0, 100],
    foreignNetBuyDays: 5,
    institutionNetBuyDays: 5,
    foreignNetBuyAmount: [-10000, 10000],
    institutionNetBuyAmount: [-10000, 10000],
    trendDirection: 'buying' as 'buying' | 'selling' | 'both',
    investorType: ['foreign', 'institution'] as ('foreign' | 'institution' | 'pension')[],
    minConsecutiveBuyDays: 3
  })
  
  const allSectors = [
    'IT', '바이오', '2차전지', '반도체', '화학', '철강',
    '건설', '조선', '자동차', '금융', '유통', '음식료',
    '엔터테인먼트', '게임', '의료', '제약', '전기전자',
    '기계', '섬유', '종이목재', '운수', '통신', '유틸리티', '기타'
  ]
  
  // 프리셋 템플릿
  const filterPresets = [
    {
      name: '가치주',
      icon: <Diamond />,
      color: 'primary',
      filters: {
        valuation: { per: [5, 15], pbr: [0.5, 1.5], marketCap: [1000, 50000] },
        financial: { roe: [10, 30], debtRatio: [0, 50] }
      }
    },
    {
      name: '성장주',
      icon: <LocalFireDepartment />,
      color: 'error',
      filters: {
        valuation: { per: [15, 40], marketCap: [500, 20000] },
        financial: { revenueGrowth: [20, 100], profitGrowth: [20, 200] }
      }
    },
    {
      name: '배당주',
      icon: <Savings />,
      color: 'success',
      filters: {
        valuation: { per: [5, 20] },
        financial: { dividendYield: [2, 8], dividendPayout: [20, 60] }
      }
    },
    {
      name: '우량주',
      icon: <AutoAwesome />,
      color: 'info',
      filters: {
        valuation: { marketCap: [10000, 100000], foreignRatio: [10, 50] },
        financial: { roe: [15, 40], debtRatio: [0, 30] }
      }
    }
  ]
  
  const [activeTab, setActiveTab] = useState(0)
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [selectedMatrix, setSelectedMatrix] = useState<string | null>(null)
  const [marketCapRange, setMarketCapRange] = useState<number[]>([1000, 50000])

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
  const handleFilterApplication = async (filterType: string, filters: any) => {
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
    
    setTimeout(async () => {
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
      
      // 4. 투자자 필터 (새로 추가)
      if (filterType === 'investor') {
        const investorFilters = filters
        
        // 필터 값 저장
        setCurrentFilterValues((prev: any) => ({ ...prev, investor: investorFilters }))
        
        // 이전 필터가 적용된 데이터에서 시작
        if (appliedFilters.sector && currentFilterValues.sector) {
          // 섹터 필터까지 적용된 데이터 사용
        } else if (appliedFilters.financial && currentFilterValues.financial) {
          // 재무 필터까지 적용된 데이터 사용
        } else if (appliedFilters.valuation && currentFilterValues.valuation) {
          // 가치 필터까지 적용된 데이터 사용
        }
        
        // 실제 투자자 데이터로 필터링
        const stockCodes = filteredData.map(stock => stock.stock_code)
        
        try {
          const filteredCodes = await investorDataService.filterStocksByInvestor(
            stockCodes,
            investorFilters
          )
          
          // 필터링된 종목 코드로 데이터 필터링
          filteredData = filteredData.filter(stock => 
            filteredCodes.includes(stock.stock_code)
          )
          
          currentCount = filteredData.length
          newStats.afterInvestor = currentCount
          
          console.log(`투자자 필터 적용: ${stockCodes.length} → ${currentCount}`)
        } catch (error) {
          console.error('투자자 필터링 중 오류:', error)
          // 오류 시 기존 시뮬레이션 방식으로 폴백
          const prevCount = newStats.afterSector || newStats.afterFinancial || newStats.afterMarketCap || total
          currentCount = Math.floor(prevCount * 0.7)
          newStats.afterInvestor = currentCount
        }
        
        setAppliedFilters(prev => ({ ...prev, investor: true }))
      }
      
      // 최종 결과 설정
      // 현재 적용된 모든 필터를 고려한 최종 카운트
      if (appliedFilters.investor || filterType === 'investor') {
        newStats.final = newStats.afterInvestor || currentCount
      } else if (appliedFilters.sector || filterType === 'sector') {
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
      
      // localStorage에 필터 설정과 필터링 결과 저장
      const filterConfig = {
        filters: {
          valuation: currentFilterValues.valuation,
          financial: currentFilterValues.financial,
          sector: currentFilterValues.sector,
          investor: currentFilterValues.investor
        },
        appliedFilters,
        filteredStocks: filteredData.map(stock => ({
          code: stock.stock_code || stock.code,
          name: stock.stock_name || stock.name,
          market_cap: stock.market_cap,
          per: stock.per,
          pbr: stock.pbr,
          roe: stock.roe,
          sector: stock.sector
        })),
        filterStats: newStats,
        timestamp: new Date().toISOString()
      }
      
      // 기존 investmentConfig 업데이트
      const existingConfig = localStorage.getItem('investmentConfig')
      let updatedConfig = existingConfig ? JSON.parse(existingConfig) : {}
      updatedConfig = {
        ...updatedConfig,
        universe: {
          ...updatedConfig.universe,
          ...filterConfig
        }
      }
      localStorage.setItem('investmentConfig', JSON.stringify(updatedConfig))
      console.log('필터 설정 저장 완료:', filterConfig)
      
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
      {/* 왼쪽: 투자 설정 및 필터 */}
      <Box sx={{ flex: showUniverse ? '0 0 70%' : '1', transition: 'all 0.3s' }}>
        <Paper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList />
              투자 설정
            </Typography>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                size="small"
                startIcon={<SaveIcon />}
                onClick={() => setSaveDialogOpen(true)}
                disabled={!appliedFilters.valuation && !appliedFilters.financial && !appliedFilters.sector}
              >
                필터 저장
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Folder />}
                onClick={() => setLoadDialogOpen(true)}
              >
                필터 불러오기
              </Button>
              <Divider orientation="vertical" flexItem />
              <Button
                variant="outlined"
                size="small"
                startIcon={showUniverse ? <VisibilityOff /> : <Visibility />}
                onClick={() => setShowUniverse(!showUniverse)}
              >
                {showUniverse ? '유니버스 숨기기' : '유니버스 보기'}
              </Button>
            </Stack>
          </Box>
          <Box sx={{ p: 2 }}>
            {/* 창의적인 필터 UI */}
            
            {/* 1. 프리셋 템플릿 (Quick Filters) */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ mb: 2, fontWeight: 'bold' }}>
                🎯 빠른 필터 템플릿
              </Typography>
              <Grid container spacing={1}>
                {filterPresets.map((preset) => (
                  <Grid item xs={6} key={preset.name}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        border: selectedPreset === preset.name ? 2 : 0,
                        borderColor: `${preset.color}.main`,
                        transition: 'all 0.3s',
                        '&:hover': { 
                          transform: 'translateY(-2px)',
                          boxShadow: 3
                        }
                      }}
                      onClick={() => {
                        setSelectedPreset(preset.name)
                        // 프리셋 필터 적용
                        if (preset.filters.valuation) {
                          setValuationFilters({...valuationFilters, ...preset.filters.valuation})
                        }
                        if (preset.filters.financial) {
                          setFinancialFilters({...financialFilters, ...preset.filters.financial})
                        }
                      }}
                    >
                      <CardContent sx={{ py: 1.5, px: 2 }}>
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Box sx={{ color: `${preset.color}.main` }}>
                            {preset.icon}
                          </Box>
                          <Typography variant="body2" fontWeight="medium">
                            {preset.name}
                          </Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            {/* 2. 탭 기반 필터 카테고리 */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={activeTab} 
                onChange={(e, v) => setActiveTab(v)}
                variant="fullWidth"
                sx={{
                  '& .MuiTab-root': {
                    minHeight: 48,
                    textTransform: 'none',
                    fontSize: '0.875rem'
                  }
                }}
              >
                <Tab icon={<Assessment />} label="가치" />
                <Tab icon={<AccountBalance />} label="재무" />
                <Tab icon={<Category />} label="섹터" />
                <Tab icon={<Groups />} label="투자자" />
                <Tab icon={<ViewModule />} label="매트릭스" />
                <Tab icon={<Timeline />} label="대시보드" />
              </Tabs>
            </Box>
            
            {/* 탭 내용 */}
            <Box sx={{ mt: 2 }}>
              {/* 가치 탭 */}
              {activeTab === 0 && (
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">시가총액 (억원)</Typography>
                    <Slider
                      value={valuationFilters.marketCap}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, marketCap: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100000}
                      step={100}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 50000, label: '5조' }
                      ]}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  {/* 가치 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mt: 1, fontWeight: 'bold' }}>
                      📊 가치 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">PER (주가수익비율)</Typography>
                    <Slider
                      value={valuationFilters.per}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, per: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">PBR (주가순자산비율)</Typography>
                    <Slider
                      value={valuationFilters.pbr}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, pbr: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.1}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">PCR (주가현금흐름비율)</Typography>
                    <Slider
                      value={valuationFilters.pcr || [0, 50]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, pcr: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={50}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">PSR (주가매출비율)</Typography>
                    <Slider
                      value={valuationFilters.psr || [0, 10]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, psr: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.1}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">PEG (이익성장비율)</Typography>
                    <Slider
                      value={valuationFilters.peg || [0, 3]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, peg: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={5}
                      step={0.1}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">EPS (주당순이익)</Typography>
                    <Slider
                      value={valuationFilters.eps || [0, 10000]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, eps: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-5000}
                      max={50000}
                      step={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">BPS (주당순자산)</Typography>
                    <Slider
                      value={valuationFilters.bps || [0, 50000]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, bps: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={200000}
                      step={1000}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  
                  {/* 가격 관련 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mt: 2, fontWeight: 'bold' }}>
                      💰 가격 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">현재가 (원)</Typography>
                    <Slider
                      value={valuationFilters.currentPrice || [1000, 100000]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, currentPrice: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={1000000}
                      step={1000}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">52주 최고가 대비 (%)</Typography>
                    <Slider
                      value={valuationFilters.priceToHigh52w || [50, 100]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, priceToHigh52w: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">거래량 (천주)</Typography>
                    <Slider
                      value={valuationFilters.volume || [100, 10000]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, volume: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100000}
                      step={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">외국인 보유비율 (%)</Typography>
                    <Slider
                      value={valuationFilters.foreignRatio || [0, 50]}
                      onChange={(e, v) => setValuationFilters({...valuationFilters, foreignRatio: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button 
                      variant="contained" 
                      fullWidth
                      startIcon={<Speed />}
                      onClick={() => {
                        const event = new CustomEvent('applyFilter', {
                          detail: { filterType: 'valuation', filters: valuationFilters }
                        })
                        window.dispatchEvent(event)
                      }}
                    >
                      가치 필터 적용
                    </Button>
                  </Grid>
                </Grid>
              )}
              
              {/* 재무 탭 */}
              {activeTab === 1 && (
                <Grid container spacing={2}>
                  {/* 수익성 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      📈 수익성 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">ROE (자기자본이익률) %</Typography>
                    <Slider
                      value={financialFilters.roe}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, roe: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-20}
                      max={50}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">ROA (총자산이익률) %</Typography>
                    <Slider
                      value={financialFilters.roa || [0, 20]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, roa: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-10}
                      max={30}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">영업이익률 (%)</Typography>
                    <Slider
                      value={financialFilters.operatingMargin}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, operatingMargin: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-20}
                      max={50}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">순이익률 (%)</Typography>
                    <Slider
                      value={financialFilters.netMargin || [0, 30]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, netMargin: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-20}
                      max={50}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  
                  {/* 안정성 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mt: 2, fontWeight: 'bold' }}>
                      🛡️ 안정성 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">부채비율 (%)</Typography>
                    <Slider
                      value={financialFilters.debtRatio}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, debtRatio: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={200}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">유동비율 (%)</Typography>
                    <Slider
                      value={financialFilters.currentRatio || [100, 300]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, currentRatio: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={500}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">당좌비율 (%)</Typography>
                    <Slider
                      value={financialFilters.quickRatio || [50, 200]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, quickRatio: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={300}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  
                  {/* 성장성 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mt: 2, fontWeight: 'bold' }}>
                      🚀 성장성 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">매출성장률 (%)</Typography>
                    <Slider
                      value={financialFilters.revenueGrowth || [-10, 50]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, revenueGrowth: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-50}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">이익성장률 (%)</Typography>
                    <Slider
                      value={financialFilters.profitGrowth || [-10, 50]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, profitGrowth: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-50}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">자본성장률 (%)</Typography>
                    <Slider
                      value={financialFilters.equityGrowth || [0, 30]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, equityGrowth: v as number[]})}
                      valueLabelDisplay="auto"
                      min={-20}
                      max={50}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  
                  {/* 배당 지표 섹션 */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mt: 2, fontWeight: 'bold' }}>
                      💵 배당 지표
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">배당수익률 (%)</Typography>
                    <Slider
                      value={financialFilters.dividendYield}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, dividendYield: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.5}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">배당성향 (%)</Typography>
                    <Slider
                      value={financialFilters.dividendPayout || [0, 50]}
                      onChange={(e, v) => setFinancialFilters({...financialFilters, dividendPayout: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ mt: 1 }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button 
                      variant="contained" 
                      fullWidth
                      color="secondary"
                      startIcon={<Timeline />}
                      onClick={() => {
                        const event = new CustomEvent('applyFilter', {
                          detail: { filterType: 'financial', filters: financialFilters }
                        })
                        window.dispatchEvent(event)
                      }}
                    >
                      재무 필터 적용
                    </Button>
                  </Grid>
                </Grid>
              )}
              
              {/* 섹터 탭 */}
              {activeTab === 2 && (
                <Box>
                  <Grid container spacing={1}>
                    {allSectors.map(sector => (
                      <Grid item xs={4} key={sector}>
                        <Chip
                          label={sector}
                          size="small"
                          color={sectorFilters.sectors.includes(sector) ? "primary" : "default"}
                          onClick={() => {
                            if (sectorFilters.sectors.includes(sector)) {
                              setSectorFilters({
                                sectors: sectorFilters.sectors.filter(s => s !== sector)
                              })
                            } else {
                              setSectorFilters({
                                sectors: [...sectorFilters.sectors, sector]
                              })
                            }
                          }}
                          sx={{ 
                            width: '100%',
                            cursor: 'pointer',
                            '&:hover': { transform: 'scale(1.05)' }
                          }}
                        />
                      </Grid>
                    ))}
                  </Grid>
                  <Button 
                    variant="contained" 
                    fullWidth
                    color="info"
                    startIcon={<Category />}
                    sx={{ mt: 2 }}
                    onClick={() => {
                      const event = new CustomEvent('applyFilter', {
                        detail: { filterType: 'sector', filters: sectorFilters }
                      })
                      window.dispatchEvent(event)
                    }}
                  >
                    섹터 필터 적용
                  </Button>
                </Box>
              )}
              
              {/* 투자자 탭 */}
              {activeTab === 3 && (
                <Box>
                  <InvestorTrendFilter
                    initialFilters={investorFilters}
                    onFilterChange={(filters) => {
                      setInvestorFilters(filters as any)
                      setCurrentFilterValues(prev => ({ ...prev, investor: filters }))
                    }}
                    onApplyFilter={() => {
                      const event = new CustomEvent('applyFilter', {
                        detail: { filterType: 'investor', filters: investorFilters }
                      })
                      window.dispatchEvent(event)
                    }}
                  />
                </Box>
              )}
              
              {/* 상세 탭 - Matrix View */}
              {activeTab === 4 && (
                <Box>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ViewModule />
                    매트릭스 필터 뷰
                  </Typography>
                  
                  {/* Visual Matrix Grid */}
                  <Grid container spacing={1} sx={{ mb: 3 }}>
                    {[
                      { label: 'PER', value: valuationFilters.per, color: '#FF6B6B' },
                      { label: 'PBR', value: valuationFilters.pbr, color: '#4ECDC4' },
                      { label: 'ROE', value: financialFilters.roe, color: '#45B7D1' },
                      { label: '부채비율', value: financialFilters.debtRatio, color: '#96CEB4' }
                    ].map((metric) => (
                      <Grid item xs={6} key={metric.label}>
                        <Paper
                          sx={{
                            p: 2,
                            cursor: 'pointer',
                            border: '2px solid',
                            borderColor: selectedMatrix === metric.label ? metric.color : 'transparent',
                            transition: 'all 0.3s',
                            '&:hover': {
                              borderColor: metric.color,
                              transform: 'scale(1.02)'
                            }
                          }}
                          onClick={() => setSelectedMatrix(metric.label)}
                        >
                          <Typography variant="subtitle2" color="text.secondary">
                            {metric.label}
                          </Typography>
                          <Typography variant="h6">
                            {metric.value[0]} ~ {metric.value[1]}
                          </Typography>
                          <Box
                            sx={{
                              height: 4,
                              bgcolor: metric.color,
                              borderRadius: 2,
                              mt: 1,
                              width: `${((metric.value[1] - metric.value[0]) / 100) * 100}%`
                            }}
                          />
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>

                  {/* Circular Range Selector */}
                  {selectedMatrix && (
                    <Paper sx={{ p: 3, mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        {selectedMatrix} 범위 조정
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <TextField
                          type="number"
                          label="최소"
                          size="small"
                          value={
                            selectedMatrix === 'PER' ? valuationFilters.per[0] :
                            selectedMatrix === 'PBR' ? valuationFilters.pbr[0] :
                            selectedMatrix === 'ROE' ? financialFilters.roe[0] :
                            financialFilters.debtRatio[0]
                          }
                          onChange={(e) => {
                            const val = Number(e.target.value);
                            if (selectedMatrix === 'PER') {
                              setValuationFilters({...valuationFilters, per: [val, valuationFilters.per[1]]});
                            } else if (selectedMatrix === 'PBR') {
                              setValuationFilters({...valuationFilters, pbr: [val, valuationFilters.pbr[1]]});
                            } else if (selectedMatrix === 'ROE') {
                              setFinancialFilters({...financialFilters, roe: [val, financialFilters.roe[1]]});
                            } else {
                              setFinancialFilters({...financialFilters, debtRatio: [val, financialFilters.debtRatio[1]]});
                            }
                          }}
                          sx={{ width: 100 }}
                        />
                        <Box sx={{ flex: 1 }}>
                          <Slider
                            value={
                              selectedMatrix === 'PER' ? valuationFilters.per :
                              selectedMatrix === 'PBR' ? valuationFilters.pbr :
                              selectedMatrix === 'ROE' ? financialFilters.roe :
                              financialFilters.debtRatio
                            }
                            onChange={(e, v) => {
                              if (selectedMatrix === 'PER') {
                                setValuationFilters({...valuationFilters, per: v as number[]});
                              } else if (selectedMatrix === 'PBR') {
                                setValuationFilters({...valuationFilters, pbr: v as number[]});
                              } else if (selectedMatrix === 'ROE') {
                                setFinancialFilters({...financialFilters, roe: v as number[]});
                              } else {
                                setFinancialFilters({...financialFilters, debtRatio: v as number[]});
                              }
                            }}
                            valueLabelDisplay="auto"
                            min={0}
                            max={selectedMatrix === 'PER' ? 100 : selectedMatrix === 'PBR' ? 10 : 100}
                            step={selectedMatrix === 'PBR' ? 0.1 : 1}
                          />
                        </Box>
                        <TextField
                          type="number"
                          label="최대"
                          size="small"
                          value={
                            selectedMatrix === 'PER' ? valuationFilters.per[1] :
                            selectedMatrix === 'PBR' ? valuationFilters.pbr[1] :
                            selectedMatrix === 'ROE' ? financialFilters.roe[1] :
                            financialFilters.debtRatio[1]
                          }
                          onChange={(e) => {
                            const val = Number(e.target.value);
                            if (selectedMatrix === 'PER') {
                              setValuationFilters({...valuationFilters, per: [valuationFilters.per[0], val]});
                            } else if (selectedMatrix === 'PBR') {
                              setValuationFilters({...valuationFilters, pbr: [valuationFilters.pbr[0], val]});
                            } else if (selectedMatrix === 'ROE') {
                              setFinancialFilters({...financialFilters, roe: [financialFilters.roe[0], val]});
                            } else {
                              setFinancialFilters({...financialFilters, debtRatio: [financialFilters.debtRatio[0], val]});
                            }
                          }}
                          sx={{ width: 100 }}
                        />
                      </Box>
                    </Paper>
                  )}

                  {/* Bubble Chart Style Filter */}
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      버블 차트 필터
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                      {[
                        { label: '소형주', size: 40, marketCap: [100, 1000] },
                        { label: '중형주', size: 60, marketCap: [1000, 10000] },
                        { label: '대형주', size: 80, marketCap: [10000, 50000] },
                        { label: '초대형주', size: 100, marketCap: [50000, 500000] }
                      ].map((bubble) => (
                        <Box
                          key={bubble.label}
                          sx={{
                            width: bubble.size,
                            height: bubble.size,
                            borderRadius: '50%',
                            bgcolor: marketCapRange[0] === bubble.marketCap[0] ? 'primary.main' : 'grey.300',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.3s',
                            '&:hover': {
                              transform: 'scale(1.1)'
                            }
                          }}
                          onClick={() => {
                            setMarketCapRange(bubble.marketCap);
                            setValuationFilters({...valuationFilters, marketCap: bubble.marketCap});
                          }}
                        >
                          <Typography variant="caption" sx={{ color: 'white', textAlign: 'center' }}>
                            {bubble.label}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                </Box>
              )}

              {/* Floating Action Menu */}
              <SpeedDial
                ariaLabel="Filter Actions"
                sx={{ position: 'fixed', bottom: 16, right: 16 }}
                icon={<SpeedDialIcon icon={<FilterList />} />}
              >
                <SpeedDialAction
                  icon={<Assessment />}
                  tooltipTitle="가치평가 필터 적용"
                  onClick={() => {
                    const event = new CustomEvent('applyFilter', {
                      detail: { filterType: 'valuation', filters: valuationFilters }
                    })
                    window.dispatchEvent(event)
                  }}
                />
                <SpeedDialAction
                  icon={<AccountBalance />}
                  tooltipTitle="재무지표 필터 적용"
                  onClick={() => {
                    const event = new CustomEvent('applyFilter', {
                      detail: { filterType: 'financial', filters: financialFilters }
                    })
                    window.dispatchEvent(event)
                  }}
                />
                <SpeedDialAction
                  icon={<Business />}
                  tooltipTitle="섹터 필터 적용"
                  onClick={() => {
                    const event = new CustomEvent('applyFilter', {
                      detail: { filterType: 'sector', sectors: selectedSectors }
                    })
                    window.dispatchEvent(event)
                  }}
                />
                <SpeedDialAction
                  icon={<Refresh />}
                  tooltipTitle="필터 초기화"
                  onClick={() => {
                    setValuationFilters({
                      marketCap: [100, 50000],
                      per: [0, 50],
                      pbr: [0, 10],
                      pcr: [0, 30],
                      psr: [0, 5],
                      peg: [0, 3],
                      eps: [-1000, 10000],
                      bps: [0, 100000],
                      currentPrice: [1000, 1000000],
                      priceToHigh52w: [30, 100],
                      volume: [10000, 100000000],
                      foreignRatio: [0, 50]
                    })
                    setFinancialFilters({
                      roe: [-10, 30],
                      roa: [-5, 20],
                      debtRatio: [0, 100],
                      currentRatio: [50, 300],
                      quickRatio: [30, 200],
                      operatingMargin: [-10, 30],
                      netMargin: [-10, 20],
                      revenueGrowth: [-20, 50],
                      profitGrowth: [-50, 100],
                      equityGrowth: [-10, 30],
                      dividendYield: [0, 10],
                      dividendPayout: [0, 100]
                    })
                    setSelectedSectors([])
                  }}
                />
              </SpeedDial>

              {/* Visual Dashboard Filter */}
              {activeTab === 5 && (
                <Box>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Timeline />
                    대시보드 필터
                  </Typography>
                  
                  {/* Gauge Charts */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="subtitle2">시가총액</Typography>
                        <Box sx={{ position: 'relative', height: 100 }}>
                          <CircularProgress
                            variant="determinate"
                            value={(valuationFilters.marketCap[1] / 100000) * 100}
                            size={80}
                            thickness={8}
                            sx={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}
                          />
                          <Typography
                            variant="caption"
                            sx={{
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              transform: 'translate(-50%, -50%)'
                            }}
                          >
                            {(valuationFilters.marketCap[1] / 1000).toFixed(0)}조
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="subtitle2">PER</Typography>
                        <Box sx={{ position: 'relative', height: 100 }}>
                          <CircularProgress
                            variant="determinate"
                            value={(valuationFilters.per[1] / 100) * 100}
                            size={80}
                            thickness={8}
                            color="secondary"
                            sx={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}
                          />
                          <Typography
                            variant="caption"
                            sx={{
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              transform: 'translate(-50%, -50%)'
                            }}
                          >
                            {valuationFilters.per[1]}
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="subtitle2">ROE</Typography>
                        <Box sx={{ position: 'relative', height: 100 }}>
                          <CircularProgress
                            variant="determinate"
                            value={(financialFilters.roe[1] / 50) * 100}
                            size={80}
                            thickness={8}
                            color="success"
                            sx={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}
                          />
                          <Typography
                            variant="caption"
                            sx={{
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              transform: 'translate(-50%, -50%)'
                            }}
                          >
                            {financialFilters.roe[1]}%
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>

                  {/* Heatmap Style Filter Grid */}
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>히트맵 필터</Typography>
                    <Grid container spacing={1}>
                      {[
                        { name: 'PER', min: 0, max: 20, color: '#00FF00' },
                        { name: 'PBR', min: 0, max: 2, color: '#33FF33' },
                        { name: 'ROE', min: 15, max: 30, color: '#66FF66' },
                        { name: '부채비율', min: 0, max: 50, color: '#99FF99' },
                        { name: 'ROA', min: 5, max: 15, color: '#CCFFCC' },
                        { name: '영업이익률', min: 10, max: 25, color: '#FFFF00' },
                        { name: '순이익률', min: 5, max: 15, color: '#FFCC00' },
                        { name: '매출성장률', min: 0, max: 30, color: '#FF9900' },
                        { name: '배당수익률', min: 2, max: 5, color: '#FF6600' }
                      ].map((metric) => (
                        <Grid item xs={4} key={metric.name}>
                          <Paper
                            sx={{
                              p: 1.5,
                              bgcolor: metric.color,
                              opacity: 0.7,
                              cursor: 'pointer',
                              transition: 'all 0.3s',
                              '&:hover': {
                                opacity: 1,
                                transform: 'scale(1.05)'
                              }
                            }}
                            onClick={() => {
                              // Apply predefined filter range
                              if (metric.name === 'PER') {
                                setValuationFilters({...valuationFilters, per: [metric.min, metric.max]})
                              } else if (metric.name === 'PBR') {
                                setValuationFilters({...valuationFilters, pbr: [metric.min, metric.max]})
                              } else if (metric.name === 'ROE') {
                                setFinancialFilters({...financialFilters, roe: [metric.min, metric.max]})
                              }
                              // ... handle other metrics
                            }}
                          >
                            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                              {metric.name}
                            </Typography>
                            <Typography variant="caption" display="block">
                              {metric.min}~{metric.max}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>
                </Box>
              )}
            </Box>
          </Box>
        </Paper>
      </Box>

      {/* 오른쪽: 필터링된 투자 유니버스 */}
      {showUniverse && (
        <Box sx={{ flex: '0 0 30%', display: 'flex', flexDirection: 'column', gap: 2 }}>
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
                  {dataFreshness?.totalStocks || 0}개 종목 데이터 준비 완료
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
      
      {/* 필터 저장 다이얼로그 */}
      <SaveFilterDialog
        open={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
        filterData={{
          filters: currentFilterValues,
          appliedFilters,
          filteredStocks: cumulativeFilteredStocks,
          filterStats
        }}
        onSaveComplete={(saveType, savedName) => {
          setSaveDialogOpen(false)
          // 저장 완료 알림 (선택사항)
          console.log(`필터 "${savedName}"이(가) ${saveType === 'local' ? '로컬' : '클라우드'}에 저장되었습니다.`)
        }}
      />
      
      {/* 필터 불러오기 다이얼로그 */}
      <LoadFilterDialog
        open={loadDialogOpen}
        onClose={() => setLoadDialogOpen(false)}
        onLoadFilter={(filter) => {
          // 불러온 필터 적용
          if (filter.filters) {
            setCurrentFilterValues(filter.filters)
          }
          if (filter.appliedFilters) {
            setAppliedFilters(filter.appliedFilters)
          }
          if (filter.filterStats) {
            setFilterStats(filter.filterStats)
          }
          if (filter.filteredStocks) {
            setCumulativeFilteredStocks(filter.filteredStocks)
            setFilteredStocks(filter.filteredStocks.slice(0, 10))
          }
          
          // 필터 UI 업데이트
          if (filter.filters?.valuation) {
            setValuationFilters(filter.filters.valuation)
          }
          if (filter.filters?.financial) {
            setFinancialFilters(filter.filters.financial)
          }
          if (filter.filters?.sector) {
            setSectorFilters(filter.filters.sector)
          }
          
          setLoadDialogOpen(false)
          console.log(`필터 "${filter.name}"을(를) 불러왔습니다.`)
        }}
      />
    </Box>
  )
}

export default TradingSettingsWithUniverse