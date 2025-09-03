import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  TrendingDown,
  Activity,
  DollarSign,
  Target,
  Shield,
  Award,
  AlertCircle,
  BarChart3,
  LineChart,
  PieChart
} from 'lucide-react'
import { Strategy, strategyService } from '@/services/strategyService'
import { cn } from '@/lib/utils'

interface StrategyPerformanceProps {
  strategies: Strategy[]
}

interface PerformanceData {
  totalProfit: number
  winCount: number
  loseCount: number
  totalTrades: number
  winRate: number
  activePositions: number
}

const StrategyPerformance: React.FC<StrategyPerformanceProps> = ({ strategies }) => {
  const [selectedStrategy, setSelectedStrategy] = useState<string>('all')
  const [performanceData, setPerformanceData] = useState<{ [key: string]: PerformanceData }>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPerformanceData()
  }, [strategies])

  const loadPerformanceData = async () => {
    setLoading(true)
    const data: { [key: string]: PerformanceData } = {}
    
    for (const strategy of strategies) {
      const performance = await strategyService.getPerformance(strategy.id)
      if (performance) {
        data[strategy.id] = performance
      }
    }
    
    // 전체 통계 계산
    const allPerformance: PerformanceData = {
      totalProfit: Object.values(data).reduce((sum, p) => sum + p.totalProfit, 0),
      winCount: Object.values(data).reduce((sum, p) => sum + p.winCount, 0),
      loseCount: Object.values(data).reduce((sum, p) => sum + p.loseCount, 0),
      totalTrades: Object.values(data).reduce((sum, p) => sum + p.totalTrades, 0),
      winRate: 0,
      activePositions: Object.values(data).reduce((sum, p) => sum + p.activePositions, 0)
    }
    
    if (allPerformance.totalTrades > 0) {
      allPerformance.winRate = (allPerformance.winCount / allPerformance.totalTrades) * 100
    }
    
    data['all'] = allPerformance
    setPerformanceData(data)
    setLoading(false)
  }

  const currentPerformance = performanceData[selectedStrategy] || performanceData['all'] || {
    totalProfit: 0,
    winCount: 0,
    loseCount: 0,
    totalTrades: 0,
    winRate: 0,
    activePositions: 0
  }

  // 최고 성과 전략 찾기
  const topStrategy = strategies.reduce((best, strategy) => {
    const perf = performanceData[strategy.id]
    const bestPerf = performanceData[best?.id || '']
    
    if (!perf) return best
    if (!bestPerf) return strategy
    
    return perf.totalProfit > bestPerf.totalProfit ? strategy : best
  }, strategies[0])

  const topStrategyPerf = performanceData[topStrategy?.id || '']

  return (
    <div className="space-y-4">
      {/* 전략 선택 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>전략 성과 분석</CardTitle>
              <CardDescription>
                전략별 수익률과 거래 통계를 확인합니다
              </CardDescription>
            </div>
            <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="전략 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 전략</SelectItem>
                {strategies.map(strategy => (
                  <SelectItem key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
      </Card>

      {/* 주요 지표 */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 수익</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={cn(
              "text-2xl font-bold",
              currentPerformance.totalProfit >= 0 ? "text-green-600" : "text-red-600"
            )}>
              {currentPerformance.totalProfit >= 0 ? '+' : ''}
              {(currentPerformance.totalProfit / 1000).toFixed(0)}K
            </div>
            <p className="text-xs text-muted-foreground">
              누적 실현 손익
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">승률</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currentPerformance.winRate.toFixed(1)}%
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              <span className="text-green-600">{currentPerformance.winCount}승</span>
              <span className="mx-1">/</span>
              <span className="text-red-600">{currentPerformance.loseCount}패</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 거래</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currentPerformance.totalTrades}
            </div>
            <p className="text-xs text-muted-foreground">
              완료된 거래 횟수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 포지션</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currentPerformance.activePositions}
            </div>
            <p className="text-xs text-muted-foreground">
              현재 보유 종목
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="ranking">전략 순위</TabsTrigger>
          <TabsTrigger value="analysis">상세 분석</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview">
          <div className="grid gap-4 md:grid-cols-2">
            {/* 최고 성과 전략 */}
            {topStrategy && topStrategyPerf && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-yellow-500" />
                    최고 성과 전략
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <h3 className="font-semibold text-lg">{topStrategy.name}</h3>
                      <p className="text-sm text-muted-foreground">{topStrategy.description}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">수익:</span>
                        <span className={cn(
                          "ml-2 font-medium",
                          topStrategyPerf.totalProfit >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {topStrategyPerf.totalProfit >= 0 ? '+' : ''}
                          {topStrategyPerf.totalProfit.toLocaleString()}원
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">승률:</span>
                        <span className="ml-2 font-medium">{topStrategyPerf.winRate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 수익 분포 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  수익 분포
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {strategies.slice(0, 5).map(strategy => {
                    const perf = performanceData[strategy.id]
                    if (!perf) return null
                    
                    const profitRate = performanceData['all']?.totalProfit 
                      ? (perf.totalProfit / performanceData['all'].totalProfit) * 100
                      : 0

                    return (
                      <div key={strategy.id} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="truncate">{strategy.name}</span>
                          <span className={cn(
                            "font-medium",
                            perf.totalProfit >= 0 ? "text-green-600" : "text-red-600"
                          )}>
                            {perf.totalProfit >= 0 ? '+' : ''}{(perf.totalProfit / 1000).toFixed(0)}K
                          </span>
                        </div>
                        <Progress 
                          value={Math.abs(profitRate)} 
                          className="h-2"
                        />
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 전략 순위 탭 */}
        <TabsContent value="ranking">
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b">
                    <tr className="text-left">
                      <th className="p-4 font-medium">순위</th>
                      <th className="p-4 font-medium">전략명</th>
                      <th className="p-4 font-medium">총 수익</th>
                      <th className="p-4 font-medium">승률</th>
                      <th className="p-4 font-medium">거래 횟수</th>
                      <th className="p-4 font-medium">상태</th>
                    </tr>
                  </thead>
                  <tbody>
                    {strategies
                      .sort((a, b) => {
                        const perfA = performanceData[a.id]?.totalProfit || 0
                        const perfB = performanceData[b.id]?.totalProfit || 0
                        return perfB - perfA
                      })
                      .map((strategy, index) => {
                        const perf = performanceData[strategy.id]
                        
                        return (
                          <tr key={strategy.id} className="border-b hover:bg-muted/50">
                            <td className="p-4">
                              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                                {index + 1}
                              </div>
                            </td>
                            <td className="p-4">
                              <div>
                                <p className="font-medium">{strategy.name}</p>
                                <p className="text-xs text-muted-foreground">{strategy.description}</p>
                              </div>
                            </td>
                            <td className="p-4">
                              <span className={cn(
                                "font-medium",
                                (perf?.totalProfit || 0) >= 0 ? "text-green-600" : "text-red-600"
                              )}>
                                {(perf?.totalProfit || 0) >= 0 ? '+' : ''}
                                {((perf?.totalProfit || 0) / 1000).toFixed(0)}K
                              </span>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                <span>{perf?.winRate.toFixed(1) || 0}%</span>
                                {perf && perf.winRate >= 60 && (
                                  <Badge variant="default" className="text-xs">우수</Badge>
                                )}
                              </div>
                            </td>
                            <td className="p-4">{perf?.totalTrades || 0}</td>
                            <td className="p-4">
                              <Badge variant={strategy.is_active ? "default" : "secondary"}>
                                {strategy.is_active ? "활성" : "비활성"}
                              </Badge>
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 상세 분석 탭 */}
        <TabsContent value="analysis">
          <Card>
            <CardHeader>
              <CardTitle>상세 분석</CardTitle>
              <CardDescription>
                선택한 전략의 상세 통계와 분석 정보
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  상세 분석 차트는 준비 중입니다.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default StrategyPerformance