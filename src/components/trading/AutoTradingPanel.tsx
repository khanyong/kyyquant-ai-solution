import React, { useState } from 'react'
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Paper,
  Stack,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material'
import {
  Add,
  Delete,
  Edit,
  PlayArrow,
  Stop,
  Settings
} from '@mui/icons-material'
import {
  TradingStrategy,
  startAutoTrading,
  stopAutoTrading,
  registerStrategy,
  unregisterStrategy,
  exampleStrategies
} from '../../services/autoTrading'

interface AutoTradingPanelProps {
  strategies?: any[]
}

const AutoTradingPanel: React.FC<AutoTradingPanelProps> = ({ strategies: externalStrategies }) => {
  const [autoTradingEnabled, setAutoTradingEnabled] = useState(false)
  const [strategies, setStrategies] = useState<TradingStrategy[]>(exampleStrategies)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingStrategy, setEditingStrategy] = useState<TradingStrategy | null>(null)
  
  // 외부에서 전달된 전략이 있으면 추가
  React.useEffect(() => {
    if (externalStrategies && externalStrategies.length > 0) {
      const newStrategies = externalStrategies.map((s, index) => ({
        id: `external-${Date.now()}-${index}`,
        name: s.name || '전략빌더 전략',
        description: s.description || '전략빌더에서 생성된 전략',
        type: 'technical' as const,
        enabled: true,
        parameters: {
          symbol: s.symbol || 'AUTO',
          ...s
        }
      }))
      setStrategies(prev => [...prev, ...newStrategies])
    }
  }, [externalStrategies])

  const handleAutoTradingToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked
    setAutoTradingEnabled(enabled)
    
    if (enabled) {
      startAutoTrading()
    } else {
      stopAutoTrading()
    }
  }

  const handleStrategyToggle = (strategyId: string) => {
    setStrategies(prev => prev.map(s => {
      if (s.id === strategyId) {
        const updated = { ...s, enabled: !s.enabled }
        if (updated.enabled) {
          registerStrategy(updated)
        } else {
          unregisterStrategy(strategyId)
        }
        return updated
      }
      return s
    }))
  }

  const handleAddStrategy = () => {
    setEditingStrategy({
      id: `strategy_${Date.now()}`,
      name: '',
      enabled: false,
      stockCode: '',
      conditions: [{ type: 'price_below', value: 0 }],
      action: { type: 'buy', quantity: 1, orderMethod: 'limit' }
    })
    setDialogOpen(true)
  }

  const handleEditStrategy = (strategy: TradingStrategy) => {
    setEditingStrategy(strategy)
    setDialogOpen(true)
  }

  const handleDeleteStrategy = (strategyId: string) => {
    unregisterStrategy(strategyId)
    setStrategies(prev => prev.filter(s => s.id !== strategyId))
  }

  const handleSaveStrategy = () => {
    if (!editingStrategy) return

    setStrategies(prev => {
      const exists = prev.find(s => s.id === editingStrategy.id)
      if (exists) {
        return prev.map(s => s.id === editingStrategy.id ? editingStrategy : s)
      } else {
        return [...prev, editingStrategy]
      }
    })

    if (editingStrategy.enabled && autoTradingEnabled) {
      registerStrategy(editingStrategy)
    }

    setDialogOpen(false)
    setEditingStrategy(null)
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">
          자동매매 설정
        </Typography>
        
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={autoTradingEnabled}
                onChange={handleAutoTradingToggle}
                color="primary"
              />
            }
            label={autoTradingEnabled ? "자동매매 ON" : "자동매매 OFF"}
          />
          
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddStrategy}
            size="small"
          >
            전략 추가
          </Button>
        </Stack>
      </Stack>

      {!autoTradingEnabled && (
        <Alert severity="info" sx={{ mb: 2 }}>
          자동매매가 비활성화되어 있습니다. 스위치를 켜서 자동매매를 시작하세요.
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>상태</TableCell>
              <TableCell>전략명</TableCell>
              <TableCell>종목</TableCell>
              <TableCell>조건</TableCell>
              <TableCell>동작</TableCell>
              <TableCell align="center">관리</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {strategies.map((strategy) => (
              <TableRow key={strategy.id}>
                <TableCell>
                  <Switch
                    checked={strategy.enabled}
                    onChange={() => handleStrategyToggle(strategy.id)}
                    disabled={!autoTradingEnabled}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{strategy.name}</Typography>
                </TableCell>
                <TableCell>
                  <Chip label={strategy.stockCode} size="small" />
                </TableCell>
                <TableCell>
                  {strategy.conditions.map((cond, idx) => (
                    <Typography key={idx} variant="caption" display="block">
                      {cond.type}: {cond.value.toLocaleString()}
                    </Typography>
                  ))}
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${strategy.action.type === 'buy' ? '매수' : '매도'} ${strategy.action.quantity}주`}
                    color={strategy.action.type === 'buy' ? 'error' : 'primary'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="center">
                  <IconButton size="small" onClick={() => handleEditStrategy(strategy)}>
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDeleteStrategy(strategy.id)}>
                    <Delete fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 전략 편집 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingStrategy?.name ? '전략 수정' : '새 전략 추가'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              label="전략명"
              value={editingStrategy?.name || ''}
              onChange={(e) => setEditingStrategy(prev => prev ? {...prev, name: e.target.value} : null)}
              fullWidth
            />
            
            <TextField
              label="종목코드"
              value={editingStrategy?.stockCode || ''}
              onChange={(e) => setEditingStrategy(prev => prev ? {...prev, stockCode: e.target.value} : null)}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>조건 타입</InputLabel>
              <Select
                value={editingStrategy?.conditions[0]?.type || 'price_below'}
                onChange={(e) => setEditingStrategy(prev => prev ? {
                  ...prev, 
                  conditions: [{...prev.conditions[0], type: e.target.value as any}]
                } : null)}
              >
                <MenuItem value="price_below">가격 이하</MenuItem>
                <MenuItem value="price_above">가격 이상</MenuItem>
                <MenuItem value="volume_above">거래량 이상</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="조건 값"
              type="number"
              value={editingStrategy?.conditions[0]?.value || 0}
              onChange={(e) => setEditingStrategy(prev => prev ? {
                ...prev,
                conditions: [{...prev.conditions[0], value: Number(e.target.value)}]
              } : null)}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>동작</InputLabel>
              <Select
                value={editingStrategy?.action.type || 'buy'}
                onChange={(e) => setEditingStrategy(prev => prev ? {
                  ...prev,
                  action: {...prev.action, type: e.target.value as 'buy' | 'sell'}
                } : null)}
              >
                <MenuItem value="buy">매수</MenuItem>
                <MenuItem value="sell">매도</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="수량"
              type="number"
              value={editingStrategy?.action.quantity || 1}
              onChange={(e) => setEditingStrategy(prev => prev ? {
                ...prev,
                action: {...prev.action, quantity: Number(e.target.value)}
              } : null)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button onClick={handleSaveStrategy} variant="contained">저장</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default AutoTradingPanel