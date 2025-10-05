import React, { useState } from 'react'
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
  Avatar,
  LinearProgress,
  alpha,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  TrendingUp,
  People,
  AttachMoney,
  Star,
  Verified,
  Info,
  ArrowForward,
  Speed,
  ShowChart,
  AccountBalance
} from '@mui/icons-material'

interface StrategyMarketplaceSectionProps {
  onLoginClick: () => void
}

const StrategyMarketplaceSection: React.FC<StrategyMarketplaceSectionProps> = ({ onLoginClick }) => {
  // Mock data - 실제로는 Supabase에서 가져올 데이터
  const topStrategies = [
    {
      id: 1,
      name: '모멘텀 퀀트 골드',
      creator: '퀀트킹',
      creatorAvatar: 'Q',
      verified: true,
      premium: true,
      returnRate: 156.8,
      period: '1년',
      followers: 2847,
      monthlyFee: 49000,
      totalEarnings: 139513000,
      winRate: 78.5,
      maxDrawdown: -12.3,
      description: '모멘텀과 가치 지표를 결합한 중장기 전략',
      tags: ['모멘텀', '가치투자', '중장기'],
      color: '#FFB800',
      rating: 4.9
    },
    {
      id: 2,
      name: '변동성 돌파 시스템',
      creator: '알고마스터',
      creatorAvatar: 'A',
      verified: true,
      premium: true,
      returnRate: 89.3,
      period: '6개월',
      followers: 1563,
      monthlyFee: 39000,
      totalEarnings: 60957000,
      winRate: 82.1,
      maxDrawdown: -8.7,
      description: '변동성 돌파를 활용한 단기 스윙 전략',
      tags: ['변동성', '스윙', '단기'],
      color: '#00E5FF',
      rating: 4.8
    },
    {
      id: 3,
      name: 'AI 딥러닝 전략',
      creator: 'AI트레이더',
      creatorAvatar: 'AI',
      verified: true,
      premium: true,
      returnRate: 203.5,
      period: '18개월',
      followers: 3421,
      monthlyFee: 99000,
      totalEarnings: 338679000,
      winRate: 71.3,
      maxDrawdown: -18.9,
      description: 'LSTM 기반 머신러닝 예측 모델',
      tags: ['AI', 'ML', '고수익'],
      color: '#B388FF',
      rating: 4.7
    }
  ]

  return (
    <Box
      sx={{
        py: 12,
        background: `linear-gradient(180deg, #0A0E1A 0%, #1A1F3A 50%, #0A0E1A 100%)`,
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
          width: '1200px',
          height: '1200px',
          background: 'radial-gradient(circle, rgba(255, 184, 0, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center" sx={{ mb: 3 }}>
          <Chip
            icon={<Star sx={{ color: '#FFB800 !important' }} />}
            label="핵심 기능"
            sx={{
              background: alpha('#FFB800', 0.15),
              border: `2px solid ${alpha('#FFB800', 0.4)}`,
              color: '#FFB800',
              fontWeight: 700,
              fontSize: '0.9rem',
              px: 2,
              py: 2.5,
              '& .MuiChip-icon': {
                fontSize: 20
              }
            }}
          />
          <Typography
            variant="h2"
            sx={{
              fontWeight: 900,
              background: 'linear-gradient(135deg, #FFB800 0%, #FFFFFF 50%, #00E5FF 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1.2
            }}
          >
            전략 마켓플레이스
          </Typography>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              color: '#FFB800',
              mb: 2
            }}
          >
            전문가의 전략을 따라하고 수익을 창출하세요
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 900,
              color: alpha('#FFFFFF', 0.85),
              lineHeight: 1.9,
              fontWeight: 400
            }}
          >
            전략을 개발할 시간이 없으신가요? <strong style={{ color: '#FFB800' }}>검증된 전략을 팔로우</strong>하면
            <br />
            전문가의 매매 시그널이 <strong style={{ color: '#00E5FF' }}>자동으로 실행</strong>됩니다.
            <br />
            전략 개발자는 <strong style={{ color: '#B388FF' }}>수익률 + 사용료</strong>로 이중 수익을 얻습니다.
          </Typography>
        </Stack>

        {/* Value Proposition Cards */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {[
            {
              icon: <People sx={{ fontSize: 40 }} />,
              title: '팔로워에게',
              subtitle: '전략 상세 없이도 수익 창출',
              features: [
                '검증된 전문가 전략 선택',
                '자동 매매 시그널 실행',
                '전략 내용 비공개로 안전',
                '월 사용료만 지불'
              ],
              color: '#00E5FF',
              highlight: '전략을 몰라도 OK!'
            },
            {
              icon: <AccountBalance sx={{ fontSize: 40 }} />,
              title: '전략 개발자에게',
              subtitle: '이중 수익 구조',
              features: [
                '본인 투자 수익률',
                '+ 팔로워 사용료 수익',
                '팔로워 많을수록 고수익',
                '전략은 비공개 유지'
              ],
              color: '#FFB800',
              highlight: '수익 X 팔로워!'
            },
            {
              icon: <ShowChart sx={{ fontSize: 40 }} />,
              title: '플랫폼 특장점',
              subtitle: 'Win-Win 생태계',
              features: [
                '투명한 수익률 공개',
                '실시간 성과 추적',
                '안전한 결제 시스템',
                '전략 보호 및 보안'
              ],
              color: '#B388FF',
              highlight: '모두가 이익!'
            }
          ].map((card, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  background: alpha('#1A1F3A', 0.6),
                  backdropFilter: 'blur(20px)',
                  border: `2px solid ${alpha(card.color, 0.3)}`,
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.4s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    borderColor: card.color,
                    boxShadow: `0 20px 60px ${alpha(card.color, 0.4)}`
                  }
                }}
              >
                {/* Top Bar */}
                <Box
                  sx={{
                    height: 4,
                    background: `linear-gradient(90deg, ${card.color} 0%, transparent 100%)`
                  }}
                />

                {/* Highlight Badge */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    px: 2,
                    py: 0.5,
                    borderRadius: 2,
                    background: alpha(card.color, 0.2),
                    border: `1px solid ${alpha(card.color, 0.5)}`
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      color: card.color,
                      fontWeight: 700
                    }}
                  >
                    {card.highlight}
                  </Typography>
                </Box>

                <CardContent sx={{ p: 4 }}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: alpha(card.color, 0.1),
                      border: `1px solid ${alpha(card.color, 0.3)}`,
                      color: card.color,
                      display: 'inline-flex',
                      mb: 3
                    }}
                  >
                    {card.icon}
                  </Box>

                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      color: '#FFFFFF',
                      mb: 1
                    }}
                  >
                    {card.title}
                  </Typography>

                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha('#FFFFFF', 0.6),
                      mb: 3
                    }}
                  >
                    {card.subtitle}
                  </Typography>

                  <Stack spacing={1.5}>
                    {card.features.map((feature, idx) => (
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
                            background: card.color,
                            boxShadow: `0 0 10px ${alpha(card.color, 0.6)}`
                          }}
                        />
                        <Typography
                          variant="body2"
                          sx={{
                            color: alpha('#FFFFFF', 0.9),
                            fontWeight: 500
                          }}
                        >
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

        {/* Top Strategies */}
        <Box sx={{ mb: 6 }}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 800,
              color: '#FFFFFF',
              mb: 1,
              textAlign: 'center'
            }}
          >
            인기 전략 TOP 3
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: alpha('#FFFFFF', 0.7),
              mb: 6,
              textAlign: 'center'
            }}
          >
            실제 수익률과 팔로워 수가 증명하는 검증된 전략
          </Typography>

          <Grid container spacing={3}>
            {topStrategies.map((strategy, index) => (
              <Grid item xs={12} md={4} key={strategy.id}>
                <Card
                  sx={{
                    height: '100%',
                    background: alpha('#0A0E1A', 0.8),
                    backdropFilter: 'blur(20px)',
                    border: `2px solid ${alpha(strategy.color, 0.4)}`,
                    borderRadius: 3,
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'pointer',
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-12px)',
                      borderColor: strategy.color,
                      boxShadow: `0 24px 80px ${alpha(strategy.color, 0.5)}`
                    }
                  }}
                  onClick={onLoginClick}
                >
                  {/* Rank Badge */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -5,
                      left: 20,
                      px: 2,
                      py: 1,
                      borderRadius: '0 0 8px 8px',
                      background: `linear-gradient(135deg, ${strategy.color} 0%, ${alpha(strategy.color, 0.8)} 100%)`,
                      boxShadow: `0 4px 20px ${alpha(strategy.color, 0.6)}`,
                      zIndex: 2
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 900,
                        color: '#000',
                        lineHeight: 1
                      }}
                    >
                      #{index + 1}
                    </Typography>
                  </Box>

                  {/* Top Gradient Bar */}
                  <Box
                    sx={{
                      height: 6,
                      background: `linear-gradient(90deg, ${strategy.color} 0%, transparent 100%)`
                    }}
                  />

                  <CardContent sx={{ p: 3 }}>
                    {/* Strategy Name & Creator */}
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 700,
                        color: '#FFFFFF',
                        mb: 2,
                        mt: 1
                      }}
                    >
                      {strategy.name}
                      {strategy.premium && (
                        <Chip
                          label="프리미엄"
                          size="small"
                          sx={{
                            ml: 1,
                            background: alpha('#FFB800', 0.2),
                            color: '#FFB800',
                            border: `1px solid ${alpha('#FFB800', 0.4)}`,
                            fontWeight: 700
                          }}
                        />
                      )}
                    </Typography>

                    <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                      <Avatar
                        sx={{
                          width: 36,
                          height: 36,
                          background: alpha(strategy.color, 0.2),
                          border: `2px solid ${alpha(strategy.color, 0.5)}`,
                          color: strategy.color,
                          fontWeight: 700
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
                              color: '#FFFFFF'
                            }}
                          >
                            {strategy.creator}
                          </Typography>
                          {strategy.verified && (
                            <Verified sx={{ fontSize: 16, color: '#4CAF50' }} />
                          )}
                        </Stack>
                        <Stack direction="row" spacing={0.5} alignItems="center">
                          <Star sx={{ fontSize: 14, color: '#FFB800' }} />
                          <Typography variant="caption" sx={{ color: '#FFB800', fontWeight: 600 }}>
                            {strategy.rating}
                          </Typography>
                        </Stack>
                      </Box>
                    </Stack>

                    {/* Description */}
                    <Typography
                      variant="body2"
                      sx={{
                        color: alpha('#FFFFFF', 0.7),
                        mb: 2,
                        minHeight: 40
                      }}
                    >
                      {strategy.description}
                    </Typography>

                    {/* Tags */}
                    <Stack direction="row" spacing={1} sx={{ mb: 3 }} flexWrap="wrap" gap={1}>
                      {strategy.tags.map((tag, idx) => (
                        <Chip
                          key={idx}
                          label={tag}
                          size="small"
                          sx={{
                            background: alpha(strategy.color, 0.1),
                            border: `1px solid ${alpha(strategy.color, 0.3)}`,
                            color: strategy.color,
                            fontSize: '0.75rem'
                          }}
                        />
                      ))}
                    </Stack>

                    {/* Stats Grid */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={6}>
                        <Box
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            background: alpha(strategy.color, 0.1),
                            border: `1px solid ${alpha(strategy.color, 0.3)}`,
                            textAlign: 'center'
                          }}
                        >
                          <Typography
                            variant="h4"
                            sx={{
                              fontWeight: 900,
                              color: strategy.color,
                              lineHeight: 1,
                              mb: 0.5
                            }}
                          >
                            +{strategy.returnRate}%
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: alpha('#FFFFFF', 0.7)
                            }}
                          >
                            누적 수익률 ({strategy.period})
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            background: alpha('#4CAF50', 0.1),
                            border: `1px solid ${alpha('#4CAF50', 0.3)}`,
                            textAlign: 'center'
                          }}
                        >
                          <Typography
                            variant="h4"
                            sx={{
                              fontWeight: 900,
                              color: '#4CAF50',
                              lineHeight: 1,
                              mb: 0.5
                            }}
                          >
                            {strategy.winRate}%
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: alpha('#FFFFFF', 0.7)
                            }}
                          >
                            승률
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Earnings Info */}
                    <Box
                      sx={{
                        p: 2.5,
                        mb: 3,
                        borderRadius: 2,
                        background: `linear-gradient(135deg, ${alpha('#FFB800', 0.15)} 0%, ${alpha(strategy.color, 0.1)} 100%)`,
                        border: `1px solid ${alpha('#FFB800', 0.3)}`
                      }}
                    >
                      <Stack spacing={2}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Stack direction="row" spacing={1} alignItems="center">
                            <People sx={{ fontSize: 20, color: '#00E5FF' }} />
                            <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.8) }}>
                              팔로워
                            </Typography>
                          </Stack>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 700,
                              color: '#00E5FF'
                            }}
                          >
                            {strategy.followers.toLocaleString()}명
                          </Typography>
                        </Stack>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Stack direction="row" spacing={1} alignItems="center">
                            <AttachMoney sx={{ fontSize: 20, color: '#FFB800' }} />
                            <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.8) }}>
                              월 사용료
                            </Typography>
                          </Stack>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 700,
                              color: '#FFB800'
                            }}
                          >
                            {strategy.monthlyFee.toLocaleString()}원
                          </Typography>
                        </Stack>
                        <Box
                          sx={{
                            pt: 2,
                            borderTop: `1px solid ${alpha('#FFFFFF', 0.1)}`
                          }}
                        >
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Typography
                              variant="body2"
                              sx={{
                                color: alpha('#FFFFFF', 0.9),
                                fontWeight: 600
                              }}
                            >
                              개발자 예상 월수익
                            </Typography>
                            <Typography
                              variant="h5"
                              sx={{
                                fontWeight: 900,
                                background: 'linear-gradient(135deg, #FFB800 0%, #FF6B00 100%)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent'
                              }}
                            >
                              ₩{(strategy.followers * strategy.monthlyFee).toLocaleString()}
                            </Typography>
                          </Stack>
                          <Typography
                            variant="caption"
                            sx={{
                              color: alpha('#FFFFFF', 0.5),
                              display: 'block',
                              textAlign: 'right',
                              mt: 0.5
                            }}
                          >
                            누적 총수익: ₩{strategy.totalEarnings.toLocaleString()}
                          </Typography>
                        </Box>
                      </Stack>
                    </Box>

                    {/* Follow Button */}
                    <Button
                      fullWidth
                      variant="contained"
                      size="large"
                      endIcon={<ArrowForward />}
                      onClick={onLoginClick}
                      sx={{
                        py: 1.5,
                        fontWeight: 700,
                        background: `linear-gradient(135deg, ${strategy.color} 0%, ${alpha(strategy.color, 0.8)} 100%)`,
                        boxShadow: `0 8px 32px ${alpha(strategy.color, 0.4)}`,
                        color: '#000',
                        '&:hover': {
                          boxShadow: `0 12px 48px ${alpha(strategy.color, 0.6)}`,
                          transform: 'translateY(-2px)'
                        },
                        transition: 'all 0.3s ease'
                      }}
                    >
                      전략 팔로우하기
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* CTA Section */}
        <Box
          sx={{
            mt: 8,
            p: 6,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${alpha('#FFB800', 0.15)} 0%, ${alpha('#1A1F3A', 0.9)} 100%)`,
            border: `2px solid ${alpha('#FFB800', 0.4)}`,
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'radial-gradient(circle at center, rgba(255, 184, 0, 0.1) 0%, transparent 70%)',
              pointerEvents: 'none'
            }}
          />

          <Typography
            variant="h3"
            sx={{
              fontWeight: 800,
              color: '#FFFFFF',
              mb: 2,
              position: 'relative'
            }}
          >
            지금 바로 시작하세요
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: alpha('#FFFFFF', 0.8),
              mb: 4,
              position: 'relative'
            }}
          >
            전략을 팔로우하거나, 나만의 전략을 공유하고 수익을 창출하세요
          </Typography>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            justifyContent="center"
            sx={{ position: 'relative' }}
          >
            <Button
              variant="contained"
              size="large"
              endIcon={<People />}
              onClick={onLoginClick}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                fontWeight: 700,
                background: 'linear-gradient(135deg, #00E5FF 0%, #00B8D4 100%)',
                boxShadow: `0 8px 32px ${alpha('#00E5FF', 0.4)}`,
                '&:hover': {
                  boxShadow: `0 12px 48px ${alpha('#00E5FF', 0.6)}`,
                  transform: 'translateY(-2px)'
                }
              }}
            >
              전략 팔로우 시작
            </Button>
            <Button
              variant="outlined"
              size="large"
              endIcon={<ShowChart />}
              onClick={onLoginClick}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                fontWeight: 700,
                borderWidth: 2,
                borderColor: '#FFB800',
                color: '#FFB800',
                '&:hover': {
                  borderWidth: 2,
                  borderColor: '#FFB800',
                  background: alpha('#FFB800', 0.1),
                  transform: 'translateY(-2px)'
                }
              }}
            >
              전략 개발하고 수익 창출
            </Button>
          </Stack>
        </Box>
      </Container>
    </Box>
  )
}

export default StrategyMarketplaceSection
