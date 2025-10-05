import React from 'react'
import { Box, Container, Typography, Grid, Stack, Paper, alpha } from '@mui/material'
import { Business, People, Timeline, EmojiEvents } from '@mui/icons-material'

const AboutPage: React.FC = () => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" fontWeight="bold" sx={{ mb: 6, textAlign: 'center' }}>
          회사 소개
        </Typography>

        {/* Company Overview */}
        <Paper sx={{ p: 6, mb: 6, background: alpha('#1A1F3A', 0.6) }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
            <Business sx={{ fontSize: 40, color: '#FFB800' }} />
            <Typography variant="h4" fontWeight="bold">
              KyyQuant AI Solution
            </Typography>
          </Stack>
          <Typography variant="body1" sx={{ lineHeight: 1.8, color: alpha('#FFFFFF', 0.8) }}>
            KyyQuant는 개인 투자자도 기관 투자자처럼 체계적이고 과학적인 투자를 할 수 있도록
            AI 기반 퀀트 투자 플랫폼을 제공합니다. 우리의 전략 마켓플레이스를 통해
            전문가의 투자 전략을 쉽게 따라하거나, 나만의 전략을 공유하고 수익을 창출할 수 있습니다.
          </Typography>
        </Paper>

        {/* Mission & Vision */}
        <Grid container spacing={4} sx={{ mb: 6 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, height: '100%', background: alpha('#FFB800', 0.1) }}>
              <Typography variant="h5" fontWeight="bold" sx={{ mb: 2, color: '#FFB800' }}>
                Our Mission
              </Typography>
              <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                모든 개인 투자자가 데이터 기반의 체계적인 투자 전략을 통해
                안정적인 수익을 창출할 수 있는 환경을 만듭니다.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, height: '100%', background: alpha('#00E5FF', 0.1) }}>
              <Typography variant="h5" fontWeight="bold" sx={{ mb: 2, color: '#00E5FF' }}>
                Our Vision
              </Typography>
              <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                AI와 빅데이터 기술을 활용하여 금융 시장의 불균형을 해소하고,
                개인 투자자와 기관 투자자의 정보 격차를 없앱니다.
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Team */}
        <Paper sx={{ p: 6, mb: 6, background: alpha('#1A1F3A', 0.6) }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 4 }}>
            <People sx={{ fontSize: 40, color: '#FFB800' }} />
            <Typography variant="h4" fontWeight="bold">
              팀 소개
            </Typography>
          </Stack>
          <Typography variant="body1" sx={{ lineHeight: 1.8, color: alpha('#FFFFFF', 0.8) }}>
            KyyQuant는 금융공학, AI/ML, 소프트웨어 엔지니어링 전문가들로 구성된 팀입니다.
            우리는 각자의 전문성을 바탕으로 최고의 퀀트 투자 플랫폼을 만들어가고 있습니다.
          </Typography>
        </Paper>

        {/* History */}
        <Paper sx={{ p: 6, background: alpha('#1A1F3A', 0.6) }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 4 }}>
            <Timeline sx={{ fontSize: 40, color: '#FFB800' }} />
            <Typography variant="h4" fontWeight="bold">
              연혁
            </Typography>
          </Stack>
          <Stack spacing={3}>
            {[
              { year: '2024', event: '전략 마켓플레이스 출시, 자동매매 시스템 고도화' },
              { year: '2023', event: 'AI 백테스팅 엔진 v2.0 출시' },
              { year: '2022', event: '사용자 1,000명 돌파' },
              { year: '2020', event: 'KyyQuant 설립' }
            ].map((item, index) => (
              <Stack key={index} direction="row" spacing={3}>
                <Typography variant="h6" sx={{ minWidth: 80, color: '#FFB800', fontWeight: 700 }}>
                  {item.year}
                </Typography>
                <Typography variant="body1" sx={{ color: alpha('#FFFFFF', 0.8) }}>
                  {item.event}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </Paper>
      </Container>
    </Box>
  )
}

export default AboutPage
