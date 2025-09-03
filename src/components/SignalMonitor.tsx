import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity,
  Clock,
  RefreshCw,
  Bell,
  BellOff,
  ChevronUp,
  ChevronDown,
  Zap
} from 'lucide-react'
import { TradingSignal, Strategy } from '@/services/strategyService'
import { cn } from '@/lib/utils'

interface SignalMonitorProps {
  signals: TradingSignal[]
  strategies: Strategy[]
  onRefresh?: () => void
}

const SignalMonitor: React.FC<SignalMonitorProps> = ({ signals, strategies, onRefresh }) => {
  const [filterStrategy, setFilterStrategy] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [notifications, setNotifications] = useState(true)
  const [expandedSignals, setExpandedSignals] = useState<Set<string>>(new Set())

  const filteredSignals = signals.filter(signal => {
    if (filterStrategy !== 'all' && signal.strategy_id !== filterStrategy) return false
    if (filterType !== 'all' && signal.signal_type !== filterType) return false
    return true
  })

  const toggleExpand = (signalId: string) => {
    const newExpanded = new Set(expandedSignals)
    if (newExpanded.has(signalId)) {
      newExpanded.delete(signalId)
    } else {
      newExpanded.add(signalId)
    }
    setExpandedSignals(newExpanded)
  }

  const getSignalColor = (strength: number) => {
    if (strength >= 0.8) return 'text-green-600'
    if (strength >= 0.6) return 'text-blue-600'
    if (strength >= 0.4) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'BUY':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'SELL':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return '방금 전'
    if (minutes < 60) return `${minutes}분 전`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}시간 전`
    return `${Math.floor(hours / 24)}일 전`
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>실시간 매매 신호</CardTitle>
              <CardDescription>
                전략별 매수/매도 신호를 실시간으로 모니터링합니다
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setNotifications(!notifications)}
              >
                {notifications ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              </Button>
              <Button variant="outline" size="icon" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Select value={filterStrategy} onValueChange={setFilterStrategy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="전략 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">모든 전략</SelectItem>
                {strategies.map(strategy => (
                  <SelectItem key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="신호 타입" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="BUY">매수</SelectItem>
                <SelectItem value="SELL">매도</SelectItem>
                <SelectItem value="HOLD">보류</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <ScrollArea className="h-[600px]">
            {filteredSignals.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
                <Activity className="h-8 w-8 mb-2" />
                <p>신호가 없습니다</p>
              </div>
            ) : (
              <div className="divide-y">
                {filteredSignals.map((signal) => {
                  const strategy = strategies.find(s => s.id === signal.strategy_id)
                  const isExpanded = expandedSignals.has(signal.id)
                  
                  return (
                    <div key={signal.id} className="p-4 hover:bg-muted/50 transition-colors">
                      <div 
                        className="flex items-start justify-between cursor-pointer"
                        onClick={() => toggleExpand(signal.id)}
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {getSignalIcon(signal.signal_type)}
                            <span className="font-semibold">
                              {signal.stock_name || signal.stock_code}
                            </span>
                            <Badge 
                              variant={signal.signal_type === 'BUY' ? 'default' : 'destructive'}
                              className="text-xs"
                            >
                              {signal.signal_type}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {strategy?.name || '알 수 없음'}
                            </Badge>
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span>현재가: {signal.current_price?.toLocaleString()}원</span>
                            <span>거래량: {signal.volume?.toLocaleString()}</span>
                            <span className={cn('font-medium', getSignalColor(signal.signal_strength))}>
                              강도: {(signal.signal_strength * 100).toFixed(0)}%
                            </span>
                          </div>

                          <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            <span>{formatTime(signal.created_at)}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10">
                            <Zap className={cn(
                              'h-5 w-5',
                              signal.signal_strength >= 0.8 ? 'text-green-600' :
                              signal.signal_strength >= 0.6 ? 'text-blue-600' :
                              signal.signal_strength >= 0.4 ? 'text-yellow-600' :
                              'text-gray-600'
                            )} />
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-muted-foreground" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>

                      {isExpanded && signal.indicators && (
                        <div className="mt-4 p-3 bg-muted/30 rounded-lg">
                          <h4 className="text-sm font-medium mb-2">기술적 지표</h4>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(signal.indicators).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground">{key}:</span>
                                <span className="font-medium">
                                  {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-muted-foreground">실시간 연결됨</span>
            </div>
            <span className="text-muted-foreground">
              총 {filteredSignals.length}개 신호
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SignalMonitor