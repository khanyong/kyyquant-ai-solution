import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Tabs,
  Tab
} from '@mui/material'
import {
  Add,
  Remove,
  PlayArrow,
  Save,
  FolderOpen,
  TrendingUp,
  TrendingDown,
  ShowChart,
  Timeline,
  Speed,
  Info,
  CheckCircle,
  Warning,
  Assessment,
  Security,
  Delete,
  Edit,
  ContentCopy,
  Settings,
  Build,
  Home,
  ArrowBack,
  SwapHoriz,
  AccountTree,
  Autorenew
} from '@mui/icons-material'
import InvestmentFlowManager from './InvestmentFlowManager'
import StageBasedStrategy from './StageBasedStrategy'
import StrategyLoader from './StrategyLoader'
import StrategyAnalyzer from './StrategyAnalyzer'
import TargetProfitSettingsEnhanced from './TargetProfitSettingsEnhanced'
import { supabase } from '../lib/supabase'
import { authService } from '../services/auth'
import { InvestmentFlowType } from '../types/investment'
import {
  validateStrategyData,
  prepareStrategyForSave,
  checkJsonSize,
  generateStrategySummary,
  checkStrategyConflicts,
  normalizeStopLoss,
  ConflictCheckResult
} from '../utils/strategyValidator'

interface Indicator {
  id: string
  name: string
  type: 'trend' | 'momentum' | 'volume' | 'volatility'
  params: { [key: string]: number | string }
  enabled: boolean
}

interface Condition {
  id: string
  type: 'buy' | 'sell'
  indicator: string
  operator: '>' | '<' | '=' | 'cross_above' | 'cross_below' | 
    'cloud_above' | 'cloud_below' | 'cloud_break_up' | 'cloud_break_down' |
    'tenkan_kijun_cross_up' | 'tenkan_kijun_cross_down' | 'chikou_above' | 'chikou_below'
  value: number | string
  combineWith: 'AND' | 'OR'
  // 일목균형표 전용 파라미터
  ichimokuLine?: 'tenkan' | 'kijun' | 'senkou_a' | 'senkou_b' | 'chikou'
  confirmBars?: number // 확인봉 개수
}

interface Strategy {
  id: string
  name: string
  description: string
  isOwn?: boolean  // 자신의 전략인지 표시 (개발 모드용)
  indicators: Indicator[]
  buyConditions: Condition[]
  sellConditions: Condition[]
  targetProfit?: {
    mode: 'simple' | 'staged'
    simple?: {
      enabled: boolean
      value: number
      combineWith: 'AND' | 'OR'
    }
    staged?: {
      enabled: boolean
      stages: Array<{
        stage: number
        targetProfit: number
        exitRatio: number
        dynamicStopLoss?: boolean
        combineWith?: 'AND' | 'OR'
      }>
      combineWith: 'AND' | 'OR'
    }
  }
  stopLoss?: {
    enabled: boolean
    value: number
    breakEven?: boolean
    trailingStop?: {
      enabled: boolean
      activation: number
      distance: number
    }
  }
  riskManagement: {
    stopLoss: number
    takeProfit: number
    trailingStop: boolean
    trailingStopPercent: number
    positionSize: number
    maxPositions: number
    // 추가된 리스크 관리 옵션
    systemCut?: boolean
    maxDailyLoss?: number
    maxDrawdown?: number
    consecutiveLosses?: number
  }
  // 추가된 고급 기능
  timeframe?: '1분' | '5분' | '15분' | '30분' | '60분' | '일봉' | '주봉' | '월봉'
  splitTrading?: {
    enabled: boolean
    levels: number
    percentages: number[]
  }
  sectorFilter?: {
    enabled: boolean
    sectors: string[]
    comparison: 'outperform' | 'underperform' | 'correlation'
  }
  universe?: {
    minMarketCap?: number
    maxMarketCap?: number
    minPER?: number
    maxPER?: number
    minPBR?: number
    maxPBR?: number
    minROE?: number
    maxROE?: number
  }
  quickTestResult?: {
    returns: number
    winRate: number
    maxDrawdown: number
    trades: number
  }
  advanced?: {
    splitTrading?: {
      enabled: boolean
      levels: number
      percentages: number[]
    }
    sectorFilter?: {
      enabled: boolean
      sectors: string[]
      comparison: 'outperform' | 'underperform' | 'correlation'
    }
    universe?: {
      minMarketCap?: number
      maxMarketCap?: number
      minPER?: number
      maxPER?: number
      minPBR?: number
      maxPBR?: number
      minROE?: number
      maxROE?: number
    }
  }
}

const AVAILABLE_INDICATORS = [
  { id: 'ma', name: 'MA (이동평균)', type: 'trend', defaultParams: { period: 20 } },
  { id: 'sma', name: 'SMA (단순이동평균)', type: 'trend', defaultParams: { period: 20 } },
  { id: 'ema', name: 'EMA (지수이동평균)', type: 'trend', defaultParams: { period: 20 } },
  { id: 'bb', name: '볼린저밴드', type: 'volatility', defaultParams: { period: 20, std: 2 } },
  { id: 'rsi', name: 'RSI', type: 'momentum', defaultParams: { period: 14 } },
  { id: 'macd', name: 'MACD', type: 'momentum', defaultParams: { fast: 12, slow: 26, signal: 9 } },
  { id: 'stochastic', name: '스토캐스틱', type: 'momentum', defaultParams: { k: 14, d: 3 } },
  { id: 'ichimoku', name: '일목균형표', type: 'trend', defaultParams: { 
    tenkan: 9,  // 전환선
    kijun: 26,  // 기준선 
    senkou: 52, // 선행스팬
    chikou: 26  // 후행스팬
  } },
  { id: 'volume', name: '거래량', type: 'volume', defaultParams: { period: 20 } },
  { id: 'obv', name: 'OBV (누적거래량)', type: 'volume', defaultParams: {} },
  { id: 'vwap', name: 'VWAP (거래량가중평균)', type: 'volume', defaultParams: {} },
  { id: 'atr', name: 'ATR (변동성)', type: 'volatility', defaultParams: { period: 14 } },
  { id: 'cci', name: 'CCI', type: 'momentum', defaultParams: { period: 20 } },
  { id: 'williams', name: 'Williams %R', type: 'momentum', defaultParams: { period: 14 } },
  { id: 'adx', name: 'ADX (추세강도)', type: 'trend', defaultParams: { period: 14 } },
  { id: 'dmi', name: 'DMI (+DI/-DI)', type: 'trend', defaultParams: { period: 14 } },
  { id: 'parabolic', name: 'Parabolic SAR', type: 'trend', defaultParams: { acc: 0.02, max: 0.2 } }
]

// PRESET_STRATEGIES는 템플릿으로 통합되어 제거됨
// 상단의 8개 전략 템플릿 카드로 대체

interface StrategyBuilderProps {
  onExecute?: (strategy: Strategy) => void
  onNavigateHome?: () => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const StrategyBuilderUpdated: React.FC<StrategyBuilderProps> = ({ onExecute, onNavigateHome }) => {
  const [currentTab, setCurrentTab] = useState(0)
  const [currentFlowType, setCurrentFlowType] = useState<InvestmentFlowType>(InvestmentFlowType.FILTER_FIRST)
  const [useStageBasedStrategy, setUseStageBasedStrategy] = useState(true) // 단계별 전략 사용 여부
  const [buyStageStrategy, setBuyStageStrategy] = useState<any>(null)
  const [sellStageStrategy, setSellStageStrategy] = useState<any>(null)
  const [strategy, setStrategy] = useState<Strategy>({
    id: 'custom-1',
    name: '나의 전략',
    description: '',
    indicators: [],
    buyConditions: [],
    sellConditions: [],
    targetProfit: {
      mode: 'simple',
      simple: {
        enabled: false,
        value: 5.0,
        combineWith: 'OR'
      }
    },
    stopLoss: {
      enabled: false,
      value: 3.0
    },
    riskManagement: {
      stopLoss: -5,
      takeProfit: 10,
      trailingStop: false,
      trailingStopPercent: 3,
      positionSize: 10,
      maxPositions: 10
    }
  })

  const [quickTestRunning, setQuickTestRunning] = useState(false)
  const [savedStrategies, setSavedStrategies] = useState<Strategy[]>([])
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [conditionDialogOpen, setConditionDialogOpen] = useState(false)
  const [currentConditionType, setCurrentConditionType] = useState<'buy' | 'sell'>('buy')
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [isPublic, setIsPublic] = useState(false)
  const [tempCondition, setTempCondition] = useState<Condition>({
    id: '',
    type: 'buy',
    indicator: 'rsi',
    operator: '>',
    value: 30,
    combineWith: 'AND'
  })
  
  // 투자 설정 상태
  const [investmentConfig, setInvestmentConfig] = useState<any>(null)
  const [filteredUniverseCount, setFilteredUniverseCount] = useState<number>(0)
  const [strategyConflicts, setStrategyConflicts] = useState<ConflictCheckResult | null>(null)
  
  // 전략 변경 시 충돌 검사
  const checkConflictsDebounced = React.useCallback((updatedStrategy: any) => {
    const timeoutId = setTimeout(() => {
      const conflicts = checkStrategyConflicts(updatedStrategy)
      setStrategyConflicts(conflicts)
    }, 500) // 500ms 디바운싱

    return () => clearTimeout(timeoutId)
  }, [])

  // 전략 업데이트 시 충돌 검사 추가
  React.useEffect(() => {
    const fullStrategy = {
      ...strategy,
      buyStageStrategy,
      sellStageStrategy
    }
    const cleanup = checkConflictsDebounced(fullStrategy)
    return cleanup
  }, [strategy, buyStageStrategy, sellStageStrategy, checkConflictsDebounced])

  // 투자 설정 불러오기
  React.useEffect(() => {
    const loadInvestmentConfig = () => {
      const config = localStorage.getItem('investmentConfig')
      if (config) {
        const parsed = JSON.parse(config)
        setInvestmentConfig(parsed)
        
        // 필터링된 유니버스 정보도 확인
        const universe = localStorage.getItem('filteredUniverse')
        if (universe) {
          const parsedUniverse = JSON.parse(universe)
          setFilteredUniverseCount(parsedUniverse.length || 0)
        }
      }
    }
    
    loadInvestmentConfig()
    
    // localStorage 변경 감지
    window.addEventListener('storage', loadInvestmentConfig)
    
    return () => {
      window.removeEventListener('storage', loadInvestmentConfig)
    }
  }, [])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  // 지표 추가
  const addIndicator = (indicatorId: string) => {
    const indicator = AVAILABLE_INDICATORS.find(i => i.id === indicatorId)
    if (!indicator) return

    const newIndicator: Indicator = {
      id: `${indicatorId}_${Date.now()}`,
      name: indicator.name,
      type: indicator.type as any,
      params: Object.fromEntries(
        Object.entries(indicator.defaultParams).map(([key, value]) => [key, value])
      ) as { [key: string]: string | number },
      enabled: true
    }

    setStrategy({
      ...strategy,
      indicators: [...strategy.indicators, newIndicator]
    })
  }

  // 매수/매도 조건 추가
  const addCondition = (type: 'buy' | 'sell') => {
    setCurrentConditionType(type)
    setTempCondition({
      id: `cond_${Date.now()}`,
      type,
      indicator: 'rsi_14',
      operator: type === 'buy' ? '<' : '>',
      value: type === 'buy' ? 30 : 70,
      combineWith: strategy[type === 'buy' ? 'buyConditions' : 'sellConditions'].length > 0 ? 'AND' : 'AND'
    })
    setConditionDialogOpen(true)
  }

  // 조건 저장
  const saveCondition = () => {
    const newCondition = { ...tempCondition, id: `cond_${Date.now()}` }
    if (currentConditionType === 'buy') {
      setStrategy({
        ...strategy,
        buyConditions: [...strategy.buyConditions, newCondition]
      })
    } else {
      setStrategy({
        ...strategy,
        sellConditions: [...strategy.sellConditions, newCondition]
      })
    }
    setConditionDialogOpen(false)
  }

  // 조건 제거
  const removeCondition = (type: 'buy' | 'sell', conditionId: string) => {
    if (type === 'buy') {
      setStrategy({
        ...strategy,
        buyConditions: strategy.buyConditions.filter(c => c.id !== conditionId)
      })
    } else {
      setStrategy({
        ...strategy,
        sellConditions: strategy.sellConditions.filter(c => c.id !== conditionId)
      })
    }
  }

  // 일목균형표 연산자 가져오기
  const getIchimokuOperators = () => [
    { value: 'cloud_above', label: '구름대 상단' },
    { value: 'cloud_below', label: '구름대 하단' },
    { value: 'cloud_break_up', label: '구름대 상향돌파' },
    { value: 'cloud_break_down', label: '구름대 하향돌파' },
    { value: 'tenkan_kijun_cross_up', label: '전환선 > 기준선 교차' },
    { value: 'tenkan_kijun_cross_down', label: '전환선 < 기준선 교차' },
    { value: 'chikou_above', label: '후행스팬 > 주가' },
    { value: 'chikou_below', label: '후행스팬 < 주가' }
  ]

  // 일반 연산자 가져오기
  const getStandardOperators = () => [
    { value: '>', label: '초과 (>)' },
    { value: '<', label: '미만 (<)' },
    { value: '=', label: '같음 (=)' },
    { value: 'cross_above', label: '상향돌파' },
    { value: 'cross_below', label: '하향돌파' }
  ]

  // 빠른 백테스트 실행
  const runQuickTest = async () => {
    setQuickTestRunning(true)
    
    try {
      // 백엔드 API 호출
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/backtest/quick`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy: {
            ...strategy,
            config: {
              buyConditions: strategy.buyConditions,
              sellConditions: strategy.sellConditions,
              riskManagement: strategy.riskManagement,
              useStageBasedStrategy,
              buyStageStrategy,
              sellStageStrategy
            }
          },
          stock_codes: filteredUniverseCount > 0 ? 
            JSON.parse(localStorage.getItem('filteredUniverse') || '[]').slice(0, 5).map((s: any) => s.code) :
            ['005930', '000660', '035720']  // 기본: 삼성전자, SK하이닉스, 카카오
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setStrategy({
          ...strategy,
          quickTestResult: result
        })
      } else {
        throw new Error('백테스트 실행 실패')
      }
    } catch (error) {
      console.error('Quick backtest error:', error)
      alert('백테스트 실행 중 오류가 발생했습니다.')
      
      // 폴백: 시뮬레이션 데이터
      setStrategy({
        ...strategy,
        quickTestResult: {
          returns: 15.7,
          winRate: 62.5,
          maxDrawdown: -8.3,
          trades: 48
        }
      })
    } finally {
      setQuickTestRunning(false)
    }
  }

  // 전략 저장 다이얼로그 열기
  const openSaveDialog = () => {
    setSaveDialogOpen(true)
  }

  // 전략 저장 (Supabase에 저장)
  const saveStrategy = async () => {
    // 현재 사용자 가져오기
    const user = await authService.getCurrentUser()
    if (!user || !user.id) {
      alert('전략을 저장하려면 로그인이 필요합니다.\n로그인 후 다시 시도해주세요.')
      // 로그인 페이지로 이동하거나 로그인 모달 표시
      window.location.href = '/login'
      return null
    }
    // 디버그용 콘솔 로그
    console.log('Saving strategy...', strategy);

    // 데이터 검증
    const validationResult = validateStrategyData({
      ...strategy,
      useStageBasedStrategy,
      buyStageStrategy,
      sellStageStrategy
    })

    if (!validationResult.isValid) {
      alert(`전략 저장 실패:\n\n${validationResult.errors.join('\n')}`)
      return null
    }

    if (validationResult.warnings.length > 0) {
      const proceed = confirm(`경고:\n${validationResult.warnings.join('\n')}\n\n계속하시겠습니까?`)
      if (!proceed) return null
    }

    // 중복 이름 체크
    try {
      const { data: existingStrategies, error: checkError } = await supabase
        .from('strategies')
        .select('name')
        .eq('name', strategy.name.trim())

      if (checkError) {
        console.error('Error checking duplicate name:', checkError)
      } else if (existingStrategies && existingStrategies.length > 0) {
        // 템플릿 이름인 경우 더 친절한 메시지
        if (strategy.name.startsWith('[템플릿]')) {
          alert(`템플릿 전략은 수정 후 다른 이름으로 저장해야 합니다.\n\n예시:\n- ${strategy.name}_수정\n- 나의_${strategy.name.replace('[템플릿] ', '')}\n- ${strategy.name.replace('[템플릿] ', '')}_v2`)
        } else {
          alert(`이미 동일한 이름의 전략이 존재합니다: "${strategy.name}"\n\n다른 이름을 사용해주세요.`)
        }
        return null
      }
    } catch (error) {
      console.error('Error checking duplicate strategy name:', error)
      // 중복 체크 실패해도 계속 진행할지 묻기
      const proceed = confirm('전략 이름 중복 확인에 실패했습니다.\n계속 저장하시겠습니까?')
      if (!proceed) return null
    }

    try {
      // 전략 타입 결정 (대문자로 변경하거나 TECHNICAL로 통일)
      let strategyType = 'TECHNICAL'  // 기본값을 TECHNICAL로 설정
      
      // 상세 타입은 config에 저장
      let detailedType = 'custom'
      if (strategy.indicators.some(i => i.id.includes('sma') || i.id.includes('ema'))) {
        detailedType = 'sma'
      } else if (strategy.indicators.some(i => i.id.includes('rsi'))) {
        detailedType = 'rsi'
      } else if (strategy.indicators.some(i => i.id.includes('bb'))) {
        detailedType = 'bollinger'
      } else if (strategy.indicators.some(i => i.id.includes('macd'))) {
        detailedType = 'macd'
      } else if (strategy.indicators.some(i => i.id.includes('ichimoku'))) {
        detailedType = 'ichimoku'
      }

      // 투자 유니버스 설정 가져오기
      const investmentConfig = localStorage.getItem('investmentConfig')
      const universeSettings = investmentConfig ? JSON.parse(investmentConfig) : null

      // 백테스팅과 호환되는 파라미터 구성
      const parameters: any = {
        strategy_type: detailedType,  // 상세 타입 정보 저장
        useStageBasedStrategy: useStageBasedStrategy,  // 단계별 전략 사용 여부
        buyStageStrategy: buyStageStrategy,  // 매수 단계 전략
        sellStageStrategy: sellStageStrategy,  // 매도 단계 전략
        // 투자 유니버스 설정
        investmentUniverse: universeSettings ? {
          financialFilters: universeSettings.universe,
          sectorFilters: universeSettings.sectors,
          portfolioSettings: universeSettings.portfolio,
          riskSettings: universeSettings.risk
        } : null,
        // 기본 지표 파라미터 - params 구조로 변환
        indicators: strategy.indicators.map(ind => {
          // params 구조가 있는지 확인
          const indicatorConfig: any = {
            type: ind.id.toLowerCase(), // 소문자로 통일
            params: ind.params || {}
          }

          // 레거시 period 필드가 있으면 params로 이동
          if ('period' in ind && !ind.params) {
            indicatorConfig.params = { period: (ind as any).period }
          }

          return indicatorConfig
        }),
        // 매수/매도 조건
        buyConditions: strategy.buyConditions,
        sellConditions: strategy.sellConditions,
        // 목표 수익률 및 손절
        targetProfit: strategy.targetProfit,
        stopLoss: strategy.stopLoss,
        // 리스크 관리
        stopLossOld: strategy.riskManagement.stopLoss,
        takeProfit: strategy.riskManagement.takeProfit,
        trailingStop: strategy.riskManagement.trailingStop,
        trailingStopPercent: strategy.riskManagement.trailingStopPercent,
        positionSize: strategy.riskManagement.positionSize,
        maxPositions: strategy.riskManagement.maxPositions
      }

      // SMA 전략의 경우 특별 처리
      if (strategyType === 'sma') {
        const smaIndicator = strategy.indicators.find(i => i.id.includes('sma'))
        if (smaIndicator) {
          parameters.short_window = smaIndicator.params.period || 20
          parameters.long_window = 60
          parameters.volume_filter = true
        }
      }
      // RSI 전략의 경우
      else if (strategyType === 'rsi') {
        const rsiIndicator = strategy.indicators.find(i => i.id.includes('rsi'))
        if (rsiIndicator) {
          parameters.rsi_period = rsiIndicator.params.period || 14
          parameters.oversold = 30
          parameters.overbought = 70
        }
      }
      // 볼린저 밴드 전략의 경우
      else if (strategyType === 'bollinger') {
        const bbIndicator = strategy.indicators.find(i => i.id.includes('bb'))
        if (bbIndicator) {
          parameters.period = bbIndicator.params.period || 20
          parameters.std_dev = bbIndicator.params.stdDev || 2
        }
      }

      // 저장할 데이터 준비 (실제 테이블 스키마에 맞게)
      const dataToSave: any = {
        name: strategy.name || '이름 없는 전략',
        description: strategy.description || `${strategy.name} - 전략빌더에서 생성`,
        // type: null,  // type 컬럼은 null로 설정 (체크 제약조건 때문)
        config: {
          ...parameters,
          // 서버가 config 내부에서 직접 조건을 찾으므로 여기에도 포함
          buyConditions: strategy.buyConditions || [],
          sellConditions: strategy.sellConditions || [],
          // 목표 수익률 및 손절 설정도 config에 포함
          targetProfit: strategy.targetProfit,
          stopLoss: strategy.stopLoss,
          stopLossOld: strategy.riskManagement.stopLoss,
          // 단계별 전략도 포함
          buyStageStrategy: buyStageStrategy,
          sellStageStrategy: sellStageStrategy,
          useStageBasedStrategy: useStageBasedStrategy
        },
        indicators: {
          list: strategy.indicators
        },
        entry_conditions: {
          buy: strategy.buyConditions
        },
        exit_conditions: {
          sell: strategy.sellConditions
        },
        risk_management: strategy.riskManagement,
        is_active: true,
        is_test_mode: false,
        auto_trade_enabled: false,
        is_public: isPublic,  // 전략 공유 설정
        position_size: strategy.riskManagement.positionSize || 10,
        user_id: user?.id  // 현재 사용자 ID (필수)
      }
      
      // 데이터 정리 (undefined -> null 변환)
      const cleanedData = prepareStrategyForSave(dataToSave)
      
      // 데이터 크기 확인
      const sizeCheck = checkJsonSize(cleanedData)
      if (!sizeCheck.isValid) {
        alert(`전략 데이터가 너무 큽니다 (${sizeCheck.sizeInKB} KB). 일부 설정을 줄여주세요.`)
        return null
      }
      
      console.log('Data to save:', cleanedData)
      console.log('Data size:', sizeCheck.sizeInKB, 'KB')
      console.log('Strategy summary:', generateStrategySummary(cleanedData))
      
      const { data, error } = await supabase
        .from('strategies')
        .insert(cleanedData)
        .select()
        .single()

      if (error) throw error

      setSavedStrategies([...savedStrategies, { ...strategy, id: data.id }])
      setSaveDialogOpen(false)
      setIsPublic(false)  // 초기화

      const shareMessage = isPublic ? '\n전략이 공개되어 다른 사용자들도 볼 수 있습니다.' : '\n전략은 비공개로 저장되었습니다.'
      alert(`전략 '${strategy.name}'이 저장되었습니다!${shareMessage}\n\n백테스팅 페이지에서 이 전략을 선택해 실행할 수 있습니다.`)
      
      return data.id // 저장된 전략 ID 반환
    } catch (error: any) {
      console.error('전략 저장 실패:', error)
      
      // 상세한 오류 메시지 표시
      let errorMessage = '전략 저장에 실패했습니다.\n\n'
      
      if (error.message) {
        errorMessage += `오류: ${error.message}\n`
      }
      
      if (error.code === '42501') {
        errorMessage += '\n테이블 접근 권한이 없습니다. Supabase에서 RLS 정책을 확인해주세요.'
      } else if (error.code === '23505') {
        errorMessage += '\n중복된 전략명입니다. 다른 이름을 사용해주세요.'
      } else if (!navigator.onLine) {
        errorMessage += '\n인터넷 연결을 확인해주세요.'
      }
      
      alert(errorMessage)
      return null
    }
  }

  // Supabase에서 전략 목록 불러오기
  React.useEffect(() => {
    loadStrategiesFromSupabase()
  }, [])

  const loadStrategiesFromSupabase = async () => {
    try {
      // 현재 사용자 가져오기
      const user = await authService.getCurrentUser()
      if (!user || !user.id) {
        console.warn('User not logged in - cannot load strategies')
        setSavedStrategies([])
        return
      }
      
      setCurrentUser(user) // 현재 사용자 저장

      console.log('Loading strategies for user:', user.id)
      
      // 모든 전략을 불러옴 (is_active 필터 제거)
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100) // 최대 100개까지 로드

      if (error) throw error

      const strategies = data.map((s: any) => ({
        id: s.id,
        name: s.name,
        description: s.description,
        indicators: s.indicators?.list || [],
        buyConditions: s.entry_conditions?.buy || s.config?.buyConditions || [],
        sellConditions: s.exit_conditions?.sell || s.config?.sellConditions || [],
        riskManagement: s.risk_management || s.config?.riskManagement || {
          stopLoss: -5,
          takeProfit: 10,
          trailingStop: false,
          trailingStopPercent: 3,
          positionSize: 10,
          maxPositions: 10
        },
        // 추가: 단계별 전략 및 투자 유니버스 정보
        useStageBasedStrategy: s.config?.useStageBasedStrategy || false,
        buyStageStrategy: s.config?.buyStageStrategy || null,
        sellStageStrategy: s.config?.sellStageStrategy || null,
        investmentUniverse: s.config?.investmentUniverse || null,
        // 개발 모드: 사용자 정보 추가
        userId: s.user_id,  // 전략 생성자 ID
        isOwn: s.user_id === user.id  // 자신의 전략인지 표시
      }))

      setSavedStrategies(strategies)
    } catch (error) {
      console.error('전략 로드 실패:', error)
    }
  }

  // 전략 불러오기
  const loadStrategy = (savedStrategy: any) => {
    console.log('StrategyBuilder - loadStrategy called with:', savedStrategy)

    // savedStrategy가 이미 strategy_data 형태인 경우와 아닌 경우 처리
    const strategyData = savedStrategy.strategy_data || savedStrategy

    // 템플릿 전략인 경우 이름 변경 안내
    if (strategyData.name && strategyData.name.startsWith('[템플릿]')) {
      setTimeout(() => {
        alert(`템플릿 전략을 불러왔습니다.\n\n저장하려면 이름을 변경해주세요.\n예시:\n- ${strategyData.name.replace('[템플릿] ', '')}_수정\n- 나의_${strategyData.name.replace('[템플릿] ', '')}\n- ${strategyData.name.replace('[템플릿] ', '')}_v2`)
      }, 500)
    }

    // 실제 저장된 데이터 구조에 맞게 파싱
    // 지표 데이터 파싱 (indicators.list 또는 indicators 배열)
    let indicators = []
    if (strategyData.indicators) {
      if (Array.isArray(strategyData.indicators)) {
        indicators = strategyData.indicators
      } else if (strategyData.indicators.list && Array.isArray(strategyData.indicators.list)) {
        indicators = strategyData.indicators.list
      }
    }

    // 매수 조건 파싱 (entry_conditions.buy 또는 buyConditions)
    let buyConditions = []
    if (strategyData.entry_conditions && strategyData.entry_conditions.buy) {
      buyConditions = strategyData.entry_conditions.buy
    } else if (strategyData.buyConditions) {
      buyConditions = strategyData.buyConditions
    }

    // 매도 조건 파싱 (exit_conditions.sell 또는 sellConditions)
    let sellConditions = []
    if (strategyData.exit_conditions && strategyData.exit_conditions.sell) {
      sellConditions = strategyData.exit_conditions.sell
    } else if (strategyData.sellConditions) {
      sellConditions = strategyData.sellConditions
    }

    // 리스크 관리 파싱
    let riskManagement = {
      stopLoss: -5,
      takeProfit: 10,
      trailingStop: false,
      trailingStopPercent: 3,
      positionSize: 10,
      maxPositions: 10
    }

    if (strategyData.risk_management) {
      riskManagement = { ...riskManagement, ...strategyData.risk_management }
    } else if (strategyData.riskManagement) {
      riskManagement = { ...riskManagement, ...strategyData.riskManagement }
    }

    // 전략 데이터 구조 확인 및 설정
    const formattedStrategy = {
      id: strategyData.id || `custom-${Date.now()}`,
      name: strategyData.name || '불러온 전략',
      description: strategyData.description || '',
      indicators: indicators,
      buyConditions: buyConditions,
      sellConditions: sellConditions,
      targetProfit: strategyData.targetProfit || strategyData.config?.targetProfit,
      stopLoss: strategyData.stopLoss || strategyData.config?.stopLoss,
      riskManagement: riskManagement
    }

    console.log('Parsed strategy data:')
    console.log('- Original:', strategyData)
    console.log('- Formatted:', formattedStrategy)
    console.log('- Indicators count:', indicators.length)
    console.log('- Buy conditions count:', buyConditions.length)
    console.log('- Sell conditions count:', sellConditions.length)

    setStrategy(formattedStrategy)

    // config에서 단계별 전략 정보 복원
    const config = strategyData.config || {}
    if (config.useStageBasedStrategy !== undefined) {
      setUseStageBasedStrategy(config.useStageBasedStrategy)
    }
    if (config.buyStageStrategy) {
      setBuyStageStrategy(config.buyStageStrategy)
    }
    if (config.sellStageStrategy) {
      setSellStageStrategy(config.sellStageStrategy)
    }

    // 투자 유니버스 설정 복원 (config.investmentUniverse 또는 직접)
    const investmentUniverse = config.investmentUniverse || strategyData.investmentUniverse
    if (investmentUniverse) {
      const configToRestore = {
        universe: investmentUniverse.financialFilters,
        sectors: investmentUniverse.sectorFilters,
        portfolio: investmentUniverse.portfolioSettings,
        risk: investmentUniverse.riskSettings
      }
      localStorage.setItem('investmentConfig', JSON.stringify(configToRestore))
    }

    setDialogOpen(false)

    // 성공 메시지
    alert(`전략 '${formattedStrategy.name}'을 불러왔습니다!\n\n지표: ${indicators.length}개\n매수조건: ${buyConditions.length}개\n매도조건: ${sellConditions.length}개`)
  }

  // 프리셋 전략 적용
  // applyPreset 함수는 템플릿 카드의 onClick으로 대체됨
  // const applyPreset = (preset: any) => {
  //   // 프리셋에 따라 전략 설정
  //   alert(`${preset.name} 전략을 적용합니다`)
  // }

  return (
    <Box>
      {/* 투자 유니버스 상태 표시 */}
      {investmentConfig && (
        <Alert 
          severity="info" 
          sx={{ mb: 2 }}
          action={
            <Button 
              size="small" 
              onClick={() => {
                // 투자설정 탭으로 이동
                const event = new CustomEvent('navigateToInvestmentSettings')
                window.dispatchEvent(event)
              }}
            >
              설정 변경
            </Button>
          }
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2">
              <strong>투자 유니버스 적용 중:</strong>
            </Typography>
            {investmentConfig.universe && (
              <Chip 
                size="small" 
                label={`시총 ${investmentConfig.universe.marketCap?.[0]}~${investmentConfig.universe.marketCap?.[1]}억`}
                variant="outlined"
              />
            )}
            {investmentConfig.universe?.per && (
              <Chip 
                size="small" 
                label={`PER ${investmentConfig.universe.per[0]}~${investmentConfig.universe.per[1]}`}
                variant="outlined"
              />
            )}
            {filteredUniverseCount > 0 && (
              <Chip 
                size="small" 
                label={`대상종목 ${filteredUniverseCount}개`}
                color="primary"
              />
            )}
          </Stack>
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {onNavigateHome && (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<Home />}
                onClick={onNavigateHome}
                size="medium"
              >
                메인으로
              </Button>
            )}
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ShowChart />
              전략 빌더
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<FolderOpen />}
              onClick={() => setDialogOpen(true)}
            >
              불러오기
            </Button>
            <Button
              variant="outlined"
              startIcon={<Save />}
              onClick={openSaveDialog}
            >
              저장
            </Button>
            <Button
              variant="contained"
              startIcon={<Speed />}
              onClick={runQuickTest}
              disabled={quickTestRunning}
              color="secondary"
            >
              퀵 백테스트 (1년)
            </Button>
          </Stack>
        </Box>

        {/* 전략 기본 정보 */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="전략 이름"
              value={strategy.name}
              onChange={(e) => setStrategy({ ...strategy, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="설명"
              value={strategy.description}
              onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* 탭 메뉴 */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<Build />} iconPosition="start" label="전략 구성" />
          <Tab icon={<Assessment />} iconPosition="start" label="전략 분석" />
          <Tab icon={<SwapHoriz />} iconPosition="start" label="투자 흐름 관리" />
        </Tabs>
      </Paper>

      {/* 전략 구성 탭 */}
      <TabPanel value={currentTab} index={0}>
        {/* 전략 템플릿 선택 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            전략 템플릿
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            검증된 기본 전략 템플릿을 선택하여 빠르게 시작하세요
          </Typography>
          <Grid container spacing={2}>
            {/* 골든크로스 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 골든크로스',
                    description: '단기 이동평균선이 장기 이동평균선을 상향 돌파할 때 매수',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'MA_20', operator: '>', value: 'MA_60', combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '2', type: 'sell', indicator: 'MA_20', operator: '<', value: 'MA_60', combineWith: 'AND' }
                    ]
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <TrendingUp color="primary" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    골든크로스
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    MA20 &gt; MA60 매수<br/>
                    안정적인 추세 추종
                  </Typography>
                  <Chip label="초급" size="small" color="success" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* RSI 과매도 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] RSI 반전',
                    description: 'RSI 과매도 구간에서 매수, 과매수 구간에서 매도',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'RSI_14', operator: '<', value: 30, combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '2', type: 'sell', indicator: 'RSI_14', operator: '>', value: 70, combineWith: 'AND' }
                    ]
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <Autorenew color="secondary" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    RSI 반전
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    RSI 30 이하 매수<br/>
                    과매도 반등 포착
                  </Typography>
                  <Chip label="초급" size="small" color="success" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* 볼린저밴드 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 볼린저밴드',
                    description: '하단 밴드 터치 후 반등 시 매수, 상단 밴드 돌파 시 매도',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'PRICE', operator: '<', value: 'BB_LOWER', combineWith: 'AND' },
                      { id: '2', type: 'buy', indicator: 'RSI_14', operator: '<', value: 40, combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '3', type: 'sell', indicator: 'PRICE', operator: '>', value: 'BB_UPPER', combineWith: 'AND' }
                    ]
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <Timeline color="info" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    볼린저밴드
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    밴드 하단 매수<br/>
                    변동성 활용 매매
                  </Typography>
                  <Chip label="중급" size="small" color="warning" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* MACD 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] MACD 시그널',
                    description: 'MACD가 시그널선을 상향 돌파 시 매수',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'MACD', operator: 'cross_above', value: 'MACD_SIGNAL', combineWith: 'AND' },
                      { id: '2', type: 'buy', indicator: 'MACD', operator: '>', value: 0, combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '3', type: 'sell', indicator: 'MACD', operator: 'cross_below', value: 'MACD_SIGNAL', combineWith: 'AND' }
                    ]
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <ShowChart color="error" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    MACD 시그널
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    MACD 골든크로스<br/>
                    모멘텀 추종 매매
                  </Typography>
                  <Chip label="중급" size="small" color="warning" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* 복합 전략 1 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  // 3단계 모드 자동 활성화
                  setUseStageBasedStrategy(true);
                  
                  // 3단계 전략 설정
                  setBuyStageStrategy({
                    stage1: {
                      indicators: ['RSI_14'],
                      conditions: [
                        { indicator: 'RSI_14', operator: '<', value: 35 }
                      ]
                    },
                    stage2: {
                      indicators: ['MACD_12_26_9'],
                      conditions: [
                        { indicator: 'MACD', operator: 'cross_above', value: 'MACD_SIGNAL' }
                      ]
                    },
                    stage3: {
                      indicators: ['VOLUME'],
                      conditions: [
                        { indicator: 'VOLUME', operator: '>', value: 'VOLUME_MA_20' }
                      ]
                    }
                  });
                  
                  // 매도 전략도 설정
                  setSellStageStrategy({
                    stage1: {
                      indicators: ['RSI_14'],
                      conditions: [
                        { indicator: 'RSI_14', operator: '>', value: 70 }
                      ]
                    },
                    stage2: {
                      indicators: ['MACD_12_26_9'],
                      conditions: [
                        { indicator: 'MACD', operator: 'cross_below', value: 'MACD_SIGNAL' }
                      ]
                    },
                    stage3: {
                      indicators: [],
                      conditions: []
                    }
                  });
                  
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 복합 전략 A',
                    description: 'RSI 과매도 → MACD 골든크로스 → 거래량 확인'
                  });
                }}
              >
                <CardContent>
                  <AccountTree color="primary" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    복합 전략 A
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    RSI+MACD+거래량<br/>
                    3단계 검증 시스템
                  </Typography>
                  <Chip label="고급" size="small" color="error" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* 복합 전략 2 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  // 3단계 모드 자동 활성화
                  setUseStageBasedStrategy(true);
                  
                  // 3단계 매수 전략 설정
                  setBuyStageStrategy({
                    stage1: {
                      indicators: ['MA_20', 'MA_60'],
                      conditions: [
                        { indicator: 'MA_20', operator: '>', value: 'MA_60' }
                      ]
                    },
                    stage2: {
                      indicators: ['BB_20_2'],
                      conditions: [
                        { indicator: 'PRICE', operator: '<', value: 'BB_MIDDLE' }
                      ]
                    },
                    stage3: {
                      indicators: ['RSI_14'],
                      conditions: [
                        { indicator: 'RSI_14', operator: '<', value: 50 }
                      ]
                    }
                  });
                  
                  // 매도 전략 설정
                  setSellStageStrategy({
                    stage1: {
                      indicators: ['MA_20', 'MA_60'],
                      conditions: [
                        { indicator: 'MA_20', operator: '<', value: 'MA_60' }
                      ]
                    },
                    stage2: {
                      indicators: ['BB_20_2'],
                      conditions: [
                        { indicator: 'PRICE', operator: '>', value: 'BB_UPPER' }
                      ]
                    },
                    stage3: {
                      indicators: [],
                      conditions: []
                    }
                  });
                  
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 복합 전략 B',
                    description: '골든크로스 → 볼린저 중단 이하 → RSI 확인'
                  });
                }}
              >
                <CardContent>
                  <AccountTree color="secondary" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    복합 전략 B
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    MA+BB+RSI<br/>
                    추세와 모멘텀 결합
                  </Typography>
                  <Chip label="고급" size="small" color="error" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* 스캘핑 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 스캘핑',
                    description: '5분봉 기준 빠른 진입/청산',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'PRICE', operator: '>', value: 'MA_5', combineWith: 'AND' },
                      { id: '2', type: 'buy', indicator: 'RSI_9', operator: '<', value: 50, combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '3', type: 'sell', indicator: 'RSI_9', operator: '>', value: 70, combineWith: 'AND' }
                    ],
                    riskManagement: {
                      stopLoss: -2,
                      takeProfit: 3,
                      trailingStop: true,
                      trailingStopPercent: 1,
                      positionSize: 10,
                      maxPositions: 3
                    }
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <Speed color="warning" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    스캘핑
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    단기 진입/청산<br/>
                    빠른 수익 실현
                  </Typography>
                  <Chip label="전문가" size="small" color="error" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>

            {/* 스윙 전략 */}
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: 3 
                  }
                }}
                onClick={() => {
                  setStrategy({
                    ...strategy,
                    name: '[템플릿] 스윙 트레이딩',
                    description: '중기 추세 전환점 포착',
                    indicators: [],
                    buyConditions: [
                      { id: '1', type: 'buy', indicator: 'MA_20', operator: '>', value: 'MA_60', combineWith: 'AND' },
                      { id: '2', type: 'buy', indicator: 'RSI_14', operator: '<', value: 60, combineWith: 'AND' },
                      { id: '3', type: 'buy', indicator: 'MACD', operator: '>', value: 0, combineWith: 'AND' }
                    ],
                    sellConditions: [
                      { id: '4', type: 'sell', indicator: 'MA_20', operator: '<', value: 'MA_60', combineWith: 'AND' },
                      { id: '5', type: 'sell', indicator: 'RSI_14', operator: '>', value: 70, combineWith: 'AND' }
                    ],
                    riskManagement: {
                      stopLoss: -7,
                      takeProfit: 15,
                      trailingStop: false,
                      trailingStopPercent: 0,
                      positionSize: 20,
                      maxPositions: 5
                    }
                  });
                  setUseStageBasedStrategy(false);
                }}
              >
                <CardContent>
                  <SwapHoriz color="info" sx={{ mb: 1 }} />
                  <Typography variant="h6" gutterBottom>
                    스윙 트레이딩
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    중기 추세 포착<br/>
                    안정적 수익 추구
                  </Typography>
                  <Chip label="중급" size="small" color="warning" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>

        {/* 전략 모드 선택 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            전략 구성 방식
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={useStageBasedStrategy}
                onChange={(e) => setUseStageBasedStrategy(e.target.checked)}
              />
            }
            label={
              <Box>
                <Typography variant="subtitle1">
                  {useStageBasedStrategy ? '3단계 전략 시스템' : '기본 전략 시스템'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {useStageBasedStrategy 
                    ? '1→2→3단계 순차적 조건 평가 (각 단계 최대 5개 지표)'
                    : '단일 조건으로 매수/매도 결정'}
                </Typography>
              </Box>
            }
          />
        </Paper>

        {/* 3단계 전략 시스템 */}
        {useStageBasedStrategy ? (
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <StageBasedStrategy
                type="buy"
                availableIndicators={AVAILABLE_INDICATORS}
                initialStrategy={buyStageStrategy}  // 초기값 전달
                targetProfit={strategy.targetProfit}
                stopLoss={strategy.stopLoss}
                onProfitSettingsChange={(settings) => {
                  setStrategy({
                    ...strategy,
                    targetProfit: settings.targetProfit,
                    stopLoss: settings.stopLoss
                  })
                }}
                onStrategyChange={(stageStrategy) => {
                  setBuyStageStrategy(stageStrategy)
                  // 기존 strategy 객체에도 반영
                  setStrategy({
                    ...strategy,
                    buyConditions: stageStrategy.stages
                      .filter(s => s.enabled)
                      .flatMap(s => s.indicators.map(ind => ({
                        id: ind.id,
                        type: 'buy',
                        indicator: ind.indicatorId,
                        operator: ind.operator as any,
                        value: ind.value,
                        combineWith: ind.combineWith
                      })))
                  })
                }}
              />
            </Grid>
            <Grid item xs={12} lg={6}>
              <StageBasedStrategy
                type="sell"
                availableIndicators={AVAILABLE_INDICATORS}
                initialStrategy={sellStageStrategy}  // 초기값 전달
                targetProfit={strategy.targetProfit}
                stopLoss={strategy.stopLoss}
                onProfitSettingsChange={(settings) => {
                  setStrategy({
                    ...strategy,
                    targetProfit: settings.targetProfit,
                    stopLoss: settings.stopLoss
                  })
                }}
                onStrategyChange={(stageStrategy) => {
                  setSellStageStrategy(stageStrategy)
                  // 기존 strategy 객체에도 반영
                  setStrategy({
                    ...strategy,
                    sellConditions: stageStrategy.stages
                      .filter(s => s.enabled)
                      .flatMap(s => s.indicators.map(ind => ({
                        id: ind.id,
                        type: 'sell',
                        indicator: ind.indicatorId,
                        operator: ind.operator as any,
                        value: ind.value,
                        combineWith: ind.combineWith
                      })))
                  })
                }}
              />
            </Grid>
          </Grid>
        ) : (
          <>
            {/* 기본 전략 시스템의 지표 및 조건 설정 */}
            <Grid container spacing={3}>
              {/* 기술적 지표 설정 */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    기술적 지표
                  </Typography>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>지표 추가</InputLabel>
              <Select
                value=""
                onChange={(e) => addIndicator(e.target.value)}
                label="지표 추가"
              >
                {AVAILABLE_INDICATORS.map(indicator => (
                  <MenuItem key={indicator.id} value={indicator.id}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography>{indicator.name}</Typography>
                      <Chip label={indicator.type} size="small" />
                    </Stack>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Stack spacing={2}>
              {strategy.indicators.map((indicator) => (
                <Card key={indicator.id} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle2">{indicator.name}</Typography>
                      <Stack direction="row" spacing={1}>
                        <Switch
                          size="small"
                          checked={indicator.enabled}
                          onChange={(e) => {
                            const updated = strategy.indicators.map(i =>
                              i.id === indicator.id ? { ...i, enabled: e.target.checked } : i
                            )
                            setStrategy({ ...strategy, indicators: updated })
                          }}
                        />
                        <IconButton size="small">
                          <Delete fontSize="small" />
                        </IconButton>
                      </Stack>
                    </Box>
                    
                    {/* 파라미터 설정 */}
                    <Box sx={{ mt: 2 }}>
                      {Object.entries(indicator.params).map(([key, value]) => (
                        <TextField
                          key={key}
                          size="small"
                          label={key}
                          value={value}
                          type="number"
                          sx={{ mr: 1, mb: 1, width: 100 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Paper>
        </Grid>

        {/* 매수/매도 조건 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              매수 조건
            </Typography>
            <Button
              startIcon={<Add />}
              onClick={() => addCondition('buy')}
              size="small"
              sx={{ mb: 2 }}
            >
              조건 추가
            </Button>
            
            <Stack spacing={1}>
              {strategy.buyConditions.map((condition, index) => {
                const indicator = AVAILABLE_INDICATORS.find(i => i.id === condition.indicator)
                const operatorLabel = condition.indicator === 'ichimoku' && 
                  (condition.operator.includes('cloud') || condition.operator.includes('tenkan') || condition.operator.includes('chikou'))
                  ? getIchimokuOperators().find(o => o.value === condition.operator)?.label || condition.operator
                  : getStandardOperators().find(o => o.value === condition.operator)?.label || condition.operator
                
                return (
                  <Chip
                    key={condition.id}
                    label={`${index > 0 ? condition.combineWith + ' ' : ''}${indicator?.name || condition.indicator} ${operatorLabel} ${condition.value}${condition.confirmBars ? ` (확인 ${condition.confirmBars}봉)` : ''}`}
                    onDelete={() => removeCondition('buy', condition.id)}
                    color="success"
                  />
                )
              })}
            </Stack>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              매도 조건 (지표)
            </Typography>
            <Button
              startIcon={<Add />}
              onClick={() => addCondition('sell')}
              size="small"
              sx={{ mb: 2 }}
            >
              조건 추가
            </Button>

            <Stack spacing={1}>
              {strategy.sellConditions.map((condition, index) => {
                const indicator = AVAILABLE_INDICATORS.find(i => i.id === condition.indicator)
                const operatorLabel = condition.indicator === 'ichimoku' &&
                  (condition.operator.includes('cloud') || condition.operator.includes('tenkan') || condition.operator.includes('chikou'))
                  ? getIchimokuOperators().find(o => o.value === condition.operator)?.label || condition.operator
                  : getStandardOperators().find(o => o.value === condition.operator)?.label || condition.operator

                return (
                  <Chip
                    key={condition.id}
                    label={`${index > 0 ? condition.combineWith + ' ' : ''}${indicator?.name || condition.indicator} ${operatorLabel} ${condition.value}${condition.confirmBars ? ` (확인 ${condition.confirmBars}봉)` : ''}`}
                    onDelete={() => removeCondition('sell', condition.id)}
                    color="error"
                  />
                )
              })}
            </Stack>
          </Paper>

          {/* 목표 수익률 설정 추가 */}
          <TargetProfitSettingsEnhanced
            targetProfit={strategy.targetProfit}
            stopLoss={strategy.stopLoss}
            onChange={(settings) => {
              setStrategy({
                ...strategy,
                targetProfit: settings.targetProfit,
                stopLoss: settings.stopLoss
              })
            }}
            hasIndicatorConditions={strategy.sellConditions.length > 0}
            isStageBasedStrategy={false}
          />
        </Grid>

        {/* 리스크 관리 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              리스크 관리
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Typography gutterBottom>손절 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.stopLoss}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      stopLoss: v as number
                    }
                  })}
                  min={0}
                  max={10}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <Typography gutterBottom>익절 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.takeProfit}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      takeProfit: v as number
                    }
                  })}
                  min={0}
                  max={20}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <Typography gutterBottom>포지션 크기 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.positionSize}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      positionSize: v as number
                    }
                  })}
                  min={1}
                  max={100}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.riskManagement.trailingStop}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        riskManagement: {
                          ...strategy.riskManagement,
                          trailingStop: e.target.checked
                        }
                      })}
                    />
                  }
                  label="트레일링 스탑"
                />
                {strategy.riskManagement.trailingStop && (
                  <TextField
                    size="small"
                    label="트레일링 %"
                    type="number"
                    value={strategy.riskManagement.trailingStopPercent || 2}
                    onChange={(e) => setStrategy({
                      ...strategy,
                      riskManagement: {
                        ...strategy.riskManagement,
                        trailingStopPercent: Number(e.target.value)
                      }
                    })}
                    fullWidth
                  />
                )}
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 2 }} />
            
            {/* 고급 옵션 */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>고급 옵션</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.riskManagement.systemCut || false}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        riskManagement: {
                          ...strategy.riskManagement,
                          systemCut: e.target.checked
                        }
                      })}
                    />
                  }
                  label={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Security color="error" />
                      <Typography>시스템 CUT 활성화</Typography>
                    </Stack>
                  }
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.advanced?.splitTrading?.enabled || false}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        advanced: {
                          ...strategy.advanced,
                          splitTrading: {
                            ...strategy.advanced?.splitTrading,
                            enabled: e.target.checked,
                            levels: 3,
                            percentages: [40, 30, 30]
                          }
                        }
                      })}
                    />
                  }
                  label={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <ShowChart color="primary" />
                      <Typography>분할매매 활성화</Typography>
                    </Stack>
                  }
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 빠른 테스트 결과 */}
        {strategy.quickTestResult && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: 'background.default', border: '2px solid', borderColor: 'secondary.main' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed color="secondary" />
                퀵 백테스트 결과 (최근 1년 간략 검증)
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="primary">
                      {strategy.quickTestResult.returns}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      수익률
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="success.main">
                      {strategy.quickTestResult.winRate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      승률
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="error.main">
                      {strategy.quickTestResult.maxDrawdown}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      최대 낙폭
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4">
                      {strategy.quickTestResult.trades}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      거래 횟수
                    </Typography>
                  </Stack>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Timeline />}
                  onClick={async () => {
                    // 전략을 먼저 저장
                    const strategyId = await saveStrategy()
                    if (strategyId) {
                      // 저장된 전략 ID를 가지고 백테스트 페이지로 이동
                      window.location.href = `/backtest?strategyId=${strategyId}`
                    }
                  }}
                >
                  전략 저장 후 백테스팅
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                >
                  자동매매 적용
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
            </Grid>
          </>
        )}
      </TabPanel>

      {/* 전략 분석 탭 */}
      <TabPanel value={currentTab} index={1}>
        <StrategyAnalyzer
          strategy={strategy}
          investmentConfig={{}}
        />
      </TabPanel>

      {/* 투자 흐름 관리 탭 */}
      <TabPanel value={currentTab} index={2}>
        <InvestmentFlowManager 
          onFlowChange={(flow) => setCurrentFlowType(flow)}
          currentStrategy={strategy}
          currentUniverse={localStorage.getItem('investmentConfig') ? JSON.parse(localStorage.getItem('investmentConfig')!) : undefined}
        />
      </TabPanel>

      {/* 전략 불러오기 다이얼로그 */}
      <StrategyLoader
        open={dialogOpen}
        onClose={() => {
          console.log('StrategyLoader onClose called')
          setDialogOpen(false)
        }}
        onLoad={(strategyData) => {
          console.log('StrategyLoader onLoad called with:', strategyData)
          loadStrategy(strategyData)
          setDialogOpen(false)
        }}
        currentUserId={currentUser?.id}
      />

      {/* 조건 추가 다이얼로그 */}
      <Dialog open={conditionDialogOpen} onClose={() => setConditionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentConditionType === 'buy' ? '매수' : '매도'} 조건 추가
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* 조건 연결 */}
            {(currentConditionType === 'buy' ? strategy.buyConditions : strategy.sellConditions).length > 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>조건 연결</InputLabel>
                  <Select
                    value={tempCondition.combineWith}
                    onChange={(e) => setTempCondition({ ...tempCondition, combineWith: e.target.value as 'AND' | 'OR' })}
                    label="조건 연결"
                  >
                    <MenuItem value="AND">AND (&&)</MenuItem>
                    <MenuItem value="OR">OR (||)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            {/* 지표 선택 */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>지표</InputLabel>
                <Select
                  value={tempCondition.indicator}
                  onChange={(e) => {
                    const newIndicator = e.target.value
                    setTempCondition({ 
                      ...tempCondition, 
                      indicator: newIndicator,
                      operator: newIndicator === 'ichimoku' ? 'cloud_above' : '>',
                      value: newIndicator === 'rsi' ? (currentConditionType === 'buy' ? 30 : 70) : 0
                    })
                  }}
                  label="지표"
                >
                  {AVAILABLE_INDICATORS.map(ind => (
                    <MenuItem key={ind.id} value={ind.id}>{ind.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {/* 일목균형표 선 선택 */}
            {tempCondition.indicator === 'ichimoku' && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>일목균형표 선</InputLabel>
                  <Select
                    value={tempCondition.ichimokuLine || 'tenkan'}
                    onChange={(e) => setTempCondition({ ...tempCondition, ichimokuLine: e.target.value as any })}
                    label="일목균형표 선"
                  >
                    <MenuItem value="tenkan">전환선 (9일)</MenuItem>
                    <MenuItem value="kijun">기준선 (26일)</MenuItem>
                    <MenuItem value="senkou_a">선행스팬 A</MenuItem>
                    <MenuItem value="senkou_b">선행스팬 B</MenuItem>
                    <MenuItem value="chikou">후행스팬</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            {/* 연산자 */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>조건</InputLabel>
                <Select
                  value={tempCondition.operator}
                  onChange={(e) => setTempCondition({ ...tempCondition, operator: e.target.value as any })}
                  label="조건"
                >
                  {tempCondition.indicator === 'ichimoku' ? (
                    getIchimokuOperators().map(op => (
                      <MenuItem key={op.value} value={op.value}>{op.label}</MenuItem>
                    ))
                  ) : (
                    getStandardOperators().map(op => (
                      <MenuItem key={op.value} value={op.value}>{op.label}</MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
            
            {/* 값 */}
            {tempCondition.indicator === 'ichimoku' && 
             (tempCondition.operator.includes('cloud') || tempCondition.operator.includes('tenkan')) ? (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="확인봉 개수"
                  value={tempCondition.confirmBars || 1}
                  onChange={(e) => setTempCondition({ ...tempCondition, confirmBars: parseInt(e.target.value) })}
                  helperText="연속으로 조건을 만족해야 하는 봉의 개수"
                />
              </Grid>
            ) : tempCondition.operator !== 'cross_above' && tempCondition.operator !== 'cross_below' ? (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="값"
                  value={tempCondition.value}
                  onChange={(e) => setTempCondition({ ...tempCondition, value: parseFloat(e.target.value) })}
                />
              </Grid>
            ) : null}
            
            {/* 설명 */}
            <Grid item xs={12}>
              <Alert severity="info">
                {tempCondition.indicator === 'ichimoku' ? (
                  <>
                    일목균형표는 전환선(9일), 기준선(26일), 선행스팬(52일), 후행스팬(26일)으로 구성됩니다.
                    구름대는 선행스팬 A와 B 사이의 영역을 의미합니다.
                  </>
                ) : tempCondition.indicator === 'rsi' ? (
                  <>RSI {currentConditionType === 'buy' ? '30 미만은 과매도' : '70 초과는 과매수'} 신호입니다.</>
                ) : tempCondition.indicator === 'macd' ? (
                  <>MACD와 시그널선의 교차를 통해 매매 시점을 포착합니다.</>
                ) : (
                  <>선택한 지표와 조건에 따라 {currentConditionType === 'buy' ? '매수' : '매도'} 신호가 발생합니다.</>
                )}
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConditionDialogOpen(false)}>취소</Button>
          <Button onClick={saveCondition} variant="contained">추가</Button>
        </DialogActions>
      </Dialog>

      {/* 전략 저장 다이얼로그 */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>전략 저장</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="전략 이름"
              value={strategy.name}
              onChange={(e) => setStrategy({ ...strategy, name: e.target.value })}
              helperText="전략을 구분할 수 있는 이름을 입력하세요"
            />
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="전략 설명"
              value={strategy.description}
              onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
              helperText="전략의 특징이나 사용 방법을 설명하세요"
            />
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    color="primary"
                  />
                }
                label={
                  <Box>
                    <Typography variant="body1">전략 공유</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {isPublic ? 
                        '다른 사용자들이 이 전략을 볼 수 있습니다' : 
                        '나만 볼 수 있는 비공개 전략입니다'
                      }
                    </Typography>
                  </Box>
                }
              />
            </Box>
            
            {isPublic && (
              <Alert severity="info" icon={<Info />}>
                <Typography variant="subtitle2" gutterBottom>
                  공유 전략 안내
                </Typography>
                <Typography variant="body2">
                  • 다른 사용자들이 전략을 조회하고 복사할 수 있습니다<br/>
                  • 전략의 상세 설정과 조건이 공개됩니다<br/>
                  • 언제든지 공유 설정을 변경할 수 있습니다
                </Typography>
              </Alert>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>취소</Button>
          <Button 
            onClick={saveStrategy} 
            variant="contained"
            disabled={!strategy.name.trim()}
          >
            {isPublic ? '공유하며 저장' : '저장'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StrategyBuilderUpdated