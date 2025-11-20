import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Stack,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  Refresh,
  Cancel,
  TrendingUp,
  TrendingDown,
  AccessTime
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'

interface Order {
  id: string
  stock_code: string
  order_type: 'BUY' | 'SELL'
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'PARTIAL'
  order_price: number
  quantity: number
  executed_price?: number
  executed_quantity?: number
  kiwoom_order_no?: string
  created_at: string
  updated_at: string
  stock_name?: string
}

export default function PendingOrdersPanel() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadPendingOrders()

    // Realtime 구독
    const channel = supabase
      .channel('orders_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'orders'
        },
        (payload) => {
          console.log('📦 Order changed:', payload)
          loadPendingOrders()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const loadPendingOrders = async () => {
    try {
      setRefreshing(true)
      console.log('🔄 Loading pending orders...')

      const { data, error } = await supabase
        .from('orders')
        .select('*')
        .in('status', ['PENDING', 'PARTIAL'])
        .not('user_id', 'is', null)  // user_id가 NULL인 잘못된 주문 제외
        .order('created_at', { ascending: false })
        .limit(20)

      if (error) throw error

      console.log(`✅ Loaded ${data?.length || 0} pending orders`)
      setOrders(data || [])
    } catch (error: any) {
      console.error('주문 조회 실패:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleCancelOrder = async (orderId: string) => {
    if (!confirm('정말 이 주문을 취소하시겠습니까?')) {
      return
    }

    try {
      const { error } = await supabase
        .from('orders')
        .update({ status: 'CANCELLED', updated_at: new Date().toISOString() })
        .eq('id', orderId)

      if (error) throw error

      alert('주문이 취소되었습니다.')
      loadPendingOrders()
    } catch (error: any) {
      console.error('주문 취소 실패:', error)
      alert(`주문 취소 실패: ${error.message}`)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR').format(price)
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  }

  const getOrderTypeColor = (type: string) => {
    return type === 'BUY' ? 'error' : 'primary'
  }

  const getOrderTypeIcon = (type: string) => {
    return type === 'BUY' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />
  }

  const getStatusChip = (status: string) => {
    const statusMap: Record<string, { label: string; color: 'warning' | 'success' | 'default' | 'error' }> = {
      PENDING: { label: '대기중', color: 'warning' },
      PARTIAL: { label: '부분체결', color: 'success' },
      EXECUTED: { label: '체결완료', color: 'success' },
      CANCELLED: { label: '취소됨', color: 'default' }
    }
    const { label, color } = statusMap[status] || { label: status, color: 'default' as const }
    return <Chip label={label} color={color} size="small" />
  }

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📋 미체결 주문
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <Typography color="text.secondary">로딩 중...</Typography>
          </Box>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="h6" fontWeight="bold">
              📋 미체결 주문
            </Typography>
            <Chip
              label={`${orders.length}개`}
              color={orders.length > 0 ? 'warning' : 'default'}
              size="small"
            />
          </Stack>
          <Button
            startIcon={<Refresh />}
            onClick={loadPendingOrders}
            disabled={refreshing}
            size="small"
          >
            새로고침
          </Button>
        </Stack>

        {orders.length === 0 ? (
          <Alert severity="info" icon={<AccessTime />}>
            미체결 주문이 없습니다.
          </Alert>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>주문시간</TableCell>
                  <TableCell>종목코드</TableCell>
                  <TableCell align="center">구분</TableCell>
                  <TableCell align="right">주문가격</TableCell>
                  <TableCell align="right">주문수량</TableCell>
                  <TableCell align="right">체결수량</TableCell>
                  <TableCell align="center">상태</TableCell>
                  <TableCell align="center">키움주문번호</TableCell>
                  <TableCell align="center">관리</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace">
                        {formatDateTime(order.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium" fontFamily="monospace">
                        {order.stock_code}
                      </Typography>
                      {order.stock_name && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          {order.stock_name}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        icon={getOrderTypeIcon(order.order_type)}
                        label={order.order_type === 'BUY' ? '매수' : '매도'}
                        color={getOrderTypeColor(order.order_type)}
                        size="small"
                        sx={{ minWidth: 70 }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="medium">
                        {formatPrice(order.order_price)}원
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {order.quantity.toLocaleString()}주
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color={order.executed_quantity ? 'success.main' : 'text.secondary'}>
                        {order.executed_quantity?.toLocaleString() || 0}주
                      </Typography>
                      {order.executed_price && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          @{formatPrice(order.executed_price)}원
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {getStatusChip(order.status)}
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="caption" fontFamily="monospace">
                        {order.kiwoom_order_no || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      {order.status === 'PENDING' && (
                        <Tooltip title="주문 취소">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleCancelOrder(order.id)}
                          >
                            <Cancel fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  )
}
