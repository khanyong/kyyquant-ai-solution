import React, { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Stack,
  Divider,
  Alert,
  AlertTitle,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  IconButton,
  Button
} from '@mui/material'
import {
  FilterList,
  Business,
  AccountBalance,
  Shield,
  CompareArrows,
  AttachMoney,
  Schedule,
  Notifications,
  CheckCircle,
  Warning,
  Error,
  Settings,
  Refresh,
  OpenInNew
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

interface InvestmentConfig {
  universe: {
    marketCap: [number, number]
    per: [number, number]
    pbr: [number, number]
    roe: [number, number]
    debtRatio: [number, number]
    tradingVolume: [number, number]
    foreignOwnership: [number, number]
    institutionalOwnership: [number, number]
    excludeTradingHalt: boolean
    excludeWarningStock: boolean
    excludePennyStock: boolean
    pennyStockPrice: number
  }
  sectors: {
    include: string[]
    exclude: string[]
    sectorIndices: Array<{
      code: string
      name: string
      enabled: boolean
      weight: number
    }>
    correlationAnalysis: boolean
    sectorRotation: boolean
  }
  portfolio: {
    maxPositions: number
    minPositions: number
    positionSizeMethod: string
    maxPositionSize: number
    cashBuffer: number
    rebalancePeriod: string
  }
  risk: {
    maxDrawdown: number
    stopLoss: number
    takeProfit: number
    systemCut: {
      enabled: boolean
      maxDailyLoss: number
      action: string
    }
  }
  trading: {
    orderType: string
    splitTrading: {
      enabled: boolean
      buyLevels: number[]
      sellLevels: number[]
    }
  }
  automation: {
    autoStart: boolean
    emergencyStop: {
      enabled: boolean
    }
  }
}

const InvestmentSettingsSummary: React.FC = () => {
  const navigate = useNavigate()
  const [config, setConfig] = useState<InvestmentConfig | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const loadSettings = () => {
    const saved = localStorage.getItem('completeInvestmentConfig')
    if (saved) {
      setConfig(JSON.parse(saved))
      setLastUpdate(new Date())
    }
  }

  useEffect(() => {
    loadSettings()
  }, [])

  const getStatusColor = (value: boolean) => value ? 'success' : 'default'
  const getRiskLevel = () => {
    if (!config) return { level: 'unknown', color: 'default' }
    const drawdown = config.risk.maxDrawdown
    if (drawdown <= 10) return { level: '보수적', color: 'success' }
    if (drawdown <= 20) return { level: '중립적', color: 'warning' }
    return { level: '공격적', color: 'error' }
  }

  if (!config) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            <AlertTitle>투자 설정이 없습니다</AlertTitle>
            투자 설정 페이지에서 먼저 설정을 완료해주세요.
            <Button
              size="small"
              startIcon={<Settings />}
              onClick={() => navigate('/investment-settings')}
              sx={{ mt: 1 }}
            >
              투자 설정 페이지로 이동
            </Button>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  const riskLevel = getRiskLevel()

  return (
    <Box>
      {/* 헤더 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings /> 투자 설정 요약
        </Typography>
        <Stack direction="row" spacing={1}>
          <Tooltip title="설정 새로고침">
            <IconButton size="small" onClick={loadSettings}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="설정 페이지로 이동">
            <IconButton size="small" onClick={() => navigate('/investment-settings')}>
              <OpenInNew />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      {lastUpdate && (
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          마지막 업데이트: {lastUpdate.toLocaleString()}
        </Typography>
      )}

      <Grid container spacing={2}>
        {/* 투자 유니버스 요약 */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <FilterList fontSize="small" /> 투자 유니버스
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">시가총액</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.universe.marketCap[0]}억 ~ {config.universe.marketCap[1]}억
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">PER</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.universe.per[0]} ~ {config.universe.per[1]}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">ROE</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.universe.roe[0]}% ~ {config.universe.roe[1]}%
                  </Typography>
                </Box>
                <Divider sx={{ my: 0.5 }} />
                <Stack direction="row" spacing={0.5}>
                  {config.universe.excludeTradingHalt && (
                    <Chip label="거래정지 제외" size="small" color="warning" />
                  )}
                  {config.universe.excludeWarningStock && (
                    <Chip label="투자주의 제외" size="small" color="warning" />
                  )}
                  {config.universe.excludePennyStock && (
                    <Chip label={`${config.universe.pennyStockPrice}원 미만 제외`} size="small" color="warning" />
                  )}
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* 섹터 설정 요약 */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Business fontSize="small" /> 섹터 설정
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                <Box>
                  <Typography variant="caption" color="success.main">포함 섹터 ({config.sectors.include.length}개)</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    {config.sectors.include.slice(0, 3).map(sector => (
                      <Chip key={sector} label={sector} size="small" color="success" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                    {config.sectors.include.length > 3 && (
                      <Chip label={`+${config.sectors.include.length - 3}`} size="small" variant="outlined" />
                    )}
                  </Box>
                </Box>
                <Box>
                  <Typography variant="caption" color="error.main">제외 섹터 ({config.sectors.exclude.length}개)</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    {config.sectors.exclude.slice(0, 3).map(sector => (
                      <Chip key={sector} label={sector} size="small" color="error" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                    {config.sectors.exclude.length > 3 && (
                      <Chip label={`+${config.sectors.exclude.length - 3}`} size="small" variant="outlined" />
                    )}
                  </Box>
                </Box>
                <Stack direction="row" spacing={0.5}>
                  {config.sectors.correlationAnalysis && (
                    <Chip label="상관분석" size="small" color="info" />
                  )}
                  {config.sectors.sectorRotation && (
                    <Chip label="섹터로테이션" size="small" color="info" />
                  )}
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* 포트폴리오 설정 요약 */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <AccountBalance fontSize="small" /> 포트폴리오
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">보유 종목</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.portfolio.minPositions} ~ {config.portfolio.maxPositions}개
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">종목당 비중</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    최대 {config.portfolio.maxPositionSize}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">현금 보유</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.portfolio.cashBuffer}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">리밸런싱</Typography>
                  <Chip 
                    label={config.portfolio.rebalancePeriod === 'monthly' ? '월간' : 
                           config.portfolio.rebalancePeriod === 'weekly' ? '주간' :
                           config.portfolio.rebalancePeriod === 'quarterly' ? '분기별' : '매일'} 
                    size="small" 
                  />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* 리스크 관리 요약 */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Shield fontSize="small" /> 리스크 관리
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption">리스크 수준</Typography>
                  <Chip 
                    label={riskLevel.level} 
                    size="small" 
                    color={riskLevel.color as any}
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">최대 손실(MDD)</Typography>
                  <Typography variant="caption" fontWeight="bold" color="error.main">
                    -{config.risk.maxDrawdown}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">손절/익절</Typography>
                  <Typography variant="caption" fontWeight="bold">
                    {config.risk.stopLoss}% / +{config.risk.takeProfit}%
                  </Typography>
                </Box>
                {config.risk.systemCut.enabled && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption">시스템 컷</Typography>
                    <Stack direction="row" spacing={0.5}>
                      <Chip 
                        label={`일일 ${config.risk.systemCut.maxDailyLoss}%`} 
                        size="small" 
                        color="error"
                      />
                      <Chip 
                        label={config.risk.systemCut.action === 'stop' ? '정지' : 
                               config.risk.systemCut.action === 'pause' ? '일시정지' : '축소'} 
                        size="small" 
                        variant="outlined"
                      />
                    </Stack>
                  </Box>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* 매매 설정 요약 */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <AttachMoney fontSize="small" /> 매매 설정
              </Typography>
              <Grid container spacing={2} sx={{ mt: 0.5 }}>
                <Grid item xs={12} sm={4}>
                  <Stack spacing={0.5}>
                    <Typography variant="caption" color="text.secondary">주문 방식</Typography>
                    <Chip 
                      label={config.trading.orderType === 'market' ? '시장가' : 
                             config.trading.orderType === 'limit' ? '지정가' : '스톱'} 
                      size="small" 
                    />
                  </Stack>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Stack spacing={0.5}>
                    <Typography variant="caption" color="text.secondary">분할매매</Typography>
                    <Chip 
                      label={config.trading.splitTrading.enabled ? 
                             `매수 ${config.trading.splitTrading.buyLevels.length}차 / 매도 ${config.trading.splitTrading.sellLevels.length}차` : 
                             '미사용'} 
                      size="small"
                      color={config.trading.splitTrading.enabled ? 'primary' : 'default'}
                    />
                  </Stack>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Stack spacing={0.5}>
                    <Typography variant="caption" color="text.secondary">자동화</Typography>
                    <Stack direction="row" spacing={0.5}>
                      {config.automation.autoStart && (
                        <Chip label="자동시작" size="small" color="success" />
                      )}
                      {config.automation.emergencyStop.enabled && (
                        <Chip label="비상정지" size="small" color="error" />
                      )}
                      {!config.automation.autoStart && !config.automation.emergencyStop.enabled && (
                        <Chip label="수동" size="small" />
                      )}
                    </Stack>
                  </Stack>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 설정 상태 알림 */}
        <Grid item xs={12}>
          <Alert 
            severity="info" 
            action={
              <Button 
                color="inherit" 
                size="small"
                onClick={() => navigate('/investment-settings')}
              >
                설정 변경
              </Button>
            }
          >
            현재 투자 설정이 전략 실행에 적용됩니다. 설정을 변경하려면 투자 설정 페이지를 방문하세요.
          </Alert>
        </Grid>
      </Grid>
    </Box>
  )
}

export default InvestmentSettingsSummary