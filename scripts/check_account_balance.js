import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://hznkyaomtrpzcayayayh.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs'

const supabase = createClient(supabaseUrl, supabaseKey)
const userId = 'f912da32-897f-4dbb-9242-3a438e9733a8'

async function checkAccountBalance() {
  console.log('=== 1. 계좌 잔고 직접 확인 ===')
  const { data: balance, error: balanceError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false })
    .limit(1)
    .single()

  if (balanceError) {
    console.error('계좌 잔고 조회 오류:', balanceError)
  } else {
    console.log('계좌 번호:', balance.account_number)
    console.log('총 현금:', balance.total_cash?.toLocaleString() + '원')
    console.log('사용 가능 현금:', balance.available_cash?.toLocaleString() + '원')
    console.log('마지막 업데이트:', balance.updated_at)

    const minutesAgo = Math.round((new Date() - new Date(balance.updated_at)) / 60000)
    console.log('업데이트 경과시간:', minutesAgo + '분 전')
  }

  console.log('\n=== 2. 활성 전략 확인 ===')
  const { data: strategies, error: stratError } = await supabase
    .from('strategies')
    .select('name, is_active, auto_trade_enabled, auto_execute, allocated_percent, target_stocks')
    .eq('user_id', userId)
    .eq('is_active', true)

  if (stratError) {
    console.error('전략 조회 오류:', stratError)
  } else {
    strategies.forEach(s => {
      console.log(`전략명: ${s.name}`)
      console.log(`  자동매매: ${s.auto_trade_enabled}, 자동실행: ${s.auto_execute}`)
      console.log(`  할당율: ${s.allocated_percent}%`)
      console.log(`  모니터링 종목: ${s.target_stocks ? s.target_stocks.join(', ') : '없음'}`)

      if (balance && balance.available_cash) {
        const allocated = Math.round(balance.available_cash * s.allocated_percent / 100)
        console.log(`  할당 금액: ${allocated.toLocaleString()}원`)
      }
      console.log()
    })
  }

  console.log('=== 3. 할당 금액 계산 (Cross Join) ===')
  if (balance && strategies) {
    const totalAllocation = strategies.reduce((sum, s) => sum + (s.allocated_percent || 0), 0)
    console.log(`총 할당율: ${totalAllocation}%`)
    console.log(`사용 가능 현금: ${balance.available_cash?.toLocaleString()}원`)

    strategies.forEach(s => {
      const allocated = Math.round(balance.available_cash * s.allocated_percent / 100)
      console.log(`${s.name}: ${s.allocated_percent}% = ${allocated.toLocaleString()}원`)
    })
  }
}

checkAccountBalance().catch(console.error)
