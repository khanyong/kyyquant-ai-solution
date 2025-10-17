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

    // 2. 계좌평가잔고내역 조회 (kt00018)
    // 문서: /api/dostk/acnt 엔드포인트 사용
    console.log('📊 계좌평가잔고내역 조회 시작 (TR: kt00018)')

    const [accountPrefix, accountSuffix] = accountNumber.split('-')

    const portfolioResponse = await fetch(
      `${baseUrl}/api/dostk/acnt?` +
        new URLSearchParams({
          CANO: accountPrefix,         // 계좌번호 앞자리 (8112)
          ACNT_PRDT_CD: accountSuffix, // 계좌번호 뒷자리 (5100)
          INQR_DVSN_1: '1',           // 조회구분1
          INQR_DVSN_2: '0',           // 조회구분2
        }),
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          authorization: `Bearer ${accessToken}`,
          appkey: appKey,
          appsecret: appSecret,
          'api-id': 'kt00018',        // TR ID: 계좌평가잔고내역요청
          custtype: 'P',               // 개인
        },
      }
    )

    let balanceData: KiwoomBalanceResponse | null = null

    let portfolioItems: KiwoomPortfolioItem[] = []

    console.log('📈 보유종목 조회 응답 상태:', portfolioResponse.status)

    if (portfolioResponse.ok) {
      const portfolioResult = await portfolioResponse.json()
      console.log('📈 보유종목 조회 응답:', JSON.stringify(portfolioResult))

      if (portfolioResult.rt_cd === '0') {
        // output2에서 잔고 정보 추출
        if (portfolioResult.output2 && portfolioResult.output2.length > 0) {
          balanceData = portfolioResult.output2[0]
          console.log('✅ 잔고 정보 조회 성공 (output2)')

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
        }

        // output1에서 보유종목 정보 추출
        if (portfolioResult.output1) {
          portfolioItems = portfolioResult.output1
          console.log(`✅ 보유 종목 조회 성공 (${portfolioItems.length}개)`)

          // DB에 저장
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
        }
      } else {
        console.warn('⚠️ 보유종목 조회 실패 (응답 코드):', portfolioResult.rt_cd, portfolioResult.msg1)
      }
    } else {
      const errorText = await portfolioResponse.text()
      console.warn('⚠️ 보유 종목 조회 실패:', errorText)
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
