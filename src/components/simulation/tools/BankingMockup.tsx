import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Tabs, Tab, Button, TextField, Divider, List, ListItem, ListItemText, ListItemAvatar, Avatar } from '@mui/material';
import { AccountBalance, CreditCard, Send, AccountBalanceWallet, Receipt, ArrowForward, Savings, AttachMoney } from '@mui/icons-material';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    secondary: 'var(--ipc-secondary)',
    border: 'var(--ipc-border)',
    success: 'var(--ipc-success)'
};

interface BankingMockupProps {
    initialTab?: number;
}

const BankingMockup: React.FC<BankingMockupProps> = ({ initialTab = 0 }) => {
    const [tab, setTab] = useState(initialTab);

    // Mock Data
    const accounts = [
        { id: 1, name: '주거래 입출금', number: '123-456-789012', balance: 5420000, type: 'Checking' },
        { id: 2, name: '비상금 통장', number: '333-222-111111', balance: 12500000, type: 'Savings' },
        { id: 3, name: '여행 적금', number: '987-654-321098', balance: 3400000, type: 'Savings' }
    ];

    const transactions = [
        { id: 1, title: '급여 입금', date: '2023-10-25', amount: 3500000, type: 'in' },
        { id: 2, title: '스타벅스', date: '2023-10-26', amount: -6500, type: 'out' },
        { id: 3, title: '보험료 출금', date: '2023-10-27', amount: -120000, type: 'out' },
        { id: 4, title: '배당금 입금', date: '2023-10-28', amount: 45000, type: 'in' }
    ];

    return (
        <Box sx={{ p: 4, maxWidth: 1000, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalance sx={{ fontSize: 40, color: THEME.primary }} />
                <Typography variant="h4" fontWeight="bold">뱅킹 센터</Typography>
            </Box>

            <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 4, borderBottom: 1, borderColor: THEME.border }}>
                <Tab label="조회" />
                <Tab label="이체" />
                <Tab label="대출" />
                <Tab label="외환" />
            </Tabs>

            {/* Tab 0: Inquiry */}
            {tab === 0 && (
                <Grid container spacing={3}>
                    <Grid item xs={12} md={7}>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>내 계좌</Typography>
                        {accounts.map(acc => (
                            <Card key={acc.id} sx={{ mb: 2, bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                                <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Box>
                                        <Typography variant="subtitle2" color={THEME.textDim}>{acc.type} • {acc.number}</Typography>
                                        <Typography variant="h6" fontWeight="bold">{acc.name}</Typography>
                                    </Box>
                                    <Typography variant="h5" color={THEME.primary} fontWeight="bold">
                                        ₩{acc.balance.toLocaleString()}
                                    </Typography>
                                </CardContent>
                            </Card>
                        ))}
                    </Grid>
                    <Grid item xs={12} md={5}>
                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2 }}>
                            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>최근 거래 내역</Typography>
                            <List>
                                {transactions.map(tx => (
                                    <React.Fragment key={tx.id}>
                                        <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                                            <ListItemAvatar>
                                                <Avatar sx={{ bgcolor: tx.type === 'in' ? 'rgba(44, 182, 125, 0.2)' : 'rgba(239, 69, 101, 0.2)', color: tx.type === 'in' ? THEME.success : '#EF4565' }}>
                                                    {tx.type === 'in' ? <Savings /> : <Receipt />}
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={tx.title}
                                                secondary={<Typography variant="caption" color={THEME.textDim}>{tx.date}</Typography>}
                                            />
                                            <Typography fontWeight="bold" color={tx.type === 'in' ? THEME.success : '#EF4565'}>
                                                {tx.type === 'in' ? '+' : ''}{tx.amount.toLocaleString()}
                                            </Typography>
                                        </ListItem>
                                        <Divider variant="inset" component="li" sx={{ borderColor: '#e0e0e0' }} />
                                    </React.Fragment>
                                ))}
                            </List>
                        </Paper>
                    </Grid>
                </Grid>
            )}

            {/* Tab 1: Transfer */}
            {tab === 1 && (
                <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto', bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2 }}>
                    <Typography variant="h6" fontWeight="bold" sx={{ mb: 4, textAlign: 'center' }}>간편 이체</Typography>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom color={THEME.textDim}>출금 계좌</Typography>
                        <TextField select SelectProps={{ native: true }} fullWidth sx={{ bgcolor: 'var(--ipc-bg-subtle)' }}>
                            {accounts.map(acc => (
                                <option key={acc.id} value={acc.id}>{acc.name} (₩{acc.balance.toLocaleString()})</option>
                            ))}
                        </TextField>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom color={THEME.textDim}>입금 계좌번호</Typography>
                        <TextField fullWidth placeholder="- 없이 입력해주세요" sx={{ bgcolor: 'var(--ipc-bg-subtle)' }} />
                    </Box>

                    <Box sx={{ mb: 4 }}>
                        <Typography gutterBottom color={THEME.textDim}>이체 금액 (원)</Typography>
                        <TextField fullWidth type="number" placeholder="0" sx={{ bgcolor: 'var(--ipc-bg-subtle)' }} />
                    </Box>

                    <Button variant="contained" fullWidth size="large" sx={{ bgcolor: THEME.primary, color: '#000', fontWeight: 'bold' }} startIcon={<Send />}>
                        이체하기
                    </Button>
                </Paper>
            )
            }

            {/* Tab 2: Loan */}
            {
                tab === 2 && (
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ bgcolor: THEME.panel, border: '1px solid ' + THEME.border, p: 2 }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold">신용대출</Typography>
                                        <Typography variant="h6" color={THEME.primary}>4.52%</Typography>
                                    </Box>
                                    <Typography variant="body2" color={THEME.textDim} sx={{ mb: 3 }}>
                                        신용점수 기반 사전 승인 한도입니다.
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>₩50,000,000</Typography>
                                    <Button variant="outlined" fullWidth sx={{ color: THEME.primary, borderColor: THEME.primary }}>한도 조회</Button>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ bgcolor: THEME.panel, border: '1px solid ' + THEME.border, p: 2 }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold">주택담보대출</Typography>
                                        <Typography variant="h6" color={THEME.secondary}>3.85%</Typography>
                                    </Box>
                                    <Typography variant="body2" color={THEME.textDim} sx={{ mb: 3 }}>
                                        LTV 70% 적용 주택 담보 대출.
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>₩500,000,000</Typography>
                                    <Button variant="outlined" fullWidth sx={{ color: THEME.secondary, borderColor: THEME.secondary }}>신청하기</Button>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                )
            }

            {/* Tab 3: Forex */}
            {
                tab === 3 && (
                    <Box sx={{ textAlign: 'center', py: 8, color: THEME.textDim }}>
                        <AttachMoney sx={{ fontSize: 60, mb: 2, opacity: 0.5 }} />
                        <Typography variant="h6">외환 거래 서비스 준비 중</Typography>
                        <Typography variant="body2">실시간 환율 및 다통화 지갑 기능 오픈 예정.</Typography>
                    </Box>
                )
            }

        </Box >
    );
};

export default BankingMockup;
