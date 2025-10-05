import React from 'react'
import { Box, Container, Typography, Grid, Card, CardContent, Stack, alpha } from '@mui/material'
import {
  FilterAlt,
  Architecture,
  Assessment,
  Speed,
  TrendingUp,
  Analytics,
  Store
} from '@mui/icons-material'

const ServicesPage: React.FC = () => {
  const services = [
    {
      icon: <Store sx={{ fontSize: 60 }} />,
      title: '전략 마켓플레이스',
      description: '전문가의 검증된 투자 전략을 팔로우하거나, 나만의 전략을 공유하고 수익을 창출하세요.',
      features: ['전략 팔로우', '자동 매매 실행', '이중 수익 구조', '전략 보호'],
      color: '#FFB800'
    },
    {
      icon: <FilterAlt sx={{ fontSize: 60 }} />,
      title: '투자 유니버스 필터링',
      description: '30+ 재무지표와 기술적 지표를 활용하여 우량 종목을 자동으로 선별합니다.',
      features: ['재무지표 필터링', '실시간 스크리닝', '커스텀 필터 저장', '백테스트 연동'],
      color: '#00E5FF'
    },
    {
      icon: <Architecture sx={{ fontSize: 60 }} />,
      title: '전략 빌더',
      description: '코딩 없이 클릭만으로 복잡한 매매 전략을 만들고 최적화할 수 있습니다.',
      features: ['노코드 전략 생성', '50+ 기술적 지표', '다중 조건 설정', '전략 템플릿'],
      color: '#4CAF50'
    },
    {
      icon: <Assessment sx={{ fontSize: 60 }} />,
      title: '백테스팅 엔진',
      description: '과거 10년 데이터로 전략을 검증하고 성과를 시뮬레이션합니다.',
      features: ['10년+ 과거 데이터', '실시간 결과 분석', '리스크 지표', '최적화 기능'],
      color: '#B388FF'
    },
    {
      icon: <Speed sx={{ fontSize: 60 }} />,
      title: '실시간 신호',
      description: '밀리초 단위로 시장을 모니터링하고 매매 시그널을 포착합니다.',
      features: ['실시간 모니터링', '즉시 알림', '신호 필터링', 'WebSocket 연결'],
      color: '#00BCD4'
    },
    {
      icon: <TrendingUp sx={{ fontSize: 60 }} />,
      title: '자동매매',
      description: '검증된 전략을 자동으로 실행하여 기회를 놓치지 않습니다.',
      features: ['자동 주문 실행', '위험 관리', '포지션 관리', '실시간 모니터링'],
      color: '#F44336'
    },
    {
      icon: <Analytics sx={{ fontSize: 60 }} />,
      title: '성과 분석',
      description: 'AI가 포트폴리오를 분석하고 개선점을 제안합니다.',
      features: ['AI 분석 리포트', '수익률 추적', '리스크 분석', '개선 제안'],
      color: '#9C27B0'
    }
  ]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" fontWeight="bold" sx={{ mb: 2, textAlign: 'center' }}>
          서비스 소개
        </Typography>
        <Typography variant="h6" sx={{ mb: 8, textAlign: 'center', color: alpha('#FFFFFF', 0.7) }}>
          체계적인 투자를 위한 모든 도구를 제공합니다
        </Typography>

        <Grid container spacing={4}>
          {services.map((service, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card
                sx={{
                  height: '100%',
                  background: alpha('#1A1F3A', 0.6),
                  border: `2px solid ${alpha(service.color, 0.3)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: service.color,
                    transform: 'translateY(-8px)',
                    boxShadow: `0 12px 40px ${alpha(service.color, 0.3)}`
                  }
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ color: service.color, mb: 3 }}>
                    {service.icon}
                  </Box>
                  <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
                    {service.title}
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 3, color: alpha('#FFFFFF', 0.8), lineHeight: 1.7 }}>
                    {service.description}
                  </Typography>
                  <Stack spacing={1.5}>
                    {service.features.map((feature, idx) => (
                      <Stack key={idx} direction="row" spacing={1.5} alignItems="center">
                        <Box
                          sx={{
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            background: service.color
                          }}
                        />
                        <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.9) }}>
                          {feature}
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  )
}

export default ServicesPage
