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
  IconButton,
  Box,
  CircularProgress,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  Tabs,
  Tab
} from '@mui/material'
import {
  CheckCircle,
  Cancel,
  Refresh,
  Info,
  AdminPanelSettings,
  Email,
  Person,
  CalendarToday,
  Edit,
  Save,
  Close
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { authService } from '../../services/auth'

interface User {
  id: string
  email: string
  name: string
  kiwoom_account: string | null
  created_at: string
  email_verified: boolean
  approval_status: 'pending' | 'approved' | 'rejected'
  role: string
  is_admin: boolean
}

const ROLES = [
  { value: 'trial', label: '체험 회원', color: 'default' },
  { value: 'standard', label: '일반 회원', color: 'info' },
  { value: 'premium', label: '프리미엄 회원', color: 'warning' },
  { value: 'admin', label: '관리자', color: 'error' },
  { value: 'super_admin', label: '최고 관리자', color: 'error' }
]

const AdminUserManager: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [currentAdminId, setCurrentAdminId] = useState<string>('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)
  const [editingRole, setEditingRole] = useState<{ userId: string; role: string } | null>(null)

  // 관리자 권한 확인
  const checkAdminStatus = async () => {
    try {
      const user = await authService.getCurrentUser()
      if (!user) {
        setIsAdmin(false)
        return
      }

      setCurrentAdminId(user.id)

      const { data: profile } = await supabase
        .from('profiles')
        .select('is_admin, role')
        .eq('id', user.id)
        .single()

      setIsAdmin(profile?.is_admin || profile?.role === 'admin' || profile?.role === 'super_admin')
    } catch (err) {
      console.error('Admin check error:', err)
      setIsAdmin(false)
    }
  }

  // 사용자 목록 가져오기
  const fetchUsers = async () => {
    setLoading(true)
    setError('')

    try {
      let query = supabase
        .from('profiles')
        .select('*')
        .order('created_at', { ascending: false })

      // 탭에 따라 필터링
      if (tabValue === 0) {
        query = query.eq('approval_status', 'pending')
      } else if (tabValue === 1) {
        query = query.eq('approval_status', 'approved')
      } else if (tabValue === 2) {
        query = query.eq('approval_status', 'rejected')
      }

      const { data, error } = await query

      if (error) throw error
      setUsers(data || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // 사용자 승인/거부
  const handleApproval = async (userId: string, status: 'approved' | 'rejected', reason?: string) => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const { error } = await supabase.rpc('approve_user', {
        p_user_id: userId,
        p_admin_id: currentAdminId,
        p_approval_status: status,
        p_reason: reason || null
      })

      if (error) throw error

      setMessage(`사용자를 ${status === 'approved' ? '승인' : '거부'}했습니다.`)
      await fetchUsers()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // 역할 변경
  const handleRoleChange = async (userId: string, newRole: string) => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const { data, error } = await supabase.rpc('update_user_role', {
        p_user_id: userId,
        p_admin_id: currentAdminId,
        p_new_role: newRole
      })

      if (error) throw error

      if (data && !data.success) {
        throw new Error(data.error)
      }

      setMessage('역할이 변경되었습니다.')
      setEditingRole(null)
      await fetchUsers()
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
      fetchUsers()
    }
  }, [isAdmin, tabValue])

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
          사용자 관리
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchUsers}
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

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 2 }}>
        <Tab label="승인 대기" />
        <Tab label="승인됨" />
        <Tab label="거부됨" />
        <Tab label="전체" />
      </Tabs>

      {loading && !users.length ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : users.length === 0 ? (
        <Typography variant="body1" color="text.secondary" align="center" py={3}>
          사용자가 없습니다.
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>이름</TableCell>
                <TableCell>이메일</TableCell>
                <TableCell>역할</TableCell>
                <TableCell>상태</TableCell>
                <TableCell>이메일 인증</TableCell>
                <TableCell>가입일</TableCell>
                <TableCell align="center">작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
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
                    {editingRole?.userId === user.id ? (
                      <Stack direction="row" spacing={1} alignItems="center">
                        <FormControl size="small">
                          <Select
                            value={editingRole.role}
                            onChange={(e) => setEditingRole({ userId: user.id, role: e.target.value })}
                            autoWidth
                          >
                            {ROLES.map((role) => (
                              <MenuItem key={role.value} value={role.value}>
                                {role.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleRoleChange(user.id, editingRole.role)}
                        >
                          <Save />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="default"
                          onClick={() => setEditingRole(null)}
                        >
                          <Close />
                        </IconButton>
                      </Stack>
                    ) : (
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Chip
                          label={ROLES.find(r => r.value === user.role)?.label || user.role}
                          color={ROLES.find(r => r.value === user.role)?.color as any || 'default'}
                          size="small"
                        />
                        <IconButton
                          size="small"
                          onClick={() => setEditingRole({ userId: user.id, role: user.role })}
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                      </Stack>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={
                        user.approval_status === 'approved' ? '승인됨' :
                        user.approval_status === 'rejected' ? '거부됨' : '대기중'
                      }
                      color={
                        user.approval_status === 'approved' ? 'success' :
                        user.approval_status === 'rejected' ? 'error' : 'warning'
                      }
                      size="small"
                    />
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
                    {user.approval_status === 'pending' && (
                      <Stack direction="row" spacing={1} justifyContent="center">
                        <Button
                          variant="contained"
                          color="success"
                          size="small"
                          startIcon={<CheckCircle />}
                          onClick={() => handleApproval(user.id, 'approved')}
                          disabled={loading}
                        >
                          승인
                        </Button>
                        <Button
                          variant="outlined"
                          color="error"
                          size="small"
                          startIcon={<Cancel />}
                          onClick={() => handleApproval(user.id, 'rejected', '관리자 거부')}
                          disabled={loading}
                        >
                          거부
                        </Button>
                      </Stack>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  )
}

export default AdminUserManager