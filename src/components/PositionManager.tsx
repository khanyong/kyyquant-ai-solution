import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  AlertTriangle,
  Target,
  Shield,
  Clock,
  RefreshCw
} from 'lucide-react'
import { Position } from '@/services/strategyService'
import { cn } from '@/lib/utils'

interface PositionManagerProps {
  positions: Position[]
  onRefresh?: () => void
}

const PositionManager: React.FC<PositionManagerProps> = ({ positions, onRefresh }) => {
  const totalValue = positions.reduce((sum, pos) => sum + (pos.quantity * pos.current_price), 0)
  const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0)
  const totalPnLRate = totalValue > 0 ? (totalPnL / totalValue) * 100 : 0

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  return (
    <div className="space-y-4">
      {/* 전체 요약 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>포지션 현황</CardTitle>
              <CardDescription>
                현재 보유중인 포지션과 실시간 손익을 확인합니다
              </CardDescription>
            </div>
            <Button variant="outline" size="icon" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">보유 종목</p>
              <p className="text-2xl font-bold">{positions.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">평가 금액</p>
              <p className="text-2xl font-bold">{(totalValue / 1000000).toFixed(1)}M</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">평가 손익</p>
              <p className={cn(
                "text-2xl font-bold",
                totalPnL >= 0 ? "text-green-600" : "text-red-600"
              )}>
                {totalPnL >= 0 ? '+' : ''}{(totalPnL / 1000).toFixed(0)}K
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">수익률</p>
              <p className={cn(
                "text-2xl font-bold",
                totalPnLRate >= 0 ? "text-green-600" : "text-red-600"
              )}>
                {totalPnLRate >= 0 ? '+' : ''}{totalPnLRate.toFixed(2)}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 포지션 목록 */}
      {positions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center h-48 text-muted-foreground">
            <DollarSign className="h-8 w-8 mb-2" />
            <p>보유 포지션이 없습니다</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {positions.map((position) => {
            const pnlRate = position.unrealized_pnl_rate
            const progressToTarget = position.target_price 
              ? ((position.current_price - position.avg_price) / (position.target_price - position.avg_price)) * 100
              : 0
            const progressToStopLoss = position.stop_loss_price
              ? ((position.avg_price - position.current_price) / (position.avg_price - position.stop_loss_price)) * 100
              : 0

            return (
              <Card key={position.id} className="relative">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">
                        {position.stock_name}
                      </CardTitle>
                      <CardDescription className="text-xs">
                        {position.stock_code}
                      </CardDescription>
                    </div>
                    <Badge variant={pnlRate >= 0 ? "default" : "destructive"}>
                      {pnlRate >= 0 ? '+' : ''}{pnlRate.toFixed(2)}%
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* 수량 및 가격 정보 */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">보유:</span>
                      <span className="ml-2 font-medium">{position.quantity}주</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">평단:</span>
                      <span className="ml-2 font-medium">{position.avg_price.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">현재:</span>
                      <span className="ml-2 font-medium">{position.current_price.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">평가:</span>
                      <span className="ml-2 font-medium">
                        {(position.quantity * position.current_price).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* 손익 표시 */}
                  <div className="flex justify-between items-center p-2 bg-muted/50 rounded">
                    <div className="flex items-center gap-2">
                      {pnlRate >= 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      )}
                      <span className="text-sm">손익:</span>
                    </div>
                    <span className={cn(
                      "font-bold",
                      pnlRate >= 0 ? "text-green-600" : "text-red-600"
                    )}>
                      {position.unrealized_pnl >= 0 ? '+' : ''}{position.unrealized_pnl.toLocaleString()}원
                    </span>
                  </div>

                  {/* 목표가/손절선 진행 상황 */}
                  {position.target_price && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1">
                          <Target className="h-3 w-3 text-green-500" />
                          <span>목표가 {position.target_price.toLocaleString()}</span>
                        </div>
                        <span>{Math.min(100, Math.max(0, progressToTarget)).toFixed(0)}%</span>
                      </div>
                      <Progress 
                        value={Math.min(100, Math.max(0, progressToTarget))} 
                        className="h-1"
                      />
                    </div>
                  )}

                  {position.stop_loss_price && progressToStopLoss > 0 && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1">
                          <Shield className="h-3 w-3 text-red-500" />
                          <span>손절선 {position.stop_loss_price.toLocaleString()}</span>
                        </div>
                        <span className="text-red-600">
                          {Math.min(100, Math.max(0, progressToStopLoss)).toFixed(0)}%
                        </span>
                      </div>
                      <Progress 
                        value={Math.min(100, Math.max(0, progressToStopLoss))} 
                        className="h-1 [&>div]:bg-red-500"
                      />
                      {progressToStopLoss > 80 && (
                        <div className="flex items-center gap-1 text-xs text-red-600">
                          <AlertTriangle className="h-3 w-3" />
                          <span>손절선 근접 주의</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* 진입 시간 */}
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>진입: {formatTime(position.entry_time)}</span>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default PositionManager