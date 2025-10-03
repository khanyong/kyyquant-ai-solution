import { supabase } from '../lib/supabase'

export interface IndicatorDefinition {
  id: string
  name: string
  display_name: string
  description?: string
  category: string
  calculation_type: string
  formula?: any
  default_params: any
  required_data: string[]
  output_columns: string[]
  is_active: boolean
}

export interface IndicatorColumn {
  indicator_name: string
  column_name: string
  column_type: string
  column_description?: string
  output_order: number
  is_primary: boolean
}

/**
 * Supabase에서 활성화된 지표 목록을 가져옵니다
 */
export async function fetchIndicators(): Promise<IndicatorDefinition[]> {
  const { data, error } = await supabase
    .from('indicators')
    .select('*')
    .eq('is_active', true)
    .order('category', { ascending: true })
    .order('name', { ascending: true })

  if (error) {
    console.error('Error fetching indicators:', error)
    throw error
  }

  return data || []
}

/**
 * 특정 지표의 출력 컬럼 정보를 가져옵니다
 */
export async function fetchIndicatorColumns(indicatorName: string): Promise<IndicatorColumn[]> {
  const { data, error } = await supabase
    .from('indicator_columns')
    .select('*')
    .eq('indicator_name', indicatorName)
    .eq('is_active', true)
    .order('output_order', { ascending: true })

  if (error) {
    console.error('Error fetching indicator columns:', error)
    throw error
  }

  return data || []
}

/**
 * 모든 지표의 컬럼 매핑 정보를 가져옵니다
 */
export async function fetchAllIndicatorColumns(): Promise<Map<string, IndicatorColumn[]>> {
  const { data, error } = await supabase
    .from('indicator_columns')
    .select('*')
    .eq('is_active', true)
    .neq('indicator_name', 'price') // price는 제외
    .order('indicator_name', { ascending: true })
    .order('output_order', { ascending: true })

  if (error) {
    console.error('Error fetching all indicator columns:', error)
    throw error
  }

  const columnsMap = new Map<string, IndicatorColumn[]>()

  data?.forEach(col => {
    if (!columnsMap.has(col.indicator_name)) {
      columnsMap.set(col.indicator_name, [])
    }
    columnsMap.get(col.indicator_name)!.push(col)
  })

  return columnsMap
}

/**
 * StrategyBuilder와 호환되는 형식으로 지표 데이터를 변환합니다
 */
export function convertToStrategyBuilderFormat(indicator: IndicatorDefinition) {
  // 지표 ID 매핑 (DB의 name을 프론트엔드 id로 사용)
  const id = indicator.name

  return {
    id,
    name: indicator.display_name,
    type: indicator.category as 'trend' | 'momentum' | 'volume' | 'volatility',
    defaultParams: indicator.default_params || {},
    params: indicator.default_params || {},
    enabled: true,
    outputs: indicator.output_columns || []
  }
}

/**
 * StrategyBuilder용 지표 목록을 Supabase에서 가져옵니다
 */
export async function getAvailableIndicators() {
  const indicators = await fetchIndicators()
  return indicators.map(convertToStrategyBuilderFormat)
}
