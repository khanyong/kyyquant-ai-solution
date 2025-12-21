import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Divider } from '@mui/material';
import { AccountBalance, CompareArrows } from '@mui/icons-material';

const THEME = {
    bg: '#FFFFFF',
    panel: '#FFFFFF',
    text: '#121212', // Editorial Black
    textDim: '#757575', // Corporate Grey
    success: '#C5A065', // Journalistic Gold (using gold for positive flows instead of green for style)
    border: '#121212',
    hairline: '#E0E0E0'
};

const SectionHeader: React.FC<{ title: string }> = ({ title }) => (
    <Box sx={{
        borderTop: `2px solid ${THEME.border}`,
        borderBottom: `1px solid ${THEME.hairline}`,
        py: 1,
        mb: 2
    }}>
        <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', color: THEME.text }}>
            {title}
        </Typography>
    </Box>
);

const CashFlowAnalysis: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <CompareArrows sx={{ fontSize: 40, color: THEME.success }} />
                <Box>
                    <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', color: THEME.text }}>
                        Cash Flow Analysis
                    </Typography>
                    <Typography variant="body1" sx={{ color: THEME.textDim, fontFamily: '"Playfair Display", serif', fontStyle: 'italic' }}>
                        Monthly Income & Expense Breakdown
                    </Typography>
                </Box>
            </Box>

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 0, boxShadow: 'none' }}>
                        <CardContent>
                            <SectionHeader title="Income" />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5, borderBottom: `1px dashed ${THEME.hairline}`, pb: 1 }}>
                                <Typography color={THEME.textDim} sx={{ fontWeight: 500 }}>Earned Income</Typography>
                                <Typography fontWeight="bold">₩4,500,000</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography color={THEME.textDim} sx={{ fontWeight: 500 }}>Other Income</Typography>
                                <Typography fontWeight="bold">₩200,000</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 0, boxShadow: 'none' }}>
                        <CardContent>
                            <SectionHeader title="Expenses" />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5, borderBottom: `1px dashed ${THEME.hairline}`, pb: 1 }}>
                                <Typography color={THEME.textDim} sx={{ fontWeight: 500 }}>Fixed Expenses</Typography>
                                <Typography fontWeight="bold">₩1,200,000</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography color={THEME.textDim} sx={{ fontWeight: 500 }}>Variable Expenses</Typography>
                                <Typography fontWeight="bold">₩800,000</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12}>
                    <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `2px solid ${THEME.border}`, borderRadius: 0, textAlign: 'center', boxShadow: 'none' }}>
                        <Typography variant="h6" color={THEME.textDim} sx={{ fontFamily: '"Playfair Display", serif', fontStyle: 'italic', mb: 1 }}>
                            Monthly Surplus Summary
                        </Typography>
                        <Divider sx={{ width: '50px', mx: 'auto', mb: 2, borderColor: THEME.success, borderWidth: 2 }} />
                        <Typography variant="h2" fontWeight="bold" sx={{ color: THEME.text, fontFamily: '"Playfair Display", serif' }}>
                            + ₩2,700,000
                        </Typography>
                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 2 }}>
                            Available for portfolio allocation and asset growth.
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default CashFlowAnalysis;
