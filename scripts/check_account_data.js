import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://hznkyaomtrpzcayayayh.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1NTAwMDksImV4cCI6MjA3MjEyNjAwOX0.obZl3gnWisI-Eg8zWzestO7z3IQpFi6kViEJprsaJbs'

const supabase = createClient(supabaseUrl, supabaseKey)

async function checkAccountData() {
  console.log('=== kw_account_balance 테이블 전체 조회 ===')

  // user_id 필터 없이 전체 조회
  const { data: allBalances, error: allError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .limit(10)

  if (allError) {
    console.error('전체 조회 실패:', allError)
  } else {
    console.log('총 레코드 수:', allBalances.length)
    allBalances.forEach((b, i) => {
      console.log(`\n${i + 1}. user_id: ${b.user_id}`)
      console.log(`   account_number: ${b.account_number}`)
      console.log(`   total_cash: ${b.total_cash?.toLocaleString()}`)
      console.log(`   available_cash: ${b.available_cash?.toLocaleString()}`)
    })
  }

  console.log('\n=== 스크린샷에 보인 데이터 (계좌번호로 조회) ===')

  const { data: byAccount, error: accountError } = await supabase
    .from('kw_account_balance')
    .select('*')
    .eq('account_number', '81126100')

  if (accountError) {
    console.error('계좌번호 조회 실패:', accountError)
  } else {
    console.log('조회 결과:', byAccount)
  }
}

checkAccountData().catch(console.error)
