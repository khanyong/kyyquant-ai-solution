import React, { useEffect, useRef, useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Stack,
  Button,
  alpha,
  useTheme,
  Grid
} from '@mui/material'
import { ArrowForward, Terminal, AutoGraph, Bolt, Speed } from '@mui/icons-material'
import VideoPlayerModal from './VideoPlayerModal'
import { useNavigate } from 'react-router-dom'

interface HeroSectionProps {
  onLoginClick: () => void
}

const HeroSection: React.FC<HeroSectionProps> = ({ onLoginClick }) => {
  const navigate = useNavigate()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [videoOpen, setVideoOpen] = useState(false)
  const [typedText, setTypedText] = useState('')
  const fullText = "AI ALGORITHM ANALYZING..."

  // Typing effect
  useEffect(() => {
    let index = 0
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index))
        index++
      } else {
        clearInterval(timer)
      }
    }, 100)
    return () => clearInterval(timer)
  }, [])

  // Matrix/Grid Background Effect
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    window.addEventListener('resize', resize)
    resize()

    // Grid properties
    const gridSize = 40
    let time = 0

    const draw = () => {
      ctx.fillStyle = '#050912' // Darker background
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.strokeStyle = 'rgba(0, 229, 255, 0.1)' // Cyan grid
      ctx.lineWidth = 1

      // Moving Grid Effect
      const cols = Math.ceil(canvas.width / gridSize)
      const rows = Math.ceil(canvas.height / gridSize)

      // Vertical lines
      for (let i = 0; i <= cols; i++) {
        const x = i * gridSize
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }

      // Horizontal lines (moving down)
      const offset = (time * 0.5) % gridSize
      for (let i = 0; i <= rows; i++) {
        const y = i * gridSize + offset
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }

      // Random "Data Packets"
      if (Math.random() > 0.9) {
        const x = Math.floor(Math.random() * cols) * gridSize
        const y = Math.floor(Math.random() * rows) * gridSize + offset
        ctx.fillStyle = 'rgba(0, 255, 136, 0.4)' // Green packet
        ctx.fillRect(x, y, gridSize, gridSize)
      }

      time++
      animationId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        bgcolor: '#050912',
      }}
    >
      {/* Canvas Background */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 0,
          opacity: 0.6
        }}
      />

      {/* Radial Overlay for text readability */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, transparent 0%, #050912 90%)',
          zIndex: 1
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
        <Grid container spacing={6} alignItems="center">
          <Grid item xs={12} md={7}>
            <Stack spacing={4} alignItems={{ xs: 'center', md: 'flex-start' }} textAlign={{ xs: 'center', md: 'left' }}>

              {/* Terminal Badge */}
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1.5,
                  px: 2,
                  py: 1,
                  borderRadius: 1,
                  bgcolor: alpha('#00E5FF', 0.1),
                  border: `1px solid ${alpha('#00E5FF', 0.3)}`,
                  fontFamily: '"JetBrains Mono", monospace'
                }}
              >
                <Terminal sx={{ fontSize: 16, color: '#00E5FF' }} />
                <Typography
                  variant="caption"
                  sx={{
                    color: '#00E5FF',
                    fontWeight: 700,
                    letterSpacing: 1
                  }}
                >
                  SYSTEM STATUS: ONLINE
                </Typography>
              </Box>

              {/* Main Headline */}
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    color: '#00FF88', // Cyber Green
                    fontFamily: '"JetBrains Mono", monospace',
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}
                >
                  <Box component="span" className="blinking-cursor">&gt;</Box> {typedText}
                </Typography>
                <Typography
                  variant="h1"
                  sx={{
                    fontWeight: 900,
                    fontSize: { xs: '3rem', md: '4.5rem' },
                    lineHeight: 1.1,
                    color: '#fff',
                    textShadow: '0 0 30px rgba(0, 229, 255, 0.3)',
                    mb: 2
                  }}
                >
                  QUANTUM LEVEL
                  <br />
                  <Box component="span" sx={{ color: 'transparent', background: 'linear-gradient(90deg, #00E5FF, #00FF88)', backgroundClip: 'text' }}>
                    TRADING INTELLIGENCE
                  </Box>
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    color: '#8F9EB3',
                    maxWidth: 600,
                    fontWeight: 400,
                    lineHeight: 1.6
                  }}
                >
                  Experience institutional-grade algorithm trading powered by deep learning.
                  Automate your wealth generation with precision.
                </Typography>
              </Box>

              {/* CTA Buttons - High Tech Style */}
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={onLoginClick}
                  endIcon={<ArrowForward />}
                  sx={{
                    bgcolor: '#00E5FF',
                    color: '#000',
                    fontWeight: 800,
                    fontSize: '1rem',
                    px: 4,
                    py: 1.8,
                    borderRadius: 0, // Sharp edges
                    clipPath: 'polygon(0 0, 100% 0, 100% 85%, 95% 100%, 0 100%)', // Cyber shape
                    '&:hover': {
                      bgcolor: '#00B8D4',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 0 20px rgba(0, 229, 255, 0.5)'
                    }
                  }}
                >
                  ACCESS TERMINAL
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/consulting')}
                  startIcon={<Speed />}
                  sx={{
                    borderColor: '#FF4081',
                    color: '#FF4081',
                    fontWeight: 700,
                    px: 4,
                    py: 1.8,
                    borderRadius: 0,
                    '&:hover': {
                      borderColor: '#FF4081',
                      bgcolor: alpha('#FF4081', 0.1),
                    }
                  }}
                >
                  IPC SIMULATION
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => setVideoOpen(true)}
                  startIcon={<AutoGraph />}
                  sx={{
                    borderColor: '#00FF88',
                    color: '#00FF88',
                    fontWeight: 700,
                    px: 4,
                    py: 1.8,
                    borderRadius: 0,
                    '&:hover': {
                      borderColor: '#00FF88',
                      bgcolor: alpha('#00FF88', 0.1),
                    }
                  }}
                >
                  VIEW BACKTEST
                </Button>
              </Stack>

              {/* Stats HUD */}
              <Grid container spacing={3} sx={{ mt: 4, pt: 4, borderTop: `1px solid ${alpha('#fff', 0.1)}` }}>
                {[
                  { label: 'ACTIVE ALGORITHMS', value: '892', icon: <AutoGraph /> },
                  { label: 'TOTAL VOLUME', value: '$3.2B+', icon: <Bolt /> },
                  { label: 'UPTIME', value: '99.99%', icon: <Terminal /> },
                ].map((stat, idx) => (
                  <Grid item key={idx}>
                    <Stack>
                      <Typography variant="caption" sx={{ color: '#5C6B7F', fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>
                        {stat.label}
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>
                        {stat.value}
                      </Typography>
                    </Stack>
                  </Grid>
                ))}
              </Grid>

            </Stack>
          </Grid>

          {/* Visual Element (Right Side) - 3D Mockup placeholder or similar */}
          <Grid item xs={12} md={5} sx={{ display: { xs: 'none', md: 'block' }, position: 'relative' }}>
            <Box
              sx={{
                width: '100%',
                height: 500,
                background: 'radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 70%)',
                border: `1px solid ${alpha('#00E5FF', 0.3)}`,
                borderRadius: 2,
                position: 'relative',
                backdropFilter: 'blur(10px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {/* Abstract Data Visualization Mockup */}
              <Stack spacing={2} sx={{ width: '80%' }}>
                {[100, 70, 40, 90, 60].map((w, i) => (
                  <Box key={i} sx={{ height: 4, width: `${w}%`, bgcolor: i % 2 === 0 ? '#00E5FF' : '#00FF88', opacity: 0.7, boxShadow: '0 0 10px currentColor' }} />
                ))}
                <Typography sx={{ color: '#00E5FF', fontFamily: '"JetBrains Mono", monospace', textAlign: 'center', mt: 4 }}>
                  [ SYSTEM OPTIMIZED ]
                </Typography>
              </Stack>
            </Box>
          </Grid>
        </Grid>
      </Container>

      <VideoPlayerModal
        open={videoOpen}
        onClose={() => setVideoOpen(false)}
        videoSrc={import.meta.env.VITE_DEMO_VIDEO_URL || '/Company_CI/video-1759676192502.mp4'}
        onCtaClick={onLoginClick}
      />

      <style>
        {`
          .blinking-cursor {
            animation: blink 1s step-end infinite;
          }
          @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
          }
        `}
      </style>
    </Box>
  )
}

export default HeroSection
