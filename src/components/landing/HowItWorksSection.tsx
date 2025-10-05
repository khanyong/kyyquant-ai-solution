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
  Avatar
} from '@mui/material'
import {
  Search,
  TouchApp,
  Autorenew,
  AccountBalanceWallet,
  TrendingUp,
  Share,
  People,
  MonetizationOn
} from '@mui/icons-material'

const HowItWorksSection: React.FC = () => {
  const followerSteps = [
    {
      step: '01',
      icon: <Search sx={{ fontSize: 40 }} />,
      title: '전략 검색 및 비교',
      description: '수익률, 승률, 팔로워 수 등을 비교하여 원하는 전략을 찾습니다',
      color: '#00E5FF'
    },
    {
      step: '02',
      icon: <TouchApp sx={{ fontSize: 40 }} />,
      title: '전략 팔로우',
      description: '마음에 드는 전략을 클릭 한 번으로 팔로우합니다',
      color: '#4CAF50'
    },
    {
      step: '03',
      icon: <Autorenew sx={{ fontSize: 40 }} />,
      title: '자동 매매 실행',
      description: '전략의 매수/매도 시그널이 자동으로 실행됩니다',
      color: '#FF9800'
    },
    {
      step: '04',
      icon: <AccountBalanceWallet sx={{ fontSize: 40 }} />,
      title: '수익 창출',
      description: '전문가의 전략으로 안정적인 수익을 얻고 월 사용료만 지불합니다',
      color: '#FFB800'
    }
  ]

  const creatorSteps = [
    {
      step: '01',
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      title: '전략 개발 및 검증',
      description: '자신만의 투자 전략을 개발하고 백테스트로 검증합니다',
      color: '#B388FF'
    },
    {
      step: '02',
      icon: <Share sx={{ fontSize: 40 }} />,
      title: '전략 공개',
      description: '검증된 전략을 마켓플레이스에 공개합니다 (내용은 비공개)',
      color: '#00E5FF'
    },
    {
      step: '03',
      icon: <People sx={{ fontSize: 40 }} />,
      title: '팔로워 유치',
      description: '높은 수익률로 투자자들이 전략을 팔로우합니다',
      color: '#4CAF50'
    },
    {
      step: '04',
      icon: <MonetizationOn sx={{ fontSize: 40 }} />,
      title: '이중 수익 창출',
      description: '본인 투자 수익 + (팔로워 수 × 월 사용료) 로 수익을 극대화합니다',
      color: '#FFB800'
    }
  ]

  const renderSteps = (steps: typeof followerSteps, title: string, subtitle: string) => (
    <Box sx={{ mb: 10 }}>
      <Typography
        variant="h3"
        sx={{
          fontWeight: 800,
          color: '#FFFFFF',
          mb: 2,
          textAlign: 'center'
        }}
      >
        {title}
      </Typography>
      <Typography
        variant="h6"
        sx={{
          color: alpha('#FFFFFF', 0.7),
          mb: 6,
          textAlign: 'center',
          maxWidth: 700,
          mx: 'auto'
        }}
      >
        {subtitle}
      </Typography>

      <Grid container spacing={3}>
        {steps.map((step, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                background: alpha('#1A1F3A', 0.6),
                backdropFilter: 'blur(20px)',
                border: `2px solid ${alpha(step.color, 0.3)}`,
                borderRadius: 3,
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.4s ease',
                '&:hover': {
                  transform: 'translateY(-12px)',
                  borderColor: step.color,
                  boxShadow: `0 20px 60px ${alpha(step.color, 0.5)}`,
                  '& .step-number': {
                    transform: 'scale(1.1)',
                  },
                  '& .icon-box': {
                    transform: 'rotateY(360deg)',
                  }
                }
              }}
            >
              {/* Step Number */}
              <Box
                className="step-number"
                sx={{
                  position: 'absolute',
                  top: -15,
                  right: 15,
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${step.color} 0%, ${alpha(step.color, 0.7)} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: `0 8px 32px ${alpha(step.color, 0.5)}`,
                  transition: 'transform 0.4s ease',
                  zIndex: 2
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 900,
                    color: '#000'
                  }}
                >
                  {step.step}
                </Typography>
              </Box>

              {/* Top Bar */}
              <Box
                sx={{
                  height: 5,
                  background: `linear-gradient(90deg, ${step.color} 0%, transparent 100%)`
                }}
              />

              {/* Arrow (except last card) */}
              {index < steps.length - 1 && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    right: { xs: 'auto', md: -20 },
                    bottom: { xs: -20, md: 'auto' },
                    left: { xs: '50%', md: 'auto' },
                    transform: {
                      xs: 'translate(-50%, 0) rotate(90deg)',
                      md: 'translateY(-50%)'
                    },
                    zIndex: 3,
                    display: { xs: 'none', sm: 'block' }
                  }}
                >
                  <Box
                    sx={{
                      width: 0,
                      height: 0,
                      borderTop: '15px solid transparent',
                      borderBottom: '15px solid transparent',
                      borderLeft: `20px solid ${alpha(step.color, 0.5)}`
                    }}
                  />
                </Box>
              )}

              <CardContent sx={{ p: 4, pt: 5 }}>
                {/* Icon */}
                <Box
                  className="icon-box"
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: alpha(step.color, 0.1),
                    border: `1px solid ${alpha(step.color, 0.3)}`,
                    color: step.color,
                    display: 'inline-flex',
                    mb: 3,
                    transition: 'transform 0.8s ease',
                    transformStyle: 'preserve-3d'
                  }}
                >
                  {step.icon}
                </Box>

                {/* Title */}
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    color: '#FFFFFF',
                    mb: 2,
                    minHeight: 56
                  }}
                >
                  {step.title}
                </Typography>

                {/* Description */}
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    lineHeight: 1.7
                  }}
                >
                  {step.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )

  return (
    <Box
      sx={{
        py: 12,
        background: `linear-gradient(180deg, #0A0E1A 0%, #1A1F3A 50%, #0A0E1A 100%)`,
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
            HOW IT WORKS
          </Typography>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #FFB800 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            이렇게 작동합니다
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
            간단한 4단계로 전략을 팔로우하거나 수익을 창출하세요
          </Typography>
        </Stack>

        {/* Follower Process */}
        {renderSteps(
          followerSteps,
          '팔로워: 전략 따라하기',
          '전문가의 전략을 따라하고 수익을 창출하는 과정'
        )}

        {/* Divider */}
        <Box
          sx={{
            my: 10,
            height: 2,
            background: `linear-gradient(90deg, transparent 0%, ${alpha('#FFB800', 0.5)} 50%, transparent 100%)`
          }}
        />

        {/* Creator Process */}
        {renderSteps(
          creatorSteps,
          '전략 개발자: 이중 수익 창출',
          '전략을 공유하고 본인 수익 + 팔로워 사용료로 수익을 극대화하는 과정'
        )}

        {/* Earnings Example */}
        <Box
          sx={{
            mt: 8,
            p: 6,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${alpha('#FFB800', 0.15)} 0%, ${alpha('#1A1F3A', 0.9)} 100%)`,
            border: `2px solid ${alpha('#FFB800', 0.4)}`
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 800,
              color: '#FFB800',
              mb: 4,
              textAlign: 'center'
            }}
          >
            💰 전략 개발자 수익 시뮬레이션
          </Typography>

          <Grid container spacing={3}>
            {[
              {
                followers: 100,
                fee: 39000,
                monthly: 3900000,
                yearly: 46800000,
                label: '초보 개발자'
              },
              {
                followers: 1000,
                fee: 49000,
                monthly: 49000000,
                yearly: 588000000,
                label: '중급 개발자'
              },
              {
                followers: 3000,
                fee: 99000,
                monthly: 297000000,
                yearly: 3564000000,
                label: '전문 개발자'
              }
            ].map((scenario, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card
                  sx={{
                    background: alpha('#1A1F3A', 0.6),
                    border: `2px solid ${alpha('#FFB800', 0.3)}`,
                    borderRadius: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: '#FFB800',
                      transform: 'translateY(-4px)',
                      boxShadow: `0 12px 40px ${alpha('#FFB800', 0.3)}`
                    }
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 700,
                        color: '#FFB800',
                        mb: 3,
                        textAlign: 'center'
                      }}
                    >
                      {scenario.label}
                    </Typography>

                    <Stack spacing={2}>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                          팔로워
                        </Typography>
                        <Typography variant="body1" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                          {scenario.followers.toLocaleString()}명
                        </Typography>
                      </Stack>

                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                          월 사용료
                        </Typography>
                        <Typography variant="body1" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
                          ₩{scenario.fee.toLocaleString()}
                        </Typography>
                      </Stack>

                      <Box sx={{ height: 1, background: alpha('#FFFFFF', 0.1), my: 1 }} />

                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" sx={{ color: alpha('#FFB800', 0.9), fontWeight: 700 }}>
                          월 수익
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#FFB800', fontWeight: 900 }}>
                          ₩{scenario.monthly.toLocaleString()}
                        </Typography>
                      </Stack>

                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" sx={{ color: alpha('#4CAF50', 0.9), fontWeight: 700 }}>
                          연 수익
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#4CAF50', fontWeight: 900 }}>
                          ₩{scenario.yearly.toLocaleString()}
                        </Typography>
                      </Stack>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Typography
            variant="body2"
            sx={{
              mt: 4,
              textAlign: 'center',
              color: alpha('#FFFFFF', 0.6)
            }}
          >
            * 본인 투자 수익은 별도입니다. 위 금액은 팔로워 사용료만 계산한 예상 수익입니다.
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default HowItWorksSection
