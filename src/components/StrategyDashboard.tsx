import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  ChartBar,
  Play,
  Pause,
  Plus,
  Settings,
  AlertCircle,
  CheckCircle,
  Clock,
  Target,
  Shield,
  Zap,
  Eye,
  EyeOff,
  RefreshCw,
  Download,
  Upload
} from 'lucide-react'
import StrategyCreator from './StrategyCreator'
import StrategyPerformance from './StrategyPerformance'
import PositionManager from './PositionManager'
import SignalMonitor from './SignalMonitor'
import { strategyService, Strategy, Position, TradingSignal } from '@/services/strategyService'
import { useToast } from '@/components/ui/use-toast'
import { cn } from '@/lib/utils'

interface StrategyDashboardProps {
  userId?: string
}

const StrategyDashboard: React.FC<StrategyDashboardProps> = ({ userId }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [showCreator, setShowCreator] = useState(false)
  const { toast } = useToast()

  // 초기 데이터 로드
  useEffect(() => {
    loadStrategies()
    loadPositions()
    loadSignals()
    
    // 실시간 구독
    const channel = strategyService.subscribeToStrategies((payload) => {
      if (payload.eventType === 'INSERT') {
        setStrategies(prev => [payload.new as Strategy, ...prev])
      } else if (payload.eventType === 'UPDATE') {
        setStrategies(prev => 
          prev.map(s => s.id === payload.new.id ? payload.new as Strategy : s)
        )
      } else if (payload.eventType === 'DELETE') {
        setStrategies(prev => prev.filter(s => s.id !== payload.old.id))
      }
    })

    return () => {
      strategyService.unsubscribeAll()
    }
  }, [])

  // 선택된 전략의 실시간 신호 구독
  useEffect(() => {
    if (selectedStrategy) {
      const channel = strategyService.subscribeToSignals(selectedStrategy.id, (signal) => {
        setSignals(prev => [signal, ...prev].slice(0, 50)) // 최대 50개
        
        // 신호 알림
        toast({
          title: `새 ${signal.signal_type} 신호`,
          description: `${signal.stock_name} - 강도: ${(signal.signal_strength * 100).toFixed(0)}%`,
          variant: signal.signal_type === 'BUY' ? 'default' : 'destructive'
        })
      })

      return () => {
        strategyService.unsubscribeFromSignals()
      }
    }
  }, [selectedStrategy])

  const loadStrategies = async () => {
    setLoading(true)
    const data = await strategyService.getStrategies(userId)
    setStrategies(data)
    setLoading(false)
  }

  const loadPositions = async () => {
    const data = await strategyService.getPositions()
    setPositions(data)
  }

  const loadSignals = async () => {
    const data = await strategyService.getSignals()
    setSignals(data)
  }

  const handleToggleStrategy = async (strategy: Strategy) => {
    const success = await strategyService.toggleStrategy(strategy.id, !strategy.is_active)
    if (success) {
      toast({
        title: strategy.is_active ? '전략 비활성화' : '전략 활성화',
        description: `${strategy.name}이(가) ${strategy.is_active ? '비활성화' : '활성화'}되었습니다.`
      })
      loadStrategies()
    }
  }

  const handleExecuteStrategy = async (strategy: Strategy) => {
    setLoading(true)
    const execution = await strategyService.executeStrategy(strategy.id)
    if (execution) {
      toast({
        title: '전략 실행 완료',
        description: `스캔: ${execution.scanned_stocks}개, 신호: ${execution.signals_generated}개`
      })
      loadSignals()
    }
    setLoading(false)
  }

  const handleStrategyCreated = (strategy: Strategy) => {
    setShowCreator(false)
    loadStrategies()
    toast({
      title: '전략 생성 완료',
      description: `${strategy.name}이(가) 생성되었습니다.`
    })
  }

  // 전체 통계 계산
  const totalStats = {
    activeStrategies: strategies.filter(s => s.is_active).length,
    totalPositions: positions.length,
    totalProfit: positions.reduce((sum, p) => sum + (p.unrealized_pnl || 0), 0),
    todaySignals: signals.filter(s => {
      const today = new Date().toDateString()
      return new Date(s.created_at).toDateString() === today
    }).length
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">전략 대시보드</h1>
          <p className="text-muted-foreground mt-1">
            자동매매 전략을 관리하고 실시간으로 모니터링합니다
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={loadStrategies}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button onClick={() => setShowCreator(true)}>
            <Plus className="mr-2 h-4 w-4" />
            새 전략
          </Button>
        </div>
      </div>

      {/* 전체 통계 */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 전략</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.activeStrategies}</div>
            <p className="text-xs text-muted-foreground">
              전체 {strategies.length}개 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">보유 포지션</CardTitle>
            <ChartBar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.totalPositions}</div>
            <p className="text-xs text-muted-foreground">
              실시간 모니터링 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평가 손익</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={cn(
              "text-2xl font-bold",
              totalStats.totalProfit >= 0 ? "text-green-600" : "text-red-600"
            )}>
              {totalStats.totalProfit >= 0 ? '+' : ''}{totalStats.totalProfit.toLocaleString()}원
            </div>
            <p className="text-xs text-muted-foreground">
              미실현 손익
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 신호</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.todaySignals}</div>
            <p className="text-xs text-muted-foreground">
              매수/매도 신호
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">전략 목록</TabsTrigger>
          <TabsTrigger value="positions">포지션</TabsTrigger>
          <TabsTrigger value="signals">신호</TabsTrigger>
          <TabsTrigger value="performance">성과</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        {/* 전략 목록 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {strategies.map((strategy) => (
              <Card key={strategy.id} className={cn(
                "relative",
                strategy.is_active && "ring-2 ring-primary"
              )}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{strategy.name}</CardTitle>
                      <CardDescription>{strategy.description}</CardDescription>
                    </div>
                    <Badge variant={strategy.is_active ? "default" : "secondary"}>
                      {strategy.is_active ? "활성" : "비활성"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 전략 조건 표시 */}
                  <div className="space-y-2">
                    <div className="flex items-center text-sm">
                      <Target className="mr-2 h-4 w-4 text-green-500" />
                      <span>목표 수익: {strategy.conditions.exit.profit_target}%</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Shield className="mr-2 h-4 w-4 text-red-500" />
                      <span>손절선: {strategy.conditions.exit.stop_loss}%</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <DollarSign className="mr-2 h-4 w-4 text-blue-500" />
                      <span>포지션: {strategy.position_size}% (최대 {strategy.max_positions}개)</span>
                    </div>
                  </div>

                  {/* 성과 표시 */}
                  {strategy.total_trades && strategy.total_trades > 0 && (
                    <>
                      <Separator />
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div>
                          <p className="text-xs text-muted-foreground">거래</p>
                          <p className="font-semibold">{strategy.total_trades}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">승률</p>
                          <p className="font-semibold">{strategy.win_rate?.toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">수익</p>
                          <p className={cn(
                            "font-semibold",
                            (strategy.total_profit || 0) >= 0 ? "text-green-600" : "text-red-600"
                          )}>
                            {((strategy.total_profit || 0) / 1000).toFixed(0)}K
                          </p>
                        </div>
                      </div>
                    </>
                  )}

                  {/* 액션 버튼 */}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleStrategy(strategy)}
                    >
                      {strategy.is_active ? (
                        <>
                          <Pause className="mr-1 h-3 w-3" />
                          중지
                        </>
                      ) : (
                        <>
                          <Play className="mr-1 h-3 w-3" />
                          시작
                        </>
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExecuteStrategy(strategy)}
                      disabled={loading}
                    >
                      <Zap className="mr-1 h-3 w-3" />
                      실행
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedStrategy(strategy)}
                    >
                      <Settings className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* 전략 추가 카드 */}
            <Card 
              className="border-dashed cursor-pointer hover:border-primary transition-colors"
              onClick={() => setShowCreator(true)}
            >
              <CardContent className="flex flex-col items-center justify-center h-full min-h-[300px]">
                <Plus className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">새 전략 만들기</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 포지션 탭 */}
        <TabsContent value="positions">
          <PositionManager positions={positions} onRefresh={loadPositions} />
        </TabsContent>

        {/* 신호 탭 */}
        <TabsContent value="signals">
          <SignalMonitor signals={signals} strategies={strategies} />
        </TabsContent>

        {/* 성과 탭 */}
        <TabsContent value="performance">
          <StrategyPerformance strategies={strategies} />
        </TabsContent>

        {/* 설정 탭 */}
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>전략 설정</CardTitle>
              <CardDescription>
                전체 전략 시스템 설정을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  설정 기능은 준비 중입니다.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 전략 생성 모달 */}
      {showCreator && (
        <StrategyCreator
          onClose={() => setShowCreator(false)}
          onSave={handleStrategyCreated}
        />
      )}
    </div>
  )
}

export default StrategyDashboard