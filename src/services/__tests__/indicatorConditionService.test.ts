import { IndicatorConditionValidator } from '../indicatorConditionService'

describe('IndicatorConditionValidator', () => {
  describe('validateCondition', () => {
    test('RSI 조건 검증', () => {
      // 유효한 RSI 조건
      const valid = IndicatorConditionValidator.validateCondition('rsi', 'rsi_oversold_30')
      expect(valid.isValid).toBe(true)

      // RSI 값 범위 검증
      const invalidRange = IndicatorConditionValidator.validateCondition('rsi', '>', 150)
      expect(invalidRange.isValid).toBe(false)
      expect(invalidRange.message).toContain('0-100')

      // 값이 필요한 조건
      const needsValue = IndicatorConditionValidator.validateCondition('rsi', '>', undefined)
      expect(needsValue.isValid).toBe(false)
    })

    test('Stochastic 조건 검증', () => {
      const valid = IndicatorConditionValidator.validateCondition('stochastic', 'stoch_oversold_20')
      expect(valid.isValid).toBe(true)

      const invalidRange = IndicatorConditionValidator.validateCondition('stochastic', '>', 120)
      expect(invalidRange.isValid).toBe(false)
    })

    test('일목균형표 조건 검증', () => {
      const valid = IndicatorConditionValidator.validateCondition('ichimoku', 'cloud_breakout_up')
      expect(valid.isValid).toBe(true)
    })

    test('볼린저밴드 조건 검증', () => {
      const valid = IndicatorConditionValidator.validateCondition('bb', 'price_above_upper')
      expect(valid.isValid).toBe(true)

      const widthThreshold = IndicatorConditionValidator.validateCondition('bb', 'bb_width_threshold', 10)
      expect(widthThreshold.isValid).toBe(true)

      const invalidWidth = IndicatorConditionValidator.validateCondition('bb', 'bb_width_threshold', -5)
      expect(invalidWidth.isValid).toBe(false)
    })

    test('ADX 조건 검증', () => {
      const valid = IndicatorConditionValidator.validateCondition('adx', 'adx_strong_trend')
      expect(valid.isValid).toBe(true)

      const validThreshold = IndicatorConditionValidator.validateCondition('adx', 'adx_threshold', 25)
      expect(validThreshold.isValid).toBe(true)

      const invalidThreshold = IndicatorConditionValidator.validateCondition('adx', 'adx_threshold', 150)
      expect(invalidThreshold.isValid).toBe(false)
    })
  })

  describe('evaluateCondition', () => {
    test('단순 비교 조건 평가', () => {
      expect(IndicatorConditionValidator.evaluateCondition(30, '>', 25)).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(30, '<', 25)).toBe(false)
      expect(IndicatorConditionValidator.evaluateCondition(30, '>=', 30)).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(30, '<=', 30)).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(30, '=', 30)).toBe(true)
    })

    test('RSI 특수 조건 평가', () => {
      expect(IndicatorConditionValidator.evaluateCondition(25, 'rsi_oversold_30')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(35, 'rsi_oversold_30')).toBe(false)
      expect(IndicatorConditionValidator.evaluateCondition(75, 'rsi_overbought_70')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(65, 'rsi_overbought_70')).toBe(false)
    })

    test('MACD 복합 조건 평가', () => {
      const macdData = {
        macd: 0.5,
        signal: 0.3,
        histogram: 0.2
      }

      expect(IndicatorConditionValidator.evaluateCondition(macdData, 'macd_above_signal')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(macdData, 'macd_below_signal')).toBe(false)
      expect(IndicatorConditionValidator.evaluateCondition(macdData, 'macd_above_zero')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(macdData, 'histogram_positive')).toBe(true)
    })

    test('볼린저밴드 복합 조건 평가', () => {
      const bbData = {
        upper: 110,
        middle: 100,
        lower: 90,
        price: 112
      }

      expect(IndicatorConditionValidator.evaluateCondition(bbData, 'price_above_upper')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCondition(bbData, 'price_below_lower')).toBe(false)
      expect(IndicatorConditionValidator.evaluateCondition(bbData, 'price_above_middle')).toBe(true)
    })
  })

  describe('evaluateCrossCondition', () => {
    test('RSI 크로스 조건 평가', () => {
      expect(IndicatorConditionValidator.evaluateCrossCondition(45, 55, 'rsi_cross_50_up')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCrossCondition(55, 45, 'rsi_cross_50_down')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCrossCondition(25, 35, 'rsi_exit_oversold')).toBe(true)
      expect(IndicatorConditionValidator.evaluateCrossCondition(75, 65, 'rsi_exit_overbought')).toBe(true)
    })

    test('MACD 크로스 조건 평가', () => {
      const prevMacd = { macd: -0.2, signal: 0.1 }
      const currMacd = { macd: 0.2, signal: 0.1 }

      expect(IndicatorConditionValidator.evaluateCrossCondition(
        prevMacd, currMacd, 'macd_cross_signal_up'
      )).toBe(true)

      const prevMacd2 = { macd: -0.1, signal: -0.2 }
      const currMacd2 = { macd: 0.1, signal: 0.05 }

      expect(IndicatorConditionValidator.evaluateCrossCondition(
        prevMacd2, currMacd2, 'macd_cross_zero_up'
      )).toBe(true)
    })

    test('Stochastic 크로스 조건 평가', () => {
      const prevStoch = { k: 15, d: 20 }
      const currStoch = { k: 25, d: 20 }

      expect(IndicatorConditionValidator.evaluateCrossCondition(
        prevStoch, currStoch, 'stoch_k_cross_d_up'
      )).toBe(true)

      const prevStoch2 = { k: 15, d: 20 }
      const currStoch2 = { k: 18, d: 17 }

      expect(IndicatorConditionValidator.evaluateCrossCondition(
        prevStoch2, currStoch2, 'stoch_k_cross_d_oversold'
      )).toBe(true)
    })
  })

  describe('evaluateDivergence', () => {
    test('강세 다이버전스 평가', () => {
      const priceData = [100, 95, 90] // 가격 하락
      const indicatorData = [30, 35, 40] // 지표 상승

      expect(IndicatorConditionValidator.evaluateDivergence(
        priceData, indicatorData, 'bullish_divergence'
      )).toBe(true)

      expect(IndicatorConditionValidator.evaluateDivergence(
        priceData, indicatorData, 'rsi_bullish_divergence'
      )).toBe(true)
    })

    test('약세 다이버전스 평가', () => {
      const priceData = [100, 105, 110] // 가격 상승
      const indicatorData = [70, 65, 60] // 지표 하락

      expect(IndicatorConditionValidator.evaluateDivergence(
        priceData, indicatorData, 'bearish_divergence'
      )).toBe(true)

      expect(IndicatorConditionValidator.evaluateDivergence(
        priceData, indicatorData, 'macd_bearish_divergence'
      )).toBe(true)
    })

    test('숨은 다이버전스 평가', () => {
      const priceData = [100, 105, 110] // 가격 상승
      const indicatorData = [50, 60, 75] // 지표 더 크게 상승

      expect(IndicatorConditionValidator.evaluateDivergence(
        priceData, indicatorData, 'hidden_bullish_div'
      )).toBe(true)
    })
  })

  describe('doesConditionNeedValue', () => {
    test('값이 필요한 조건 확인', () => {
      expect(IndicatorConditionValidator.doesConditionNeedValue('rsi', '>')).toBe(true)
      expect(IndicatorConditionValidator.doesConditionNeedValue('rsi', 'distance_from_ma')).toBe(true)
      expect(IndicatorConditionValidator.doesConditionNeedValue('rsi', 'rsi_oversold_30')).toBe(false)
      expect(IndicatorConditionValidator.doesConditionNeedValue('macd', 'macd_above_signal')).toBe(false)
    })
  })
})

describe('실제 백테스트 시나리오', () => {
  test('3단계 전략 조건 평가', () => {
    // Stage 1: RSI 과매도
    const stage1 = IndicatorConditionValidator.evaluateCondition(25, 'rsi_oversold_30')
    expect(stage1).toBe(true)

    // Stage 2: MACD 골든크로스
    const prevMacd = { macd: -0.5, signal: -0.3 }
    const currMacd = { macd: 0.1, signal: -0.1 }
    const stage2 = IndicatorConditionValidator.evaluateCrossCondition(
      prevMacd, currMacd, 'macd_cross_signal_up'
    )
    expect(stage2).toBe(true)

    // Stage 3: 볼린저밴드 하단 터치
    const bbData = { upper: 110, middle: 100, lower: 90, price: 89 }
    const stage3 = IndicatorConditionValidator.evaluateCondition(bbData, 'price_below_lower')
    expect(stage3).toBe(true)

    // 모든 단계 통과 시 매수 신호
    const buySignal = stage1 && stage2 && stage3
    expect(buySignal).toBe(true)
  })

  test('복합 조건 검증', () => {
    // 일목균형표 삼역호전 조건
    const ichimokuData = {
      tenkan: 105,
      kijun: 100,
      senkouA: 102,
      senkouB: 98,
      price: 108,
      chikou: 106
    }

    // 1. 전환선 > 기준선
    const cond1 = IndicatorConditionValidator.evaluateCondition(ichimokuData, 'tenkan_above_kijun')
    // 2. 가격 > 구름대
    const cond2 = IndicatorConditionValidator.evaluateCondition(ichimokuData, 'price_above_cloud')
    
    expect(cond1).toBe(true)
    expect(cond2).toBe(true)
  })
})