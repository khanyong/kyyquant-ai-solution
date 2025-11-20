import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://hznkyaomtrpzcayayayh.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs'

const supabase = createClient(supabaseUrl, supabaseKey)
const userId = 'f912da32-897f-4dbb-9242-3a438e9733a8'

async function diagnoseAllocation() {
  console.log('=== 1. 계좌 잔고 확인 ===')

  const { data: balance, error: balanceError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })
    .limit(1)

  if (balanceError) {
    console.error('계좌 조회 실패:', balanceError)
    return
  }

  if (balance && balance.length > 0) {
    const b = balance[0]
    console.log('계좌번호:', b.account_number)
    console.log('총 현금 (total_cash):', b.total_cash?.toLocaleString())
    console.log('사용가능 현금 (available_cash):', b.available_cash?.toLocaleString())
    console.log('예수금 (deposit):', b.deposit?.toLocaleString())
    console.log('총 자산 (total_asset):', b.total_asset?.toLocaleString())
    console.log('업데이트 시간:', b.updated_at)
  } else {
    console.log('❌ 계좌 잔고 데이터 없음')
  }

  console.log('\n=== 2. 전략 상태 확인 ===')

  const { data: strategies, error: stratError } = await supabase
    .from('strategies')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })

  if (stratError) {
    console.error('전략 조회 실패:', stratError)
    return
  }

  console.log(`총 전략 수: ${strategies.length}`)
  strategies.forEach((s, i) => {
    console.log(`\n${i + 1}. ${s.name}`)
    console.log(`   is_active: ${s.is_active}`)
    console.log(`   auto_trade_enabled: ${s.auto_trade_enabled}`)
    console.log(`   auto_execute: ${s.auto_execute}`)
    console.log(`   allocated_percent: ${s.allocated_percent}%`)
    console.log(`   allocated_capital: ${s.allocated_capital?.toLocaleString() || 0}원`)
    console.log(`   target_stocks: ${s.target_stocks ? s.target_stocks.join(', ') : '없음'}`)
    console.log(`   updated_at: ${s.updated_at}`)
  })

  console.log('\n=== 3. 활성 전략 집계 ===')

  const activeStrategies = strategies.filter(s => s.is_active)
  const totalAllocatedPercent = activeStrategies.reduce((sum, s) => sum + (s.allocated_percent || 0), 0)
  const totalAllocatedCapital = activeStrategies.reduce((sum, s) => sum + (s.allocated_capital || 0), 0)

  console.log(`활성 전략 수: ${activeStrategies.length}`)
  console.log(`총 할당 비율: ${totalAllocatedPercent}%`)
  console.log(`총 할당 금액: ${totalAllocatedCapital.toLocaleString()}원`)

  if (balance && balance.length > 0) {
    const expectedAllocation = balance[0].available_cash * 0.5
    console.log(`\n예상 할당 금액 (50%): ${expectedAllocation.toLocaleString()}원`)
    console.log(`실제 할당 금액: ${totalAllocatedCapital.toLocaleString()}원`)
    console.log(`차이: ${(expectedAllocation - totalAllocatedCapital).toLocaleString()}원`)
  }

  console.log('\n=== 4. 문제 진단 ===')

  if (activeStrategies.length === 0) {
    console.log('❌ 활성화된 전략이 없습니다')
  } else if (totalAllocatedCapital === 0) {
    console.log('❌ allocated_capital이 0입니다')
    console.log('   원인 가능성:')
    console.log('   1. EditStrategyDialog에서 저장 실패')
    console.log('   2. UI에서 allocated_capital을 업데이트하지 않음')
    console.log('   3. DB 업데이트 후 다른 프로세스가 0으로 덮어씀')
  } else if (balance && balance[0].available_cash === balance[0].total_cash) {
    console.log('❌ available_cash가 차감되지 않았습니다')
    console.log('   원인: EditStrategyDialog의 available_cash 차감 로직이 실행되지 않음')
  } else {
    console.log('✅ 정상적으로 할당됨')
  }
}

diagnoseAllocation().catch(console.error)
