import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  X, 
  Plus, 
  Save,
  Info,
  TrendingUp,
  TrendingDown,
  Activity,
  ChartBar,
  Shield,
  Target,
  DollarSign,
  Clock,
  Zap
} from 'lucide-react'
import { strategyService, Strategy } from '@/services/strategyService'
import { useToast } from '@/components/ui/use-toast'

interface StrategyCreatorProps {
  onClose: () => void
  onSave: (strategy: Strategy) => void
  editStrategy?: Strategy
}

const INDICATORS = [
  { id: 'rsi', name: 'RSI', description: '상대강도지수' },
  { id: 'macd', name: 'MACD', description: '이동평균수렴발산' },
  { id: 'bollinger', name: '볼린저밴드', description: '변동성 지표' },
  { id: 'volume', name: '거래량', description: '거래량 기반' },
  { id: 'ma', name: '이동평균', description: '가격 평균' },
  { id: 'stochastic', name: '스토캐스틱', description: '과매수/과매도' }
]

const STOCK_LIST = [
  { code: '005930', name: '삼성전자' },
  { code: '000660', name: 'SK하이닉스' },
  { code: '035720', name: '카카오' },
  { code: '035420', name: 'NAVER' },
  { code: '051910', name: 'LG화학' },
  { code: '006400', name: '삼성SDI' },
  { code: '068270', name: '셀트리온' },
  { code: '005380', name: '현대차' },
  { code: '012330', name: '현대모비스' },
  { code: '066570', name: 'LG전자' }
]

const PRESET_STRATEGIES = [
  {
    name: 'RSI 과매도 전략',
    description: 'RSI 30 이하에서 매수, 70 이상에서 매도',
    conditions: {
      entry: { rsi: { operator: '<', value: 30 } },
      exit: { profit_target: 5, stop_loss: -3 }
    }
  },
  {
    name: '볼린저밴드 전략',
    description: '하단 밴드 터치시 매수, 상단 밴드 터치시 매도',
    conditions: {
      entry: { bollinger: { operator: 'touch_lower', value: 2 } },
      exit: { profit_target: 7, stop_loss: -4 }
    }
  },
  {
    name: '거래량 돌파 전략',
    description: '평균 거래량 2배 돌파시 매수',
    conditions: {
      entry: { volume: { operator: '>', value: 'avg_volume * 2' } },
      exit: { profit_target: 10, stop_loss: -5 }
    }
  }
]

const StrategyCreator: React.FC<StrategyCreatorProps> = ({ onClose, onSave, editStrategy }) => {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('basic')
  const [loading, setLoading] = useState(false)
  
  // 전략 상태
  const [strategy, setStrategy] = useState({
    name: editStrategy?.name || '',
    description: editStrategy?.description || '',
    conditions: editStrategy?.conditions || {
      entry: {},
      exit: {
        profit_target: 5,
        stop_loss: -3,
        trailing_stop: 0
      }
    },
    position_size: editStrategy?.position_size || 10,
    max_positions: editStrategy?.max_positions || 5,
    target_stocks: editStrategy?.target_stocks || [],
    execution_time: editStrategy?.execution_time || {
      start: '09:00',
      end: '15:20'
    }
  })

  // 선택된 지표들
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([])
  const [entryConditions, setEntryConditions] = useState<any[]>([])

  const handlePresetSelect = (preset: any) => {
    setStrategy({
      ...strategy,
      name: preset.name,
      description: preset.description,
      conditions: preset.conditions
    })
    toast({
      title: '프리셋 적용',
      description: `${preset.name} 설정이 적용되었습니다.`
    })
  }

  const handleAddIndicator = (indicatorId: string) => {
    if (!selectedIndicators.includes(indicatorId)) {
      setSelectedIndicators([...selectedIndicators, indicatorId])
    }
  }

  const handleRemoveIndicator = (indicatorId: string) => {
    setSelectedIndicators(selectedIndicators.filter(id => id !== indicatorId))
  }

  const handleAddStock = (stockCode: string) => {
    if (!strategy.target_stocks.includes(stockCode)) {
      setStrategy({
        ...strategy,
        target_stocks: [...strategy.target_stocks, stockCode]
      })
    }
  }

  const handleRemoveStock = (stockCode: string) => {
    setStrategy({
      ...strategy,
      target_stocks: strategy.target_stocks.filter(code => code !== stockCode)
    })
  }

  const handleSave = async () => {
    // 유효성 검사
    if (!strategy.name.trim()) {
      toast({
        title: '오류',
        description: '전략 이름을 입력해주세요.',
        variant: 'destructive'
      })
      return
    }

    setLoading(true)
    
    try {
      const savedStrategy = await strategyService.createStrategy(strategy)
      
      if (savedStrategy) {
        onSave(savedStrategy)
        toast({
          title: '성공',
          description: '전략이 저장되었습니다.'
        })
      } else {
        throw new Error('전략 저장 실패')
      }
    } catch (error) {
      toast({
        title: '오류',
        description: '전략 저장에 실패했습니다.',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            {editStrategy ? '전략 수정' : '새 전략 만들기'}
          </DialogTitle>
          <DialogDescription>
            자동매매 전략을 설정하고 백테스팅을 실행할 수 있습니다
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic">기본 정보</TabsTrigger>
            <TabsTrigger value="conditions">매매 조건</TabsTrigger>
            <TabsTrigger value="risk">리스크 관리</TabsTrigger>
            <TabsTrigger value="stocks">대상 종목</TabsTrigger>
          </TabsList>

          {/* 기본 정보 탭 */}
          <TabsContent value="basic" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">전략 이름</Label>
              <Input
                id="name"
                value={strategy.name}
                onChange={(e) => setStrategy({ ...strategy, name: e.target.value })}
                placeholder="예: RSI 과매도 전략"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">설명</Label>
              <Textarea
                id="description"
                value={strategy.description}
                onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
                placeholder="전략에 대한 설명을 입력하세요"
                rows={3}
              />
            </div>

            {/* 프리셋 전략 */}
            <div className="space-y-2">
              <Label>프리셋 전략 템플릿</Label>
              <div className="grid grid-cols-1 gap-2">
                {PRESET_STRATEGIES.map((preset, idx) => (
                  <Card 
                    key={idx} 
                    className="cursor-pointer hover:border-primary transition-colors"
                    onClick={() => handlePresetSelect(preset)}
                  >
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">{preset.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {preset.description}
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* 매매 조건 탭 */}
          <TabsContent value="conditions" className="space-y-4">
            {/* 지표 선택 */}
            <div className="space-y-2">
              <Label>기술적 지표</Label>
              <div className="grid grid-cols-2 gap-2">
                {INDICATORS.map((indicator) => (
                  <div
                    key={indicator.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedIndicators.includes(indicator.id) 
                        ? 'border-primary bg-primary/10' 
                        : 'hover:border-primary/50'
                    }`}
                    onClick={() => 
                      selectedIndicators.includes(indicator.id)
                        ? handleRemoveIndicator(indicator.id)
                        : handleAddIndicator(indicator.id)
                    }
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{indicator.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {indicator.description}
                        </p>
                      </div>
                      {selectedIndicators.includes(indicator.id) && (
                        <Badge variant="default">선택</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 진입 조건 설정 */}
            <div className="space-y-2">
              <Label>진입 조건 (매수)</Label>
              {selectedIndicators.includes('rsi') && (
                <div className="flex items-center gap-2">
                  <span className="text-sm">RSI</span>
                  <Select defaultValue="<">
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<">{'<'}</SelectItem>
                      <SelectItem value=">">{'>'}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input 
                    type="number" 
                    defaultValue="30" 
                    className="w-20"
                    onChange={(e) => setStrategy({
                      ...strategy,
                      conditions: {
                        ...strategy.conditions,
                        entry: {
                          ...strategy.conditions.entry,
                          rsi: { operator: '<', value: Number(e.target.value) }
                        }
                      }
                    })}
                  />
                </div>
              )}
              
              {selectedIndicators.includes('volume') && (
                <div className="flex items-center gap-2">
                  <span className="text-sm">거래량</span>
                  <Select defaultValue=">">
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<">{'<'}</SelectItem>
                      <SelectItem value=">">{'>'}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input 
                    defaultValue="avg_volume * 2" 
                    className="w-40"
                    placeholder="평균 거래량 * 2"
                    onChange={(e) => setStrategy({
                      ...strategy,
                      conditions: {
                        ...strategy.conditions,
                        entry: {
                          ...strategy.conditions.entry,
                          volume: { operator: '>', value: e.target.value }
                        }
                      }
                    })}
                  />
                </div>
              )}
            </div>
          </TabsContent>

          {/* 리스크 관리 탭 */}
          <TabsContent value="risk" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-green-500" />
                  목표 수익률 (%)
                </Label>
                <Slider
                  value={[strategy.conditions.exit.profit_target]}
                  onValueChange={([value]) => setStrategy({
                    ...strategy,
                    conditions: {
                      ...strategy.conditions,
                      exit: {
                        ...strategy.conditions.exit,
                        profit_target: value
                      }
                    }
                  })}
                  min={1}
                  max={20}
                  step={0.5}
                />
                <p className="text-sm text-muted-foreground text-center">
                  {strategy.conditions.exit.profit_target}%
                </p>
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-red-500" />
                  손절선 (%)
                </Label>
                <Slider
                  value={[Math.abs(strategy.conditions.exit.stop_loss)]}
                  onValueChange={([value]) => setStrategy({
                    ...strategy,
                    conditions: {
                      ...strategy.conditions,
                      exit: {
                        ...strategy.conditions.exit,
                        stop_loss: -value
                      }
                    }
                  })}
                  min={1}
                  max={10}
                  step={0.5}
                />
                <p className="text-sm text-muted-foreground text-center">
                  {strategy.conditions.exit.stop_loss}%
                </p>
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-blue-500" />
                  포지션 크기 (%)
                </Label>
                <Slider
                  value={[strategy.position_size]}
                  onValueChange={([value]) => setStrategy({
                    ...strategy,
                    position_size: value
                  })}
                  min={5}
                  max={30}
                  step={5}
                />
                <p className="text-sm text-muted-foreground text-center">
                  {strategy.position_size}%
                </p>
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  최대 보유 종목
                </Label>
                <Slider
                  value={[strategy.max_positions]}
                  onValueChange={([value]) => setStrategy({
                    ...strategy,
                    max_positions: value
                  })}
                  min={1}
                  max={10}
                  step={1}
                />
                <p className="text-sm text-muted-foreground text-center">
                  {strategy.max_positions}개
                </p>
              </div>
            </div>

            {/* 실행 시간 설정 */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                실행 시간
              </Label>
              <div className="flex gap-2 items-center">
                <Input
                  type="time"
                  value={strategy.execution_time.start}
                  onChange={(e) => setStrategy({
                    ...strategy,
                    execution_time: {
                      ...strategy.execution_time,
                      start: e.target.value
                    }
                  })}
                />
                <span>~</span>
                <Input
                  type="time"
                  value={strategy.execution_time.end}
                  onChange={(e) => setStrategy({
                    ...strategy,
                    execution_time: {
                      ...strategy.execution_time,
                      end: e.target.value
                    }
                  })}
                />
              </div>
            </div>
          </TabsContent>

          {/* 대상 종목 탭 */}
          <TabsContent value="stocks" className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                종목을 선택하지 않으면 전체 시장을 대상으로 스캔합니다.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label>대상 종목 선택</Label>
              <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
                {STOCK_LIST.map((stock) => (
                  <div
                    key={stock.code}
                    className={`p-2 border rounded cursor-pointer transition-colors text-sm ${
                      strategy.target_stocks.includes(stock.code)
                        ? 'border-primary bg-primary/10'
                        : 'hover:border-primary/50'
                    }`}
                    onClick={() => 
                      strategy.target_stocks.includes(stock.code)
                        ? handleRemoveStock(stock.code)
                        : handleAddStock(stock.code)
                    }
                  >
                    {stock.name} ({stock.code})
                  </div>
                ))}
              </div>
            </div>

            {strategy.target_stocks.length > 0 && (
              <div className="space-y-2">
                <Label>선택된 종목 ({strategy.target_stocks.length}개)</Label>
                <div className="flex flex-wrap gap-2">
                  {strategy.target_stocks.map((code) => {
                    const stock = STOCK_LIST.find(s => s.code === code)
                    return (
                      <Badge key={code} variant="secondary">
                        {stock?.name || code}
                        <X
                          className="ml-1 h-3 w-3 cursor-pointer"
                          onClick={() => handleRemoveStock(code)}
                        />
                      </Badge>
                    )
                  })}
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* 액션 버튼 */}
        <div className="flex justify-between items-center pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            취소
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" disabled>
              <ChartBar className="mr-2 h-4 w-4" />
              백테스트
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              <Save className="mr-2 h-4 w-4" />
              {loading ? '저장 중...' : '전략 저장'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default StrategyCreator