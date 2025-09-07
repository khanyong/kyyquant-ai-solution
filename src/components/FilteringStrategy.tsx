import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Switch,
  Select,
  MenuItem,
  InputLabel,
  Card,
  CardContent,
  Chip,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  ExpandMore,
  FilterAlt,
  Speed,
  Timeline,
  CheckCircle,
  Cancel,
  Info,
  TrendingUp,
  Assessment,
  Warning,
  ArrowForward,
  Refresh,
  Settings,
  FolderOpen
} from '@mui/icons-material'
import { 
  FilteringMode, 
  FilteringModeType, 
  RebalancePeriod,
  FILTERING_MODE_DESCRIPTIONS,
  FilterRules 
} from '../types/filteringMode'
import LoadFilterDialog from './LoadFilterDialog'

interface FilteringStrategyProps {
  currentFilters?: FilterRules
  onFilteringModeChange?: (mode: FilteringMode, filterData?: any) => void
}

const FilteringStrategy: React.FC<FilteringStrategyProps> = ({
  currentFilters,
  onFilteringModeChange
}) => {
  const [filteringMode, setFilteringMode] = useState<FilteringMode>({
    mode: 'pre-filter',
    preFilterRules: currentFilters,
    postFilterRules: undefined,
    hybridSettings: undefined,
    dynamicRebalance: false,
    rebalancePeriod: 'monthly',
    filterPriority: {
      required: [],
      preferred: [],
      excluded: []
    }
  })

  const [expandedMode, setExpandedMode] = useState<FilteringModeType | null>('pre-filter')
  const [showLoadFilterDialog, setShowLoadFilterDialog] = useState(false)
  const [loadedFilterName, setLoadedFilterName] = useState<string>('')

  const handleFilterLoad = (filterData: any) => {
    // 불러온 필터 데이터를 현재 모드에 맞게 적용
    const filters = filterData.filters || {}
    const updatedMode = { ...filteringMode }
    
    // 종목 코드 추출
    let stockCodes = []
    if (filterData.stock_codes && Array.isArray(filterData.stock_codes)) {
      // Supabase에서 온 데이터 (stock_codes 필드)
      stockCodes = filterData.stock_codes
    } else if (filterData.filteredStocks && Array.isArray(filterData.filteredStocks)) {
      // 로컬 스토리지에서 온 데이터 (filteredStocks 필드)
      stockCodes = filterData.filteredStocks.map((stock: any) => {
        if (typeof stock === 'string') return stock
        return stock.code || stock.stock_code || stock.symbol || String(stock)
      }).filter((code: string) => code && code.trim() !== '')
    }
    
    if (filteringMode.mode === 'pre-filter') {
      updatedMode.preFilterRules = filters
      // 사전 필터링 모드에서는 filter_id와 종목 코드를 포함
      updatedMode.filterId = filterData.id
      updatedMode.stockCodes = stockCodes
    } else if (filteringMode.mode === 'post-filter') {
      updatedMode.postFilterRules = filters
    } else if (filteringMode.mode === 'hybrid') {
      updatedMode.hybridSettings = {
        primaryFilter: filters,
        secondaryFilter: updatedMode.hybridSettings?.secondaryFilter || {}
      }
    }
    
    setFilteringMode(updatedMode)
    setLoadedFilterName(filterData.name)
    setShowLoadFilterDialog(false)
    
    // 상위 컴포넌트에 변경사항과 필터 데이터 전달 (종목 코드 포함)
    const enrichedFilterData = { ...filterData, stock_codes: stockCodes }
    onFilteringModeChange?.(updatedMode, enrichedFilterData)
  }

  const handleModeChange = (newMode: FilteringModeType) => {
    const updatedMode: FilteringMode = {
      ...filteringMode,
      mode: newMode
    }

    // 모드별 기본 설정
    if (newMode === 'pre-filter') {
      updatedMode.preFilterRules = currentFilters
      updatedMode.postFilterRules = undefined
      updatedMode.hybridSettings = undefined
    } else if (newMode === 'post-filter') {
      updatedMode.preFilterRules = undefined
      updatedMode.postFilterRules = currentFilters
      updatedMode.hybridSettings = undefined
    } else if (newMode === 'hybrid') {
      updatedMode.hybridSettings = {
        primaryFilter: currentFilters || {},
        secondaryFilter: {}
      }
      updatedMode.preFilterRules = undefined
      updatedMode.postFilterRules = undefined
    }

    setFilteringMode(updatedMode)
    setExpandedMode(newMode)
    onFilteringModeChange?.(updatedMode)
  }

  const handleRebalanceToggle = () => {
    const updated = {
      ...filteringMode,
      dynamicRebalance: !filteringMode.dynamicRebalance
    }
    setFilteringMode(updated)
    onFilteringModeChange?.(updated)
  }

  const handleRebalancePeriodChange = (period: RebalancePeriod) => {
    const updated = {
      ...filteringMode,
      rebalancePeriod: period
    }
    setFilteringMode(updated)
    onFilteringModeChange?.(updated)
  }

  const getModeIcon = (mode: FilteringModeType) => {
    switch (mode) {
      case 'pre-filter':
        return <Speed color="primary" />
      case 'post-filter':
        return <Timeline color="secondary" />
      case 'hybrid':
        return <Assessment color="success" />
      default:
        return <FilterAlt />
    }
  }

  const getModeColor = (mode: FilteringModeType) => {
    switch (mode) {
      case 'pre-filter':
        return 'primary'
      case 'post-filter':
        return 'secondary'
      case 'hybrid':
        return 'success'
      default:
        return 'default'
    }
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FilterAlt />
        필터링 전략 설정
      </Typography>

      <Box sx={{ mt: 3 }}>
        {/* 필터링 모드 선택 */}
        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
          필터링 모드 선택
        </Typography>

        <Grid container spacing={2}>
          {(Object.keys(FILTERING_MODE_DESCRIPTIONS) as FilteringModeType[]).map((mode) => {
            const desc = FILTERING_MODE_DESCRIPTIONS[mode]
            const isSelected = filteringMode.mode === mode
            
            return (
              <Grid item xs={12} md={4} key={mode}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: isSelected ? 2 : 1,
                    borderColor: isSelected ? `${getModeColor(mode)}.main` : 'divider',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 3
                    }
                  }}
                  onClick={() => handleModeChange(mode)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getModeIcon(mode)}
                      <Typography variant="h6" component="div">
                        {desc.title}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 48 }}>
                      {desc.description}
                    </Typography>

                    <Divider sx={{ my: 1 }} />

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="success.main" sx={{ fontWeight: 'bold' }}>
                        장점:
                      </Typography>
                      {desc.pros.map((pro: string, idx: number) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <CheckCircle sx={{ fontSize: 12, color: 'success.main' }} />
                          <Typography variant="caption">{pro}</Typography>
                        </Box>
                      ))}
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="warning.main" sx={{ fontWeight: 'bold' }}>
                        단점:
                      </Typography>
                      {desc.cons.map((con: string, idx: number) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Cancel sx={{ fontSize: 12, color: 'warning.main' }} />
                          <Typography variant="caption">{con}</Typography>
                        </Box>
                      ))}
                    </Box>

                    <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        <strong>적합한 경우:</strong> {desc.useCase}
                      </Typography>
                    </Box>

                    {isSelected && (
                      <Box sx={{ mt: 2 }}>
                        <Chip 
                          label="선택됨" 
                          color={getModeColor(mode)} 
                          size="small" 
                        />
                        {mode === 'pre-filter' && (
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<FolderOpen />}
                            onClick={(e) => {
                              e.stopPropagation()
                              setShowLoadFilterDialog(true)
                            }}
                            sx={{ ml: 1 }}
                          >
                            저장된 필터 불러오기
                          </Button>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )
          })}
        </Grid>
        
        {/* 불러온 필터 정보 표시 */}
        {loadedFilterName && filteringMode.mode === 'pre-filter' && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              사전 필터링: <strong>"{loadedFilterName}"</strong> 필터가 적용되었습니다.
            </Typography>
          </Alert>
        )}

        {/* 리밸런싱 설정 */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            리밸런싱 설정
          </Typography>
          
          <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={filteringMode.dynamicRebalance}
                      onChange={handleRebalanceToggle}
                      color="primary"
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1">동적 리밸런싱</Typography>
                      <Typography variant="caption" color="text.secondary">
                        주기적으로 유니버스를 재필터링하여 업데이트
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth disabled={!filteringMode.dynamicRebalance}>
                  <InputLabel>리밸런싱 주기</InputLabel>
                  <Select
                    value={filteringMode.rebalancePeriod}
                    onChange={(e) => handleRebalancePeriodChange(e.target.value as RebalancePeriod)}
                    label="리밸런싱 주기"
                  >
                    <MenuItem value="daily">매일</MenuItem>
                    <MenuItem value="weekly">매주</MenuItem>
                    <MenuItem value="monthly">매월</MenuItem>
                    <MenuItem value="quarterly">분기별</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        </Box>

        {/* 모드별 상세 설정 */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            필터링 플로우
          </Typography>

          <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
            {filteringMode.mode === 'pre-filter' && (
              <Box>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Chip label="1" color="primary" />
                  <Typography>유니버스 필터링</Typography>
                  <ArrowForward />
                  <Chip label="2" color="primary" />
                  <Typography>전략 적용</Typography>
                  <ArrowForward />
                  <Chip label="3" color="primary" />
                  <Typography>시그널 생성</Typography>
                </Stack>
                {filteringMode.dynamicRebalance && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <strong>{filteringMode.rebalancePeriod === 'daily' ? '매일' :
                             filteringMode.rebalancePeriod === 'weekly' ? '매주' :
                             filteringMode.rebalancePeriod === 'monthly' ? '매월' : '분기별'}</strong> 
                    유니버스가 재필터링됩니다.
                  </Alert>
                )}
              </Box>
            )}

            {filteringMode.mode === 'post-filter' && (
              <Box>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Chip label="1" color="secondary" />
                  <Typography>전체 종목 스캔</Typography>
                  <ArrowForward />
                  <Chip label="2" color="secondary" />
                  <Typography>전략 시그널 체크</Typography>
                  <ArrowForward />
                  <Chip label="3" color="secondary" />
                  <Typography>필터 검증</Typography>
                  <ArrowForward />
                  <Chip label="4" color="secondary" />
                  <Typography>매매 실행</Typography>
                </Stack>
                <Alert severity="warning" sx={{ mt: 2 }}>
                  전체 종목을 스캔하므로 백테스트 시간이 더 오래 걸릴 수 있습니다.
                </Alert>
              </Box>
            )}

            {filteringMode.mode === 'hybrid' && (
              <Box>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ flexWrap: 'wrap' }}>
                  <Chip label="1" color="success" />
                  <Typography>1차 필터 (기본)</Typography>
                  <ArrowForward />
                  <Chip label="2" color="success" />
                  <Typography>전략 적용</Typography>
                  <ArrowForward />
                  <Chip label="3" color="success" />
                  <Typography>시그널 체크</Typography>
                  <ArrowForward />
                  <Chip label="4" color="success" />
                  <Typography>2차 필터 (검증)</Typography>
                  <ArrowForward />
                  <Chip label="5" color="success" />
                  <Typography>최종 매매</Typography>
                </Stack>
                <Alert severity="success" sx={{ mt: 2 }}>
                  균형잡힌 접근으로 성능과 정확도를 모두 고려합니다.
                </Alert>
              </Box>
            )}
          </Paper>
        </Box>

        {/* 현재 필터 요약 */}
        {currentFilters && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
              현재 적용된 필터
            </Typography>
            <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {currentFilters.valuation && <Chip label="가치지표 필터" size="small" color="primary" />}
                {currentFilters.financial && <Chip label="재무지표 필터" size="small" color="secondary" />}
                {currentFilters.sector && <Chip label="섹터 필터" size="small" color="info" />}
                {currentFilters.custom && <Chip label="커스텀 필터" size="small" color="warning" />}
              </Stack>
            </Paper>
          </Box>
        )}
      </Box>
      
      {/* 필터 불러오기 다이얼로그 */}
      <LoadFilterDialog
        open={showLoadFilterDialog}
        onClose={() => setShowLoadFilterDialog(false)}
        onLoadFilter={handleFilterLoad}
      />
    </Paper>
  )
}

export default FilteringStrategy