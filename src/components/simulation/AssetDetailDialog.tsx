import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
    Grid,
    Paper
} from '@mui/material';
import {
    CheckCircle,
    Cancel,
    TrendingDown,
    Info
} from '@mui/icons-material';
import { AssetProfile } from '../../utils/SimulationEngine';

interface AssetDetailDialogProps {
    open: boolean;
    onClose: () => void;
    asset: AssetProfile | null;
}

const AssetDetailDialog: React.FC<AssetDetailDialogProps> = ({ open, onClose, asset }) => {
    if (!asset) return null;

    const getQuantLabel = (score: number) => {
        if (score >= 4.5) return { label: 'Strong Buy', color: '#169d4d' }; // SA Green
        if (score >= 3.5) return { label: 'Buy', color: '#8bc34a' };
        if (score >= 3.0) return { label: 'Hold', color: '#ffc107' };
        if (score >= 2.0) return { label: 'Sell', color: '#ff9800' };
        return { label: 'Strong Sell', color: '#f44336' };
    };

    const quantInfo = asset.quantScore ? getQuantLabel(asset.quantScore) : null;

    const renderGrade = (grade: string) => {
        const color = grade.startsWith('A') ? '#169d4d' : grade.startsWith('B') ? '#8bc34a' : grade.startsWith('C') ? '#ffc107' : grade.startsWith('D') ? '#ff9800' : '#f44336';
        return <Typography fontWeight="bold" sx={{ color }}>{grade}</Typography>
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2, borderBottom: '1px solid #eee' }}>
                <Typography variant="h5" fontWeight="bold">{asset.name}</Typography>
                <Chip label={asset.id.toUpperCase().includes('US') ? 'US TICKER' : 'KOREA'} size="small" variant="outlined" />
                {quantInfo && (
                    <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1, bgcolor: quantInfo.color, px: 2, py: 0.5, borderRadius: 1 }}>
                        <Typography variant="subtitle2" fontWeight="bold" color="#fff">QUANT RATING: {asset.quantScore}</Typography>
                        <Typography variant="body2" fontWeight="bold" color="#fff">| {quantInfo.label}</Typography>
                    </Box>
                )}
            </DialogTitle>

            <DialogContent>
                <Grid container spacing={4} sx={{ mt: 1 }}>
                    {/* Left Column: Factor Grades & Dividend Scorecard */}
                    <Grid item xs={12} md={5}>
                        {asset.factorGrades && (
                            <Paper elevation={0} variant="outlined" sx={{ mb: 3, overflow: 'hidden' }}>
                                <Box sx={{ bgcolor: '#f8f9fa', px: 2, py: 1, borderBottom: '1px solid #eee' }}>
                                    <Typography variant="subtitle2" fontWeight="bold">Factor Grades</Typography>
                                </Box>
                                <List dense>
                                    <ListItem divider>
                                        <ListItemText primary="Valuation" />
                                        {renderGrade(asset.factorGrades.valuation)}
                                    </ListItem>
                                    <ListItem divider>
                                        <ListItemText primary="Growth" />
                                        {renderGrade(asset.factorGrades.growth)}
                                    </ListItem>
                                    <ListItem divider>
                                        <ListItemText primary="Profitability" />
                                        {renderGrade(asset.factorGrades.profitability)}
                                    </ListItem>
                                    <ListItem divider>
                                        <ListItemText primary="Momentum" />
                                        {renderGrade(asset.factorGrades.momentum)}
                                    </ListItem>
                                    <ListItem>
                                        <ListItemText primary="Revisions" />
                                        {renderGrade(asset.factorGrades.revisions)}
                                    </ListItem>
                                </List>
                            </Paper>
                        )}

                        {asset.dividendStats && (
                            <Paper elevation={0} variant="outlined">
                                <Box sx={{ bgcolor: '#f8f9fa', px: 2, py: 1, borderBottom: '1px solid #eee' }}>
                                    <Typography variant="subtitle2" fontWeight="bold">Dividend Scorecard</Typography>
                                </Box>
                                <Box sx={{ p: 2, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">Yield (TTM)</Typography>
                                        <Typography variant="h6">{asset.dividendStats.yieldTTM}%</Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">Payout Ratio</Typography>
                                        <Typography variant="h6">{asset.dividendStats.payoutRatio}%</Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">5Y Growth</Typography>
                                        <Typography variant="h6" color="success.main">+{asset.dividendStats.growthRate5Y}%</Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">Growth Streak</Typography>
                                        <Typography variant="h6">{asset.dividendStats.growthStreak} Years</Typography>
                                    </Box>
                                </Box>
                            </Paper>
                        )}
                    </Grid>

                    {/* Right Column: Descriptions & Bull/Bear */}
                    <Grid item xs={12} md={7}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">Summary</Typography>
                        <Typography variant="body1" color="text.secondary" paragraph>
                            {asset.description}
                        </Typography>

                        <Divider sx={{ my: 3 }} />

                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" fontWeight="bold" color="#169d4d" gutterBottom>
                                Bulls Say (긍정적 시각)
                            </Typography>
                            {asset.pros?.map((pro, i) => (
                                <Typography key={i} variant="body2" sx={{ display: 'flex', gap: 1, mb: 1 }}>
                                    <Box component="span" sx={{ color: '#169d4d' }}>▲</Box> {pro}
                                </Typography>
                            ))}
                        </Box>

                        <Box>
                            <Typography variant="subtitle1" fontWeight="bold" color="#f44336" gutterBottom>
                                Bears Say (부정적 시각)
                            </Typography>
                            {asset.cons?.map((con, i) => (
                                <Typography key={i} variant="body2" sx={{ display: 'flex', gap: 1, mb: 1 }}>
                                    <Box component="span" sx={{ color: '#f44336' }}>▼</Box> {con}
                                </Typography>
                            ))}
                        </Box>
                    </Grid>
                </Grid>
            </DialogContent>

            <DialogActions sx={{ p: 2, borderTop: '1px solid #eee' }}>
                <Button onClick={onClose} variant="contained" color="primary" disableElevation>
                    Close Analysis
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AssetDetailDialog;
