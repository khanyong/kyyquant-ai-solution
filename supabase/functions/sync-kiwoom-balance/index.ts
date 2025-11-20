// Supabase Edge Function: 키움 계좌 잔고 동기화
// 사용법: POST /functions/v1/sync-kiwoom-balance

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface KiwoomBalanceResponse {
  dnca_tot_amt: string      // 예수금 총액 (현금)
  nxdy_excc_amt: string     // 익일정산금액 (출금가능금액)
  ord_psbl_cash: string     // 주문가능현금
  prvs_rcdl_excc_amt: string // 전일정산금액 (예수금)
  pchs_amt_smtl_amt: string // 매입금액합계 (대용금)
}

interface KiwoomPortfolioItem {
  pdno: string              // 종목코드
  prdt_name: string         // 종목명
  hldg_qty: string          // 보유수량
  ord_psbl_qty: string      // 주문가능수량
  pchs_avg_pric: string     // 매입평균가격
  prpr: string              // 현재가
  pchs_amt: string          // 매입금액
  evlu_amt: string          // 평가금액
  evlu_pfls_amt: string     // 평가손익금액
  evlu_pfls_rt: string      // 평가손익율
}

serve(async (req) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Supabase 클라이언트 생성
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // 사용자 인증 확인
    const {
      data: { user },
      error: authError,
    } = await supabaseClient.auth.getUser()

    if (authError || !user) {
      throw new Error('인증되지 않은 사용자입니다')
    }

    // 사용자 프로필에서 키움 계좌 정보 가져오기
    const { data: profile, error: profileError } = await supabaseClient
      .from('profiles')
      .select('kiwoom_account')
      .eq('id', user.id)
      .single()

    if (profileError || !profile || !profile.kiwoom_account) {
      throw new Error('키움 계좌 정보가 없습니다')
    }

    const accountNumber = profile.kiwoom_account

    // 키움 API 키 가져오기 (user_api_keys 테이블에서)
    const { data: apiKeys, error: keysError } = await supabaseClient
      .from('user_api_keys')
      .select('key_type, encrypted_value, is_test_mode')
      .eq('user_id', user.id)
      .eq('provider', 'kiwoom')
      .eq('is_active', true)

    if (keysError || !apiKeys || apiKeys.length === 0) {
      throw new Error('키움 API 키가 설정되지 않았습니다')
    }

    // API 키 추출
    const appKeyRecord = apiKeys.find((k) => k.key_type === 'app_key')
    const appSecretRecord = apiKeys.find((k) => k.key_type === 'app_secret')

    if (!appKeyRecord || !appSecretRecord) {
      throw new Error('키움 API 키가 완전하지 않습니다')
    }

    // Base64 디코딩
    const appKey = atob(appKeyRecord.encrypted_value)
    const appSecret = atob(appSecretRecord.encrypted_value)
    const isTestMode = appKeyRecord.is_test_mode

    const baseUrl = isTestMode
      ? 'https://mockapi.kiwoom.com'
      : 'https://openapi.kiwoom.com'

    console.log('🔑 키움 API 연동 시작:', { accountNumber, isTestMode })

    // 1. OAuth 토큰 발급
    console.log('🔑 토큰 발급 요청:', { baseUrl, appKeyLength: appKey.length, secretLength: appSecret.length })

    const tokenResponse = await fetch(`${baseUrl}/oauth2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        grant_type: 'client_credentials',
        appkey: appKey,
        secretkey: appSecret,  // 키움 API는 'secretkey' 사용
      }),
    })

    console.log('📡 토큰 응답 상태:', tokenResponse.status, tokenResponse.statusText)

    if (!tokenResponse.ok) {
      const errorText = await tokenResponse.text()
      console.error('❌ 토큰 발급 실패 응답:', errorText)
      throw new Error(`토큰 발급 실패: ${errorText}`)
    }

    const tokenData = await tokenResponse.json()
    console.log('📦 토큰 응답 데이터:', JSON.stringify(tokenData))

    // 키움 API 응답 확인
    if (tokenData.return_code && tokenData.return_code !== 0) {
      throw new Error(`키움 API 에러: ${tokenData.return_msg} (코드: ${tokenData.return_code})`)
    }

    // 다양한 필드명 시도
    const accessToken = tokenData.access_token || tokenData.token || tokenData.accessToken || tokenData.TOKEN

    if (!accessToken) {
      console.error('❌ 토큰을 찾을 수 없음. 응답 전체:', tokenData)
      throw new Error(`액세스 토큰을 받지 못했습니다. 응답: ${JSON.stringify(tokenData)}`)
    }

    console.log('✅ 토큰 발급 성공:', accessToken.substring(0, 20) + '...')

    // 2. 계좌평가잔고내역 조회
    // 모의투자: kt00018 (국내주식 계좌평가잔고내역)
    const TR_ID = 'kt00018'
    console.log(`📊 계좌평가잔고내역 조회 시작 (TR: ${TR_ID})`)

    const portfolioResponse = await fetch(
      `${baseUrl}/api/dostk/acnt`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8',
          'authorization': `Bearer ${accessToken}`,
          'api-id': TR_ID,
          'cont-yn': 'N',
          'next-key': '',
        },
        body: JSON.stringify({
          qry_tp: '1',          // 조회구분 1:합산, 2:개별
          dmst_stex_tp: 'KRX',  // 국내거래소구분 KRX:한국거래소 (모의투자는 KRX만 지원)
        }),
      }
    )

    let balanceData: KiwoomBalanceResponse | null = null

    let portfolioItems: KiwoomPortfolioItem[] = []

    console.log('📈 보유종목 조회 응답 상태:', portfolioResponse.status)

    if (portfolioResponse.ok) {
      const portfolioResult = await portfolioResponse.json()
      console.log('📈 보유종목 조회 응답:', JSON.stringify(portfolioResult))

      if (portfolioResult.return_code === 0) {
        // 잔고 정보 구성
        const totalCash = portfolioResult.prsm_dpst_aset_amt || '0'
        balanceData = {
          dnca_tot_amt: totalCash,  // 예수금 총액
          nxdy_excc_amt: totalCash,  // 사용가능 현금 (초기값: 전체 현금)
          ord_psbl_cash: totalCash,  // 주문가능 현금
          prvs_rcdl_excc_amt: totalCash,  // 전일정산금액
          pchs_amt_smtl_amt: portfolioResult.tot_pur_amt || '0',  // 매입금액합계
        }
        console.log('✅ 잔고 정보 조회 성공')

        // DB에 잔고 저장
        try {
          await supabaseClient.rpc('sync_kiwoom_account_balance', {
            p_user_id: user.id,
            p_account_number: accountNumber,
            p_balance_data: balanceData,
          })
        } catch (e) {
          console.warn('⚠️ 잔고 저장 실패:', e)
        }

        // 보유종목 정보 추출
        portfolioItems = portfolioResult.acnt_evlt_remn_indv_tot || []
        console.log(`✅ 보유 종목 조회 성공 (${portfolioItems.length}개)`)

        // DB에 저장 (보유 종목이 0개여도 호출하여 기존 데이터 삭제)
        try {
          await supabaseClient.rpc('sync_kiwoom_portfolio', {
            p_user_id: user.id,
            p_account_number: accountNumber,
            p_portfolio_data: portfolioItems,
          })

          // 합계 업데이트
          await supabaseClient.rpc('update_account_totals', {
            p_user_id: user.id,
            p_account_number: accountNumber,
          })
        } catch (e) {
          console.warn('⚠️ 포트폴리오 저장 실패:', e)
        }
      } else {
        console.warn('⚠️ 보유종목 조회 실패 (응답 코드):', portfolioResult.return_code, portfolioResult.return_msg)
      }
    } else {
      const errorText = await portfolioResponse.text()
      console.error('❌ 보유 종목 조회 실패:', errorText)

      // 키움 API 에러 처리
      let errorMessage = '키움 API 계좌 조회 실패'
      try {
        const errorJson = JSON.parse(errorText)
        if (errorJson.status === 500) {
          errorMessage = '키움 서버 오류: 장중 시간(09:00~15:30)에 다시 시도해주세요'
        } else {
          errorMessage = `키움 API 에러: ${errorJson.message || errorText}`
        }
      } catch {
        errorMessage = `키움 API 에러 (${portfolioResponse.status}): ${errorText}`
      }

      throw new Error(errorMessage)
    }

    // 성공 응답 (balanceData가 있는 경우만)
    if (!balanceData) {
      throw new Error('키움 API에서 계좌 데이터를 받지 못했습니다')
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: '계좌 정보 동기화 완료',
        data: {
          balance: balanceData,
          portfolio_count: portfolioItems.length,
          account_number: accountNumber,
          is_test_mode: isTestMode,
        },
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  } catch (error) {
    console.error('❌ 에러:', error)

    return new Response(
      JSON.stringify({
        success: false,
        error: error.message || '알 수 없는 에러가 발생했습니다',
        details: error.stack || String(error),
      }),
      {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})
