import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
  Avatar,
  alpha,
  Button,
  IconButton
} from '@mui/material'
import {
  TrendingUp,
  AccessTime,
  Visibility,
  ThumbUp,
  ArrowForward,
  ShowChart,
  Person
} from '@mui/icons-material'

interface CommunityHighlightSectionProps {
  onLoginClick: () => void
}

const CommunityHighlightSection: React.FC<CommunityHighlightSectionProps> = ({ onLoginClick }) => {
  // Mock data - 실제로는 Supabase에서 가져올 데이터
  const highlightPosts = [
    {
      id: 1,
      title: '모멘텀 + RSI 조합 전략으로 3개월 만에 45% 수익 달성',
      author: '퀀트마스터',
      avatar: null,
      category: '전략 공유',
      returnRate: 45.2,
      period: '3개월',
      views: 1240,
      likes: 89,
      timeAgo: '2시간 전',
      verified: true,
      color: '#4CAF50'
    },
    {
      id: 2,
      title: 'PER/PBR 가치주 전략 백테스트 결과 (10년 데이터)',
      author: '장기투자왕',
      avatar: null,
      category: '백테스트 결과',
      returnRate: 128.5,
      period: '10년',
      views: 2130,
      likes: 156,
      timeAgo: '5시간 전',
      verified: true,
      color: '#FF9800'
    },
    {
      id: 3,
      title: '변동성 돌파 전략 최적화 - 승률 78% 달성',
      author: '알고왕초보',
      avatar: null,
      category: '시장 분석',
      returnRate: 32.8,
      period: '2개월',
      views: 856,
      likes: 67,
      timeAgo: '1일 전',
      verified: false,
      color: '#00BCD4'
    }
  ]

  const [activeUsers, setActiveUsers] = useState(127)
  const [totalPosts, setTotalPosts] = useState(2456)
  const [totalStrategies, setTotalStrategies] = useState(892)

  // 실시간 카운터 애니메이션
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveUsers(prev => prev + Math.floor(Math.random() * 3))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Box
      sx={{
        py: 12,
        background: `linear-gradient(180deg, #1A1F3A 0%, #0A0E1A 100%)`,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '1000px',
          height: '1000px',
          background: 'radial-gradient(circle, rgba(0, 229, 255, 0.05) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 8 }}>
          <Typography
            variant="overline"
            sx={{
              color: '#00E5FF',
              fontWeight: 700,
              letterSpacing: 2,
              fontSize: '0.9rem'
            }}
          >
            COMMUNITY HIGHLIGHTS
          </Typography>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #00E5FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            실시간 커뮤니티 활동
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
            전문 투자자들의 생생한 전략과 백테스트 결과를 확인하세요
          </Typography>
        </Stack>

        {/* Live Stats */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {[
            {
              label: '현재 접속자',
              value: activeUsers,
              suffix: '명',
              icon: <Person />,
              color: '#00E5FF',
              pulse: true
            },
            {
              label: '공유된 전략',
              value: totalStrategies,
              suffix: '개',
              icon: <ShowChart />,
              color: '#4CAF50',
              pulse: false
            },
            {
              label: '커뮤니티 게시글',
              value: totalPosts,
              suffix: '개',
              icon: <TrendingUp />,
              color: '#FFB800',
              pulse: false
            }
          ].map((stat, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  background: alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `1px solid ${alpha(stat.color, 0.3)}`,
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: stat.color,
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 40px ${alpha(stat.color, 0.3)}`
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        background: alpha(stat.color, 0.1),
                        border: `1px solid ${alpha(stat.color, 0.3)}`,
                        color: stat.color,
                        display: 'flex',
                        position: 'relative'
                      }}
                    >
                      {stat.icon}
                      {stat.pulse && (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: -2,
                            right: -2,
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            background: '#4CAF50',
                            animation: 'pulse 2s infinite',
                            '@keyframes pulse': {
                              '0%, 100%': {
                                opacity: 1,
                                transform: 'scale(1)'
                              },
                              '50%': {
                                opacity: 0.5,
                                transform: 'scale(1.2)'
                              }
                            }
                          }}
                        />
                      )}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ mb: 0.5 }}>
                        <Typography
                          component="span"
                          variant="h4"
                          sx={{
                            fontWeight: 900,
                            color: stat.color
                          }}
                        >
                          {stat.value.toLocaleString()}
                        </Typography>
                        <Typography
                          component="span"
                          variant="h6"
                          sx={{ ml: 0.5, color: alpha('#FFFFFF', 0.6) }}
                        >
                          {stat.suffix}
                        </Typography>
                      </Box>
                      <Typography
                        variant="body2"
                        sx={{ color: alpha('#FFFFFF', 0.7) }}
                      >
                        {stat.label}
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Highlight Posts */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {highlightPosts.map((post, index) => (
            <Grid item xs={12} md={4} key={post.id}>
              <Card
                sx={{
                  height: '100%',
                  background: alpha('#0A0E1A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `2px solid ${alpha(post.color, 0.3)}`,
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    borderColor: post.color,
                    boxShadow: `0 20px 60px ${alpha(post.color, 0.4)}`,
                    '& .return-badge': {
                      transform: 'scale(1.1)',
                    }
                  }
                }}
                onClick={onLoginClick}
              >
                {/* Top Bar */}
                <Box
                  sx={{
                    height: 4,
                    background: `linear-gradient(90deg, ${post.color} 0%, transparent 100%)`,
                  }}
                />

                <CardContent sx={{ p: 3 }}>
                  {/* Category & Time */}
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Chip
                      label={post.category}
                      size="small"
                      sx={{
                        background: alpha(post.color, 0.1),
                        border: `1px solid ${alpha(post.color, 0.3)}`,
                        color: post.color,
                        fontWeight: 600,
                        fontSize: '0.75rem'
                      }}
                    />
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <AccessTime sx={{ fontSize: 14, color: alpha('#FFFFFF', 0.5) }} />
                      <Typography variant="caption" sx={{ color: alpha('#FFFFFF', 0.5) }}>
                        {post.timeAgo}
                      </Typography>
                    </Stack>
                  </Stack>

                  {/* Title */}
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      color: '#FFFFFF',
                      mb: 2,
                      minHeight: 64,
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}
                  >
                    {post.title}
                  </Typography>

                  {/* Return Rate Badge */}
                  <Box
                    className="return-badge"
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 1,
                      px: 2,
                      py: 1,
                      mb: 3,
                      borderRadius: 2,
                      background: alpha(post.color, 0.15),
                      border: `1px solid ${alpha(post.color, 0.4)}`,
                      transition: 'transform 0.3s ease'
                    }}
                  >
                    <TrendingUp sx={{ color: post.color, fontSize: 20 }} />
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 900,
                        color: post.color
                      }}
                    >
                      +{post.returnRate}%
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: alpha('#FFFFFF', 0.7)
                      }}
                    >
                      ({post.period})
                    </Typography>
                  </Box>

                  {/* Author & Stats */}
                  <Stack spacing={2}>
                    <Stack direction="row" alignItems="center" spacing={1.5}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          background: alpha(post.color, 0.2),
                          border: `2px solid ${alpha(post.color, 0.4)}`,
                          color: post.color,
                          fontSize: '0.9rem',
                          fontWeight: 700
                        }}
                      >
                        {post.author[0]}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            color: '#FFFFFF'
                          }}
                        >
                          {post.author}
                          {post.verified && (
                            <Chip
                              label="인증"
                              size="small"
                              sx={{
                                ml: 1,
                                height: 18,
                                fontSize: '0.65rem',
                                background: alpha('#4CAF50', 0.2),
                                color: '#4CAF50',
                                border: `1px solid ${alpha('#4CAF50', 0.4)}`
                              }}
                            />
                          )}
                        </Typography>
                      </Box>
                    </Stack>

                    <Stack direction="row" spacing={3}>
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <Visibility sx={{ fontSize: 16, color: alpha('#FFFFFF', 0.5) }} />
                        <Typography variant="caption" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                          {post.views.toLocaleString()}
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <ThumbUp sx={{ fontSize: 16, color: alpha('#FFFFFF', 0.5) }} />
                        <Typography variant="caption" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                          {post.likes}
                        </Typography>
                      </Stack>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* CTA */}
        <Box sx={{ textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            endIcon={<ArrowForward />}
            onClick={onLoginClick}
            sx={{
              py: 2,
              px: 5,
              fontSize: '1.1rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #00E5FF 0%, #00B8D4 100%)',
              boxShadow: `0 8px 32px ${alpha('#00E5FF', 0.4)}`,
              '&:hover': {
                background: 'linear-gradient(135deg, #00B8D4 0%, #0097A7 100%)',
                boxShadow: `0 12px 48px ${alpha('#00E5FF', 0.6)}`,
                transform: 'translateY(-2px)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            커뮤니티 둘러보기
          </Button>
          <Typography
            variant="body2"
            sx={{
              mt: 2,
              color: alpha('#FFFFFF', 0.6)
            }}
          >
            로그인하고 더 많은 전략과 인사이트를 확인하세요
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default CommunityHighlightSection
