import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Person,
  Notifications,
  Security,
  AccountBalance,
  Save
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

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
  }
  trading: {
    defaultOrderType: 'limit' | 'market'
    confirmBeforeOrder: boolean
    maxOrderAmount: number
  }
  display: {
    theme: 'light' | 'dark' | 'auto'
    chartType: 'candlestick' | 'line'
    language: 'ko' | 'en'
  }
}

const Settings: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      emailAlerts: true,
      tradingSignals: true,
      marketNews: false
    },
    trading: {
      defaultOrderType: 'limit',
      confirmBeforeOrder: true,
      maxOrderAmount: 1000000
    },
    display: {
      theme: 'light',
      chartType: 'candlestick',
      language: 'ko'
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
        .maybeSingle()

      if (error) throw error

      if (data) {
        setProfile(data)
      } else {
        // Fallback for missing profile
        setProfile({
          id: user.id,
          email: user.email || '',
          name: user.user_metadata?.name || '',
          kiwoom_account: null,
          is_approved: false,
          approval_status: 'pending',
          created_at: new Date().toISOString(),
          email_verified: !!user.email_confirmed_at
        })
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
      setError('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = () => {
    // Load settings from localStorage or database
    const savedSettings = localStorage.getItem('userSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
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
          // kiwoom_account is now managed via API Keys
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

  const handleSaveSettings = () => {
    setSaving(true)
    setMessage('')

    // Save settings to localStorage (or database)
    localStorage.setItem('userSettings', JSON.stringify(settings))

    setTimeout(() => {
      setSaving(false)
      setMessage('Settings saved successfully')
    }, 500)
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

        <Grid container spacing={3}>
          {/* Profile Information */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Person />
                  Profile Information
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
                      disabled
                      margin="normal"
                      helperText="Managed via MyPage > Account Link"
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

          {/* Notification Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Notifications />
                  Notification Preferences
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.emailAlerts}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, emailAlerts: e.target.checked }
                      })}
                    />
                  }
                  label="Email Alerts"
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.tradingSignals}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, tradingSignals: e.target.checked }
                      })}
                    />
                  }
                  label="Trading Signals"
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.marketNews}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, marketNews: e.target.checked }
                      })}
                    />
                  }
                  label="Market News"
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Trading Preferences */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <AccountBalance />
                  Trading Preferences
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.trading.confirmBeforeOrder}
                      onChange={(e) => setSettings({
                        ...settings,
                        trading: { ...settings.trading, confirmBeforeOrder: e.target.checked }
                      })}
                    />
                  }
                  label="Confirm Before Order"
                />

                <TextField
                  fullWidth
                  type="number"
                  label="Max Order Amount (KRW)"
                  value={settings.trading.maxOrderAmount}
                  onChange={(e) => setSettings({
                    ...settings,
                    trading: { ...settings.trading, maxOrderAmount: parseInt(e.target.value) }
                  })}
                  margin="normal"
                />
              </CardContent>
              <CardActions>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSaveSettings}
                  disabled={saving}
                >
                  Save Settings
                </Button>
              </CardActions>
            </Card>
          </Grid>

          {/* Security Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Security />
                  Security
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
      </Box>
    </Container>
  )
}

export default Settings