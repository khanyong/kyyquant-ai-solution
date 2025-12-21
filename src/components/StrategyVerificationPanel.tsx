import React, { useState, useMemo } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Alert,
    Stack,
    IconButton,
    Tooltip,
    TablePagination,
    Grid,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Divider,
    LinearProgress
} from '@mui/material';
import {
    PlayArrow as PlayArrowIcon,
    Download as DownloadIcon,
    ExpandMore as ExpandMoreIcon,
    CheckCircle as CheckCircleIcon,
    Cancel as CancelIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    FilterList as FilterListIcon,
    Visibility as VisibilityIcon,
    FactCheck
} from '@mui/icons-material';
import { format } from 'date-fns';

// Type definition for verification result
interface VerificationResult {
    strategy_name: string;
    stock_code: string;
    stock_name: string;
    current_price: number;
    signal_type: string;
    score: number;
    details: {
        reasons: string[];
        indicators: any;
    };
}

export default function StrategyVerificationPanel() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<VerificationResult[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [lastRunTime, setLastRunTime] = useState<Date | null>(null);

    // Filtering & Pagination
    const [searchTerm, setSearchTerm] = useState('');
    const [signalFilter, setSignalFilter] = useState<string>('all');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    // Dialog State
    const [selectedResult, setSelectedResult] = useState<VerificationResult | null>(null);
    const [detailsOpen, setDetailsOpen] = useState(false);

    const [progress, setProgress] = useState(0);
    const [statusMessage, setStatusMessage] = useState('');

    const handleVerify = async () => {
        setLoading(true);
        setError(null);
        setResults([]);
        setProgress(0);
        setStatusMessage('검증 대상 조회 중...');

        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';

            // 1. 검증 대상 조회
            const targetsResponse = await fetch(`${apiUrl}/api/strategy/verification-targets`);
            if (!targetsResponse.ok) throw new Error('Failed to fetch verification targets');

            const targets = await targetsResponse.json();

            if (targets.length === 0) {
                setStatusMessage('검증 대상이 없습니다.');
                setLoading(false);
                return;
            }

            // 2. 전체 작업량 계산
            let totalStocks = 0;
            targets.forEach((t: any) => totalStocks += t.stock_codes.length);

            let processedCount = 0;
            const BATCH_SIZE = 20; // 20개씩 끊어서 요청 (Timeout 방지)
            const allResults: VerificationResult[] = [];

            // 3. 전략별 배치 처리
            for (const target of targets) {
                const stockCodes = target.stock_codes;

                for (let i = 0; i < stockCodes.length; i += BATCH_SIZE) {
                    const batch = stockCodes.slice(i, i + BATCH_SIZE);
                    setStatusMessage(`${target.strategy_name}: ${i + 1}/${stockCodes.length} 처리 중...`);

                    try {
                        const batchResponse = await fetch(`${apiUrl}/api/strategy/batch-check`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                strategy_id: target.strategy_id,
                                stock_codes: batch
                            })
                        });

                        if (batchResponse.ok) {
                            const batchResults = await batchResponse.json();
                            allResults.push(...batchResults);
                            // 실시간 결과 업데이트 (선택 사항, 성능 위해 나중에 한 번에 할 수도 있음)
                            setResults(prev => [...prev, ...batchResults]);
                        } else {
                            console.error(`Batch failed for ${target.strategy_name}`);
                        }
                    } catch (e) {
                        console.error(`Batch error: ${e}`);
                    }

                    processedCount += batch.length;
                    setProgress(Math.min((processedCount / totalStocks) * 100, 100));

                    // UI 렌더링 양보 (비동기 지연)
                    await new Promise(r => setTimeout(r, 10));
                }
            }

            setLastRunTime(new Date());
            setStatusMessage(`완료! 총 ${allResults.length}건 검증됨`);
            setPage(0);

        } catch (err: any) {
            console.error("Verification failed:", err);
            setError(err.message || "Failed to verify strategies");
            setStatusMessage('오류 발생');
        } finally {
            setLoading(false);
            setProgress(0);
        }
    };

    const handleDownloadExcel = () => {
        if (results.length === 0) return;

        const headers = ['Strategy', 'Stock Code', 'Stock Name', 'Current Price', 'Signal', 'Score', 'Reasons'];
        const rows = results.map(r => [
            r.strategy_name,
            r.stock_code,
            r.stock_name,
            r.current_price,
            r.signal_type,
            r.score,
            r.details.reasons.join('; ')
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        ].join('\n');

        const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `strategy_verification_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    // Filter Logic
    const filteredResults = useMemo(() => {
        return results.filter(result => {
            const matchesTerm = (
                result.strategy_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                result.stock_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                result.stock_code.includes(searchTerm)
            );
            const matchesSignal = signalFilter === 'all' || result.signal_type.toLowerCase() === signalFilter.toLowerCase();
            return matchesTerm && matchesSignal;
        });
    }, [results, searchTerm, signalFilter]);

    // Summary Stats
    const summaryStats = useMemo(() => {
        return {
            total: results.length,
            buy: results.filter(r => r.signal_type.toUpperCase() === 'BUY').length,
            sell: results.filter(r => r.signal_type.toUpperCase() === 'SELL').length,
            hold: results.filter(r => r.signal_type.toUpperCase() === 'HOLD' || r.signal_type.toUpperCase() === 'CONFLICT').length
        };
    }, [results]);

    // Signal color helper
    const getSignalColor = (signal: string) => {
        switch (signal?.toUpperCase()) {
            case 'BUY': return 'error'; // Red
            case 'SELL': return 'primary'; // Blue
            case 'HOLD': return 'default';
            default: return 'default';
        }
    };

    const handleOpenDetails = (result: VerificationResult) => {
        setSelectedResult(result);
        setDetailsOpen(true);
    };

    return (
        <Accordion defaultExpanded={false} sx={{ mt: 3, mb: 3, border: '1px solid #e0e0e0', boxShadow: 'none' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ width: '100%' }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
                        <FactCheck color="action" /> 전체 종목 전략 검증 & 엑셀 다운로드
                    </Typography>
                    {lastRunTime && (
                        <Chip
                            label={`Last checked: ${format(lastRunTime, 'HH:mm:ss')}`}
                            size="small"
                            variant="outlined"
                        />
                    )}
                </Stack>
            </AccordionSummary>
            <AccordionDetails>
                {/* Controls Header */}
                <Stack direction="row" spacing={2} sx={{ mb: 3 }} alignItems="center">
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                        onClick={handleVerify}
                        disabled={loading}
                        sx={{ height: 40 }}
                    >
                        {loading ? '검증 중단' : '전체 검증 실행'}
                    </Button>

                    {loading && (
                        <Stack direction="column" sx={{ minWidth: 200, ml: 2, mr: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                <Typography variant="caption" color="text.secondary">{statusMessage}</Typography>
                                <Typography variant="caption" color="primary">{Math.round(progress)}%</Typography>
                            </Box>
                            <LinearProgress variant="determinate" value={progress} sx={{ height: 6, borderRadius: 1 }} />
                        </Stack>
                    )}

                    <Button
                        variant="outlined"
                        color="success"
                        startIcon={<DownloadIcon />}
                        onClick={handleDownloadExcel}
                        disabled={results.length === 0 || loading}
                        sx={{ height: 40 }}
                    >
                        엑셀 다운로드
                    </Button>

                    <Box sx={{ flexGrow: 1 }} />

                    {/* Filters */}
                    <TextField
                        placeholder="전략/종목명 검색"
                        size="small"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        InputProps={{
                            startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
                        }}
                        sx={{ width: 200 }}
                    />

                    <FormControl size="small" sx={{ width: 120 }}>
                        <InputLabel>신호 필터</InputLabel>
                        <Select
                            value={signalFilter}
                            label="신호 필터"
                            onChange={(e) => setSignalFilter(e.target.value)}
                        >
                            <MenuItem value="all">전체</MenuItem>
                            <MenuItem value="buy">매수 (Buy)</MenuItem>
                            <MenuItem value="sell">매도 (Sell)</MenuItem>
                            <MenuItem value="hold">관망 (Hold)</MenuItem>
                        </Select>
                    </FormControl>
                </Stack>

                {/* Summary Cards */}
                {results.length > 0 && (
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={3}>
                            <Card variant="outlined">
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Typography variant="body2" color="text.secondary">Total Scanned</Typography>
                                    <Typography variant="h5" fontWeight="bold">{summaryStats.total}</Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={3}>
                            <Card variant="outlined">
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Typography variant="body2" color="text.secondary">Buy Candidates</Typography>
                                    <Typography variant="h5" fontWeight="bold" color="text.primary">{summaryStats.buy}</Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={3}>
                            <Card variant="outlined">
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Typography variant="body2" color="text.secondary">Sell Candidates</Typography>
                                    <Typography variant="h5" fontWeight="bold" color="text.primary">{summaryStats.sell}</Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={3}>
                            <Card variant="outlined">
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Typography variant="body2" color="text.secondary">Hold/Conflict</Typography>
                                    <Typography variant="h5" fontWeight="bold">{summaryStats.hold}</Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                )}

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
                )}

                {/* Results Table */}
                <Paper variant="outlined" sx={{ width: '100%', overflow: 'hidden' }}>
                    <TableContainer sx={{ maxHeight: 600 }}>
                        <Table stickyHeader size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>전략명</TableCell>
                                    <TableCell>종목명 (코드)</TableCell>
                                    <TableCell align="right">현재가</TableCell>
                                    <TableCell align="center">신호</TableCell>
                                    <TableCell align="center">점수</TableCell>
                                    <TableCell>주요 사유</TableCell>
                                    <TableCell align="center">상세</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {filteredResults.length > 0 ? (
                                    filteredResults
                                        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                        .map((row, index) => (
                                            <TableRow key={`${row.stock_code}-${index}`} hover>
                                                <TableCell>{row.strategy_name}</TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" fontWeight="bold">{row.stock_name}</Typography>
                                                    <Typography variant="caption" color="text.secondary">{row.stock_code}</Typography>
                                                </TableCell>
                                                <TableCell align="right">{row.current_price.toLocaleString()}원</TableCell>
                                                <TableCell align="center">
                                                    <Chip
                                                        label={row.signal_type}
                                                        size="small"
                                                        variant="outlined"
                                                        sx={{ minWidth: 60, color: 'text.primary', borderColor: 'rgba(0, 0, 0, 0.23)' }}
                                                    />
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                        <CircularProgress
                                                            variant="determinate"
                                                            value={row.score}
                                                            size={20}
                                                            color="info"
                                                            sx={{ mr: 1 }}
                                                        />
                                                        <Typography variant="caption">{row.score}</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell sx={{ maxWidth: 300 }}>
                                                    <Typography variant="body2" noWrap title={row.details.reasons.join(', ')}>
                                                        {row.details.reasons[0] || '-'}
                                                        {row.details.reasons.length > 1 && ` (+${row.details.reasons.length - 1})`}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <IconButton size="small" onClick={() => handleOpenDetails(row)}>
                                                        <VisibilityIcon fontSize="small" />
                                                    </IconButton>
                                                </TableCell>
                                            </TableRow>
                                        ))) : (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                                            {loading ? '검증 데이터를 불러오는 중입니다...' :
                                                results.length === 0 ? '검증 실행 버튼을 눌러주세요.' : '검색 결과가 없습니다.'}
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        rowsPerPageOptions={[10, 25, 50, 100]}
                        component="div"
                        count={filteredResults.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </Paper>
            </AccordionDetails>

            {/* Detail Dialog */}
            <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    {selectedResult?.stock_name} ({selectedResult?.stock_code}) 검증 상세
                    <IconButton
                        aria-label="close"
                        onClick={() => setDetailsOpen(false)}
                        sx={{ position: 'absolute', right: 8, top: 8, color: (theme) => theme.palette.grey[500] }}
                    >
                        <CancelIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers>
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <Typography variant="subtitle2" color="text.secondary">전략명</Typography>
                            <Typography variant="body1" gutterBottom>{selectedResult?.strategy_name}</Typography>

                            <Typography variant="subtitle2" color="text.secondary">현재가</Typography>
                            <Typography variant="body1" gutterBottom>{selectedResult?.current_price.toLocaleString()}원</Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="subtitle2" color="text.secondary">신호 / 점수</Typography>
                            <Stack direction="row" spacing={1} alignItems="center">
                                <Chip
                                    label={selectedResult?.signal_type}
                                    color={getSignalColor(selectedResult?.signal_type || '') as any}
                                />
                                <Typography variant="body1">{selectedResult?.score}점</Typography>
                            </Stack>
                        </Grid>

                        <Grid item xs={12}>
                            <Divider sx={{ my: 1 }} />
                            <Typography variant="h6" gutterBottom>상세 사유</Typography>
                            {selectedResult?.details.reasons.length === 0 ? (
                                <Typography color="text.secondary">특별한 사유 없음</Typography>
                            ) : (
                                <Stack spacing={1}>
                                    {selectedResult?.details.reasons.map((reason, idx) => (
                                        <Alert key={idx} severity="info" icon={false} sx={{ py: 0, px: 1 }}>
                                            {reason}
                                        </Alert>
                                    ))}
                                </Stack>
                            )}
                        </Grid>

                        <Grid item xs={12}>
                            <Divider sx={{ my: 1 }} />
                            <Typography variant="h6" gutterBottom>지표 값 (Snapshot)</Typography>
                            <Paper variant="outlined" sx={{ p: 2, fontFamily: 'monospace', maxHeight: 400, overflow: 'auto' }}>
                                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                                    {JSON.stringify(selectedResult?.details.indicators, null, 2)}
                                </pre>
                            </Paper>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDetailsOpen(false)}>닫기</Button>
                </DialogActions>
            </Dialog>
        </Accordion>
    );
}
