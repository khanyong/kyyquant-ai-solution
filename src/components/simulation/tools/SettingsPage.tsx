import React from 'react';
import { Box, Typography, Paper, Switch, List, ListItem, ListItemText, ListItemSecondaryAction, Divider } from '@mui/material';
import { Settings } from '@mui/icons-material';

const THEME = {
    bg: '#FFFFFF',
    panel: '#FFFFFF',
    text: '#121212', // Editorial Black
    textDim: '#757575', // Corporate Grey
    border: '#121212',
    hairline: '#E0E0E0',
    accent: '#C5A065' // Journalistic Gold
};

const SettingsPage: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 800, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2, borderBottom: `1px solid ${THEME.border}`, pb: 2 }}>
                <Settings sx={{ fontSize: 40, color: THEME.text }} />
                <Box>
                    <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', color: THEME.text }}>Settings</Typography>
                    <Typography variant="body1" sx={{ fontFamily: '"Playfair Display", serif', fontStyle: 'italic', color: THEME.textDim }}>System Configurations</Typography>
                </Box>
            </Box>

            <Paper sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 0, boxShadow: 'none' }}>
                <List>
                    <ListItem sx={{ py: 3 }}>
                        <ListItemText
                            primary={
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', mb: 0.5 }}>
                                    Dark Mode
                                </Typography>
                            }
                            secondary="Maintain a dark editorial theme throughout the session."
                            secondaryTypographyProps={{ color: THEME.textDim, sx: { fontStyle: 'italic' } }}
                        />
                        <ListItemSecondaryAction>
                            <Switch edge="end" checked={false} color="default" sx={{ '& .MuiSwitch-thumb': { backgroundColor: THEME.text } }} />
                        </ListItemSecondaryAction>
                    </ListItem>
                    <Divider sx={{ borderColor: THEME.hairline }} />
                    <ListItem sx={{ py: 3 }}>
                        <ListItemText
                            primary={
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', mb: 0.5 }}>
                                    Notifications
                                </Typography>
                            }
                            secondary="Receive alerts for significant market movements."
                            secondaryTypographyProps={{ color: THEME.textDim, sx: { fontStyle: 'italic' } }}
                        />
                        <ListItemSecondaryAction>
                            <Switch edge="end" checked={true} color="default" sx={{ '& .MuiSwitch-thumb': { backgroundColor: THEME.accent } }} />
                        </ListItemSecondaryAction>
                    </ListItem>
                    <Divider sx={{ borderColor: THEME.hairline }} />
                    <ListItem sx={{ py: 3 }}>
                        <ListItemText
                            primary={
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold', mb: 0.5, color: '#D32F2F' }}>
                                    Reset Simulation Data
                                </Typography>
                            }
                            secondary="Clear all saved portfolios and assumptions."
                            secondaryTypographyProps={{ color: THEME.textDim, sx: { fontStyle: 'italic' } }}
                        />
                    </ListItem>
                </List>
            </Paper>

            <Box sx={{ mt: 4, textAlign: 'center', color: THEME.textDim }}>
                <Typography variant="caption">IPC Terminal v2.0.0</Typography>
            </Box>
        </Box>
    );
};

export default SettingsPage;
