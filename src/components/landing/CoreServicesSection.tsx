import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  alpha,
  Button
} from '@mui/material'
import {
  FilterAlt,
  Architecture,
  Assessment,
  Speed,
  TrendingUp,
  Analytics,
  ArrowForward
} from '@mui/icons-material'

const CoreServicesSection: React.FC = () => {
  const services = [
    {
      icon: <FilterAlt sx={{ fontSize: 60 }} />,
      title: '투자 유니버스 필터링',
      subtitle: 'Investment Universe',
      description: '재무지표, 기술적 지표, 펀더멘털 분석을 통해 우량 종목을 자동으로 선별합니다.',
      features: [
        'PER, PBR, ROE 등 30+ 재무지표',
        '실시간 스크리닝',
        '커스텀 필터 저장',
        '백테스트 연동'
      ],
      color: '#00E5FF',
      gradient: 'linear-gradient(135deg, #00E5FF 0%, #00B8D4 100%)'
    },
    {
      icon: <Architecture sx={{ fontSize: 60 }} />,
      title: '전략 빌더',
      subtitle: 'Strategy Builder',
      description: '코딩 없이 클릭만으로 복잡한 매매 전략을 만들고 최적화할 수 있습니다.',
      features: [
        '노코드 전략 생성',
        '50+ 기술적 지표',
        '다중 조건 설정',
        '전략 템플릿 제공'
      ],
      color: '#FFB800',
      gradient: 'linear-gradient(135deg, #FFB800 0%, #FF8A00 100%)'
    },
    {
      icon: <Assessment sx={{ fontSize: 60 }} />,
      title: '백테스팅 엔진',
      subtitle: 'Backtesting Engine',
      description: '과거 10년 데이터로 전략을 검증하고 성과를 시뮬레이션합니다.',
      features: [
        '10년+ 과거 데이터',
        '실시간 결과 분석',
        '리스크 지표 제공',
        '최적화 기능'
      ],
      color: '#B388FF',
      gradient: 'linear-gradient(135deg, #B388FF 0%, #7C4DFF 100%)'
    }
  ]

  return (
    <Box
      sx={{
        py: 12,
        background: `linear-gradient(180deg, #0A0E1A 0%, #1A1F3A 100%)`,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.03,
          backgroundImage: `
            linear-gradient(0deg, transparent 24%, rgba(255, 255, 255, .05) 25%, rgba(255, 255, 255, .05) 26%, transparent 27%, transparent 74%, rgba(255, 255, 255, .05) 75%, rgba(255, 255, 255, .05) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(255, 255, 255, .05) 25%, rgba(255, 255, 255, .05) 26%, transparent 27%, transparent 74%, rgba(255, 255, 255, .05) 75%, rgba(255, 255, 255, .05) 76%, transparent 77%, transparent)
          `,
          backgroundSize: '50px 50px'
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 10 }}>
          <Typography
            variant="overline"
            sx={{
              color: '#FFB800',
              fontWeight: 700,
              letterSpacing: 2,
              fontSize: '0.9rem'
            }}
          >
            CORE SERVICES
          </Typography>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #90CAF9 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            3가지 핵심 서비스
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              color: alpha('#FFFFFF', 0.7),
              lineHeight: 1.8,
              fontWeight: 300
            }}
          >
            종목 선정부터 전략 수립, 백테스팅까지
            <br />
            체계적인 투자를 위한 모든 도구를 제공합니다
          </Typography>
        </Stack>

        {/* Services Grid */}
        <Grid container spacing={4}>
          {services.map((service, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  background: alpha('#0A0E1A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `2px solid ${alpha(service.color, 0.3)}`,
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  transform: 'perspective(1000px) rotateX(0deg)',
                  '&:hover': {
                    transform: 'perspective(1000px) rotateX(2deg) translateY(-12px)',
                    borderColor: service.color,
                    boxShadow: `0 20px 60px ${alpha(service.color, 0.4)}`,
                    '& .service-icon': {
                      transform: 'scale(1.1) rotateY(360deg)',
                    },
                    '& .gradient-overlay': {
                      opacity: 0.15,
                    },
                    '& .learn-more': {
                      transform: 'translateX(5px)',
                    }
                  }
                }}
              >
                {/* Gradient Overlay */}
                <Box
                  className="gradient-overlay"
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '200px',
                    background: service.gradient,
                    opacity: 0.1,
                    transition: 'opacity 0.4s ease',
                    pointerEvents: 'none'
                  }}
                />

                {/* Top Bar */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 4,
                    background: service.gradient,
                  }}
                />

                <CardContent sx={{ p: 4, position: 'relative' }}>
                  {/* Icon */}
                  <Box
                    className="service-icon"
                    sx={{
                      display: 'inline-flex',
                      p: 2,
                      borderRadius: 2,
                      background: alpha(service.color, 0.1),
                      border: `1px solid ${alpha(service.color, 0.3)}`,
                      color: service.color,
                      mb: 3,
                      transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                      transformStyle: 'preserve-3d',
                    }}
                  >
                    {service.icon}
                  </Box>

                  {/* Title */}
                  <Typography
                    variant="overline"
                    sx={{
                      color: alpha(service.color, 0.8),
                      fontWeight: 600,
                      letterSpacing: 1,
                      display: 'block',
                      mb: 1
                    }}
                  >
                    {service.subtitle}
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      color: '#FFFFFF',
                      mb: 2
                    }}
                  >
                    {service.title}
                  </Typography>

                  {/* Description */}
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha('#FFFFFF', 0.7),
                      lineHeight: 1.7,
                      mb: 3
                    }}
                  >
                    {service.description}
                  </Typography>

                  {/* Features List */}
                  <Stack spacing={1.5} sx={{ mb: 3 }}>
                    {service.features.map((feature, idx) => (
                      <Stack
                        key={idx}
                        direction="row"
                        spacing={1.5}
                        alignItems="center"
                      >
                        <Box
                          sx={{
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            background: service.color,
                            boxShadow: `0 0 10px ${alpha(service.color, 0.6)}`
                          }}
                        />
                        <Typography
                          variant="body2"
                          sx={{
                            color: alpha('#FFFFFF', 0.8),
                            fontSize: '0.9rem'
                          }}
                        >
                          {feature}
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>

                  {/* Learn More Link */}
                  <Button
                    endIcon={<ArrowForward className="learn-more" sx={{ transition: 'transform 0.3s ease' }} />}
                    sx={{
                      color: service.color,
                      fontWeight: 600,
                      p: 0,
                      '&:hover': {
                        background: 'transparent',
                      }
                    }}
                  >
                    자세히 보기
                  </Button>
                </CardContent>

                {/* Bottom Accent */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '1px',
                    background: `linear-gradient(90deg, transparent 0%, ${service.color} 50%, transparent 100%)`,
                    opacity: 0.5
                  }}
                />
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Additional Features */}
        <Box sx={{ mt: 12, textAlign: 'center' }}>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              mb: 6,
              color: '#FFFFFF'
            }}
          >
            더 많은 기능들
          </Typography>
          <Grid container spacing={3}>
            {[
              {
                icon: <Speed />,
                title: '실시간 신호',
                description: '밀리초 단위 시장 모니터링'
              },
              {
                icon: <TrendingUp />,
                title: '자동매매',
                description: '검증된 전략 자동 실행'
              },
              {
                icon: <Analytics />,
                title: '성과 분석',
                description: 'AI 기반 포트폴리오 리포트'
              }
            ].map((feature, index) => (
              <Grid item xs={12} sm={4} key={index}>
                <Stack
                  alignItems="center"
                  spacing={2}
                  sx={{
                    p: 3,
                    borderRadius: 2,
                    background: alpha('#1A1F3A', 0.4),
                    border: `1px solid ${alpha('#FFFFFF', 0.1)}`,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: alpha('#1A1F3A', 0.6),
                      borderColor: alpha('#FFB800', 0.5),
                      transform: 'translateY(-4px)'
                    }
                  }}
                >
                  <Box
                    sx={{
                      color: '#FFB800',
                      '& svg': { fontSize: 40 }
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      color: '#FFFFFF'
                    }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha('#FFFFFF', 0.7)
                    }}
                  >
                    {feature.description}
                  </Typography>
                </Stack>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default CoreServicesSection
