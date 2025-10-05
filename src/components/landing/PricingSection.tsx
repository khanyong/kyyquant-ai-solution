import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  alpha
} from '@mui/material'
import {
  CheckCircle,
  ArrowForward,
  Star
} from '@mui/icons-material'

interface PricingSectionProps {
  onLoginClick: () => void
}

const PricingSection: React.FC<PricingSectionProps> = ({ onLoginClick }) => {
  const plans = [
    {
      name: 'Basic',
      price: '무료',
      period: '',
      description: '개인 투자자를 위한 기본 플랜',
      features: [
        '기본 백테스팅 (월 10회)',
        '투자 유니버스 필터링',
        '3개 전략 저장',
        '일별 시장 리포트',
        '커뮤니티 접근'
      ],
      color: '#90CAF9',
      popular: false,
      gradient: 'linear-gradient(135deg, #90CAF9 0%, #64B5F6 100%)'
    },
    {
      name: 'Pro',
      price: '49,000원',
      period: '/ 월',
      description: '전문 투자자를 위한 프리미엄 플랜',
      features: [
        '무제한 백테스팅',
        '고급 필터링 도구',
        '무제한 전략 저장',
        '실시간 신호 알림',
        '자동매매 연동',
        'AI 포트폴리오 분석',
        '우선 고객 지원',
        '전략 템플릿 제공'
      ],
      color: '#FFB800',
      popular: true,
      gradient: 'linear-gradient(135deg, #FFB800 0%, #FF8A00 100%)'
    },
    {
      name: 'Enterprise',
      price: '문의',
      period: '',
      description: '기관/법인을 위한 맞춤형 솔루션',
      features: [
        'Pro 플랜 모든 기능',
        '전용 서버 환경',
        'API 접근 권한',
        '맞춤형 전략 개발',
        '전담 매니저 배정',
        '온사이트 교육',
        'White-label 솔루션',
        'SLA 보장'
      ],
      color: '#B388FF',
      popular: false,
      gradient: 'linear-gradient(135deg, #B388FF 0%, #7C4DFF 100%)'
    }
  ]

  return (
    <Box
      sx={{
        py: 12,
        background: '#0A0E1A',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Effects */}
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '800px',
          height: '800px',
          background: 'radial-gradient(circle, rgba(255, 184, 0, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none'
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
            PRICING PLANS
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
            당신에게 맞는 플랜을 선택하세요
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
            모든 플랜은 7일 무료 체험이 가능합니다
          </Typography>
        </Stack>

        {/* Pricing Cards */}
        <Grid container spacing={4} alignItems="stretch">
          {plans.map((plan, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  background: plan.popular
                    ? `linear-gradient(135deg, ${alpha('#FFB800', 0.15)} 0%, ${alpha('#1A1F3A', 0.9)} 100%)`
                    : alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `2px solid ${plan.popular ? plan.color : alpha(plan.color, 0.3)}`,
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  transform: plan.popular ? 'scale(1.05)' : 'scale(1)',
                  transition: 'all 0.4s ease',
                  '&:hover': {
                    transform: plan.popular ? 'scale(1.07)' : 'scale(1.03)',
                    borderColor: plan.color,
                    boxShadow: `0 20px 60px ${alpha(plan.color, 0.4)}`,
                  }
                }}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 20,
                      right: -35,
                      transform: 'rotate(45deg)',
                      background: plan.gradient,
                      color: '#000',
                      py: 0.5,
                      px: 6,
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      letterSpacing: 1,
                      boxShadow: `0 4px 20px ${alpha(plan.color, 0.5)}`
                    }}
                  >
                    <Star sx={{ fontSize: 14, mr: 0.5, mb: -0.5 }} />
                    POPULAR
                  </Box>
                )}

                {/* Top Gradient Bar */}
                <Box
                  sx={{
                    height: 6,
                    background: plan.gradient,
                  }}
                />

                <CardContent sx={{ p: 4, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Plan Name */}
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      color: plan.color,
                      mb: 1
                    }}
                  >
                    {plan.name}
                  </Typography>

                  {/* Description */}
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha('#FFFFFF', 0.7),
                      mb: 3,
                      minHeight: 40
                    }}
                  >
                    {plan.description}
                  </Typography>

                  {/* Price */}
                  <Box sx={{ mb: 4 }}>
                    <Stack direction="row" alignItems="baseline" spacing={0.5}>
                      <Typography
                        variant="h3"
                        sx={{
                          fontWeight: 900,
                          color: '#FFFFFF'
                        }}
                      >
                        {plan.price}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: alpha('#FFFFFF', 0.6)
                        }}
                      >
                        {plan.period}
                      </Typography>
                    </Stack>
                  </Box>

                  {/* Features List */}
                  <List sx={{ mb: 4, flexGrow: 1 }}>
                    {plan.features.map((feature, idx) => (
                      <ListItem key={idx} sx={{ px: 0, py: 1 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckCircle
                            sx={{
                              color: plan.color,
                              fontSize: 20
                            }}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={feature}
                          primaryTypographyProps={{
                            variant: 'body2',
                            sx: { color: alpha('#FFFFFF', 0.9) }
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  {/* CTA Button */}
                  <Button
                    variant={plan.popular ? 'contained' : 'outlined'}
                    size="large"
                    fullWidth
                    endIcon={<ArrowForward />}
                    onClick={onLoginClick}
                    sx={{
                      py: 1.5,
                      fontWeight: 700,
                      ...(plan.popular ? {
                        background: plan.gradient,
                        boxShadow: `0 8px 32px ${alpha(plan.color, 0.4)}`,
                        '&:hover': {
                          boxShadow: `0 12px 40px ${alpha(plan.color, 0.6)}`,
                          transform: 'translateY(-2px)'
                        }
                      } : {
                        borderWidth: 2,
                        borderColor: alpha(plan.color, 0.5),
                        color: plan.color,
                        '&:hover': {
                          borderWidth: 2,
                          borderColor: plan.color,
                          background: alpha(plan.color, 0.1),
                          transform: 'translateY(-2px)'
                        }
                      }),
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {plan.price === '문의' ? '문의하기' : '시작하기'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Additional Info */}
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Typography
            variant="body1"
            sx={{
              color: alpha('#FFFFFF', 0.6),
              mb: 3
            }}
          >
            모든 플랜은 언제든지 업그레이드 또는 다운그레이드가 가능합니다
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            justifyContent="center"
            flexWrap="wrap"
          >
            {[
              '7일 무료 체험',
              '신용카드 불필요',
              '언제든지 취소 가능',
              '환불 보장'
            ].map((info, index) => (
              <Chip
                key={index}
                label={info}
                sx={{
                  background: alpha('#FFB800', 0.1),
                  border: `1px solid ${alpha('#FFB800', 0.3)}`,
                  color: '#FFB800',
                  fontWeight: 600
                }}
              />
            ))}
          </Stack>
        </Box>
      </Container>
    </Box>
  )
}

export default PricingSection
