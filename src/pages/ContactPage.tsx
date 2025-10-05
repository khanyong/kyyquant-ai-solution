import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  TextField,
  Button,
  Stack,
  alpha,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import { Email, Phone, LocationOn, Send, ExpandMore } from '@mui/icons-material'

const ContactPage: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    alert('문의가 접수되었습니다. 빠른 시일 내에 답변드리겠습니다.')
    setFormData({ name: '', email: '', subject: '', message: '' })
  }

  const faqs = [
    {
      question: '무료 체험이 가능한가요?',
      answer: 'Basic 플랜은 완전 무료입니다. Pro 플랜도 7일 무료 체험이 가능합니다.'
    },
    {
      question: '전략을 팔로우하면 어떻게 되나요?',
      answer: '팔로우한 전략의 매수/매도 시그널이 자동으로 귀하의 계좌에 실행됩니다. 전략 내용은 비공개로 유지되며, 월 사용료만 지불하시면 됩니다.'
    },
    {
      question: '전략 개발자는 어떻게 수익을 얻나요?',
      answer: '본인의 투자 수익 + (팔로워 수 × 월 사용료)로 이중 수익을 얻을 수 있습니다. 전략 내용은 공개되지 않아 안전합니다.'
    },
    {
      question: '백테스팅은 어떻게 진행되나요?',
      answer: '과거 10년 이상의 실제 거래 데이터를 사용하여 전략을 검증합니다. 수익률, 승률, MDD 등 다양한 지표를 제공합니다.'
    },
    {
      question: '자동매매는 안전한가요?',
      answer: '모든 매매는 귀하가 설정한 리스크 관리 규칙에 따라 실행됩니다. 언제든지 중지하거나 수정할 수 있습니다.'
    },
    {
      question: '환불 정책은 어떻게 되나요?',
      answer: '서비스에 만족하지 못하신 경우 7일 이내 100% 환불이 가능합니다.'
    }
  ]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" fontWeight="bold" sx={{ mb: 2, textAlign: 'center' }}>
          고객센터
        </Typography>
        <Typography variant="h6" sx={{ mb: 8, textAlign: 'center', color: alpha('#FFFFFF', 0.7) }}>
          궁금하신 점이 있으시면 언제든지 문의해주세요
        </Typography>

        <Grid container spacing={6}>
          {/* Contact Info */}
          <Grid item xs={12} md={4}>
            <Stack spacing={4}>
              <Paper sx={{ p: 4, background: alpha('#1A1F3A', 0.6) }}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Email sx={{ color: '#FFB800', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      이메일
                    </Typography>
                    <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                      support@kyyquant.com
                    </Typography>
                  </Box>
                </Stack>
              </Paper>

              <Paper sx={{ p: 4, background: alpha('#1A1F3A', 0.6) }}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Phone sx={{ color: '#FFB800', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      전화
                    </Typography>
                    <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                      02-1234-5678
                    </Typography>
                    <Typography variant="caption" sx={{ color: alpha('#FFFFFF', 0.5) }}>
                      평일 09:00 - 18:00
                    </Typography>
                  </Box>
                </Stack>
              </Paper>

              <Paper sx={{ p: 4, background: alpha('#1A1F3A', 0.6) }}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <LocationOn sx={{ color: '#FFB800', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      주소
                    </Typography>
                    <Typography variant="body2" sx={{ color: alpha('#FFFFFF', 0.7) }}>
                      서울시 강남구<br />테헤란로 123
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            </Stack>
          </Grid>

          {/* Contact Form */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, background: alpha('#1A1F3A', 0.6) }}>
              <Typography variant="h5" fontWeight="bold" sx={{ mb: 4 }}>
                문의하기
              </Typography>
              <form onSubmit={handleSubmit}>
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    label="이름"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                  <TextField
                    fullWidth
                    label="이메일"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                  <TextField
                    fullWidth
                    label="제목"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    required
                  />
                  <TextField
                    fullWidth
                    label="문의 내용"
                    multiline
                    rows={6}
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                  />
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    endIcon={<Send />}
                    sx={{
                      py: 1.5,
                      background: 'linear-gradient(135deg, #FFB800 0%, #FF8A00 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #FF8A00 0%, #FFB800 100%)'
                      }
                    }}
                  >
                    문의 보내기
                  </Button>
                </Stack>
              </form>
            </Paper>
          </Grid>
        </Grid>

        {/* FAQ */}
        <Box sx={{ mt: 8 }}>
          <Typography variant="h4" fontWeight="bold" sx={{ mb: 4, textAlign: 'center' }}>
            자주 묻는 질문
          </Typography>
          <Stack spacing={2}>
            {faqs.map((faq, index) => (
              <Accordion
                key={index}
                sx={{
                  background: alpha('#1A1F3A', 0.6),
                  '&:before': { display: 'none' }
                }}
              >
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6" fontWeight="600">
                    {faq.question}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography sx={{ color: alpha('#FFFFFF', 0.8), lineHeight: 1.7 }}>
                    {faq.answer}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </Box>
      </Container>
    </Box>
  )
}

export default ContactPage
