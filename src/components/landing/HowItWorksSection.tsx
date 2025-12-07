import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Stack,
  alpha,
  Divider
} from '@mui/material'
import {
  Search,
  TouchApp,
  Autorenew,
  AccountBalanceWallet,
  TrendingUp,
  Share,
  People,
  MonetizationOn,
  ArrowForward,
  Terminal,
  Memory,
  Settings
} from '@mui/icons-material'

const HowItWorksSection: React.FC = () => {
  const followerSteps = [
    {
      step: '01',
      id: 'SCAN',
      icon: <Search sx={{ fontSize: 32 }} />,
      title: 'SCAN_MARKET',
      description: 'Filter algorithms by Sharpe ratio, Win Rate, and Drawdown.',
      color: '#00E5FF' // Cyan
    },
    {
      step: '02',
      id: 'LINK',
      icon: <Memory sx={{ fontSize: 32 }} />,
      title: 'ESTABLISH_UPLINK',
      description: 'Connect your capital to the selected node via API bridge.',
      color: '#00FF88' // Green
    },
    {
      step: '03',
      id: 'EXEC',
      icon: <Autorenew sx={{ fontSize: 32 }} />,
      title: 'AUTO_EXECUTION',
      description: 'System mirrors signals in real-time with <50ms latency.',
      color: '#EA00FF' // Purple
    },
    {
      step: '04',
      id: 'YIELD',
      icon: <AccountBalanceWallet sx={{ fontSize: 32 }} />,
      title: 'EXTRACT_YIELD',
      description: 'Monitor performance dashboard and withdraw profits.',
      color: '#FFB800' // Gold
    }
  ]

  const creatorSteps = [
    {
      step: '01',
      id: 'DEV',
      icon: <Terminal sx={{ fontSize: 32 }} />,
      title: 'DEVELOP_LOGIC',
      description: 'Code strategies in Python/C++ or use the Visual Builder.',
      color: '#00E5FF'
    },
    {
      step: '02',
      id: 'TEST',
      icon: <Settings sx={{ fontSize: 32 }} />,
      title: 'BACKTEST_CORE',
      description: 'Validate against 10 years of tick-level historical data.',
      color: '#00FF88'
    },
    {
      step: '03',
      id: 'DEPLOY',
      icon: <Share sx={{ fontSize: 32 }} />,
      title: 'DEPLOY_NODE',
      description: 'Publish to Marketplace. Logic remains encrypted/hidden.',
      color: '#EA00FF'
    },
    {
      step: '04',
      id: 'EARN',
      icon: <MonetizationOn sx={{ fontSize: 32 }} />,
      title: 'COLLECT_FEES',
      description: 'Earn performance fees + subscription revenue globally.',
      color: '#FFB800'
    }
  ]

  const renderPipeline = (steps: typeof followerSteps, title: string, subtitle: string) => (
    <Box sx={{ mb: 12 }}>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 6 }}>
        <Box sx={{ width: 4, height: 24, bgcolor: '#00E5FF' }} />
        <Box>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 800,
              color: '#fff',
              fontFamily: '"JetBrains Mono", monospace',
              letterSpacing: -1
            }}
          >
            {title}
          </Typography>
          <Typography variant="body2" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace' }}>
            {subtitle}
          </Typography>
        </Box>
      </Stack>

      <Grid container spacing={4} sx={{ position: 'relative' }}>
        {/* Connection Line (Desktop) */}
        <Box
          sx={{
            position: 'absolute',
            top: 50,
            left: 60,
            right: 60,
            height: 2,
            bgcolor: alpha('#00E5FF', 0.2),
            zIndex: 0,
            display: { xs: 'none', md: 'block' },
            backgroundImage: 'repeating-linear-gradient(90deg, #00E5FF, #00E5FF 5px, transparent 5px, transparent 10px)'
          }}
        />

        {steps.map((step, index) => (
          <Grid item xs={12} md={3} key={index} sx={{ position: 'relative', zIndex: 1 }}>
            <Box
              sx={{
                height: '100%',
                bgcolor: '#050912',
                border: `1px solid ${alpha(step.color, 0.3)}`,
                p: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: step.color,
                  boxShadow: `0 0 20px ${alpha(step.color, 0.1)}`,
                  transform: 'translateY(-5px)'
                }
              }}
            >
              <Stack spacing={2}>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box
                    sx={{
                      width: 50,
                      height: 50,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      border: `1px solid ${step.color}`,
                      color: step.color,
                      bgcolor: alpha(step.color, 0.1)
                    }}
                  >
                    {step.icon}
                  </Box>
                  <Typography variant="h2" sx={{ color: alpha('#fff', 0.1), fontWeight: 900, fontFamily: '"JetBrains Mono", monospace' }}>
                    {step.step}
                  </Typography>
                </Stack>

                <Box>
                  <Typography variant="caption" sx={{ color: step.color, fontFamily: '"JetBrains Mono", monospace' }}>
                    [{step.id}]
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, fontFamily: '"JetBrains Mono", monospace', mb: 1, minHeight: 60 }}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#8F9EB3', fontSize: '0.85rem' }}>
                    {step.description}
                  </Typography>
                </Box>
              </Stack>
            </Box>
            {/* Arrow for mobile */}
            <Box sx={{ display: { xs: 'flex', md: 'none' }, justifyContent: 'center', my: 2, color: alpha(step.color, 0.3) }}>
              {index < 3 && <ArrowForward sx={{ transform: 'rotate(90deg)' }} />}
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  )

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
      {/* Cyberpunk Grid Background */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
                    linear-gradient(transparent 95%, ${alpha('#00E5FF', 0.1)} 95%),
                    linear-gradient(90deg, transparent 95%, ${alpha('#00E5FF', 0.1)} 95%)
                `,
          backgroundSize: '40px 40px',
          opacity: 0.3,
          pointerEvents: 'none'
        }}
      />

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
              SYSTEM_ARCHITECTURE
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
            EXECUTION PROTOCOL
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
            Choose your role in the ecosystem. Initialize uplink.
          </Typography>
        </Stack>

        {/* Follower Pipeline */}
        {renderPipeline(
          followerSteps,
          'OPERATOR_PROTOCOL',
          'Sequence for capital allocation and auto-execution.'
        )}

        {/* Creator Pipeline */}
        {renderPipeline(
          creatorSteps,
          'ARCHITECT_PROTOCOL',
          'Sequence for algorithm development and monetization.'
        )}

        {/* Earnings Simulation - Terminal Style */}
        <Box
          sx={{
            mt: 8,
            p: { xs: 3, md: 6 },
            bgcolor: alpha('#1A1F3A', 0.4),
            border: `1px solid ${alpha('#00FF88', 0.3)}`,
            position: 'relative'
          }}
        >
          {/* Corner Accents */}
          <Box sx={{ position: 'absolute', top: 0, left: 0, width: 20, height: 20, borderTop: '2px solid #00FF88', borderLeft: '2px solid #00FF88' }} />
          <Box sx={{ position: 'absolute', bottom: 0, right: 0, width: 20, height: 20, borderBottom: '2px solid #00FF88', borderRight: '2px solid #00FF88' }} />

          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4, justifyContent: 'center' }}>
            <Terminal sx={{ color: '#00FF88' }} />
            <Typography
              variant="h5"
              sx={{
                fontWeight: 700,
                color: '#fff',
                fontFamily: '"JetBrains Mono", monospace'
              }}
            >
              YIELD_PROJECTION_SIMULATOR
            </Typography>
          </Stack>

          <Grid container spacing={3}>
            {[
              {
                label: 'LEVEL_1: NOVICE',
                followers: 100,
                monthly: '3,900,000',
                yearly: '46,800,000'
              },
              {
                label: 'LEVEL_2: VETERAN',
                followers: 1000,
                monthly: '49,000,000',
                yearly: '588,000,000'
              },
              {
                label: 'LEVEL_3: WHALE',
                followers: 3000,
                monthly: '297,000,000',
                yearly: '3,564,000,000'
              }
            ].map((scenario, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Box
                  sx={{
                    bgcolor: '#050912',
                    border: `1px solid ${alpha('#00FF88', 0.2)}`,
                    p: 3,
                    textAlign: 'center',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: '#00FF88',
                      bgcolor: alpha('#00FF88', 0.05)
                    }
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#00FF88', fontFamily: '"JetBrains Mono", monospace', display: 'block', mb: 2 }}>
                    {scenario.label}
                  </Typography>

                  <Stack spacing={2}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #232a3b', pb: 1 }}>
                      <Typography variant="body2" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace' }}>NODES_LINKED</Typography>
                      <Typography variant="body2" sx={{ color: '#fff', fontFamily: '"JetBrains Mono", monospace' }}>{scenario.followers}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #232a3b', pb: 1 }}>
                      <Typography variant="body2" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace' }}>MONTHLY_YIELD</Typography>
                      <Typography variant="body2" sx={{ color: '#00FF88', fontFamily: '"JetBrains Mono", monospace' }}>₩{scenario.monthly}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ color: '#8F9EB3', fontFamily: '"JetBrains Mono", monospace' }}>ANNUAL_PROJECTION</Typography>
                      <Typography variant="body2" sx={{ color: '#00FF88', fontFamily: '"JetBrains Mono", monospace', fontWeight: 700 }}>₩{scenario.yearly}</Typography>
                    </Box>
                  </Stack>
                </Box>
              </Grid>
            ))}
          </Grid>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 3,
              textAlign: 'center',
              color: '#5C6B7F',
              fontFamily: '"JetBrains Mono", monospace'
            }}
          >
            * Simulation based on standard fee structure. Actual yield may vary based on market conditions.
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default HowItWorksSection
