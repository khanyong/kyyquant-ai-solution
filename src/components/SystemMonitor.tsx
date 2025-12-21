import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, LinearProgress, Grid, Chip } from '@mui/material';
import { Memory, Storage, AccessTime, Refresh } from '@mui/icons-material';
import axios from 'axios';

interface SystemStatus {
    cpu: {
        usage_percent: number;
        count: number;
        load_avg: number[];
    };
    memory: {
        total: number;
        available: number;
        used: number;
        percent: number;
    };
    disk: {
        total: number;
        used: number;
        free: number;
        percent: number;
    };
    uptime_seconds: number;
    timestamp: number;
}

const SystemMonitor: React.FC = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch system status
    const fetchStatus = async () => {
        try {
            // Updated to point to the actual backend IP if environment variable is set, otherwise default
            // In a real scenario, this should be VITE_API_URL or similar.
            // For now, using relative path if proxied, or fully qualified if needed.
            // Assuming the frontend is configured to talk to the backend.
            const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/system/status`);
            setStatus(response.data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch system status:', err);
            setError('백엔드 연결 실패');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // 3초마다 갱신
        return () => clearInterval(interval);
    }, []);

    // Helper to format bytes
    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Helper to format uptime
    const formatUptime = (seconds: number) => {
        const d = Math.floor(seconds / (3600 * 24));
        const h = Math.floor((seconds % (3600 * 24)) / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        return `${d}일 ${h}시간 ${m}분`;
    };

    if (loading && !status) return <Typography>시스템 상태 로딩 중...</Typography>;
    if (error && !status) return <Typography color="error">{error}</Typography>;

    if (!status) return null;

    return (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.paper' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
                    <Memory sx={{ mr: 1, color: 'primary.main' }} /> 서버 시스템 상태 (13.209.204.159)
                </Typography>
                <Chip
                    icon={<AccessTime />}
                    label={`Uptime: ${formatUptime(status.uptime_seconds)}`}
                    color="success"
                    variant="outlined"
                    size="small"
                />
            </Box>

            <Grid container spacing={3}>
                {/* CPU Usage */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            CPU Usage ({status.cpu.count} Cores)
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h4" fontWeight="bold" sx={{ mr: 1 }}>
                                {status.cpu.usage_percent}%
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={status.cpu.usage_percent}
                            color={status.cpu.usage_percent > 80 ? 'error' : 'primary'}
                            sx={{ height: 8, borderRadius: 4 }}
                        />
                    </Box>
                </Grid>

                {/* Memory Usage */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Memory Usage
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h4" fontWeight="bold" sx={{ mr: 1 }}>
                                {status.memory.percent}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                ({formatBytes(status.memory.used)} / {formatBytes(status.memory.total)})
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={status.memory.percent}
                            color={status.memory.percent > 85 ? 'warning' : 'info'}
                            sx={{ height: 8, borderRadius: 4 }}
                        />
                    </Box>
                </Grid>

                {/* Disk Usage */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Disk Usage (Root)
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h4" fontWeight="bold" sx={{ mr: 1 }}>
                                {status.disk.percent}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                ({formatBytes(status.disk.used)} / {formatBytes(status.disk.total)})
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={status.disk.percent}
                            color={status.disk.percent > 90 ? 'error' : 'success'}
                            sx={{ height: 8, borderRadius: 4 }}
                        />
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
};

export default SystemMonitor;
