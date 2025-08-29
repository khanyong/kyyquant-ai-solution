import React, { useEffect, useRef } from 'react'
import { Box, Typography, Paper, Chip, Stack } from '@mui/material'
import * as LightweightCharts from 'lightweight-charts'
import { useAppSelector } from '../hooks/redux'

const StockChart: React.FC = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const candlestickSeriesRef = useRef<any>(null)
  const volumeSeriesRef = useRef<any>(null)

  const { selectedStock, realTimeData } = useAppSelector(state => state.market)

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = LightweightCharts.createChart(chartContainerRef.current, {
      layout: {
        background: { type: LightweightCharts.ColorType.Solid, color: 'transparent' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // Create volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    })

    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries
    volumeSeriesRef.current = volumeSeries

    // Sample data (replace with real data)
    const sampleData = generateSampleData()
    candlestickSeries.setData(sampleData.candlesticks as any)
    volumeSeries.setData(sampleData.volumes as any)

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Update with real-time data
  useEffect(() => {
    if (!selectedStock || !realTimeData[selectedStock.code]) return
    
    const data = realTimeData[selectedStock.code]
    
    // Update the last candle with real-time price
    if (candlestickSeriesRef.current) {
      candlestickSeriesRef.current.update({
        time: data.time as any,
        open: data.price,
        high: data.price,
        low: data.price,
        close: data.price,
      })
    }

    if (volumeSeriesRef.current) {
      volumeSeriesRef.current.update({
        time: data.time as any,
        value: data.volume,
        color: data.change >= 0 ? '#26a69a' : '#ef5350',
      })
    }
  }, [selectedStock, realTimeData])

  return (
    <Box>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h6">
          {selectedStock ? `${selectedStock.name} (${selectedStock.code})` : '종목을 선택하세요'}
        </Typography>
        {selectedStock && (
          <>
            <Chip 
              label={`₩${selectedStock.price.toLocaleString()}`}
              color="primary"
              variant="outlined"
            />
            <Chip 
              label={`${selectedStock.change >= 0 ? '+' : ''}${selectedStock.change} (${selectedStock.changeRate}%)`}
              color={selectedStock.change >= 0 ? 'success' : 'error'}
              size="small"
            />
          </>
        )}
      </Stack>
      <Paper variant="outlined" sx={{ p: 1 }}>
        <div ref={chartContainerRef} />
      </Paper>
    </Box>
  )
}

// Generate sample data for demonstration
function generateSampleData() {
  const candlesticks = []
  const volumes = []
  const basePrice = 50000
  const baseVolume = 100000
  const now = new Date()
  
  for (let i = 100; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 60 * 1000)
    const time = Math.floor(date.getTime() / 1000)
    
    const open = basePrice + (Math.random() - 0.5) * 1000
    const close = open + (Math.random() - 0.5) * 500
    const high = Math.max(open, close) + Math.random() * 200
    const low = Math.min(open, close) - Math.random() * 200
    const volume = baseVolume + (Math.random() - 0.5) * 50000

    candlesticks.push({ time, open, high, low, close })
    volumes.push({ 
      time, 
      value: volume,
      color: close >= open ? '#26a69a' : '#ef5350'
    })
  }
  
  return { candlesticks, volumes }
}

export default StockChart