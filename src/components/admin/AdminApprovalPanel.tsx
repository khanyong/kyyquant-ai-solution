import React, { useState, useEffect } from 'react'
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Stack,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Box,
  CircularProgress,
  Tooltip
} from '@mui/material'
import {
  CheckCircle,
  Cancel,
  Refresh,
  Info,
  AdminPanelSettings,
  Email,
  Person,
  CalendarToday
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { authService } from '../../services/auth'

interface PendingUser {
  id: string
  email: string
  name: string
  kiwoom_account: string | null
  created_at: string
  email_verified: boolean
  approval_status: 'pending' | 'approved' | 'rejected'
}

const AdminApprovalPanel: React.FC = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [loading, setLoading] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [selectedUser, setSelectedUser] = useState<PendingUser | null>(null)
  const [actionDialog, setActionDialog] = useState<{
    open: boolean
    action: 'approve' | 'reject' | null
    user: PendingUser | null
  }>({ open: false, action: null, user: null })
  const [rejectionReason, setRejectionReason] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // 관리자 권한 확인
  const checkAdminStatus = async () => {
    try {
      const user = await authService.getCurrentUser()
      if (!user) {
        setIsAdmin(false)
        return
      }

      const { data: profile } = await supabase
        .from('profiles')
        .select('is_admin')
        .eq('id', user.id)
        .single()

      setIsAdmin(profile?.is_admin || false)
    } catch (err) {
      console.error('Admin check error:', err)
      setIsAdmin(false)
    }
  }

  // 대기 중인 사용자 목록 가져오기
  const fetchPendingUsers = async () => {
    setLoading(true)
    setError('')

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('approval_status', 'pending')
        .order('created_at', { ascending: false })

      if (error) throw error
      setPendingUsers(data || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // 사용자 승인/거부 처리
  const handleUserAction = async () => {
    if (!actionDialog.user || !actionDialog.action) return

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const currentUser = await authService.getCurrentUser()
      if (!currentUser) {
        setError('관리자 인증이 필요합니다')
        return
      }

      const { error } = await supabase.rpc('approve_user', {
        p_user_id: actionDialog.user.id,
        p_admin_id: currentUser.id,
        p_approval_status: actionDialog.action === 'approve' ? 'approved' : 'rejected',
        p_reason: actionDialog.action === 'reject' ? rejectionReason : null
      })

      if (error) throw error

      setMessage(
        actionDialog.action === 'approve'
          ? `${actionDialog.user.name}님을 승인했습니다.`
          : `${actionDialog.user.name}님을 거부했습니다.`
      )

      // 목록 새로고침
      await fetchPendingUsers()
      
      // 다이얼로그 닫기
      setActionDialog({ open: false, action: null, user: null })
      setRejectionReason('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkAdminStatus()
  }, [])

  useEffect(() => {
    if (isAdmin) {
      fetchPendingUsers()
      
      // 실시간 업데이트 구독
      const subscription = supabase
        .channel('pending_users')
        .on('postgres_changes', 
          { 
            event: '*', 
            schema: 'public', 
            table: 'profiles',
            filter: 'approval_status=eq.pending'
          }, 
          () => {
            fetchPendingUsers()
          }
        )
        .subscribe()

      return () => {
        subscription.unsubscribe()
      }
    }
  }, [isAdmin])

  if (!isAdmin) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="warning" icon={<AdminPanelSettings />}>
          관리자 권한이 필요합니다.
        </Alert>
      </Paper>
    )
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AdminPanelSettings />
          사용자 승인 관리
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchPendingUsers}
          disabled={loading}
        >
          새로고침
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {message && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMessage('')}>
          {message}
        </Alert>
      )}

      <Alert severity="info" sx={{ mb: 2 }}>
        승인 대기 중인 사용자: {pendingUsers.length}명
      </Alert>

      {loading && !pendingUsers.length ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : pendingUsers.length === 0 ? (
        <Typography variant="body1" color="text.secondary" align="center" py={3}>
          승인 대기 중인 사용자가 없습니다.
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>이름</TableCell>
                <TableCell>이메일</TableCell>
                <TableCell>키움 ID</TableCell>
                <TableCell>이메일 인증</TableCell>
                <TableCell>가입일</TableCell>
                <TableCell align="center">작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pendingUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Person fontSize="small" />
                      <Typography>{user.name}</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Email fontSize="small" />
                      <Typography variant="body2">{user.email}</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {user.kiwoom_account || (
                      <Chip label="미등록" size="small" variant="outlined" />
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.email_verified ? '인증됨' : '미인증'}
                      color={user.email_verified ? 'success' : 'default'}
                      size="small"
                      icon={user.email_verified ? <CheckCircle /> : <Cancel />}
                    />
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                      <CalendarToday fontSize="small" />
                      <Typography variant="body2">
                        {new Date(user.created_at).toLocaleDateString()}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} justifyContent="center">
                      <Tooltip title="승인">
                        <Button
                          variant="contained"
                          color="success"
                          size="small"
                          startIcon={<CheckCircle />}
                          onClick={() => setActionDialog({
                            open: true,
                            action: 'approve',
                            user
                          })}
                          disabled={loading}
                        >
                          승인
                        </Button>
                      </Tooltip>
                      <Tooltip title="거부">
                        <Button
                          variant="outlined"
                          color="error"
                          size="small"
                          startIcon={<Cancel />}
                          onClick={() => setActionDialog({
                            open: true,
                            action: 'reject',
                            user
                          })}
                          disabled={loading}
                        >
                          거부
                        </Button>
                      </Tooltip>
                      <Tooltip title="상세 정보">
                        <IconButton
                          size="small"
                          onClick={() => setSelectedUser(user)}
                        >
                          <Info />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 승인/거부 확인 다이얼로그 */}
      <Dialog
        open={actionDialog.open}
        onClose={() => setActionDialog({ open: false, action: null, user: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {actionDialog.action === 'approve' ? '사용자 승인' : '사용자 거부'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity={actionDialog.action === 'approve' ? 'info' : 'warning'}>
              {actionDialog.user?.name} ({actionDialog.user?.email})님을{' '}
              {actionDialog.action === 'approve' ? '승인' : '거부'}하시겠습니까?
            </Alert>
            
            {actionDialog.action === 'reject' && (
              <TextField
                fullWidth
                multiline
                rows={3}
                label="거부 사유"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="거부 사유를 입력하세요 (선택사항)"
              />
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setActionDialog({ open: false, action: null, user: null })}
            disabled={loading}
          >
            취소
          </Button>
          <Button
            variant="contained"
            color={actionDialog.action === 'approve' ? 'success' : 'error'}
            onClick={handleUserAction}
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {actionDialog.action === 'approve' ? '승인' : '거부'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 사용자 상세 정보 다이얼로그 */}
      <Dialog
        open={!!selectedUser}
        onClose={() => setSelectedUser(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>사용자 상세 정보</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">ID</Typography>
                <Typography variant="body2">{selectedUser.id}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">이름</Typography>
                <Typography variant="body2">{selectedUser.name}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">이메일</Typography>
                <Typography variant="body2">{selectedUser.email}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">키움 계좌</Typography>
                <Typography variant="body2">
                  {selectedUser.kiwoom_account || '미등록'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">이메일 인증</Typography>
                <Chip
                  label={selectedUser.email_verified ? '인증 완료' : '미인증'}
                  color={selectedUser.email_verified ? 'success' : 'default'}
                  size="small"
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">가입일시</Typography>
                <Typography variant="body2">
                  {new Date(selectedUser.created_at).toLocaleString()}
                </Typography>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedUser(null)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}

export default AdminApprovalPanel