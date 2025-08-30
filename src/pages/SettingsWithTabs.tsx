import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Tabs,
  Tab,
  Slider,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  InputLabel,
  Stack
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Person,
  Notifications,
  Security,
  AccountBalance,
  Save,
  Cancel,
  TrendingUp,
  Analytics,
  Warning
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

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
      id={`settings-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

interface UserProfile {
  id: string
  email: string
  name: string
  kiwoom_account: string | null
  is_approved: boolean
  approval_status: string
  created_at: string
  email_verified: boolean
}

interface UserSettings {
  notifications: {
    emailAlerts: boolean
    tradingSignals: boolean
    marketNews: boolean
    priceAlerts: boolean
  }
  display: {
    theme: 'light' | 'dark' | 'auto'
    chartType: 'candlestick' | 'line'
    language: 'ko' | 'en'
  }
}

interface InvestmentSettings {
  universe: {
    marketCap: [number, number] // 시가총액 범위 (억원)
    per: [number, number] // PER 범위
    pbr: [number, number] // PBR 범위
    roe: [number, number] // ROE 범위 (%)
    debtRatio: [number, number] // 부채비율 범위 (%)
    includeSectors: string[] // 포함 섹터
    excludeSectors: string[] // 제외 섹터
  }
  riskManagement: {
    maxPositions: number // 최대 보유 종목 수
    positionSize: number // 종목당 투자 비중 (%)
    stopLoss: number // 손절매 기준 (%)
    takeProfit: number // 익절매 기준 (%)
    trailingStop: boolean // 추적 손절 사용
    trailingStopPercent: number // 추적 손절 비율 (%)
  }
  trading: {
    defaultOrderType: 'limit' | 'market'
    confirmBeforeOrder: boolean
    maxOrderAmount: number
    autoRebalance: boolean
    rebalancePeriod: 'daily' | 'weekly' | 'monthly'
  }
}

const Settings: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [userSettings, setUserSettings] = useState<UserSettings>({
    notifications: {
      emailAlerts: true,
      tradingSignals: true,
      marketNews: false,
      priceAlerts: true
    },
    display: {
      theme: 'dark',
      chartType: 'candlestick',
      language: 'ko'
    }
  })
  const [investmentSettings, setInvestmentSettings] = useState<InvestmentSettings>({
    universe: {
      marketCap: [10, 5000],
      per: [5, 30],
      pbr: [0.5, 5],
      roe: [5, 50],
      debtRatio: [0, 100],
      includeSectors: ['IT', '바이오', '2차전지', '반도체'],
      excludeSectors: ['건설', '조선']
    },
    riskManagement: {
      maxPositions: 10,
      positionSize: 10,
      stopLoss: -5,
      takeProfit: 10,
      trailingStop: false,
      trailingStopPercent: 3
    },
    trading: {
      defaultOrderType: 'limit',
      confirmBeforeOrder: true,
      maxOrderAmount: 1000000,
      autoRebalance: false,
      rebalancePeriod: 'monthly'
    }
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUserProfile()
    loadSettings()
  }, [])

  const fetchUserProfile = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single()

      if (error) throw error
      setProfile(data)
    } catch (error) {
      console.error('Error fetching profile:', error)
      setError('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = () => {
    const savedUserSettings = localStorage.getItem('userSettings')
    const savedInvestmentSettings = localStorage.getItem('investmentSettings')
    
    if (savedUserSettings) {
      setUserSettings(JSON.parse(savedUserSettings))
    }
    if (savedInvestmentSettings) {
      setInvestmentSettings(JSON.parse(savedInvestmentSettings))
    }
  }

  const handleSaveProfile = async () => {
    if (!profile) return

    setSaving(true)
    setMessage('')
    setError('')

    try {
      const { error } = await supabase
        .from('profiles')
        .update({
          name: profile.name,
          kiwoom_account: profile.kiwoom_account,
          updated_at: new Date().toISOString()
        })
        .eq('id', profile.id)

      if (error) throw error
      
      setMessage('Profile updated successfully')
    } catch (error) {
      console.error('Error updating profile:', error)
      setError('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveUserSettings = () => {
    setSaving(true)
    localStorage.setItem('userSettings', JSON.stringify(userSettings))
    setTimeout(() => {
      setSaving(false)
      setMessage('User settings saved successfully')
    }, 500)
  }

  const handleSaveInvestmentSettings = () => {
    setSaving(true)
    localStorage.setItem('investmentSettings', JSON.stringify(investmentSettings))
    setTimeout(() => {
      setSaving(false)
      setMessage('Investment settings saved successfully')
    }, 500)
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  const getApprovalStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'rejected':
        return 'error'
      case 'pending':
      default:
        return 'warning'
    }
  }

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <Typography>Loading settings...</Typography>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon sx={{ fontSize: 35 }} />
          Settings
        </Typography>

        {message && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMessage('')}>
            {message}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={currentTab} onChange={handleTabChange}>
              <Tab icon={<Person />} iconPosition="start" label="Profile" />
              <Tab icon={<TrendingUp />} iconPosition="start" label="Investment Settings" />
              <Tab icon={<Analytics />} iconPosition="start" label="Risk Management" />
              <Tab icon={<Notifications />} iconPosition="start" label="Notifications" />
              <Tab icon={<Security />} iconPosition="start" label="Security" />
            </Tabs>
          </Box>

          {/* Profile Tab */}
          <TabPanel value={currentTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Account Information
                    </Typography>
                    
                    {profile && (
                      <>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="textSecondary">
                            Account Status
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip 
                              label={profile.approval_status} 
                              color={getApprovalStatusColor(profile.approval_status) as any}
                              size="small"
                            />
                            {profile.email_verified && (
                              <Chip label="Email Verified" color="primary" size="small" />
                            )}
                          </Box>
                        </Box>

                        <TextField
                          fullWidth
                          label="Email"
                          value={profile.email}
                          disabled
                          margin="normal"
                        />
                        
                        <TextField
                          fullWidth
                          label="Name"
                          value={profile.name || ''}
                          onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                          margin="normal"
                        />
                        
                        <TextField
                          fullWidth
                          label="Kiwoom Account"
                          value={profile.kiwoom_account || ''}
                          onChange={(e) => setProfile({ ...profile, kiwoom_account: e.target.value })}
                          margin="normal"
                          helperText="Enter your Kiwoom securities account number"
                        />
                      </>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button 
                      variant="contained" 
                      startIcon={<Save />}
                      onClick={handleSaveProfile}
                      disabled={saving}
                    >
                      Save Profile
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Investment Settings Tab */}
          <TabPanel value={currentTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Investment Universe Filters
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Market Cap (억원)
                    </Typography>
                    <Slider
                      value={investmentSettings.universe.marketCap}
                      onChange={(e, value) => setInvestmentSettings({
                        ...investmentSettings,
                        universe: { ...investmentSettings.universe, marketCap: value as [number, number] }
                      })}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10000}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 5000, label: '5,000' },
                        { value: 10000, label: '10,000' }
                      ]}
                    />
                    
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                      PER Range
                    </Typography>
                    <Slider
                      value={investmentSettings.universe.per}
                      onChange={(e, value) => setInvestmentSettings({
                        ...investmentSettings,
                        universe: { ...investmentSettings.universe, per: value as [number, number] }
                      })}
                      valueLabelDisplay="auto"
                      min={0}
                      max={50}
                    />
                    
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                      PBR Range
                    </Typography>
                    <Slider
                      value={investmentSettings.universe.pbr}
                      onChange={(e, value) => setInvestmentSettings({
                        ...investmentSettings,
                        universe: { ...investmentSettings.universe, pbr: value as [number, number] }
                      })}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.1}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      ROE Range (%)
                    </Typography>
                    <Slider
                      value={investmentSettings.universe.roe}
                      onChange={(e, value) => setInvestmentSettings({
                        ...investmentSettings,
                        universe: { ...investmentSettings.universe, roe: value as [number, number] }
                      })}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                    />
                    
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                      Debt Ratio (%)
                    </Typography>
                    <Slider
                      value={investmentSettings.universe.debtRatio}
                      onChange={(e, value) => setInvestmentSettings({
                        ...investmentSettings,
                        universe: { ...investmentSettings.universe, debtRatio: value as [number, number] }
                      })}
                      valueLabelDisplay="auto"
                      min={0}
                      max={200}
                    />
                    
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                      Sector Preferences
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
                      {investmentSettings.universe.includeSectors.map((sector) => (
                        <Chip 
                          key={sector}
                          label={sector}
                          color="primary"
                          size="small"
                        />
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Button 
                  variant="contained" 
                  startIcon={<Save />}
                  onClick={handleSaveInvestmentSettings}
                  disabled={saving}
                >
                  Save Investment Settings
                </Button>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Risk Management Tab */}
          <TabPanel value={currentTab} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Position Management
                    </Typography>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Positions"
                      value={investmentSettings.riskManagement.maxPositions}
                      onChange={(e) => setInvestmentSettings({
                        ...investmentSettings,
                        riskManagement: { 
                          ...investmentSettings.riskManagement, 
                          maxPositions: parseInt(e.target.value) 
                        }
                      })}
                      margin="normal"
                      helperText="Maximum number of stocks to hold"
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="Position Size (%)"
                      value={investmentSettings.riskManagement.positionSize}
                      onChange={(e) => setInvestmentSettings({
                        ...investmentSettings,
                        riskManagement: { 
                          ...investmentSettings.riskManagement, 
                          positionSize: parseInt(e.target.value) 
                        }
                      })}
                      margin="normal"
                      helperText="Investment percentage per stock"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={investmentSettings.trading.autoRebalance}
                          onChange={(e) => setInvestmentSettings({
                            ...investmentSettings,
                            trading: { 
                              ...investmentSettings.trading, 
                              autoRebalance: e.target.checked 
                            }
                          })}
                        />
                      }
                      label="Auto Rebalance"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Stop Loss / Take Profit
                    </Typography>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="Stop Loss (%)"
                      value={investmentSettings.riskManagement.stopLoss}
                      onChange={(e) => setInvestmentSettings({
                        ...investmentSettings,
                        riskManagement: { 
                          ...investmentSettings.riskManagement, 
                          stopLoss: parseFloat(e.target.value) 
                        }
                      })}
                      margin="normal"
                      helperText="Automatic sell when loss exceeds this %"
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="Take Profit (%)"
                      value={investmentSettings.riskManagement.takeProfit}
                      onChange={(e) => setInvestmentSettings({
                        ...investmentSettings,
                        riskManagement: { 
                          ...investmentSettings.riskManagement, 
                          takeProfit: parseFloat(e.target.value) 
                        }
                      })}
                      margin="normal"
                      helperText="Automatic sell when profit reaches this %"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={investmentSettings.riskManagement.trailingStop}
                          onChange={(e) => setInvestmentSettings({
                            ...investmentSettings,
                            riskManagement: { 
                              ...investmentSettings.riskManagement, 
                              trailingStop: e.target.checked 
                            }
                          })}
                        />
                      }
                      label="Use Trailing Stop"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Button 
                  variant="contained" 
                  startIcon={<Save />}
                  onClick={handleSaveInvestmentSettings}
                  disabled={saving}
                >
                  Save Risk Settings
                </Button>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Notifications Tab */}
          <TabPanel value={currentTab} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Notification Preferences
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.notifications.emailAlerts}
                          onChange={(e) => setUserSettings({
                            ...userSettings,
                            notifications: { ...userSettings.notifications, emailAlerts: e.target.checked }
                          })}
                        />
                      }
                      label="Email Alerts"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.notifications.tradingSignals}
                          onChange={(e) => setUserSettings({
                            ...userSettings,
                            notifications: { ...userSettings.notifications, tradingSignals: e.target.checked }
                          })}
                        />
                      }
                      label="Trading Signals"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.notifications.marketNews}
                          onChange={(e) => setUserSettings({
                            ...userSettings,
                            notifications: { ...userSettings.notifications, marketNews: e.target.checked }
                          })}
                        />
                      }
                      label="Market News"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={userSettings.notifications.priceAlerts}
                          onChange={(e) => setUserSettings({
                            ...userSettings,
                            notifications: { ...userSettings.notifications, priceAlerts: e.target.checked }
                          })}
                        />
                      }
                      label="Price Alerts"
                    />
                  </CardContent>
                  <CardActions>
                    <Button 
                      variant="contained" 
                      startIcon={<Save />}
                      onClick={handleSaveUserSettings}
                      disabled={saving}
                    >
                      Save Notifications
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Security Tab */}
          <TabPanel value={currentTab} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Security Settings
                    </Typography>
                    
                    <Button variant="outlined" fullWidth sx={{ mb: 2 }}>
                      Change Password
                    </Button>
                    
                    <Button variant="outlined" fullWidth sx={{ mb: 2 }}>
                      Enable Two-Factor Authentication
                    </Button>
                    
                    <Typography variant="body2" color="textSecondary">
                      Last login: {profile?.created_at ? new Date(profile.created_at).toLocaleString() : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  )
}

export default Settings