import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://hznkyaomtrpzcayayayh.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs'

const supabase = createClient(supabaseUrl, supabaseKey)
const userId = 'f912da32-897f-4dbb-9242-3a438e9733a8'

async function fixAvailableCash() {
  console.log('=== 1. 현재 계좌 상태 확인 ===')

  const { data: balance, error: balanceError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })
    .limit(1)
    .single()

  if (balanceError) {
    console.error('계좌 조회 실패:', balanceError)
    return
  }

  console.log('계좌번호:', balance.account_number)
  console.log('총 현금:', balance.total_cash?.toLocaleString() + '원')
  console.log('사용 가능 현금 (현재):', balance.available_cash?.toLocaleString() + '원')
  console.log('주문 중 금액:', balance.order_cash?.toLocaleString() + '원')

  console.log('\n=== 2. 활성 전략 확인 ===')

  const { data: strategies, error: stratError } = await supabase
    .from('strategies')
    .select('*')
    .eq('user_id', userId)
    .eq('is_active', true)

  if (stratError) {
    console.error('전략 조회 실패:', stratError)
    return
  }

  console.log('활성 전략 수:', strategies.length)
  strategies.forEach(s => {
    console.log(`  - ${s.name}: ${s.allocated_capital?.toLocaleString() || 0}원 (${s.allocated_percent}%)`)
  })

  console.log('\n=== 3. 미체결 주문 확인 ===')

  const { data: orders, error: orderError } = await supabase
    .from('orders')
    .select('*')
    .eq('user_id', userId)
    .in('order_status', ['PENDING', 'PARTIAL'])

  if (orderError) {
    console.error('주문 조회 실패:', orderError)
    return
  }

  const pendingAmount = orders.reduce((sum, o) => sum + (o.order_price * o.order_quantity), 0)
  console.log('미체결 주문 수:', orders.length)
  console.log('미체결 금액:', pendingAmount.toLocaleString() + '원')

  if (orders.length > 0) {
    console.log('\n⚠️ 경고: 미체결 주문이 있습니다. 복구를 진행하시겠습니까?')
    console.log('미체결 주문이 있는 경우 신중하게 진행해야 합니다.')
  }

  console.log('\n=== 4. available_cash 복구 실행 ===')

  const orderCash = balance.order_cash || 0
  const newAvailableCash = balance.total_cash - orderCash

  console.log(`새로운 available_cash: ${newAvailableCash.toLocaleString()}원`)
  console.log(`계산: total_cash(${balance.total_cash.toLocaleString()}) - order_cash(${orderCash.toLocaleString()})`)

  const { error: updateError } = await supabase
    .from('kw_account_balance')
    .update({
      available_cash: newAvailableCash,
      updated_at: new Date().toISOString()
    })
    .eq('user_id', userId)

  if (updateError) {
    console.error('❌ 복구 실패:', updateError)
    return
  }

  console.log('✅ available_cash 복구 완료!')

  console.log('\n=== 5. 활성 전략에 금액 재할당 ===')

  for (const strategy of strategies) {
    if (strategy.allocated_percent > 0) {
      const allocatedCapital = Math.round(newAvailableCash * strategy.allocated_percent / 100)

      const { error: stratUpdateError } = await supabase
        .from('strategies')
        .update({
          allocated_capital: allocatedCapital,
          updated_at: new Date().toISOString()
        })
        .eq('id', strategy.id)

      if (stratUpdateError) {
        console.error(`❌ ${strategy.name} 할당 실패:`, stratUpdateError)
      } else {
        console.log(`✅ ${strategy.name}: ${allocatedCapital.toLocaleString()}원 (${strategy.allocated_percent}%)`)
      }
    }
  }

  console.log('\n=== 6. 최종 확인 ===')

  const { data: finalBalance, error: finalError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })
    .limit(1)
    .single()

  if (finalError) {
    console.error('최종 확인 실패:', finalError)
    return
  }

  const { data: finalStrategies, error: finalStratError } = await supabase
    .from('strategies')
    .select('*')
    .eq('user_id', userId)
    .eq('is_active', true)

  if (finalStratError) {
    console.error('전략 최종 확인 실패:', finalStratError)
    return
  }

  const totalAllocated = finalStrategies.reduce((sum, s) => sum + (s.allocated_capital || 0), 0)

  console.log('총 현금:', finalBalance.total_cash.toLocaleString() + '원')
  console.log('사용 가능 현금:', finalBalance.available_cash.toLocaleString() + '원')
  console.log('전략 할당 총액:', totalAllocated.toLocaleString() + '원')
  console.log('합계:', (finalBalance.available_cash + totalAllocated).toLocaleString() + '원')

  if (Math.abs(finalBalance.total_cash - (finalBalance.available_cash + totalAllocated)) < 1) {
    console.log('✅ 금액 일치 확인됨!')
  } else {
    console.log('⚠️ 금액 불일치 발생')
  }

  console.log('\n✅ 복구 완료! 이제 프론트엔드에서 전략 활성화/비활성화 시 자동으로 available_cash가 업데이트됩니다.')
}

fixAvailableCash().catch(console.error)
