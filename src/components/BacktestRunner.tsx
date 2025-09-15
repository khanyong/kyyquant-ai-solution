import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tabs,
  Tab,
} from '@mui/material';
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
// import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
// import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
// import { ko } from 'date-fns/locale';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HistoryIcon from '@mui/icons-material/History';
import CloseIcon from '@mui/icons-material/Close';
import { BacktestService } from '../services/backtestService';
import { supabase } from '../lib/supabase';
import { authService } from '../services/auth';
import { Link } from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import FilteringStrategy from './FilteringStrategy';
import { FilteringMode, FilterRules } from '../types/filteringMode';
import LoadFilterDialog from './LoadFilterDialog';
import { stockDataService } from '../services/stockDataService';
import BacktestResultViewer from './backtest/BacktestResultViewer';
import BacktestComparison from './backtest/BacktestComparison';
import { backtestStorageService } from '../services/backtestStorage';
import SaveIcon from '@mui/icons-material/Save';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import { STRATEGY_TEMPLATES } from '../constants/strategyTemplates';
import StyleIcon from '@mui/icons-material/Style';

interface Strategy {
  id: string;
  name: string;
  description: string;
  type: string;
  parameters: any;
  created_at?: string;
}

interface BacktestConfig {
  strategyId: string;
  startDate: Date | null;
  endDate: Date | null;
  initialCapital: number;
  commission: number;
  slippage: number;
  dataInterval: string;
  stockCodes: string[];
  filteringMode?: FilteringMode;
}

const BacktestRunner: React.FC = () => {
  const navigate = useNavigate();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [backtestId, setBacktestId] = useState<string | null>(null);
  const [backtestResults, setBacktestResults] = useState<any>(null);
  const [currentFilters, setCurrentFilters] = useState<FilterRules | undefined>(undefined);
  const [filteringMode, setFilteringMode] = useState<FilteringMode | undefined>(undefined);
  const [showLoadFilterDialog, setShowLoadFilterDialog] = useState(false);
  const [currentFilterId, setCurrentFilterId] = useState<string | null>(null);
  const [showResultDialog, setShowResultDialog] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedResultId, setSavedResultId] = useState<string | null>(null);
  const [currentSubTab, setCurrentSubTab] = useState(0); // 0: 백테스트 실행, 1: 결과 보기
  const [showTemplateDialog, setShowTemplateDialog] = useState(false); // 템플릿 선택 다이얼로그
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  
  const [config, setConfig] = useState<BacktestConfig>({
    strategyId: '',
    startDate: new Date('2024-09-14'),  // 데이터 시작일
    endDate: new Date('2025-09-12'),    // 데이터 종료일
    initialCapital: 10000000,
    commission: 0.00015,
    slippage: 0.001,
    dataInterval: '1d',
    stockCodes: [],
    filteringMode: undefined,
  });

  // 전략 목록 로드 및 URL 파라미터 처리
  React.useEffect(() => {
    console.log('BacktestRunner component mounted');
    loadStrategies();
    
    // URL에서 strategyId 파라미터 가져오기
    const urlParams = new URLSearchParams(window.location.search);
    const strategyIdFromUrl = urlParams.get('strategyId');
    if (strategyIdFromUrl) {
      console.log('Strategy ID from URL:', strategyIdFromUrl);
      setConfig(prev => ({ ...prev, strategyId: strategyIdFromUrl }));
    }
    
    // 투자설정에서 선택된 종목 가져오기 (옵션)
    // 자동 로드를 원하지 않으면 아래 코드를 주석 처리하거나
    // 사용자가 명시적으로 요청할 때만 로드하도록 변경
    const autoLoadStocks = false; // 자동 로드 비활성화
    if (autoLoadStocks) {
      const stockCodes = loadInvestmentUniverse();
      if (stockCodes && stockCodes.length > 0) {
        console.log('Setting initial stock codes:', stockCodes);
        setConfig(prev => ({ ...prev, stockCodes }));
      }
    }
  }, []);

  const loadStrategies = async () => {
    try {
      console.log('Loading strategies...');
      // 현재 사용자 가져오기
      const user = await authService.getCurrentUser();
      console.log('Current user:', user);
      
      if (!user) {
        console.warn('User not logged in, attempting to load all strategies');
        // 로그인하지 않은 경우에도 전략 로드 시도 (테스트용)
        const { data, error } = await supabase
          .from('strategies')
          .select('*')
          .eq('is_active', true)
          .order('created_at', { ascending: false });
        
        console.log('All strategies query result:', { data, error });
        
        if (error) {
          console.error('Error loading all strategies:', error);
          setStrategies([]);
          return;
        }
        
        // 전략 데이터 형식 변환
        const formattedStrategies = data?.map(s => ({
          id: s.id,
          name: s.name,
          description: s.description || '',
          type: s.config?.strategy_type || s.type || 'custom',
          parameters: s.config || s.parameters || {},
          created_at: s.created_at
        })) || [];
        
        console.log('Formatted all strategies:', formattedStrategies);
        setStrategies(formattedStrategies);
        return;
      }

      // 개발 모드: 모든 사용자의 전략을 로드
      // 프로덕션에서는 .eq('user_id', user.id) 추가 필요
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        // .eq('user_id', user.id)  // 개발 중 주석 처리 - 모든 사용자 전략 조회
        .eq('is_active', true)
        .order('created_at', { ascending: false });
      
      console.log('User strategies query result:', { data, error });
      
      if (error) {
        console.error('Error loading user strategies:', error);
        // user_id 필터 없이 다시 시도
        console.log('Retrying without user_id filter...');
        const { data: allData, error: allError } = await supabase
          .from('strategies')
          .select('*')
          .eq('is_active', true)
          .order('created_at', { ascending: false });
        
        if (allError) {
          console.error('Error loading all strategies:', allError);
          throw allError;
        }
        
        console.log('All strategies (fallback):', allData);
        
        const formattedStrategies = allData?.map(s => ({
          id: s.id,
          name: s.name,
          description: s.description || '',
          type: s.config?.strategy_type || s.type || 'custom',
          parameters: s.config || s.parameters || {},
          created_at: s.created_at
        })) || [];
        
        setStrategies(formattedStrategies);
        return;
      }
      
      // 전략 데이터 형식 변환 (config 컬럼 사용)
      const formattedStrategies = data?.map(s => ({
        id: s.id,
        name: s.name,
        description: s.description || '',
        type: s.config?.strategy_type || s.type || 'custom',  // config 내 strategy_type 사용
        config: s.config || {},  // config 필드 추가
        parameters: s.config || s.parameters || {},  // config 컬럼 우선 사용
        created_at: s.created_at,
        user_id: s.user_id,  // 사용자 ID 추가
        isOwn: s.user_id === user.id  // 자신의 전략인지 표시
      })) || [];
      
      console.log('Formatted strategies:', formattedStrategies);
      setStrategies(formattedStrategies);
      
      // URL에 strategyId가 있으면 해당 전략 선택
      const urlParams = new URLSearchParams(window.location.search);
      const strategyIdFromUrl = urlParams.get('strategyId');
      if (strategyIdFromUrl && formattedStrategies.some(s => s.id === strategyIdFromUrl)) {
        setConfig(prev => ({ ...prev, strategyId: strategyIdFromUrl }));
      }
    } catch (err) {
      console.error('전략 로드 실패:', err);
      setError('전략 목록을 불러올 수 없습니다.');
    }
  };

  // 투자설정에서 선택된 종목 가져오기
  const loadInvestmentUniverse = () => {
    try {
      const investmentConfig = localStorage.getItem('investmentConfig');
      if (investmentConfig) {
        const config = JSON.parse(investmentConfig);
        console.log('Investment config loaded:', config);
        console.log('Universe data:', config.universe);
        
        // 필터링된 종목이 있으면 우선 사용
        if (config.universe?.filteredStocks && config.universe.filteredStocks.length > 0) {
          console.log('Found filteredStocks:', config.universe.filteredStocks.length, 'stocks');
          console.log('First filtered stock structure:', config.universe.filteredStocks[0]); // 첫 번째 항목 구조 확인
          
          // stock_code, code, 또는 symbol 등 다양한 필드명 지원
          const stockCodes = config.universe.filteredStocks.map((stock: any) => {
            // 객체인 경우 속성에서 코드 추출
            if (typeof stock === 'object' && stock !== null) {
              return stock.code || stock.stock_code || stock.symbol || String(stock);
            }
            // 문자열인 경우 그대로 사용
            return String(stock);
          }).filter((code: any) => {
            // 유효한 문자열이고 '[object Object]'가 아닌 경우만 포함
            return code && 
                   typeof code === 'string' && 
                   code.trim() !== '' &&
                   code !== '[object Object]' &&
                   code !== 'undefined' &&
                   code !== 'null';
          }).map((code: any) => String(code).trim());
          
          console.log('Extracted stock codes from filteredStocks:', stockCodes);
          
          if (stockCodes.length > 0) {
            setSuccess(`필터링된 ${stockCodes.length}개 종목을 로드했습니다.`);
            
            // 필터 설정도 로드
            if (config.universe?.filters) {
              setCurrentFilters(config.universe.filters);
              console.log('Loaded filter settings:', config.universe.filters);
            }
            
            return stockCodes;
          } else {
            console.warn('No valid stock codes found in filteredStocks');
            console.warn('FilteredStocks array:', config.universe.filteredStocks);
          }
        }
        // 선택된 종목 코드 추출 (필터링 전)
        else if (config.universe?.selectedStocks && config.universe.selectedStocks.length > 0) {
          console.log('Selected stocks data:', config.universe.selectedStocks[0]); // 첫 번째 항목 구조 확인
          
          const stockCodes = config.universe.selectedStocks.map((stock: any) => {
            // 객체인 경우 속성에서 코드 추출
            if (typeof stock === 'object' && stock !== null) {
              return stock.code || stock.stock_code || stock.symbol || String(stock);
            }
            // 문자열인 경우 그대로 사용
            return String(stock);
          }).filter((code: any) => {
            // 유효한 문자열이고 '[object Object]'가 아닌 경우만 포함
            return code && 
                   typeof code === 'string' && 
                   code.trim() !== '' &&
                   code !== '[object Object]' &&
                   code !== 'undefined' &&
                   code !== 'null';
          }).map((code: any) => String(code).trim());
          
          console.log('Selected stock codes from investment settings:', stockCodes);
          
          if (stockCodes.length > 0) {
            return stockCodes;
          }
        }
        
        // 필터 설정도 로드
        if (config.universe?.filters) {
          setCurrentFilters(config.universe.filters);
        }
      }
    } catch (error) {
      console.error('Error loading investment universe:', error);
    }
    return [];
  }

  // 투자설정 종목을 백테스트 설정에 적용
  const applyInvestmentUniverse = () => {
    // LoadFilterDialog를 열어서 저장된 필터 목록을 보여줌
    setShowLoadFilterDialog(true);
  }

  // 선택한 필터를 적용하는 함수
  const handleFilterLoad = (filterData: any) => {
    try {
      console.log('Loading filter data:', filterData);
      console.log('Filter ID from filterData:', filterData.id);
      console.log('Current filteringMode state:', filteringMode);
      
      // SavedFilter 형식의 데이터 처리
      if (filterData.filtered_stocks && filterData.filtered_stocks.length > 0) {
        // Supabase에서 가져온 데이터 (filtered_stocks 필드)
        const stockCodes = filterData.filtered_stocks.map((stock: any) => {
          if (typeof stock === 'string') {
            return stock;
          }
          // 객체인 경우 속성에서 코드 추출
          if (typeof stock === 'object' && stock !== null) {
            return stock.code || stock.stock_code || stock.symbol || String(stock);
          }
          return String(stock);
        }).filter((code: any) => {
          // 유효한 문자열이고 '[object Object]'가 아닌 경우만 포함
          return code && 
                 typeof code === 'string' && 
                 code.trim() !== '' &&
                 code !== '[object Object]' &&
                 code !== 'undefined' &&
                 code !== 'null';
        }).map((code: any) => String(code).trim());
        
        if (stockCodes.length > 0) {
          console.log('Filter ID:', filterData.id);
          console.log('Filtering mode:', filteringMode);
          
          // 필터 ID는 항상 저장
          setCurrentFilterId(filterData.id || null);
          setCurrentFilters(filterData.filters);
          
          // 사전 필터링 모드가 아닌 경우에만 stockCodes 설정
          const currentMode = typeof filteringMode === 'object' ? filteringMode?.mode : filteringMode;
          if (currentMode !== 'pre-filter') {
            console.log('Setting stock codes:', stockCodes);
            setConfig(prev => ({ ...prev, stockCodes }));
          } else {
            console.log('Pre-filter mode: not setting stock codes, will use filter_id');
            // 사전 필터링 모드에서는 stockCodes를 비움
            setConfig(prev => ({ ...prev, stockCodes: [] }));
          }
          
          const filterTypes = [];
          if (filterData.filters?.valuation) filterTypes.push('가치지표');
          if (filterData.filters?.financial) filterTypes.push('재무지표');
          if (filterData.filters?.sector) filterTypes.push('섹터');
          if (filterData.filters?.investor) filterTypes.push('투자자동향');
          
          setSuccess(`"${filterData.name}" 필터를 적용했습니다. ${stockCodes.length}개 종목이 선택되었습니다. (필터: ${filterTypes.join(', ')})`);
        } else {
          setError('필터에 유효한 종목 코드가 없습니다.');
        }
      } else if (filterData.filteredStocks && filterData.filteredStocks.length > 0) {
        // 로컬 스토리지에서 가져온 데이터 (filteredStocks 필드)
        const stockCodes = filterData.filteredStocks.map((stock: any) => {
          if (typeof stock === 'string') {
            return stock;
          }
          // 객체인 경우 속성에서 코드 추출
          if (typeof stock === 'object' && stock !== null) {
            return stock.code || stock.stock_code || stock.symbol || String(stock);
          }
          return String(stock);
        }).filter((code: any) => {
          // 유효한 문자열이고 '[object Object]'가 아닌 경우만 포함
          return code && 
                 typeof code === 'string' && 
                 code.trim() !== '' &&
                 code !== '[object Object]' &&
                 code !== 'undefined' &&
                 code !== 'null';
        }).map((code: any) => String(code).trim());
        
        if (stockCodes.length > 0) {
          console.log('Setting stock codes (local):', stockCodes);
          setConfig(prev => ({ ...prev, stockCodes }));
          setCurrentFilterId(filterData.id || null);
          
          // 필터 설정도 로드
          if (filterData.filters) {
            setCurrentFilters(filterData.filters);
            
            const filterTypes = [];
            if (filterData.filters.valuation) filterTypes.push('가치지표');
            if (filterData.filters.financial) filterTypes.push('재무지표');
            if (filterData.filters.sector) filterTypes.push('섹터');
            if (filterData.filters.investor) filterTypes.push('투자자동향');
            
            setSuccess(`"${filterData.name}" 필터를 적용했습니다. ${stockCodes.length}개 종목이 선택되었습니다. (필터: ${filterTypes.join(', ')})`);
          } else {
            setSuccess(`"${filterData.name}" 필터를 적용했습니다. ${stockCodes.length}개 종목이 선택되었습니다.`);
          }
        } else {
          setError('필터에 유효한 종목 코드가 없습니다.');
        }
      } else {
        setError('선택한 필터에 종목 데이터가 없습니다.');
      }
      setShowLoadFilterDialog(false);
    } catch (error) {
      console.error('필터 로드 중 오류:', error);
      setError('필터를 불러오는 중 오류가 발생했습니다.');
    }
  }

  // 템플릿 적용 함수
  const applyTemplate = async (template: any) => {
    try {
      // 템플릿을 임시 전략으로 저장
      const user = await authService.getCurrentUser();
      if (!user) {
        setError('로그인이 필요합니다.');
        return;
      }

      // 전략 데이터 구성
      // template.name이 이미 [템플릿]을 포함하고 있는지 확인
      const templateStrategyName = template.name.startsWith('[템플릿]')
        ? template.name
        : `[템플릿] ${template.name}`;
      const strategyData = {
        name: templateStrategyName,
        description: template.description,
        type: template.type === 'complex' ? 'stage_based' : 'custom',
        config: template.type === 'complex' 
          ? {
              buyStageStrategy: template.stageStrategy.buyStages,
              sellStageStrategy: template.stageStrategy.sellStages,
              isStageBasedStrategy: true,
              templateId: template.id,  // 템플릿 ID 저장
              templateName: template.name  // 템플릿 이름 저장
            }
          : {
              indicators: template.strategy.indicators,
              buyConditions: template.strategy.buyConditions,
              sellConditions: template.strategy.sellConditions,
              riskManagement: template.strategy.riskManagement || {
                stopLoss: -5,
                takeProfit: 10,
                trailingStop: false,
                trailingStopPercent: 0,
                positionSize: 20,
                maxPositions: 5
              },
              templateId: template.id,  // 템플릿 ID 저장
              templateName: template.name,  // 템플릿 이름 저장
              strategy_type: template.type === 'complex' ? 'stage_based' : 'custom'
            },
        user_id: user.id,
        is_active: true
      };

      console.log('Saving template strategy:', strategyData);

      // Supabase에 임시 저장
      const { data, error } = await supabase
        .from('strategies')
        .insert([strategyData])
        .select()
        .single();

      if (error) {
        console.error('템플릿 저장 오류:', error);
        setError('템플릿 적용 중 오류가 발생했습니다.');
        return;
      }

      console.log('Template strategy saved:', data);

      // 저장된 전략을 strategies 배열에 즉시 추가
      const newStrategy = {
        id: data.id,
        name: templateStrategyName,
        description: data.description || '',
        type: data.config?.strategy_type || data.type || 'custom',
        parameters: data.config || {},
        created_at: data.created_at
      };
      
      // strategies 배열에 새 전략 추가
      setStrategies(prev => [...prev, newStrategy]);
      
      // 저장된 전략 ID로 설정
      setConfig(prev => ({ ...prev, strategyId: data.id }));
      
      // 전략 목록 새로고침 (비동기로 실행)
      setTimeout(() => loadStrategies(), 100);
      
      // 다이얼로그 닫기
      setShowTemplateDialog(false);
      setSelectedTemplate(null);
      
      // 성공 메시지 표시
      setSuccess(`"${template.name}" 템플릿이 적용되었습니다. 이제 백테스트를 실행할 수 있습니다.`);
    } catch (error) {
      console.error('템플릿 적용 오류:', error);
      setError('템플릿 적용 중 오류가 발생했습니다.');
    }
  };

  const runBacktest = async () => {
    if (!config.strategyId || !config.startDate || !config.endDate) {
      setError('필수 항목을 모두 입력해주세요.');
      return;
    }

    setIsRunning(true);
    setError(null);
    setSuccess(null);
    setProgress(0);

    try {
      // 종목 코드 유효성 검증
      const validStockCodes = config.stockCodes
        ?.filter(code => code && 
                        typeof code === 'string' && 
                        code.trim() !== '' &&
                        code !== '[object Object]' &&
                        code !== 'undefined' &&
                        code !== 'null')
        ?.map(code => String(code).trim()) || [];

      console.log('Valid stock codes for backtest:', validStockCodes);
      
      // 원본 종목 코드와 유효한 종목 코드 비교 로그
      if (config.stockCodes.length !== validStockCodes.length) {
        console.warn(`Filtered out ${config.stockCodes.length - validStockCodes.length} invalid stock codes`);
        console.warn('Original stock codes:', config.stockCodes);
        console.warn('Valid stock codes:', validStockCodes);
      }
      
      // 종목 코드가 있는 경우, 3-tier 데이터 소싱 전략으로 데이터 미리 로드
      if (validStockCodes && validStockCodes.length > 0) {
        console.log('Pre-loading stock data using 3-tier strategy...');
        setProgress(10);
        
        const startDateStr = config.startDate.toISOString().split('T')[0];
        const endDateStr = config.endDate.toISOString().split('T')[0];
        
        // 3-tier 전략으로 데이터 로드 (로컬 → Supabase → API)
        const stockData = await stockDataService.getStockData(
          validStockCodes,
          startDateStr,
          endDateStr
        );
        
        const loadedCount = Object.keys(stockData).length;
        console.log(`Loaded data for ${loadedCount}/${validStockCodes.length} stocks`);
        
        if (loadedCount === 0) {
          throw new Error('종목 데이터를 불러올 수 없습니다. 종목 코드를 확인해주세요.');
        } else if (loadedCount < validStockCodes.length) {
          console.warn(`Some stocks have no data: ${validStockCodes.filter(code => !stockData[code]).join(', ')}`);
        }
        
        setProgress(20);
      }

      // 백테스트 실행 요청 준비
      // 선택된 전략의 파라미터 가져오기
      const selectedStrategy = strategies.find(s => s.id === config.strategyId);

      if (!selectedStrategy) {
        console.error('🛑 오류: 선택한 전략을 찾을 수 없습니다!');
        console.error('Strategy ID:', config.strategyId);
        console.error('Available strategies:', strategies.map(s => ({ id: s.id, name: s.name })));
        setError('선택한 전략을 찾을 수 없습니다. 전략 목록을 다시 불러오거나 다른 전략을 선택해주세요.');
        setIsRunning(false);
        return;
      }

      // config 필드에서 파라미터를 가져옴 (parameters가 없을 경우 대비)
      const strategyConfig = selectedStrategy.config || selectedStrategy.parameters || {};

      console.log('Selected strategy:', selectedStrategy);
      console.log('Strategy config:', strategyConfig);

      // 디버깅: 매수/매도 조건 상세 확인
      console.log('=== Strategy Conditions Debug ===');
      console.log('Buy Conditions:', strategyConfig.buyConditions);
      console.log('Sell Conditions:', strategyConfig.sellConditions);
      console.log('Target Profit:', strategyConfig.targetProfit);
      console.log('Stop Loss:', strategyConfig.stopLoss);
      console.log('Stop Loss Old:', strategyConfig.stopLossOld);
      console.log('Buy Stage Strategy:', strategyConfig.buyStageStrategy);
      console.log('Sell Stage Strategy:', strategyConfig.sellStageStrategy);
      console.log('Use Stage Based:', strategyConfig.useStageBasedStrategy);
      console.log('================================');

      // 서버가 strategy['config']에서 직접 조건을 읽으므로 parameters를 사용하지 않음
      const requestPayload: any = {
        strategy_id: config.strategyId,
        start_date: config.startDate.toISOString().split('T')[0],
        end_date: config.endDate.toISOString().split('T')[0],
        initial_capital: config.initialCapital,
        commission: config.commission,
        slippage: config.slippage,
        data_interval: config.dataInterval,
        filtering_mode: typeof config.filteringMode === 'object' ? config.filteringMode.mode : config.filteringMode,
        use_cached_data: true  // 캐시된 데이터 사용 플래그
      };

      // 서버가 DB에서 전략을 로드하므로, DB에 저장된 데이터가 올바른지 확인하기 위해
      // 클라이언트에서도 전략 config를 확인
      console.log('⚠️ 중요: 서버는 DB에 저장된 strategy.config를 사용합니다!');
      console.log('DB에 저장된 config에 매수/매도 조건이 있는지 확인하세요:');
      console.log('- buyConditions:', strategyConfig.buyConditions);
      console.log('- sellConditions:', strategyConfig.sellConditions);
      console.log('- buyStageStrategy:', strategyConfig.buyStageStrategy);
      console.log('- sellStageStrategy:', strategyConfig.sellStageStrategy);
      console.log('- useStageBasedStrategy:', strategyConfig.useStageBasedStrategy);

      // 만약 DB에 조건이 없다면 경고
      if (!strategyConfig || Object.keys(strategyConfig).length === 0) {
        console.error('🛑 오류: 전략 설정이 비어있습니다!');
        console.error('Strategy config is empty:', strategyConfig);
        setError('선택한 전략에 설정이 없습니다. 전략을 다시 저장해주세요.');
        setIsRunning(false);
        return;
      }

      if (!strategyConfig.buyConditions?.length &&
          !strategyConfig.buyStageStrategy?.stages?.some((s: any) => s.enabled)) {
        console.error('🛑 오류: DB에 저장된 전략에 매수 조건이 없습니다!');
        console.error('전략을 다시 저장하거나, 전략 빌더에서 조건을 설정한 후 저장하세요.');
        setError('선택한 전략에 매수 조건이 없습니다. 전략 빌더에서 조건을 설정 후 다시 저장해주세요.');
        setIsRunning(false);
        return;
      }
      
      // 필터링 모드에 따라 다르게 처리
      const filterMode = typeof config.filteringMode === 'object' ? config.filteringMode.mode : config.filteringMode;
      
      // FilteringMode 객체에서 filterId 가져오기
      const filterIdFromMode = typeof config.filteringMode === 'object' ? config.filteringMode.filterId : null;
      const effectiveFilterId = filterIdFromMode || currentFilterId;
      
      console.log('=== Backtest Execution Debug ===');
      console.log('Filter mode:', filterMode);
      console.log('Current filter ID:', currentFilterId);
      console.log('Filter ID from mode:', filterIdFromMode);
      console.log('Effective filter ID:', effectiveFilterId);
      console.log('Current filters:', currentFilters);
      console.log('Stock codes count:', validStockCodes?.length || 0);
      console.log('================================');
      
      if (filterMode === 'pre-filter') {
        // 사전 필터링 모드: 필터에서 가져온 종목 코드 사용
        if (effectiveFilterId) {
          requestPayload.filter_id = effectiveFilterId;
          console.log('Using pre-filter mode with filter_id:', effectiveFilterId);
        }
        
        // FilteringMode에서 종목 코드 가져오기
        const stockCodesFromMode = typeof config.filteringMode === 'object' ? config.filteringMode.stockCodes : null;
        
        if (stockCodesFromMode && stockCodesFromMode.length > 0) {
          requestPayload.stock_codes = stockCodesFromMode;
          console.log('Using stock codes from filtering mode:', stockCodesFromMode.length, 'stocks');
        } else if (validStockCodes && validStockCodes.length > 0) {
          requestPayload.stock_codes = validStockCodes;
          console.log('Using validated stock codes:', validStockCodes.length, 'stocks');
        } else {
          console.error('Pre-filter mode selected but no stock codes available');
          setError('사전 필터링 모드가 선택되었지만 종목이 로드되지 않았습니다. "저장된 필터 불러오기" 버튼을 클릭하여 필터를 먼저 선택해주세요.');
          setIsRunning(false);
          return;
        }
      } else if (validStockCodes && validStockCodes.length > 0) {
        // 일반 모드 또는 실시간 필터링: stock_codes 전송
        requestPayload.stock_codes = validStockCodes;
        if (filterMode === 'real-time') {
          requestPayload.filter_rules = currentFilters;
        }
      } else if (!filterMode || filterMode === 'none') {
        // 필터링 없음: stock_codes가 있으면 전송
        if (validStockCodes && validStockCodes.length > 0) {
          requestPayload.stock_codes = validStockCodes;
        }
      }
      
      console.log('Backtest request payload:', JSON.stringify(requestPayload, null, 2));

      // 매수/매도 조건이 비어있는지 확인 (strategyConfig에서 확인)
      if (strategyConfig && ((!strategyConfig.buyConditions || strategyConfig.buyConditions.length === 0) &&
          (!strategyConfig.buyStageStrategy || !strategyConfig.useStageBasedStrategy))) {
        console.warn('⚠️ 경고: 매수 조건이 설정되지 않았습니다!');
        console.warn('Buy Conditions:', strategyConfig.buyConditions);
        console.warn('Buy Stage Strategy:', strategyConfig.buyStageStrategy);
        console.warn('Use Stage Based:', strategyConfig.useStageBasedStrategy);
      }

      if (strategyConfig && ((!strategyConfig.sellConditions || strategyConfig.sellConditions.length === 0) &&
          !strategyConfig.targetProfit?.simple?.enabled &&
          !strategyConfig.targetProfit?.staged?.enabled)) {
        console.warn('⚠️ 경고: 매도 조건이 설정되지 않았습니다!');
        console.warn('Sell Conditions:', strategyConfig.sellConditions);
        console.warn('Target Profit:', strategyConfig.targetProfit);
      }
      
      // 백테스트 실행 요청
      console.log('Sending backtest request to server...');
      // 프로덕션에서는 Vercel Functions 프록시 사용
      const isProduction = import.meta.env.PROD;
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      const apiUrl = isProduction
        ? '/api/backtest-run'  // Vercel Functions 프록시
        : `${baseUrl}/api/backtest/run`;

      console.log('API URL for backtest:', apiUrl);
      console.log('Base URL:', baseUrl);
      console.log('VITE_API_URL from env:', import.meta.env.VITE_API_URL);
      console.log('All env vars:', import.meta.env);
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backtest server error:', errorText);
        
        let errorMessage = '백테스트 실행 실패';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.error || errorData.detail || errorMessage;
          
          // 전략 조건 미설정 에러 강조
          if (errorMessage.includes('전략에 매수/매도 조건이 설정되지 않았습니다')) {
            errorMessage = `⚠️ ${errorMessage}`;
          }
        } catch {
          errorMessage = errorText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Backtest result:', result);
      console.log('Result structure:', {
        hasStatus: 'status' in result,
        hasResults: 'results' in result,
        status: result.status,
        results: result.results
      });

      setBacktestId(result.backtest_id);

      // 백테스트가 즉시 완료되는 경우 (success가 true이고 summary가 있는 경우)
      if (result.success && result.summary) {
        const backtestData = result;
        setProgress(100);
        setSuccess(`백테스트가 완료되었습니다.
          총 수익률: ${backtestData.summary?.total_return?.toFixed(2)}%,
          평균 승률: ${backtestData.summary?.average_win_rate?.toFixed(2)}%,
          최대 손실: ${backtestData.summary?.max_drawdown?.toFixed(2)}%`);
        setIsRunning(false);

        // 결과를 state에 저장하고 상세 정보 포맷팅
        console.log('Raw backtest result from server:', result);
        console.log('Backtest data:', backtestData);
        console.log('Summary:', backtestData.summary);
        console.log('Individual results:', backtestData.individual_results);
        console.log('First stock result:', backtestData.individual_results?.[0]);
        
        // 전략 이름 찾기 - strategies 배열이나 백엔드 응답에서
        const currentStrategy = strategies.find(s => s.id === config.strategyId);
        const strategyNameFromBackend = result.strategy_name || result.summary?.strategy_name;
        const finalStrategyName = currentStrategy?.name || strategyNameFromBackend || '알 수 없음';
        
        console.log('Strategy name resolution:', {
          fromStrategies: currentStrategy?.name,
          fromBackend: strategyNameFromBackend,
          final: finalStrategyName
        });

        // 개별 종목 결과에서 거래 데이터 집계
        const allTrades: any[] = [];
        let totalWinningTrades = 0;
        let totalLosingTrades = 0;
        let totalTradeCount = 0;

        backtestData.individual_results?.forEach((stockResult: any) => {
          const stockTrades = stockResult.result?.trades || [];
          // 각 종목의 승리/패배 거래 수 집계
          totalWinningTrades += stockResult.result?.winning_trades || 0;
          totalLosingTrades += stockResult.result?.losing_trades || 0;
          totalTradeCount += stockResult.result?.total_trades || 0;
          
          stockTrades.forEach((trade: any) => {
            allTrades.push({
              ...trade,
              stock_code: stockResult.stock_code,
              stock_name: stockResult.stock_code // 임시로 코드를 이름으로 사용
            });
          });
        });

        // 매수/매도 거래 분리 및 승패 계산
        const buyTrades = allTrades.filter(t => t.type === 'buy' || t.action === 'buy');
        const sellTrades = allTrades.filter(t => t.type === 'sell' || t.action === 'sell');
        const actualWinningTrades = sellTrades.filter(t => (t.profit || t.profit_loss || 0) > 0).length;
        const actualLosingTrades = sellTrades.filter(t => (t.profit || t.profit_loss || 0) <= 0).length;

        const formattedResult = {
          id: result.backtest_id || `backtest_${Date.now()}`,
          strategy_name: finalStrategyName,
          start_date: config.startDate.toISOString().split('T')[0],
          end_date: config.endDate.toISOString().split('T')[0],
          initial_capital: config.initialCapital,
          final_capital: config.initialCapital * (1 + (backtestData.summary?.total_return || 0) / 100),
          total_return: backtestData.summary?.total_return || 0,
          annual_return: backtestData.summary?.total_return || 0, // 연간 수익률은 별도 계산 필요
          max_drawdown: backtestData.summary?.max_drawdown || 0,
          win_rate: backtestData.summary?.average_win_rate || 0,
          total_trades: backtestData.summary?.total_trades || totalTradeCount || sellTrades.length || backtestData.summary?.processed_count || 0,
          winning_trades: backtestData.summary?.winning_trades || actualWinningTrades || totalWinningTrades,
          losing_trades: backtestData.summary?.losing_trades || actualLosingTrades || totalLosingTrades,
          buy_count: backtestData.summary?.buy_count || buyTrades.length,
          sell_count: backtestData.summary?.sell_count || sellTrades.length,
          sharpe_ratio: backtestData.summary?.average_sharpe_ratio || 0,
          volatility: 0, // 변동성은 별도 계산 필요
          // trades 배열 포맷팅
          trades: allTrades.map((trade: any) => ({
            date: trade.date || trade.trade_date || '',
            stock_code: trade.stock_code || trade.code || '',
            stock_name: trade.stock_name || trade.name || '',
            action: trade.action || trade.type || 'unknown',
            quantity: trade.quantity || trade.shares || 0,
            price: trade.price || 0,
            amount: trade.amount || trade.cost || trade.proceeds || trade.revenue || 0,
            profit_loss: trade.profit_loss || trade.profit || 0,
            profit_rate: trade.profit_rate || trade.profit_pct || trade.return_rate || 0
          })),
          // daily_returns는 개별 종목 결과에서 필요시 집계
          daily_returns: [],
          strategy_config: strategies.find(s => s.id === config.strategyId)?.parameters || {},
          investment_config: currentFilters || {},
          filtering_config: filteringMode || {},
        };
        
        console.log('Formatted result:', formattedResult);
        console.log('Formatted trades count:', formattedResult.trades.length);
        console.log('Formatted daily_returns count:', formattedResult.daily_returns.length);
        
        setBacktestResults(formattedResult);
        // 결과 다이얼로그 자동 표시
        setShowResultDialog(true);
      } else {
        // 비동기 백테스트인 경우 진행 상황 모니터링 (향후 구현)
        const subscription = BacktestService.subscribeToBacktestProgress(
          result.backtest_id,
          (progress) => {
            setProgress(progress.progress || 0);
            if (progress.status === 'completed') {
              setSuccess('백테스트가 성공적으로 완료되었습니다.');
              setIsRunning(false);
              subscription.unsubscribe();
            } else if (progress.status === 'failed') {
              setError(progress.error || '백테스트 실행 중 오류가 발생했습니다.');
              setIsRunning(false);
              subscription.unsubscribe();
            }
          }
        );
      }
    } catch (err: any) {
      console.error('Backtest error:', err);
      
      // 에러 메시지 개선
      if (err.message && err.message.includes('Failed to fetch')) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        setError(`백테스트 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요. (${baseUrl})`);
      } else if (err.message && err.message.includes('종목 데이터를 불러올 수 없습니다')) {
        setError(err.message);
      } else {
        setError(err.message || '백테스트 실행 중 오류가 발생했습니다.');
      }
      
      setIsRunning(false);
    }
  };

  const stopBacktest = async () => {
    if (!backtestId) return;

    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      const response = await fetch(`${baseUrl}/api/backtest/stop/${backtestId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('백테스트 중단 실패');
      }

      setIsRunning(false);
      setProgress(0);
      setSuccess('백테스트가 중단되었습니다.');
    } catch (err: any) {
      setError(err.message || '백테스트 중단 중 오류가 발생했습니다.');
    }
  };

  const viewResults = () => {
    if (backtestId) {
      navigate(`/backtest/results/${backtestId}`);
    }
  };

  const viewResultsList = () => {
    navigate('/backtest/results');
  };

  const saveBacktestResult = async () => {
    if (!backtestResults) return;

    setIsSaving(true);
    try {
      console.log('Saving backtest result...');
      console.log('Current strategies:', strategies);
      console.log('Current strategyId:', config.strategyId);

      const strategy = strategies.find(s => s.id === config.strategyId);
      console.log('Found strategy:', strategy);

      // backtestResults에 이미 strategy_name이 있으면 그것을 사용, 없으면 strategies에서 찾기
      const strategyName = backtestResults.strategy_name || strategy?.name || 'Unknown Strategy';
      console.log('Strategy name to save:', strategyName);

      // 실제 테이블 스키마에 맞춰서 데이터 구성
      const resultToSave = {
        strategy_id: config.strategyId,
        strategy_name: strategyName,
        start_date: config.startDate?.toISOString().split('T')[0] || '',
        end_date: config.endDate?.toISOString().split('T')[0] || '',
        test_period_start: config.startDate?.toISOString().split('T')[0],
        test_period_end: config.endDate?.toISOString().split('T')[0],
        initial_capital: config.initialCapital,
        final_capital: backtestResults.final_capital || (config.initialCapital + (backtestResults.total_return * config.initialCapital / 100)),
        total_return: backtestResults.total_return,
        max_drawdown: backtestResults.max_drawdown,
        sharpe_ratio: backtestResults.sharpe_ratio || null,
        win_rate: backtestResults.win_rate || null,
        total_trades: backtestResults.total_trades || 0,
        profitable_trades: backtestResults.winning_trades || 0,
        winning_trades: backtestResults.winning_trades || 0,
        losing_trades: backtestResults.losing_trades || 0,
        avg_profit: backtestResults.avg_profit || null,
        avg_loss: backtestResults.avg_loss || null,
        profit_factor: backtestResults.profit_factor || null,
        recovery_factor: backtestResults.recovery_factor || null,
        // JSONB 필드들
        results_data: {
          strategy_config: backtestResults.strategy_config || {},
          investment_config: {
            initial_capital: config.initialCapital,
            commission: config.commission,
            slippage: config.slippage,
            data_interval: config.dataInterval
          },
          filter_config: currentFilters || {},
          filtering_mode: filteringMode,
          stock_codes: config.stockCodes,
          filter_id: currentFilterId,
          volatility: backtestResults.volatility || 0,
          annual_return: backtestResults.annual_return || 0
        },
        trade_details: backtestResults.trades || [],
        daily_returns: backtestResults.daily_returns || []
      };

      const { data, error } = await backtestStorageService.saveResult(resultToSave);

      if (error) {
        throw error;
      }

      setSavedResultId(data.id);
      setSuccess('백테스트 결과가 저장되었습니다.');

      // 저장 성공 후 다이얼로그 닫기
      setTimeout(() => {
        setShowResultDialog(false);
        // 백테스트 상태 초기화
        resetBacktestState();
      }, 1500);
    } catch (err: any) {
      console.error('Failed to save backtest result:', err);
      setError('결과 저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const resetBacktestState = () => {
    // 백테스트 관련 상태 초기화
    setBacktestResults(null);
    setProgress(0);
    setIsRunning(false);
    setError(null);
    setSuccess(null);
    // 필요한 경우 다른 상태도 초기화
  };

  const handleCloseDialog = () => {
    setShowResultDialog(false);
    resetBacktestState();
  };

  const navigateToComparison = () => {
    // 결과 비교 탭으로 이동 (index 3)
    const tabEvent = new CustomEvent('changeTab', { detail: { tab: 3 } });
    window.dispatchEvent(tabEvent);
  };

  return (
    <Box>
      {/* 탭 메뉴 */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentSubTab} onChange={(e, newValue) => setCurrentSubTab(newValue)}>
          <Tab label="백테스트 실행" icon={<PlayArrowIcon />} iconPosition="start" />
          <Tab label="결과 보기" icon={<AssessmentIcon />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* 탭 컨텐츠 */}
      {currentSubTab === 0 ? (
        // 백테스트 실행 탭
        <Box>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              백테스트 실행
            </Typography>
            <Typography variant="body2" color="text.secondary">
              전략빌더에서 생성한 전략을 선택하여 백테스트를 실행할 수 있습니다.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          )}

          {/* 전략 선택 카드 */}
          <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              전략 선택
            </Typography>
            <Button
              variant="outlined"
              startIcon={<StyleIcon />}
              onClick={() => setShowTemplateDialog(true)}
              disabled={isRunning}
            >
              템플릿에서 선택
            </Button>
          </Box>
          <FormControl fullWidth>
            <InputLabel id="strategy-select-label">전략 선택</InputLabel>
            <Select
              labelId="strategy-select-label"
              value={config.strategyId}
              label="전략 선택"
              onChange={(e) => setConfig({ ...config, strategyId: e.target.value })}
              disabled={isRunning}
            >
              <MenuItem value="">
                <em>전략을 선택하세요</em>
              </MenuItem>
              {strategies.length === 0 ? (
                <MenuItem disabled>
                  <em>저장된 전략이 없습니다. 전략빌더에서 생성해주세요.</em>
                </MenuItem>
              ) : (
                strategies.map((strategy) => (
                  <MenuItem key={strategy.id} value={strategy.id}>
                    <Box>
                      <Typography>{strategy.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {strategy.type} | {strategy.description?.substring(0, 50)}
                        {strategy.created_at && ` | ${new Date(strategy.created_at).toLocaleDateString('ko-KR')}`}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
          {strategies.length > 0 && (
            <>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                총 {strategies.length}개의 전략이 있습니다.
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="caption">
                  ⚠️ 백테스트를 실행하기 전에 전략에 매수/매도 조건이 설정되어 있는지 확인하세요.
                  조건이 없는 전략은 백테스트를 실행할 수 없습니다.
                </Typography>
              </Alert>
            </>
          )}
        </CardContent>
      </Card>

      {/* 백테스트 설정 카드 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            백테스트 설정
          </Typography>
          <Grid container spacing={3}>

            {/* 데이터 간격 */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>데이터 간격</InputLabel>
                <Select
                  value={config.dataInterval}
                  label="데이터 간격"
                  onChange={(e) => setConfig({ ...config, dataInterval: e.target.value })}
                  disabled={isRunning}
                >
                  <MenuItem value="1d">일봉 (Daily)</MenuItem>
                  <MenuItem value="1w">주봉 (Weekly)</MenuItem>
                  <MenuItem value="1M">월봉 (Monthly)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* 기간 설정 */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="시작일"
                type="date"
                value={config.startDate ? config.startDate.toISOString().split('T')[0] : ''}
                onChange={(e) => setConfig({ ...config, startDate: new Date(e.target.value) })}
                disabled={isRunning}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="종료일"
                type="date"
                value={config.endDate ? config.endDate.toISOString().split('T')[0] : ''}
                onChange={(e) => setConfig({ ...config, endDate: new Date(e.target.value) })}
                disabled={isRunning}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            {/* 자본금 설정 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="초기 자본금"
                type="number"
                value={config.initialCapital}
                onChange={(e) => setConfig({ ...config, initialCapital: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '원',
                }}
              />
            </Grid>

            {/* 수수료 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="수수료율"
                type="number"
                value={config.commission}
                onChange={(e) => setConfig({ ...config, commission: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '%',
                }}
                helperText="거래금액 대비 수수료율"
              />
            </Grid>

            {/* 슬리피지 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="슬리피지"
                type="number"
                value={config.slippage}
                onChange={(e) => setConfig({ ...config, slippage: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '%',
                }}
                helperText="예상 체결가와 실제 체결가의 차이"
              />
            </Grid>

            {/* 종목 코드 입력 */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="종목 코드 직접 입력 (선택사항)"
                placeholder="005930, 000660, 035720 (쉼표로 구분)"
                value={config.stockCodes.join(', ')}
                onChange={(e) => {
                  const codes = e.target.value
                    .split(',')
                    .map(code => code.trim())
                    .filter(code => code.length > 0);
                  setConfig({ ...config, stockCodes: codes });
                }}
                disabled={isRunning}
                helperText={
                  <Typography variant="caption" component="div">
                    💡 종목 선택 방법:
                    <br />
                    1. 여기에 직접 종목 코드 입력 (수동)
                    <br />
                    2. 아래 "필터링 전략 설정"에서 저장된 필터 불러오기 (권장)
                    <br />
                    {config.stockCodes.length > 0 
                      ? `✅ 현재 ${config.stockCodes.length}개 종목 선택됨` 
                      : '⚠️ 비어있으면 전체 종목 대상'}
                  </Typography>
                }
              />
            </Grid>
          </Grid>

          {/* 필터링 전략 설정 섹션 */}
          <Accordion sx={{ mt: 3 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">
                필터링 전략 설정
                {currentFilters && (
                  <Chip 
                    label="필터 로드됨" 
                    size="small" 
                    color="success" 
                    sx={{ ml: 2 }}
                  />
                )}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <FilteringStrategy
                currentFilters={currentFilters}
                onFilteringModeChange={(mode, filterData) => {
                  setFilteringMode(mode)
                  setConfig({ ...config, filteringMode: mode })
                  
                  // 필터 데이터가 있고 사전 필터링 모드인 경우 처리
                  if (filterData && mode.mode === 'pre-filter') {
                    console.log('Pre-filter mode with filter data:', filterData)
                    
                    // Filter ID 설정
                    if (mode.filterId) {
                      console.log('Setting currentFilterId from FilteringStrategy:', mode.filterId)
                      setCurrentFilterId(mode.filterId)
                    }
                    
                    // 종목 코드 설정
                    if (filterData.stock_codes && filterData.stock_codes.length > 0) {
                      console.log('Setting stock codes from filter:', filterData.stock_codes.length, 'stocks')
                      setConfig(prev => ({ ...prev, stockCodes: filterData.stock_codes }))
                    } else if (mode.stockCodes && mode.stockCodes.length > 0) {
                      console.log('Setting stock codes from mode:', mode.stockCodes.length, 'stocks')
                      setConfig(prev => ({ ...prev, stockCodes: mode.stockCodes || [] }))
                    }
                    
                    // 필터 데이터도 업데이트
                    if (filterData.filters) {
                      setCurrentFilters(filterData.filters)
                    }
                    
                    // 성공 메시지
                    const stockCount = filterData.stock_codes?.length || mode.stockCodes?.length || 0
                    setSuccess(`사전 필터링 모드: "${filterData.name}" 필터가 적용되었습니다. (${stockCount}개 종목)`)
                  }
                }}
              />
            </AccordionDetails>
          </Accordion>

          <Grid container spacing={3}>
            {/* 진행 상황 */}
            {isRunning && (
              <Grid item xs={12}>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    백테스트 진행 중... {progress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={progress} />
                </Box>
              </Grid>
            )}

            {/* 진행 상황 표시 */}
            {isRunning && (
              <Grid item xs={12}>
                <Box sx={{ mt: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress 
                        variant={progress > 0 ? "determinate" : "indeterminate"}
                        value={progress}
                      />
                    </Box>
                    {progress > 0 && (
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {`${Math.round(progress)}%`}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {progress > 0 
                      ? `처리 중... (${Math.round(progress)}% 완료)`
                      : '백테스트 실행 중... 서버 콘솔에서 진행 상황을 확인할 수 있습니다.'}
                  </Typography>
                  <Typography variant="caption" color="info.main" display="block" sx={{ mt: 1 }}>
                    💡 팁: 서버 콘솔 창에서 각 종목별 처리 상황을 실시간으로 확인할 수 있습니다.
                  </Typography>
                </Box>
              </Grid>
            )}

            {/* 실행 버튼 */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                {!isRunning ? (
                  <>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<PlayArrowIcon />}
                      onClick={runBacktest}
                      disabled={!config.strategyId}
                    >
                      백테스트 실행
                    </Button>
                    {backtestId && (
                      <Button
                        variant="outlined"
                        size="large"
                        startIcon={<AssessmentIcon />}
                        onClick={viewResults}
                      >
                        결과 보기
                      </Button>
                    )}
                    {backtestResults && (
                      <>
                        <Button
                          variant="contained"
                          color="secondary"
                          size="large"
                          startIcon={<AssessmentIcon />}
                          onClick={() => setShowResultDialog(true)}
                        >
                          상세 결과 보기
                        </Button>
                        {!savedResultId && (
                          <Button
                            variant="outlined"
                            size="large"
                            startIcon={<SaveIcon />}
                            onClick={saveBacktestResult}
                            disabled={isSaving}
                          >
                            {isSaving ? '저장 중...' : '결과 저장'}
                          </Button>
                        )}
                        <Button
                          variant="outlined"
                          size="large"
                          startIcon={<CompareArrowsIcon />}
                          onClick={navigateToComparison}
                        >
                          결과 비교
                        </Button>
                      </>
                    )}
                  </>
                ) : (
                  <Button
                    variant="contained"
                    color="error"
                    size="large"
                    startIcon={<StopIcon />}
                    onClick={stopBacktest}
                  >
                    백테스트 중단
                  </Button>
                )}
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 전략이 없을 때 안내 */}
      {strategies.length === 0 && (
        <Card sx={{ mt: 2 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              아직 저장된 전략이 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              전략빌더에서 새로운 전략을 만들어 저장한 후 백테스트를 실행할 수 있습니다.
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
              (로그인 상태와 전략 데이터를 확인 중입니다. 콘솔을 확인해주세요.)
            </Typography>
            <Button
              variant="contained"
              color="primary"
              href="/strategy-builder"
              startIcon={<AssessmentIcon />}
            >
              전략빌더로 이동
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 전략 정보 표시 */}
      {config.strategyId && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              선택한 전략 정보
            </Typography>
            {strategies
              .filter(s => s.id === config.strategyId)
              .map(strategy => (
                <Box key={strategy.id}>
                  <Typography variant="body1" gutterBottom>
                    <strong>{strategy.name}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {strategy.description}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip label={strategy.type} size="small" color="primary" />
                    {strategy.parameters && Object.keys(strategy.parameters)
                      .filter(key => typeof strategy.parameters[key] !== 'object')
                      .slice(0, 5)
                      .map(key => (
                        <Chip 
                          key={key}
                          label={`${key}: ${strategy.parameters[key]}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    {Object.keys(strategy.parameters || {}).length > 5 && (
                      <Chip 
                        label={`+${Object.keys(strategy.parameters).length - 5} more`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Stack>
                </Box>
              ))}
          </CardContent>
        </Card>
      )}

      {/* 필터 불러오기 다이얼로그 */}
      <LoadFilterDialog
        open={showLoadFilterDialog}
        onClose={() => setShowLoadFilterDialog(false)}
        onLoadFilter={handleFilterLoad}
      />

      {/* 템플릿 선택 다이얼로그 */}
      <Dialog
        open={showTemplateDialog}
        onClose={() => setShowTemplateDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            전략 템플릿 선택
            <IconButton onClick={() => setShowTemplateDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            검증된 전략 템플릿을 선택하여 백테스트를 진행하세요
          </Typography>
          <Grid container spacing={2}>
            {STRATEGY_TEMPLATES.map((template) => (
              <Grid item xs={12} sm={6} md={4} key={template.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    border: selectedTemplate?.id === template.id ? 2 : 0,
                    borderColor: 'primary.main',
                    '&:hover': { 
                      transform: 'translateY(-4px)',
                      boxShadow: 3 
                    }
                  }}
                  onClick={() => setSelectedTemplate(template)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                      <Typography variant="h6">
                        {template.name}
                      </Typography>
                      <Chip 
                        label={template.difficulty === 'beginner' ? '초급' :
                               template.difficulty === 'intermediate' ? '중급' :
                               template.difficulty === 'advanced' ? '고급' : '전문가'}
                        size="small"
                        color={template.difficulty === 'beginner' ? 'success' :
                               template.difficulty === 'intermediate' ? 'warning' :
                               template.difficulty === 'advanced' ? 'error' : 'error'}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {template.description}
                    </Typography>
                    <Chip 
                      label={template.type === 'complex' ? '3단계 전략' : '기본 전략'}
                      size="small"
                      variant="outlined"
                      color={template.type === 'complex' ? 'secondary' : 'primary'}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTemplateDialog(false)}>
            취소
          </Button>
          <Button 
            onClick={() => selectedTemplate && applyTemplate(selectedTemplate)}
            variant="contained"
            disabled={!selectedTemplate}
          >
            템플릿 적용
          </Button>
        </DialogActions>
      </Dialog>

      {/* 백테스트 결과 다이얼로그 */}
      <Dialog
        open={showResultDialog}
        onClose={handleCloseDialog}
        maxWidth="xl"
        fullWidth
        PaperProps={{
          sx: { minHeight: '80vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">백테스트 결과</Typography>
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {backtestResults && (
            <BacktestResultViewer
              result={backtestResults}
              onRefresh={() => {
                // 필요시 결과 새로고침 로직 추가
                console.log('Refreshing backtest results...');
              }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={saveBacktestResult}
            disabled={isSaving || !backtestResults}
          >
            {isSaving ? '저장 중...' : '결과 저장'}
          </Button>
          <Button
            variant="outlined"
            onClick={handleCloseDialog}
          >
            닫기
          </Button>
        </DialogActions>
      </Dialog>
        </Box>
      ) : (
        // 결과 보기 탭
        <BacktestComparison />
      )}
    </Box>
  );
};

export default BacktestRunner;