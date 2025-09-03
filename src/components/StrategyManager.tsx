import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign,
  Play,
  Pause,
  Settings,
  ChartBar,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  conditions: {
    entry: {
      rsi?: { operator: string; value: number };
      volume?: { operator: string; value: string };
      price?: { operator: string; value: string };
    };
    exit: {
      profit_target: number;
      stop_loss: number;
    };
  };
  position_size: number;
  max_positions: number;
  total_trades: number;
  win_rate: number;
  total_profit: number;
}

const StrategyManager: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 새 전략 폼 상태
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    rsi_operator: '<',
    rsi_value: 30,
    volume_operator: '>',
    volume_value: 'avg_volume * 2',
    profit_target: 5,
    stop_loss: -3,
    position_size: 10,
    max_positions: 5,
    target_stocks: [] as string[]
  });

  const API_URL = 'http://localhost:8001';

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await fetch(`${API_URL}/api/strategies`);
      const data = await response.json();
      if (data.success) {
        setStrategies(data.strategies);
      }
    } catch (error) {
      console.error('전략 조회 실패:', error);
    }
  };

  const createStrategy = async () => {
    setLoading(true);
    try {
      const strategyData = {
        name: newStrategy.name,
        description: newStrategy.description,
        conditions: {
          entry: {
            rsi: {
              operator: newStrategy.rsi_operator,
              value: newStrategy.rsi_value
            },
            volume: {
              operator: newStrategy.volume_operator,
              value: newStrategy.volume_value
            }
          },
          exit: {
            profit_target: newStrategy.profit_target,
            stop_loss: newStrategy.stop_loss
          }
        },
        position_size: newStrategy.position_size,
        max_positions: newStrategy.max_positions,
        target_stocks: newStrategy.target_stocks
      };

      const response = await fetch(`${API_URL}/api/strategies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategyData)
      });

      const data = await response.json();
      if (data.success) {
        setMessage('전략이 생성되었습니다');
        fetchStrategies();
        setIsCreating(false);
      }
    } catch (error) {
      setMessage('전략 생성 실패');
    } finally {
      setLoading(false);
    }
  };

  const toggleStrategy = async (strategyId: string, isActive: boolean) => {
    const endpoint = isActive ? 'activate' : 'deactivate';
    try {
      const response = await fetch(`${API_URL}/api/strategies/${strategyId}/${endpoint}`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        setMessage(data.message);
        fetchStrategies();
      }
    } catch (error) {
      setMessage('상태 변경 실패');
    }
  };

  const executeStrategy = async (strategyId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/strategies/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: strategyId,
          test_mode: true
        })
      });

      const data = await response.json();
      if (data.success) {
        setMessage(data.message);
      }
    } catch (error) {
      setMessage('실행 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">전략 관리</h1>
        <Button onClick={() => setIsCreating(true)} variant="default">
          새 전략 만들기
        </Button>
      </div>

      {message && (
        <Alert className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="list" className="w-full">
        <TabsList>
          <TabsTrigger value="list">전략 목록</TabsTrigger>
          <TabsTrigger value="performance">성과 분석</TabsTrigger>
          <TabsTrigger value="positions">포지션</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          {/* 전략 목록 */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {strategies.map((strategy) => (
              <Card key={strategy.id}>
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
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">총 거래</span>
                      <span>{strategy.total_trades || 0}회</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">승률</span>
                      <span className="font-medium">
                        {strategy.win_rate || 0}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">총 수익</span>
                      <span className={strategy.total_profit > 0 ? "text-green-600" : "text-red-600"}>
                        {strategy.total_profit?.toLocaleString() || 0}원
                      </span>
                    </div>

                    <div className="flex gap-2 pt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleStrategy(strategy.id, !strategy.is_active)}
                      >
                        {strategy.is_active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => executeStrategy(strategy.id)}
                        disabled={loading}
                      >
                        실행
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setSelectedStrategy(strategy)}
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>성과 분석</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground">
                성과 차트가 여기에 표시됩니다
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="positions">
          <Card>
            <CardHeader>
              <CardTitle>현재 포지션</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground">
                보유 포지션이 여기에 표시됩니다
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 새 전략 생성 다이얼로그 */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-auto">
            <CardHeader>
              <CardTitle>새 전략 만들기</CardTitle>
              <CardDescription>거래 전략을 설정하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>전략 이름</Label>
                <Input
                  value={newStrategy.name}
                  onChange={(e) => setNewStrategy({...newStrategy, name: e.target.value})}
                  placeholder="예: RSI 과매도 전략"
                />
              </div>

              <div className="space-y-2">
                <Label>설명</Label>
                <Input
                  value={newStrategy.description}
                  onChange={(e) => setNewStrategy({...newStrategy, description: e.target.value})}
                  placeholder="전략 설명"
                />
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">진입 조건</h3>
                
                <div className="flex gap-2 items-center">
                  <Label className="w-20">RSI</Label>
                  <Select 
                    value={newStrategy.rsi_operator}
                    onValueChange={(value) => setNewStrategy({...newStrategy, rsi_operator: value})}
                  >
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<">{'<'}</SelectItem>
                      <SelectItem value=">">{'>'}</SelectItem>
                      <SelectItem value="<=">{'<='}</SelectItem>
                      <SelectItem value=">=">{'>='}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    type="number"
                    value={newStrategy.rsi_value}
                    onChange={(e) => setNewStrategy({...newStrategy, rsi_value: Number(e.target.value)})}
                    className="w-20"
                  />
                </div>

                <div className="flex gap-2 items-center">
                  <Label className="w-20">거래량</Label>
                  <Select
                    value={newStrategy.volume_operator}
                    onValueChange={(value) => setNewStrategy({...newStrategy, volume_operator: value})}
                  >
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<">{'<'}</SelectItem>
                      <SelectItem value=">">{'>'}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    value={newStrategy.volume_value}
                    onChange={(e) => setNewStrategy({...newStrategy, volume_value: e.target.value})}
                    placeholder="avg_volume * 2"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">청산 조건</h3>
                
                <div className="space-y-2">
                  <Label>목표 수익률 (%)</Label>
                  <Slider
                    value={[newStrategy.profit_target]}
                    onValueChange={([value]) => setNewStrategy({...newStrategy, profit_target: value})}
                    min={1}
                    max={20}
                    step={0.5}
                  />
                  <span className="text-sm text-muted-foreground">{newStrategy.profit_target}%</span>
                </div>

                <div className="space-y-2">
                  <Label>손절선 (%)</Label>
                  <Slider
                    value={[Math.abs(newStrategy.stop_loss)]}
                    onValueChange={([value]) => setNewStrategy({...newStrategy, stop_loss: -value})}
                    min={1}
                    max={10}
                    step={0.5}
                  />
                  <span className="text-sm text-muted-foreground">{newStrategy.stop_loss}%</span>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">리스크 관리</h3>
                
                <div className="space-y-2">
                  <Label>포지션 크기 (%)</Label>
                  <Slider
                    value={[newStrategy.position_size]}
                    onValueChange={([value]) => setNewStrategy({...newStrategy, position_size: value})}
                    min={5}
                    max={30}
                    step={5}
                  />
                  <span className="text-sm text-muted-foreground">{newStrategy.position_size}%</span>
                </div>

                <div className="space-y-2">
                  <Label>최대 보유 종목</Label>
                  <Input
                    type="number"
                    value={newStrategy.max_positions}
                    onChange={(e) => setNewStrategy({...newStrategy, max_positions: Number(e.target.value)})}
                    min={1}
                    max={10}
                  />
                </div>
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <Button variant="outline" onClick={() => setIsCreating(false)}>
                  취소
                </Button>
                <Button onClick={createStrategy} disabled={loading}>
                  {loading ? "생성 중..." : "전략 생성"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default StrategyManager;