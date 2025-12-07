import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  CardContent,
  Stack,
  Button,
  Chip,
  Avatar,
  alpha
} from '@mui/material'
import {
  People,
  AttachMoney,
  Verified,
  ArrowForward,
  ShowChart,
  AccountBalance,
  Terminal,
  Code,
  DataObject
} from '@mui/icons-material'

interface StrategyMarketplaceSectionProps {
  onLoginClick: () => void
}

const StrategyMarketplaceSection: React.FC<StrategyMarketplaceSectionProps> = ({ onLoginClick }) => {
  const topStrategies = [
    {
      id: 1,
      name: 'QUANTUM_GOLD_V1',
      creator: 'SYS_ADMIN',
      creatorAvatar: 'Q',
      verified: true,
      premium: true,
      returnRate: 156.8,
      period: '1Y',
      followers: 2847,
      monthlyFee: 49000,
      totalEarnings: 139513000,
      winRate: 78.5,
      maxDrawdown: -12.3,
      description: 'Momentum-based algorithm focusing on high-volatility assets.',
      tags: ['MOMENTUM', 'HFT', 'LONG_ONLY'],
      color: '#00E5FF', // Cyan
      rating: 4.9
    },
    {
      id: 2,
      name: 'NEURAL_NET_ALPHA',
      creator: 'AI_LABS',
      creatorAvatar: 'A',
      verified: true,
      premium: true,
      returnRate: 89.3,
      period: '6M',
      followers: 1563,
      monthlyFee: 39000,
      totalEarnings: 60957000,
      winRate: 82.1,
      maxDrawdown: -8.7,
      description: 'Deep learning model trained on 10 years of tick data.',
      tags: ['AI', 'SWING', 'STABLE'],
      color: '#00FF88', // Green
      rating: 4.8
    },
    {
      id: 3,
      name: 'VOLATILITY_BREAK_X',
      creator: 'TRADER_ZERO',
      creatorAvatar: 'Z',
      verified: true,
      premium: true,
      returnRate: 203.5,
      period: '18M',
      followers: 3421,
      monthlyFee: 99000,
      totalEarnings: 338679000,
      winRate: 71.3,
      maxDrawdown: -18.9,
      description: 'Aggressive breakout strategy for maximum capital efficiency.',
      tags: ['AGGRESSIVE', 'SCALPING', 'HIGH_RISK'],
      color: '#EA00FF', // Purple
      rating: 4.7
    }
  ]

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
      {/* Background Grid */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: '30px 30px',
          opacity: 0.3,
          zIndex: 0
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 8 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: 2,
              py: 0.5,
              border: '1px solid #00FF88',
              bgcolor: alpha('#00FF88', 0.1),
              mb: 2
            }}
          >
            <Code sx={{ fontSize: 16, color: '#00FF88' }} />
            <Typography variant="caption" sx={{ color: '#00FF88', fontFamily: '"JetBrains Mono", monospace', fontWeight: 700 }}>
              ALGORITHM_MARKETPLACE.EXE
            </Typography>
          </Box>
          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              color: '#fff',
              fontFamily: '"JetBrains Mono", monospace',
              textTransform: 'uppercase',
              letterSpacing: -2,
              mb: 1
            }}
          >
            EXECUTE PRO STRATEGIES
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 800,
              color: '#8F9EB3',
              lineHeight: 1.6,
              fontWeight: 400,
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            Deploy verified algorithms from top architects. Zero latency execution.
          </Typography>
        </Stack>

        {/* Value Props - Terminal Style */}
        <Grid container spacing={3} sx={{ mb: 10 }}>
          {[
            {
              icon: <DataObject />,
              title: 'FOR OPERATORS',
              subtitle: 'AUTO-EXECUTION',
              desc: 'Select an algorithm. Allocate capital. Let the system execute trades automatically 24/7.',
              color: '#00E5FF'
            },
            {
              icon: <Terminal />,
              title: 'FOR ARCHITECTS',
              subtitle: 'MONETIZE LOGIC',
              desc: 'Publish your strategy. Earn subscription fees from followers while keeping your logic private.',
              color: '#00FF88'
            },
            {
              icon: <AccountBalance />,
              title: 'ECOSYSTEM',
              subtitle: 'TRANSPARENCY',
              desc: 'Real-time performance tracking. Verified historical data. Immutable trade records.',
              color: '#EA00FF'
            }
          ].map((card, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Box
                sx={{
                  height: '100%',
                  p: 4,
                  bgcolor: alpha('#0A0E1A', 0.6),
                  border: `1px solid ${alpha(card.color, 0.3)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: card.color,
                    bgcolor: alpha(card.color, 0.05),
                    boxShadow: `0 0 20px ${alpha(card.color, 0.1)}`
                  }
                }}
              >
                <Box sx={{ color: card.color, mb: 2 }}>{card.icon}</Box>
                <Typography variant="caption" sx={{ color: card.color, fontFamily: '"JetBrains Mono", monospace', fontWeight: 700 }}>
                  {card.title}
                </Typography>
                <Typography variant="h5" sx={{ color: '#fff', fontFamily: '"JetBrains Mono", monospace', fontWeight: 800, mb: 2 }}>
                  {card.subtitle}
                </Typography>
                <Typography variant="body2" sx={{ color: '#8F9EB3' }}>
                  {card.desc}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Top Strategies Grid */}
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            color: '#fff',
            fontFamily: '"JetBrains Mono", monospace',
            mb: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}
        >
          <Box component="span" sx={{ color: '#00FF88' }}>&gt;</Box> TOP_PERFORMING_NODES
        </Typography>

        <Grid container spacing={3} sx={{ mb: 8 }}>
          {topStrategies.map((strategy, index) => (
            <Grid item xs={12} md={4} key={strategy.id}>
              <Box
                sx={{
                  height: '100%',
                  bgcolor: '#0A0E1A',
                  border: `1px solid ${alpha(strategy.color, 0.3)}`,
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: strategy.color,
                    transform: 'translateY(-5px)',
                    boxShadow: `0 0 30px ${alpha(strategy.color, 0.1)}`
                  }
                }}
                onClick={onLoginClick}
              >
                {/* Header Bar */}
                <Box
                  sx={{
                    p: 2,
                    borderBottom: `1px solid ${alpha(strategy.color, 0.3)}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    bgcolor: alpha(strategy.color, 0.05)
                  }}
                >
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="h6" sx={{ color: '#fff', fontFamily: '"JetBrains Mono", monospace', fontWeight: 700, fontSize: '1rem' }}>
                      {strategy.name}
                    </Typography>
                    {strategy.premium && (
                      <Box sx={{ px: 0.5, bgcolor: strategy.color, color: '#000', fontSize: '0.6rem', fontWeight: 800 }}>P</Box>
                    )}
                  </Stack>
                  <Typography variant="caption" sx={{ color: strategy.color, fontFamily: '"JetBrains Mono", monospace' }}>
                    ID: {strategy.id.toString().padStart(4, '0')}
                  </Typography>
                </Box>

                <CardContent sx={{ p: 3 }}>
                  {/* Creator Info */}
                  <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: 'transparent',
                        border: `1px solid ${strategy.color}`,
                        color: strategy.color,
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.9rem',
                        fontWeight: 700,
                        borderRadius: 0
                      }}
                    >
                      {strategy.creatorAvatar}
                    </Avatar>
                    <Box>
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            color: '#fff',
                            fontFamily: '"JetBrains Mono", monospace'
                          }}
                        >
                          {strategy.creator}
                        </Typography>
                        {strategy.verified && (
                          <Verified sx={{ fontSize: 14, color: '#00FF88' }} />
                        )}
                      </Stack>
                    </Box>
                  </Stack>

                  {/* Stats */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, border: `1px solid ${alpha(strategy.color, 0.3)}`, bgcolor: alpha(strategy.color, 0.05) }}>
                        <Typography variant="caption" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace', display: 'block', mb: 0.5 }}>RETURN ({strategy.period})</Typography>
                        <Typography variant="h5" sx={{ color: strategy.color, fontFamily: '"JetBrains Mono", monospace', fontWeight: 700 }}>
                          +{strategy.returnRate}%
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, border: `1px solid ${alpha('#00FF88', 0.3)}`, bgcolor: alpha('#00FF88', 0.05) }}>
                        <Typography variant="caption" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace', display: 'block', mb: 0.5 }}>WIN RATE</Typography>
                        <Typography variant="h5" sx={{ color: '#00FF88', fontFamily: '"JetBrains Mono", monospace', fontWeight: 700 }}>
                          {strategy.winRate}%
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  {/* Description */}
                  <Typography
                    variant="body2"
                    sx={{
                      color: '#8F9EB3',
                      mb: 2,
                      minHeight: 40,
                      fontSize: '0.85rem'
                    }}
                  >
                    {strategy.description}
                  </Typography>

                  {/* Tags */}
                  <Stack direction="row" spacing={1} sx={{ mb: 3 }} flexWrap="wrap" gap={0.5}>
                    {strategy.tags.map((tag, idx) => (
                      <Chip
                        key={idx}
                        label={tag}
                        size="small"
                        sx={{
                          bgcolor: 'transparent',
                          border: `1px solid ${alpha('#fff', 0.2)}`,
                          color: '#8F9EB3',
                          fontSize: '0.65rem',
                          fontFamily: '"JetBrains Mono", monospace',
                          borderRadius: 0,
                          height: 20
                        }}
                      />
                    ))}
                  </Stack>

                  {/* Footer Info */}
                  <Stack spacing={1} sx={{ pt: 2, borderTop: `1px solid ${alpha('#fff', 0.1)}` }}>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="caption" sx={{ color: '#5C6B7F' }}>FOLLOWERS</Typography>
                      <Typography variant="caption" sx={{ color: '#fff', fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>{strategy.followers.toLocaleString()}</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="caption" sx={{ color: '#5C6B7F' }}>FEE / MO</Typography>
                      <Typography variant="caption" sx={{ color: strategy.color, fontWeight: 700, fontFamily: '"JetBrains Mono", monospace' }}>₩{strategy.monthlyFee.toLocaleString()}</Typography>
                    </Stack>
                  </Stack>

                  <Button
                    fullWidth
                    variant="outlined"
                    endIcon={<ArrowForward />}
                    sx={{
                      mt: 3,
                      borderColor: strategy.color,
                      color: strategy.color,
                      fontFamily: '"JetBrains Mono", monospace',
                      fontWeight: 700,
                      borderRadius: 0,
                      '&:hover': {
                        bgcolor: alpha(strategy.color, 0.1),
                        borderColor: strategy.color
                      }

                    }}
                  >
                    INITIALIZE
                  </Button>
                </CardContent>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* CTA Banner */}
        <Box
          sx={{
            p: 6,
            border: `1px solid #00E5FF`,
            bgcolor: alpha('#00E5FF', 0.05),
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              right: 0,
              p: 1,
              bgcolor: '#00E5FF',
              color: '#000',
              fontWeight: 700,
              fontSize: '0.7rem',
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            SYSTEM_READY
          </Box>
          <Typography variant="h4" sx={{ color: '#fff', fontFamily: '"JetBrains Mono", monospace', fontWeight: 800, mb: 2 }}>
            READY TO DEPLOY?
          </Typography>
          <Typography variant="body1" sx={{ color: '#8F9EB3', mb: 4, maxWidth: 600, mx: 'auto' }}>
            Join the network of algorithmic traders. Access institutional tools today.
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="contained"
              size="large"
              onClick={onLoginClick}
              sx={{
                bgcolor: '#00E5FF',
                color: '#000',
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 800,
                borderRadius: 0,
                px: 4,
                '&:hover': { bgcolor: '#00B8D4' }
              }}
            >
              ACCESS TERMINAL
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={onLoginClick}
              sx={{
                borderColor: '#00FF88',
                color: '#00FF88',
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 800,
                borderRadius: 0,
                px: 4,
                '&:hover': { borderColor: '#00B8D4', bgcolor: 'transparent' }
              }}
            >
              VIEW DOCS
            </Button>
          </Stack>
        </Box>

      </Container>
    </Box>
  )
}

export default StrategyMarketplaceSection
