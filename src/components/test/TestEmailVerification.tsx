import React, { useState, useEffect } from 'react'
import {
  Paper,
  Typography,
  Button,
  Stack,
  Alert,
  Box,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'
import { Refresh, Send, CheckCircle, Cancel } from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { authService } from '../../services/auth'

interface VerificationStatus {
  userId: string
  email: string
  authConfirmedAt: string | null
  profileVerified: boolean
  profileVerifiedAt: string | null
  syncStatus: 'synced' | 'needs_sync' | 'not_verified'
}

const TestEmailVerification: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const checkVerificationStatus = async () => {
    setLoading(true)
    setError('')
    
    try {
      const user = await authService.getCurrentUser()
      if (!user) {
        setError('No user logged in')
        setLoading(false)
        return
      }

      setCurrentUser(user)

      // Get profile data
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('email_verified, email_verified_at')
        .eq('id', user.id)
        .single()

      if (profileError) {
        setError(`Profile fetch error: ${profileError.message}`)
        setLoading(false)
        return
      }

      // Determine sync status
      let syncStatus: 'synced' | 'needs_sync' | 'not_verified' = 'not_verified'
      
      if (user.email_confirmed_at && profile?.email_verified_at) {
        syncStatus = 'synced'
      } else if (user.email_confirmed_at && !profile?.email_verified_at) {
        syncStatus = 'needs_sync'
      }

      setVerificationStatus({
        userId: user.id,
        email: user.email || '',
        authConfirmedAt: user.email_confirmed_at,
        profileVerified: profile?.email_verified || false,
        profileVerifiedAt: profile?.email_verified_at,
        syncStatus
      })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const resendVerificationEmail = async () => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      if (!currentUser?.email) {
        setError('No email address found')
        return
      }

      const { error } = await supabase.auth.resend({
        type: 'signup',
        email: currentUser.email,
      })

      if (error) {
        setError(`Failed to resend: ${error.message}`)
      } else {
        setMessage('Verification email sent! Please check your inbox.')
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const manualSync = async () => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      if (!currentUser?.id) {
        setError('No user ID found')
        return
      }

      // Call the manual sync function
      const { error } = await supabase.rpc('manual_sync_email_verification', {
        user_id: currentUser.id
      })

      if (error) {
        setError(`Sync failed: ${error.message}`)
      } else {
        setMessage('Manual sync completed!')
        await checkVerificationStatus()
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkVerificationStatus()
  }, [])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleString()
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Email Verification Status Test
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : verificationStatus ? (
        <Stack spacing={3}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Field</TableCell>
                  <TableCell>Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>User ID</TableCell>
                  <TableCell>{verificationStatus.userId}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>{verificationStatus.email}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Auth Confirmed At</TableCell>
                  <TableCell>
                    {formatDate(verificationStatus.authConfirmedAt)}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Profile Verified</TableCell>
                  <TableCell>
                    <Chip
                      label={verificationStatus.profileVerified ? 'Yes' : 'No'}
                      color={verificationStatus.profileVerified ? 'success' : 'default'}
                      size="small"
                      icon={verificationStatus.profileVerified ? <CheckCircle /> : <Cancel />}
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Profile Verified At</TableCell>
                  <TableCell>
                    {formatDate(verificationStatus.profileVerifiedAt)}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Sync Status</TableCell>
                  <TableCell>
                    <Chip
                      label={verificationStatus.syncStatus}
                      color={
                        verificationStatus.syncStatus === 'synced' ? 'success' :
                        verificationStatus.syncStatus === 'needs_sync' ? 'warning' :
                        'default'
                      }
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={checkVerificationStatus}
              disabled={loading}
            >
              Refresh Status
            </Button>

            {verificationStatus.syncStatus === 'needs_sync' && (
              <Button
                variant="outlined"
                color="warning"
                onClick={manualSync}
                disabled={loading}
              >
                Manual Sync
              </Button>
            )}

            {!verificationStatus.authConfirmedAt && (
              <Button
                variant="outlined"
                startIcon={<Send />}
                onClick={resendVerificationEmail}
                disabled={loading}
              >
                Resend Verification Email
              </Button>
            )}
          </Stack>
        </Stack>
      ) : (
        <Typography>No verification data available</Typography>
      )}
    </Paper>
  )
}

export default TestEmailVerification