import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  Tab,
  Tabs,
  Grid,
  Card,
  CardContent,
  Divider,
  Button
} from '@mui/material'
import {
  AdminPanelSettings,
  People,
  Assessment,
  Settings,
  Security,
  Dashboard,
  Home,
  ArrowBack
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import AdminApprovalPanel from '../components/admin/AdminApprovalPanel'
import AdminUserManager from '../components/admin/AdminUserManager'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

interface Stats {
  totalUsers: number
  pendingApprovals: number
  approvedUsers: number
  rejectedUsers: number
  adminCount: number
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate()
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)
  const [currentTab, setCurrentTab] = useState(0)
  const [stats, setStats] = useState<Stats>({
    totalUsers: 0,
    pendingApprovals: 0,
    approvedUsers: 0,
    rejectedUsers: 0,
    adminCount: 0
  })

  // Check admin status
  useEffect(() => {
    checkAdminStatus()
    fetchStats()
  }, [])

  const checkAdminStatus = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        setIsAdmin(false)
        setLoading(false)
        return
      }

      const { data: profile } = await supabase
        .from('profiles')
        .select('is_admin')
        .eq('id', user.id)
        .single()

      setIsAdmin(profile?.is_admin || false)
    } catch (error) {
      console.error('Error checking admin status:', error)
      setIsAdmin(false)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      // Fetch all user statistics
      const { data: profiles, error } = await supabase
        .from('profiles')
        .select('approval_status, is_admin')

      if (error) throw error

      if (profiles) {
        const stats = profiles.reduce(
          (acc, profile) => {
            acc.totalUsers++
            if (profile.is_admin) acc.adminCount++
            
            switch (profile.approval_status) {
              case 'pending':
                acc.pendingApprovals++
                break
              case 'approved':
                acc.approvedUsers++
                break
              case 'rejected':
                acc.rejectedUsers++
                break
            }
            return acc
          },
          {
            totalUsers: 0,
            pendingApprovals: 0,
            approvedUsers: 0,
            rejectedUsers: 0,
            adminCount: 0
          }
        )
        setStats(stats)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <Typography>Loading...</Typography>
        </Box>
      </Container>
    )
  }

  if (!isAdmin) {
    return (
      <Container>
        <Box sx={{ mt: 4 }}>
          <Alert severity="error" icon={<Security />}>
            <Typography variant="h6">Access Denied</Typography>
            <Typography>
              You do not have administrator privileges to access this page.
            </Typography>
          </Alert>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AdminPanelSettings sx={{ fontSize: 35 }} />
            Admin Dashboard
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Home />}
              onClick={() => navigate('/')}
              size="large"
            >
              메인으로
            </Button>
            <Button
              variant="contained"
              startIcon={<ArrowBack />}
              onClick={() => navigate(-1)}
              size="large"
            >
              뒤로가기
            </Button>
          </Box>
        </Box>
        
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4">
                  {stats.totalUsers}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pending
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {stats.pendingApprovals}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Approved
                </Typography>
                <Typography variant="h4" color="success.main">
                  {stats.approvedUsers}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Rejected
                </Typography>
                <Typography variant="h4" color="error.main">
                  {stats.rejectedUsers}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Admins
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {stats.adminCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Admin Tabs */}
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={currentTab} onChange={handleTabChange} aria-label="admin tabs">
              <Tab 
                icon={<People />} 
                iconPosition="start" 
                label="사용자 관리" 
                id="admin-tab-0"
                aria-controls="admin-tabpanel-0"
              />
              <Tab 
                icon={<AdminPanelSettings />} 
                iconPosition="start" 
                label="승인 대기" 
                id="admin-tab-1"
                aria-controls="admin-tabpanel-1"
              />
              <Tab 
                icon={<Assessment />} 
                iconPosition="start" 
                label="System Reports" 
                id="admin-tab-2"
                aria-controls="admin-tabpanel-2"
              />
              <Tab 
                icon={<Settings />} 
                iconPosition="start" 
                label="System Settings" 
                id="admin-tab-3"
                aria-controls="admin-tabpanel-3"
              />
            </Tabs>
          </Box>

          <TabPanel value={currentTab} index={0}>
            <AdminUserManager />
          </TabPanel>

          <TabPanel value={currentTab} index={1}>
            <AdminApprovalPanel />
          </TabPanel>

          <TabPanel value={currentTab} index={2}>
            <Box>
              <Typography variant="h6" gutterBottom>
                System Reports
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                System reports and analytics will be available here.
              </Alert>
            </Box>
          </TabPanel>

          <TabPanel value={currentTab} index={3}>
            <Box>
              <Typography variant="h6" gutterBottom>
                System Settings
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                System-wide configuration options will be available here.
              </Alert>
            </Box>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  )
}

export default AdminDashboard