import React, { useEffect, useRef, useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Stack,
  Button,
  alpha,
  useTheme
} from '@mui/material'
import { ArrowForward, PlayArrow } from '@mui/icons-material'
import VideoPlayerModal from './VideoPlayerModal'

interface HeroSectionProps {
  onLoginClick: () => void
}

const HeroSection: React.FC<HeroSectionProps> = ({ onLoginClick }) => {
  const theme = useTheme()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [videoOpen, setVideoOpen] = useState(false)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    canvas.width = window.innerWidth * dpr
    canvas.height = window.innerHeight * dpr
    ctx.scale(dpr, dpr)

    canvas.style.width = `${window.innerWidth}px`
    canvas.style.height = `${window.innerHeight}px`

    // Particle system
    class Particle {
      x: number
      y: number
      size: number
      speedX: number
      speedY: number
      opacity: number

      constructor() {
        this.x = Math.random() * canvas!.width
        this.y = Math.random() * canvas!.height
        this.size = Math.random() * 2 + 1
        this.speedX = Math.random() * 0.5 - 0.25
        this.speedY = Math.random() * 0.5 - 0.25
        this.opacity = Math.random() * 0.5 + 0.2
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY

        if (this.x > canvas!.width) this.x = 0
        if (this.x < 0) this.x = canvas!.width
        if (this.y > canvas!.height) this.y = 0
        if (this.y < 0) this.y = canvas!.height
      }

      draw() {
        if (!ctx) return
        ctx.fillStyle = `rgba(144, 202, 249, ${this.opacity})`
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    const particles: Particle[] = []
    for (let i = 0; i < 100; i++) {
      particles.push(new Particle())
    }

    let animationId: number

    const animate = () => {
      ctx.fillStyle = 'rgba(26, 31, 58, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      particles.forEach(particle => {
        particle.update()
        particle.draw()
      })

      // Draw connections
      particles.forEach((a, i) => {
        particles.slice(i + 1).forEach(b => {
          const dx = a.x - b.x
          const dy = a.y - b.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 100) {
            ctx.strokeStyle = `rgba(144, 202, 249, ${0.2 * (1 - distance / 100)})`
            ctx.lineWidth = 0.5
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.stroke()
          }
        })
      })

      animationId = requestAnimationFrame(animate)
    }

    animate()

    const handleResize = () => {
      const dpr = window.devicePixelRatio || 1
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      ctx.scale(dpr, dpr)

      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
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
        background: `linear-gradient(135deg, #1A1F3A 0%, #0f1419 100%)`,
      }}
    >
      {/* Animated Canvas Background */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          zIndex: 0,
          pointerEvents: 'none'
        }}
      />

      {/* Gradient Overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 30% 50%, rgba(255, 184, 0, 0.08) 0%, transparent 50%), radial-gradient(circle at 70% 50%, rgba(179, 136, 255, 0.08) 0%, transparent 50%)',
          zIndex: 1
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2, py: 8 }}>
        <Stack spacing={4} alignItems="center" textAlign="center">
          {/* Premium Badge */}
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 1,
              px: 3,
              py: 1,
              borderRadius: 50,
              background: `linear-gradient(135deg, ${alpha('#FFB800', 0.2)} 0%, ${alpha('#B388FF', 0.2)} 100%)`,
              border: `1px solid ${alpha('#FFB800', 0.3)}`,
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: '#FFB800',
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                  '50%': { opacity: 0.5, transform: 'scale(1.2)' }
                }
              }}
            />
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(135deg, #FFB800 0%, #B388FF 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              전략 마켓플레이스 + AI 퀀트 트레이딩
            </Typography>
          </Box>

          {/* Main Headline */}
          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: '2.5rem', md: '4rem', lg: '5rem' },
              fontWeight: 900,
              lineHeight: 1.1,
              letterSpacing: '-0.02em',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #90CAF9 50%, #B388FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: '0 0 80px rgba(144, 202, 249, 0.3)',
              animation: 'fadeInUp 1s ease-out',
              '@keyframes fadeInUp': {
                from: { opacity: 0, transform: 'translateY(30px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
              }
            }}
          >
            AI가 분석하고
            <br />
            알고리즘이 실행하는
            <br />
            <Box
              component="span"
              sx={{
                background: 'linear-gradient(135deg, #FFB800 0%, #FF6B00 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              스마트 투자
            </Box>
          </Typography>

          {/* Subheadline */}
          <Typography
            variant="h5"
            sx={{
              maxWidth: 900,
              color: alpha('#FFFFFF', 0.8),
              fontWeight: 300,
              lineHeight: 1.8,
              animation: 'fadeInUp 1s ease-out 0.2s backwards',
            }}
          >
            <Box component="span" sx={{ color: '#FFB800', fontWeight: 600 }}>전문가의 전략을 따라하거나</Box>,
            <Box component="span" sx={{ color: '#00E5FF', fontWeight: 600 }}> 나만의 전략을 공유</Box>하세요.
            <br />
            팔로워는 자동 매매로 수익을, 개발자는 <Box component="span" sx={{ color: '#B388FF', fontWeight: 600 }}>이중 수익</Box>을 창출합니다.
          </Typography>

          {/* CTA Buttons */}
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            sx={{
              animation: 'fadeInUp 1s ease-out 0.4s backwards',
            }}
          >
            <Button
              variant="contained"
              size="large"
              onClick={onLoginClick}
              endIcon={<ArrowForward />}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                fontWeight: 700,
                background: 'linear-gradient(135deg, #FFB800 0%, #FF8A00 100%)',
                boxShadow: `0 8px 32px ${alpha('#FFB800', 0.4)}`,
                border: 'none',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: '-100%',
                  width: '100%',
                  height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)',
                  transition: 'left 0.5s',
                },
                '&:hover': {
                  background: 'linear-gradient(135deg, #FF8A00 0%, #FFB800 100%)',
                  boxShadow: `0 12px 48px ${alpha('#FFB800', 0.6)}`,
                  transform: 'translateY(-2px)',
                  '&::before': {
                    left: '100%',
                  }
                },
                transition: 'all 0.3s ease'
              }}
            >
              무료로 시작하기
            </Button>

            <Button
              variant="outlined"
              size="large"
              startIcon={<PlayArrow />}
              onClick={() => setVideoOpen(true)}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                fontWeight: 700,
                borderWidth: 2,
                borderColor: alpha('#00E5FF', 0.5),
                color: '#00E5FF',
                backdropFilter: 'blur(10px)',
                background: alpha('#00E5FF', 0.05),
                '&:hover': {
                  borderWidth: 2,
                  borderColor: '#00E5FF',
                  background: alpha('#00E5FF', 0.15),
                  transform: 'translateY(-2px)',
                  boxShadow: `0 8px 32px ${alpha('#00E5FF', 0.3)}`
                },
                transition: 'all 0.3s ease'
              }}
            >
              데모 영상 보기
            </Button>
          </Stack>

          {/* Live Stats */}
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={6}
            sx={{
              mt: 8,
              animation: 'fadeInUp 1s ease-out 0.6s backwards',
            }}
          >
            {[
              { value: '892', label: '공유된 전략' },
              { value: '2,847', label: '전략 팔로워' },
              { value: '₩3.2억', label: '월 전략 수익' }
            ].map((stat, index) => (
              <Box
                key={index}
                sx={{
                  textAlign: 'center',
                  px: 4,
                  py: 2,
                  borderRadius: 2,
                  background: alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${alpha('#FFB800', 0.2)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: '#FFB800',
                    transform: 'translateY(-4px)',
                    boxShadow: `0 8px 32px ${alpha('#FFB800', 0.2)}`
                  }
                }}
              >
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 900,
                    background: 'linear-gradient(135deg, #FFB800 0%, #FFFFFF 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    fontWeight: 500,
                    mt: 1
                  }}
                >
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Stack>

          {/* Scroll Indicator */}
          <Box
            sx={{
              position: 'absolute',
              bottom: 40,
              left: '50%',
              transform: 'translateX(-50%)',
              animation: 'bounce 2s infinite',
              '@keyframes bounce': {
                '0%, 100%': { transform: 'translateX(-50%) translateY(0)' },
                '50%': { transform: 'translateX(-50%) translateY(10px)' }
              }
            }}
          >
            <Box
              sx={{
                width: 30,
                height: 50,
                border: `2px solid ${alpha('#FFB800', 0.5)}`,
                borderRadius: 20,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 8,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: 4,
                  height: 8,
                  borderRadius: 2,
                  background: '#FFB800',
                  animation: 'scrollIndicator 2s infinite',
                },
                '@keyframes scrollIndicator': {
                  '0%': { top: 8, opacity: 1 },
                  '100%': { top: 32, opacity: 0 }
                }
              }}
            />
          </Box>
        </Stack>
      </Container>

      {/* Video Player Modal */}
      <VideoPlayerModal
        open={videoOpen}
        onClose={() => setVideoOpen(false)}
        videoSrc={import.meta.env.VITE_DEMO_VIDEO_URL || '/Company_CI/video-1759676192502.mp4'}
        onCtaClick={onLoginClick}
      />
    </Box>
  )
}

export default HeroSection
