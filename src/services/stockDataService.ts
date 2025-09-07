import { supabase } from '../lib/supabase'

interface StockData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  [key: string]: any
}

interface CachedData {
  timestamp: number
  data: { [stockCode: string]: StockData[] }
}

class StockDataService {
  private cache: Map<string, CachedData> = new Map()
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5분
  private readonly BATCH_SIZE = 10 // 한 번에 처리할 종목 수
  private readonly MAX_LOCAL_STORAGE_SIZE = 50 * 1024 * 1024 // 50MB
  
  // 로컬 스토리지 캐시 키 생성
  private getLocalStorageKey(stockCode: string, startDate: string, endDate: string): string {
    return `stock_data_${stockCode}_${startDate}_${endDate}`
  }
  
  // 로컬 스토리지 크기 체크
  private getLocalStorageSize(): number {
    let size = 0
    for (const key in localStorage) {
      if (key.startsWith('stock_data_')) {
        size += localStorage[key].length * 2 // UTF-16 encoding
      }
    }
    return size
  }
  
  // 오래된 캐시 삭제
  private clearOldCache(): void {
    const now = Date.now()
    const oneWeek = 7 * 24 * 60 * 60 * 1000
    const keysToDelete: string[] = []
    
    for (const key in localStorage) {
      if (key.startsWith('stock_data_')) {
        try {
          const data = JSON.parse(localStorage[key])
          if (!data.timestamp || now - data.timestamp > oneWeek) {
            keysToDelete.push(key)
          }
        } catch (error) {
          // 파싱 실패한 키도 삭제
          keysToDelete.push(key)
        }
      }
    }
    
    // 배치로 삭제
    keysToDelete.forEach(key => {
      try {
        localStorage.removeItem(key)
      } catch (error) {
        console.warn(`Failed to remove cache key ${key}:`, error)
      }
    })
  }
  
  // 로컬 스토리지에서 데이터 로드
  private loadFromLocalStorage(stockCode: string, startDate: string, endDate: string): StockData[] | null {
    try {
      const key = this.getLocalStorageKey(stockCode, startDate, endDate)
      const cached = localStorage.getItem(key)
      
      if (cached) {
        const data = JSON.parse(cached)
        // 캐시가 1주일 이내인 경우만 사용
        if (data.timestamp && Date.now() - data.timestamp < 7 * 24 * 60 * 60 * 1000) {
          console.log(`✓ Local cache hit for ${stockCode}`)
          return data.data
        } else {
          // 오래된 캐시 삭제
          localStorage.removeItem(key)
        }
      }
    } catch (error) {
      console.warn('Failed to load from localStorage:', error)
    }
    return null
  }
  
  // 로컬 스토리지에 데이터 저장
  private saveToLocalStorage(stockCode: string, startDate: string, endDate: string, data: StockData[]): void {
    try {
      // 크기 체크 및 정리
      if (this.getLocalStorageSize() > this.MAX_LOCAL_STORAGE_SIZE * 0.8) {
        console.log('LocalStorage approaching limit, clearing old cache...')
        this.clearOldCache()
      }
      
      const key = this.getLocalStorageKey(stockCode, startDate, endDate)
      const cacheData = {
        timestamp: Date.now(),
        data: data
      }
      
      try {
        localStorage.setItem(key, JSON.stringify(cacheData))
        console.log(`✓ Saved to local cache: ${stockCode}`)
      } catch (quotaError) {
        // 용량 초과 시 오래된 캐시 삭제 후 재시도
        console.warn('LocalStorage quota exceeded, clearing old cache...')
        this.clearOldCache()
        
        try {
          localStorage.setItem(key, JSON.stringify(cacheData))
        } catch (retryError) {
          console.error('Failed to save to localStorage after clearing:', retryError)
        }
      }
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  }
  
  // Supabase에서 데이터 로드
  private async loadFromSupabase(
    stockCode: string, 
    startDate: string, 
    endDate: string
  ): Promise<StockData[]> {
    try {
      console.log(`Loading from Supabase: ${stockCode} (${startDate} ~ ${endDate})`)
      
      const { data, error } = await supabase
        .from('kw_price_daily')
        .select('*')
        .eq('stock_code', stockCode)
        .gte('trade_date', startDate)
        .lte('trade_date', endDate)
        .order('trade_date', { ascending: true })
      
      if (error) {
        console.error(`Supabase error for ${stockCode}:`, error)
        return []
      }
      
      if (data && data.length > 0) {
        console.log(`✓ Supabase data loaded for ${stockCode}: ${data.length} records`)
        // 로컬 스토리지에 캐싱
        this.saveToLocalStorage(stockCode, startDate, endDate, data)
        return data
      } else {
        console.log(`✗ No Supabase data for ${stockCode}`)
        return []
      }
    } catch (error) {
      console.error(`Failed to load from Supabase for ${stockCode}:`, error)
      return []
    }
  }
  
  // 외부 API에서 데이터 로드 (폴백)
  private async loadFromAPI(
    stockCode: string, 
    startDate: string, 
    endDate: string
  ): Promise<StockData[]> {
    try {
      console.log(`Fetching from API: ${stockCode}`)
      
      // API 엔드포인트 (백엔드 서버)
      const response = await fetch(`http://localhost:8000/api/stock/${stockCode}/daily?start_date=${startDate}&end_date=${endDate}`)
      
      if (!response.ok) {
        console.error(`API error for ${stockCode}: ${response.status}`)
        return []
      }
      
      const data = await response.json()
      
      if (data && data.length > 0) {
        console.log(`✓ API data fetched for ${stockCode}: ${data.length} records`)
        // Supabase에 저장 (백그라운드)
        this.saveToSupabase(stockCode, data).catch(err => 
          console.error(`Failed to save ${stockCode} to Supabase:`, err)
        )
        // 로컬 스토리지에도 캐싱
        this.saveToLocalStorage(stockCode, startDate, endDate, data)
        return data
      } else {
        console.log(`✗ No API data for ${stockCode}`)
        return []
      }
    } catch (error) {
      console.error(`Failed to fetch from API for ${stockCode}:`, error)
      return []
    }
  }
  
  // Supabase에 데이터 저장
  private async saveToSupabase(stockCode: string, data: StockData[]): Promise<void> {
    if (!data || data.length === 0) return
    
    try {
      const { error } = await supabase
        .from('kw_stock_daily')
        .upsert(
          data.map(d => ({
            ...d,
            stock_code: stockCode
          })),
          { onConflict: 'stock_code,date' }
        )
      
      if (error) {
        console.error(`Failed to save ${stockCode} to Supabase:`, error)
      } else {
        console.log(`✓ Saved ${stockCode} to Supabase: ${data.length} records`)
      }
    } catch (error) {
      console.error(`Error saving to Supabase:`, error)
    }
  }
  
  // 3-tier 데이터 로딩 전략
  async getStockData(
    stockCodes: string[], 
    startDate: string, 
    endDate: string
  ): Promise<{ [stockCode: string]: StockData[] }> {
    const result: { [stockCode: string]: StockData[] } = {}
    
    // 병렬 처리를 위한 배치 분할
    const batches: string[][] = []
    for (let i = 0; i < stockCodes.length; i += this.BATCH_SIZE) {
      batches.push(stockCodes.slice(i, i + this.BATCH_SIZE))
    }
    
    console.log(`Loading data for ${stockCodes.length} stocks in ${batches.length} batches...`)
    
    // 배치별로 순차 처리 (너무 많은 동시 요청 방지)
    for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
      const batch = batches[batchIndex]
      console.log(`Processing batch ${batchIndex + 1}/${batches.length}...`)
      
      await Promise.all(
        batch.map(async (stockCode) => {
          try {
            // 1. 로컬 스토리지 체크
            let data = this.loadFromLocalStorage(stockCode, startDate, endDate)
            
            // 2. Supabase에서 로드
            if (!data || data.length === 0) {
              data = await this.loadFromSupabase(stockCode, startDate, endDate)
            }
            
            // 3. 외부 API에서 로드 (폴백)
            if (!data || data.length === 0) {
              data = await this.loadFromAPI(stockCode, startDate, endDate)
            }
            
            if (data && data.length > 0) {
              result[stockCode] = data
            }
          } catch (error) {
            console.error(`Failed to load data for ${stockCode}:`, error)
          }
        })
      )
      
      // 배치 간 짧은 딜레이 (서버 부하 방지)
      if (batchIndex < batches.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
    
    console.log(`✓ Data loading complete: ${Object.keys(result).length}/${stockCodes.length} stocks loaded`)
    
    return result
  }
  
  // 캐시 클리어
  clearCache(): void {
    this.cache.clear()
    this.clearOldCache()
    console.log('✓ All cache cleared')
  }
  
  // 특정 종목 캐시 클리어
  clearStockCache(stockCode: string): void {
    // 메모리 캐시 클리어
    for (const key of this.cache.keys()) {
      if (key.includes(stockCode)) {
        this.cache.delete(key)
      }
    }
    
    // 로컬 스토리지 캐시 클리어
    for (const key in localStorage) {
      if (key.includes(stockCode)) {
        localStorage.removeItem(key)
      }
    }
    
    console.log(`✓ Cache cleared for ${stockCode}`)
  }
}

export const stockDataService = new StockDataService()