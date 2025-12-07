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
  Button
} from '@mui/material'
import {
  TrendingUp,
  AccessTime,
  Visibility,
  ThumbUp,
  ArrowForward,
  ShowChart,
  Person,
  Wifi
} from '@mui/icons-material'

interface CommunityHighlightSectionProps {
  onLoginClick: () => void
}

const CommunityHighlightSection: React.FC<CommunityHighlightSectionProps> = ({ onLoginClick }) => {
  // Mock data
  const highlightPosts = [
    {
      id: 1,
      title: 'MOMENTUM_RSI_HYBRID_V3',
      author: 'QUANT_MASTER',
      category: 'STRATEGY',
      returnRate: 45.2,
      period: '3M',
      views: 1240,
      likes: 89,
      timeAgo: '2H_AGO',
      verified: true,
      color: '#4CAF50'
    },
    {
      id: 2,
      title: 'VALUE_FACTOR_DEEP_TEST',
      author: 'LTS_KING',
      category: 'BACKTEST',
      returnRate: 128.5,
      period: '10Y',
      views: 2130,
      likes: 156,
      timeAgo: '5H_AGO',
      verified: true,
      color: '#FF9800'
    },
    {
      id: 3,
      title: 'VOLATILITY_BREAKOUT_OPT',
      author: 'ALGO_NEWBIE',
      category: 'ANALYSIS',
      returnRate: 32.8,
      period: '2M',
      views: 856,
      likes: 67,
      timeAgo: '1D_AGO',
      verified: false,
      color: '#00BCD4'
    }
  ]

  const [activeUsers, setActiveUsers] = useState(127)
  const [totalPosts, setTotalPosts] = useState(2456)
  const [totalStrategies, setTotalStrategies] = useState(892)

  // Randomize stats slightly
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveUsers(prev => prev + Math.floor(Math.random() * 3) - 1)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Box
      sx={{
        py: 12,
        bgcolor: '#050912',
        position: 'relative',
        overflow: 'hidden',
        borderTop: `1px solid ${alpha('#00E5FF', 0.1)}`
      }}
    >
      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 10 }}>
          <Box
            sx={{
              border: '1px solid #00E5FF',
              px: 2,
              py: 0.5,
              bgcolor: alpha('#00E5FF', 0.1)
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: '#00E5FF',
                fontWeight: 700,
                fontFamily: '"JetBrains Mono", monospace',
                letterSpacing: 2
              }}
            >
              NETWORK_STATUS
            </Typography>
          </Box>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              color: '#fff',
              fontFamily: '"JetBrains Mono", monospace',
              textTransform: 'uppercase',
              letterSpacing: -2
            }}
          >
            LIVE DATA FEED
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              color: '#8F9EB3',
              lineHeight: 1.6,
              fontWeight: 400,
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            Real-time transmission of strategies and backtest results from the grid.
          </Typography>
        </Stack>

        {/* Live Stats */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {[
            {
              label: 'ACTIVE_NODES',
              value: activeUsers,
              suffix: '',
              icon: <Wifi />,
              color: '#00E5FF',
              pulse: true
            },
            {
              label: 'STRATEGIES_DEPLOYED',
              value: totalStrategies,
              suffix: '',
              icon: <ShowChart />,
              color: '#4CAF50',
              pulse: false
            },
            {
              label: 'DATA_LOGS',
              value: totalPosts,
              suffix: '',
              icon: <TrendingUp />,
              color: '#FFB800',
              pulse: false
            }
          ].map((stat, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Box
                sx={{
                  bgcolor: '#050912',
                  border: `1px solid ${alpha(stat.color, 0.3)}`,
                  p: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 3,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: stat.color,
                    boxShadow: `0 0 20px ${alpha(stat.color, 0.1)}`
                  }
                }}
              >
                <Box
                  sx={{
                    p: 1.5,
                    color: stat.color,
                    bgcolor: alpha(stat.color, 0.1),
                    border: `1px solid ${stat.color}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  {stat.icon}
                </Box>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 700,
                      color: '#fff',
                      fontFamily: '"JetBrains Mono", monospace',
                      lineHeight: 1
                    }}
                  >
                    {stat.value.toLocaleString()}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#5C6B7F',
                      fontFamily: '"JetBrains Mono", monospace',
                      letterSpacing: 1
                    }}
                  >
                    {stat.label}
                  </Typography>
                </Box>
                {stat.pulse && (
                  <Box
                    sx={{
                      ml: 'auto',
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      bgcolor: stat.color,
                      boxShadow: `0 0 10px ${stat.color}`,
                      animation: 'pulse 2s infinite',
                      '@keyframes pulse': {
                        '0%': { opacity: 1 },
                        '50%': { opacity: 0.5 },
                        '100%': { opacity: 1 }
                      }
                    }}
                  />
                )}
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Highlight Posts */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {highlightPosts.map((post, index) => (
            <Grid item xs={12} md={4} key={post.id}>
              <Box
                sx={{
                  height: '100%',
                  bgcolor: '#0A0E1A',
                  border: `1px solid ${alpha(post.color, 0.3)}`,
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    borderColor: post.color,
                    boxShadow: `0 0 20px ${alpha(post.color, 0.1)}`
                  }
                }}
                onClick={onLoginClick}
              >
                {/* Decorative Status Bar */}
                <Box
                  sx={{
                    height: 2,
                    width: '100%',
                    bgcolor: alpha(post.color, 0.5),
                    boxShadow: `0 0 10px ${post.color}`
                  }}
                />

                <CardContent sx={{ p: 3 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: post.color,
                        fontFamily: '"JetBrains Mono", monospace',
                        border: `1px solid ${post.color}`,
                        px: 1,
                        py: 0.25
                      }}
                    >
                      {post.category}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#5C6B7F',
                        fontFamily: '"JetBrains Mono", monospace'
                      }}
                    >
                      {post.timeAgo}
                    </Typography>
                  </Stack>

                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      color: '#fff',
                      mb: 2,
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '1rem',
                      lineHeight: 1.4,
                      minHeight: 50
                    }}
                  >
                    {post.title}
                  </Typography>

                  {/* Metrics */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1, bgcolor: alpha(post.color, 0.1), borderLeft: `2px solid ${post.color}` }}>
                        <Typography variant="caption" display="block" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>RETURN</Typography>
                        <Typography variant="body1" sx={{ color: post.color, fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>+{post.returnRate}%</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1, bgcolor: alpha('#fff', 0.05), borderLeft: `2px solid #5C6B7F` }}>
                        <Typography variant="caption" display="block" sx={{ color: '#5C6B7F', fontFamily: '"JetBrains Mono", monospace' }}>PERIOD</Typography>
                        <Typography variant="body1" sx={{ color: '#fff', fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>{post.period}</Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Stack direction="row" alignItems="center" justifyContent="space-between">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Avatar
                        sx={{
                          width: 24,
                          height: 24,
                          bgcolor: post.color,
                          color: '#000',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          fontFamily: '"JetBrains Mono", monospace'
                        }}
                      >
                        {post.author[0]}
                      </Avatar>
                      <Typography variant="caption" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace' }}>
                        {post.author}
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={2} sx={{ color: '#5C6B7F' }}>
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <Visibility sx={{ fontSize: 14 }} />
                        <Typography variant="caption" sx={{ fontFamily: '"JetBrains Mono", monospace' }}>{post.views}</Typography>
                      </Stack>
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <ThumbUp sx={{ fontSize: 14 }} />
                        <Typography variant="caption" sx={{ fontFamily: '"JetBrains Mono", monospace' }}>{post.likes}</Typography>
                      </Stack>
                    </Stack>
                  </Stack>
                </CardContent>
              </Box>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ textAlign: 'center' }}>
          <Button
            variant="outlined"
            endIcon={<ArrowForward />}
            onClick={onLoginClick}
            sx={{
              py: 1.5,
              px: 4,
              borderRadius: 0,
              fontFamily: '"JetBrains Mono", monospace',
              fontWeight: 700,
              color: '#00E5FF',
              borderColor: '#00E5FF',
              '&:hover': {
                bgcolor: alpha('#00E5FF', 0.1),
                borderColor: '#00E5FF',
                boxShadow: `0 0 20px ${alpha('#00E5FF', 0.3)}`
              }
            }}
          >
            ACCESS_FULL_LOGS
          </Button>
        </Box>
      </Container>
    </Box>
  )
}

export default CommunityHighlightSection
