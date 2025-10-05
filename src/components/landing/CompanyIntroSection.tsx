import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Stack,
  Paper,
  alpha,
  useTheme
} from '@mui/material'
import {
  TrendingUp,
  Security,
  Speed,
  AutoGraph
} from '@mui/icons-material'

const CompanyIntroSection: React.FC = () => {
  const theme = useTheme()

  return (
    <Box sx={{ py: 12, background: '#0A0E1A' }}>
      <Container maxWidth="lg">
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 8 }}>
          <Typography
            variant="overline"
            sx={{
              color: '#FFB800',
              fontWeight: 700,
              letterSpacing: 2,
              fontSize: '0.9rem'
            }}
          >
            ABOUT KYYQUANT
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
            개인 투자자를 위한
            <br />
            AI 퀀트 투자 혁명
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
            KyyQuant는 개인 투자자도 기관 투자자처럼 체계적이고 과학적인 투자를 할 수 있도록
            AI 기반 퀀트 투자 플랫폼을 제공합니다.
          </Typography>
        </Stack>

        {/* Mission & Vision */}
        <Grid container spacing={4} sx={{ mb: 8 }}>
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 5,
                height: '100%',
                background: `linear-gradient(135deg, ${alpha('#FFB800', 0.1)} 0%, ${alpha('#1A1F3A', 0.8)} 100%)`,
                backdropFilter: 'blur(10px)',
                border: `1px solid ${alpha('#FFB800', 0.3)}`,
                borderRadius: 3,
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: `0 20px 60px ${alpha('#FFB800', 0.3)}`,
                },
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: 4,
                  height: '100%',
                  background: 'linear-gradient(180deg, #FFB800 0%, #FF6B00 100%)',
                }
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800'
                }}
              >
                Our Mission
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha('#FFFFFF', 0.8),
                  lineHeight: 1.8,
                  fontSize: '1.1rem'
                }}
              >
                모든 개인 투자자가 데이터 기반의 체계적인 투자 전략을 통해
                안정적인 수익을 창출할 수 있는 환경을 만듭니다.
                감정이 아닌 알고리즘으로, 추측이 아닌 데이터로 투자하는 새로운 시대를 엽니다.
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 5,
                height: '100%',
                background: `linear-gradient(135deg, ${alpha('#B388FF', 0.1)} 0%, ${alpha('#1A1F3A', 0.8)} 100%)`,
                backdropFilter: 'blur(10px)',
                border: `1px solid ${alpha('#B388FF', 0.3)}`,
                borderRadius: 3,
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: `0 20px 60px ${alpha('#B388FF', 0.3)}`,
                },
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: 4,
                  height: '100%',
                  background: 'linear-gradient(180deg, #B388FF 0%, #7C4DFF 100%)',
                }
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#B388FF'
                }}
              >
                Our Vision
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha('#FFFFFF', 0.8),
                  lineHeight: 1.8,
                  fontSize: '1.1rem'
                }}
              >
                AI와 빅데이터 기술을 활용하여 금융 시장의 불균형을 해소하고,
                개인 투자자와 기관 투자자의 정보 격차를 없앱니다.
                누구나 공정하고 투명한 투자 기회를 얻을 수 있는 미래를 만들어갑니다.
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Core Values */}
        <Grid container spacing={3}>
          {[
            {
              icon: <AutoGraph sx={{ fontSize: 48 }} />,
              title: 'AI 기반 분석',
              description: '머신러닝과 딥러닝 기술로 시장을 분석하고 최적의 투자 전략을 제시합니다',
              color: '#00E5FF'
            },
            {
              icon: <TrendingUp sx={{ fontSize: 48 }} />,
              title: '검증된 백테스팅',
              description: '10년 이상의 과거 데이터로 전략을 검증하고 리스크를 사전에 파악합니다',
              color: '#4CAF50'
            },
            {
              icon: <Speed sx={{ fontSize: 48 }} />,
              title: '실시간 자동화',
              description: '밀리초 단위 시장 모니터링과 자동 매매로 기회를 놓치지 않습니다',
              color: '#FF6B00'
            },
            {
              icon: <Security sx={{ fontSize: 48 }} />,
              title: '안전한 보안',
              description: '엔터프라이즈급 보안 시스템으로 고객의 자산과 데이터를 안전하게 보호합니다',
              color: '#B388FF'
            }
          ].map((value, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper
                sx={{
                  p: 4,
                  height: '100%',
                  background: alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${alpha(value.color, 0.2)}`,
                  borderRadius: 2,
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    borderColor: value.color,
                    boxShadow: `0 12px 40px ${alpha(value.color, 0.3)}`,
                    '& .icon': {
                      transform: 'scale(1.1) rotateY(360deg)',
                    }
                  }
                }}
              >
                <Box
                  className="icon"
                  sx={{
                    color: value.color,
                    mb: 2,
                    transition: 'transform 0.6s ease',
                    transformStyle: 'preserve-3d',
                  }}
                >
                  {value.icon}
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    mb: 2,
                    color: '#FFFFFF'
                  }}
                >
                  {value.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: alpha('#FFFFFF', 0.7),
                    lineHeight: 1.6
                  }}
                >
                  {value.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Company Info */}
        <Box
          sx={{
            mt: 10,
            p: 5,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${alpha('#1A1F3A', 0.8)} 0%, ${alpha('#0A0E1A', 0.9)} 100%)`,
            border: `1px solid ${alpha('#FFB800', 0.2)}`,
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              right: 0,
              width: '300px',
              height: '300px',
              background: 'radial-gradient(circle, rgba(255, 184, 0, 0.1) 0%, transparent 70%)',
              pointerEvents: 'none'
            }}
          />

          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800'
                }}
              >
                회사 정보
              </Typography>
              <Stack spacing={2}>
                {[
                  { label: '회사명', value: 'KyyQuant AI Solution' },
                  { label: '대표자', value: '홍길동' },
                  { label: '설립일', value: '2020년 1월' },
                  { label: '주요사업', value: 'AI 기반 퀀트 투자 플랫폼' }
                ].map((item, index) => (
                  <Stack
                    key={index}
                    direction="row"
                    spacing={2}
                    sx={{
                      py: 1.5,
                      borderBottom: `1px solid ${alpha('#FFFFFF', 0.1)}`
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        minWidth: 100,
                        fontWeight: 600,
                        color: alpha('#FFFFFF', 0.6)
                      }}
                    >
                      {item.label}
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 500,
                        color: '#FFFFFF'
                      }}
                    >
                      {item.value}
                    </Typography>
                  </Stack>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  color: '#FFB800'
                }}
              >
                연혁
              </Typography>
              <Stack spacing={2}>
                {[
                  { year: '2024', event: '자동매매 시스템 고도화' },
                  { year: '2023', event: 'AI 백테스팅 엔진 v2.0 출시' },
                  { year: '2022', event: '사용자 1,000명 돌파' },
                  { year: '2020', event: 'KyyQuant 설립' }
                ].map((item, index) => (
                  <Stack
                    key={index}
                    direction="row"
                    spacing={2}
                    sx={{
                      position: 'relative',
                      pl: 3,
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: 8,
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: '#FFB800',
                        boxShadow: `0 0 20px ${alpha('#FFB800', 0.6)}`
                      }
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        minWidth: 60,
                        fontWeight: 700,
                        color: '#FFB800'
                      }}
                    >
                      {item.year}
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{
                        color: alpha('#FFFFFF', 0.8)
                      }}
                    >
                      {item.event}
                    </Typography>
                  </Stack>
                ))}
              </Stack>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  )
}

export default CompanyIntroSection
