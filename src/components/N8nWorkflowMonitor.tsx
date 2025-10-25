import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  Stack,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  ExpandMore,
  CheckCircle,
  Error,
  Schedule,
  PlayArrow,
  Refresh,
  TrendingUp,
  Timer,
} from '@mui/icons-material'
import { n8nClient, WorkflowExecutionSummary, NodeExecutionStatus } from '../lib/n8n'
import { isMarketOpen, getMarketStatusMessage } from '../utils/marketHours'

export default function N8nWorkflowMonitor() {
  const [workflows, setWorkflows] = useState<WorkflowExecutionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [expandedWorkflow, setExpandedWorkflow] = useState<string | false>(false)
  const [marketStatus, setMarketStatus] = useState<string>('')

  useEffect(() => {
    fetchWorkflowData()

    // 시장 상태 초기화 및 주기적 업데이트
    setMarketStatus(getMarketStatusMessage())
    const statusInterval = setInterval(() => {
      setMarketStatus(getMarketStatusMessage())
    }, 60000) // 1분마다 시장 상태 업데이트

    // 30초마다 자동 새로고침 (시장 운영 중에만)
    const interval = setInterval(() => {
      if (isMarketOpen()) {
        fetchWorkflowData()
      }
    }, 30000)

    return () => {
      clearInterval(statusInterval)
      clearInterval(interval)
    }
  }, [])

  const fetchWorkflowData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await n8nClient.getAllWorkflowsSummary(20)
      setWorkflows(data)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('워크플로우 데이터 로드 실패:', err)
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success'
      case 'error':
        return 'error'
      case 'running':
        return 'info'
      case 'waiting':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getStatusIcon = (status: string): React.ReactElement | undefined => {
    switch (status) {
      case 'success':
        return <CheckCircle fontSize="small" />
      case 'error':
        return <Error fontSize="small" />
      case 'running':
        return <PlayArrow fontSize="small" />
      case 'waiting':
        return <Schedule fontSize="small" />
      default:
        return undefined
    }
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return '-'
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}초`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}분 ${remainingSeconds}초`
  }

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const handleAccordionChange = (workflowId: string) => (_: any, isExpanded: boolean) => {
    setExpandedWorkflow(isExpanded ? workflowId : false)
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <IconButton size="small" onClick={fetchWorkflowData}>
          <Refresh />
        </IconButton>
      }>
        <Typography variant="body2">
          <strong>n8n 연결 오류:</strong> {error}
        </Typography>
        <Typography variant="caption" display="block" mt={1}>
          n8n이 실행 중이고 API 키가 올바르게 설정되어 있는지 확인하세요.
        </Typography>
      </Alert>
    )
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="h5" component="h2">
                ⚡ n8n 워크플로우 활동
              </Typography>
              <Chip
                label={marketStatus}
                color={isMarketOpen() ? 'success' : 'default'}
                size="small"
                variant={isMarketOpen() ? 'filled' : 'outlined'}
              />
            </Stack>
            <Stack direction="row" spacing={1} alignItems="center">
              {lastUpdate && (
                <Typography variant="caption" color="text.secondary">
                  {isMarketOpen()
                    ? `마지막 업데이트: ${lastUpdate.toLocaleTimeString()}`
                    : '주식시장 휴장 중 - 실시간 업데이트 일시정지'
                  }
                </Typography>
              )}
              <IconButton size="small" onClick={fetchWorkflowData} disabled={loading}>
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {workflows.length === 0 && !loading && (
            <Alert severity="info">
              활성화된 워크플로우가 없습니다. n8n에서 워크플로우를 활성화하세요.
            </Alert>
          )}

          {/* 전체 통계 요약 */}
          {workflows.length > 0 && (
            <>
              <Grid container spacing={2} mb={3}>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <CheckCircle color="success" />
                      <Typography variant="caption" color="text.secondary">
                        최근 1분
                      </Typography>
                    </Stack>
                    <Typography variant="h4" color="success.main" fontWeight="bold">
                      {workflows.filter(w =>
                        w.lastExecution?.status === 'success' &&
                        w.lastExecution.startedAt &&
                        new Date().getTime() - new Date(w.lastExecution.startedAt).getTime() < 60000
                      ).length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">실행 성공</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <Error color="error" />
                      <Typography variant="caption" color="text.secondary">
                        최근 5분
                      </Typography>
                    </Stack>
                    <Typography variant="h4" color="error.main" fontWeight="bold">
                      {workflows.filter(w =>
                        w.lastExecution?.status === 'error' &&
                        w.lastExecution.startedAt &&
                        new Date().getTime() - new Date(w.lastExecution.startedAt).getTime() < 300000
                      ).length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">실행 실패</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <TrendingUp color="primary" />
                      <Typography variant="caption" color="text.secondary">
                        평균 성공률
                      </Typography>
                    </Stack>
                    <Typography variant="h4" color="primary.main" fontWeight="bold">
                      {workflows.length > 0
                        ? Math.round(workflows.reduce((sum, w) => sum + w.successRate, 0) / workflows.length)
                        : 0}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">전체 워크플로우</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(2, 136, 209, 0.1)', border: '1px solid rgba(2, 136, 209, 0.3)' }}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <Timer color="info" />
                      <Typography variant="caption" color="text.secondary">
                        총 실행 횟수
                      </Typography>
                    </Stack>
                    <Typography variant="h4" color="info.main" fontWeight="bold">
                      {workflows.reduce((sum, w) => sum + w.totalExecutions, 0)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">최근 20건</Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* 워크플로우별 상세 정보 */}
              {workflows.map((workflow) => (
                <Accordion
                  key={workflow.workflowId}
                  expanded={expandedWorkflow === workflow.workflowId}
                  onChange={handleAccordionChange(workflow.workflowId)}
                  sx={{ mb: 1 }}
                >
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {workflow.workflowName}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ID: {workflow.workflowId}
                        </Typography>
                      </Box>

                      {workflow.lastExecution && (
                        <>
                          <Chip
                            icon={getStatusIcon(workflow.lastExecution.status)}
                            label={workflow.lastExecution.status.toUpperCase()}
                            color={getStatusColor(workflow.lastExecution.status) as any}
                            size="small"
                          />
                          <Tooltip title="성공률">
                            <Chip
                              label={`${Math.round(workflow.successRate)}%`}
                              size="small"
                              variant="outlined"
                            />
                          </Tooltip>
                          <Typography variant="caption" color="text.secondary">
                            {formatTime(workflow.lastExecution.startedAt)}
                          </Typography>
                        </>
                      )}
                    </Stack>
                  </AccordionSummary>

                  <AccordionDetails>
                    {/* 실행 정보 */}
                    {workflow.lastExecution && (
                      <Box mb={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          📊 최근 실행 정보
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={6} md={3}>
                            <Typography variant="caption" color="text.secondary">
                              실행 ID
                            </Typography>
                            <Typography variant="body2" fontFamily="monospace">
                              {workflow.lastExecution.id}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Typography variant="caption" color="text.secondary">
                              실행 시간
                            </Typography>
                            <Typography variant="body2">
                              {formatDuration(workflow.lastExecution.duration)}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Typography variant="caption" color="text.secondary">
                              시작 시각
                            </Typography>
                            <Typography variant="body2">
                              {formatTime(workflow.lastExecution.startedAt)}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Typography variant="caption" color="text.secondary">
                              종료 시각
                            </Typography>
                            <Typography variant="body2">
                              {formatTime(workflow.lastExecution.stoppedAt)}
                            </Typography>
                          </Grid>
                        </Grid>
                      </Box>
                    )}

                    {/* 노드별 실행 상태 */}
                    {workflow.nodeExecutions.length > 0 && (
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          🔍 노드별 실행 상태
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>노드명</TableCell>
                                <TableCell>유형</TableCell>
                                <TableCell align="center">상태</TableCell>
                                <TableCell align="right">처리 항목</TableCell>
                                <TableCell align="right">실행 시간</TableCell>
                                <TableCell>마지막 실행</TableCell>
                                <TableCell>에러</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {workflow.nodeExecutions.map((node, idx) => (
                                <TableRow key={idx} hover>
                                  <TableCell>
                                    <Typography variant="body2" fontWeight="medium">
                                      {node.nodeName}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Chip label={node.nodeType} size="small" variant="outlined" />
                                  </TableCell>
                                  <TableCell align="center">
                                    <Chip
                                      icon={getStatusIcon(node.status)}
                                      label={node.status}
                                      color={getStatusColor(node.status) as any}
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell align="right">
                                    <Typography variant="body2">
                                      {node.itemsProcessed ?? '-'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell align="right">
                                    <Typography variant="body2">
                                      {node.executionTime ? `${node.executionTime}ms` : '-'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="caption">
                                      {formatTime(node.lastExecutedAt)}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    {node.error && (
                                      <Tooltip title={node.error}>
                                        <Chip
                                          label="에러 보기"
                                          size="small"
                                          color="error"
                                          variant="outlined"
                                        />
                                      </Tooltip>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>
                    )}

                    {workflow.nodeExecutions.length === 0 && (
                      <Alert severity="info">
                        아직 실행 기록이 없습니다.
                      </Alert>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </>
          )}
        </CardContent>
      </Card>

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          💡 <strong>실시간 모니터링:</strong> 워크플로우 실행 상태가 30초마다 자동으로 업데이트됩니다.
          각 워크플로우를 클릭하면 노드별 상세 실행 정보를 확인할 수 있습니다.
        </Typography>
      </Alert>
    </Box>
  )
}
