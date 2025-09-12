import React, { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Alert,
  Stack,
  Divider,
  TextField,
  CircularProgress
} from '@mui/material'
import { BugReport, CheckCircle, Error } from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { ApiKeyService } from '../services/apiKeyService'

interface TestResult {
  name: string
  status: 'pending' | 'success' | 'error'
  message?: string
  data?: any
}

const ApiKeyTest: React.FC = () => {
  const [testing, setTesting] = useState(false)
  const [results, setResults] = useState<TestResult[]>([])
  const [testUserId, setTestUserId] = useState('')

  const runTests = async () => {
    setTesting(true)
    setResults([])
    
    const tests: TestResult[] = []
    
    // Test 1: Check current user
    tests.push({ name: 'Get Current User', status: 'pending' })
    setResults([...tests])
    
    try {
      const { data: { user } } = await supabase.auth.getUser()
      const userId = user?.id || testUserId || '00000000-0000-0000-0000-000000000000'
      tests[0] = {
        ...tests[0],
        status: 'success',
        message: `User ID: ${userId}`,
        data: user
      }
      setResults([...tests])
      
      // Test 2: Test RPC function existence
      tests.push({ name: 'Test RPC Function', status: 'pending' })
      setResults([...tests])
      
      const rpcTest = await ApiKeyService.testRpcFunction()
      tests[1] = {
        ...tests[1],
        status: rpcTest.success ? 'success' : 'error',
        message: rpcTest.success ? 'RPC function is accessible' : 'RPC function not found',
        data: rpcTest
      }
      setResults([...tests])
      
      // Test 3: Try RPC with standard parameters
      tests.push({ name: 'RPC with p_ prefix', status: 'pending' })
      setResults([...tests])
      
      try {
        const { data, error } = await supabase.rpc('save_user_api_key', {
          p_user_id: userId,
          p_provider: 'test_rpc',
          p_key_type: 'test_key',
          p_key_name: 'RPC Test',
          p_key_value: 'test_value_123',
          p_is_test_mode: true
        })
        
        tests[2] = {
          ...tests[2],
          status: error ? 'error' : 'success',
          message: error ? error.message : 'RPC call successful',
          data: { data, error }
        }
      } catch (err: any) {
        tests[2] = {
          ...tests[2],
          status: 'error',
          message: err.message,
          data: err
        }
      }
      setResults([...tests])
      
      // Test 4: Try RPC without prefix
      tests.push({ name: 'RPC without prefix', status: 'pending' })
      setResults([...tests])
      
      try {
        const { data, error } = await supabase.rpc('save_user_api_key', {
          user_id: userId,
          provider: 'test_rpc_no_prefix',
          key_type: 'test_key',
          key_name: 'RPC Test No Prefix',
          key_value: 'test_value_456',
          is_test_mode: true
        })
        
        tests[3] = {
          ...tests[3],
          status: error ? 'error' : 'success',
          message: error ? error.message : 'RPC call successful',
          data: { data, error }
        }
      } catch (err: any) {
        tests[3] = {
          ...tests[3],
          status: 'error',
          message: err.message,
          data: err
        }
      }
      setResults([...tests])
      
      // Test 5: Direct table insert
      tests.push({ name: 'Direct Table Insert', status: 'pending' })
      setResults([...tests])
      
      try {
        const result = await ApiKeyService.saveApiKeyDirect(userId, {
          provider: 'test_direct',
          keyType: 'test_key',
          keyName: 'Direct Insert Test',
          keyValue: 'test_value_789',
          isTestMode: true
        })
        
        tests[4] = {
          ...tests[4],
          status: result.success ? 'success' : 'error',
          message: result.success ? 'Direct insert successful' : 'Direct insert failed',
          data: result
        }
      } catch (err: any) {
        tests[4] = {
          ...tests[4],
          status: 'error',
          message: err.message,
          data: err
        }
      }
      setResults([...tests])
      
      // Test 6: Use ApiKeyService with fallback
      tests.push({ name: 'ApiKeyService with Fallback', status: 'pending' })
      setResults([...tests])
      
      try {
        const result = await ApiKeyService.saveApiKey(userId, {
          provider: 'test_service',
          keyType: 'test_key',
          keyName: 'Service Test',
          keyValue: 'test_value_service',
          isTestMode: true
        })
        
        tests[5] = {
          ...tests[5],
          status: result.success ? 'success' : 'error',
          message: `${result.success ? 'Success' : 'Failed'} using method: ${result.method}`,
          data: result
        }
      } catch (err: any) {
        tests[5] = {
          ...tests[5],
          status: 'error',
          message: err.message,
          data: err
        }
      }
      setResults([...tests])
      
      // Test 7: Check if data was saved
      tests.push({ name: 'Verify Saved Data', status: 'pending' })
      setResults([...tests])
      
      try {
        const { data, error } = await supabase
          .from('user_api_keys')
          .select('*')
          .eq('user_id', userId)
          .like('provider', 'test%')
        
        tests[6] = {
          ...tests[6],
          status: error ? 'error' : 'success',
          message: error ? error.message : `Found ${data?.length || 0} test keys`,
          data: data
        }
        
        // Clean up test data
        if (data && data.length > 0) {
          await supabase
            .from('user_api_keys')
            .delete()
            .eq('user_id', userId)
            .like('provider', 'test%')
        }
      } catch (err: any) {
        tests[6] = {
          ...tests[6],
          status: 'error',
          message: err.message,
          data: err
        }
      }
      setResults([...tests])
      
    } catch (error: any) {
      console.error('Test error:', error)
    } finally {
      setTesting(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BugReport />
          API Key Function Test
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          이 페이지는 API 키 저장 기능을 테스트합니다. RPC 함수와 직접 저장 방법을 모두 시도합니다.
        </Alert>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Test User ID (optional)"
            value={testUserId}
            onChange={(e) => setTestUserId(e.target.value)}
            helperText="Leave empty to use current user or default test ID"
            sx={{ mb: 2 }}
          />
          
          <Button
            variant="contained"
            onClick={runTests}
            disabled={testing}
            startIcon={testing ? <CircularProgress size={20} /> : <BugReport />}
          >
            {testing ? 'Testing...' : 'Run Tests'}
          </Button>
        </Box>
        
        {results.length > 0 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" gutterBottom>
              Test Results
            </Typography>
            
            <Stack spacing={2}>
              {results.map((result, index) => (
                <Paper
                  key={index}
                  elevation={2}
                  sx={{
                    p: 2,
                    borderLeft: 4,
                    borderColor: 
                      result.status === 'success' ? 'success.main' :
                      result.status === 'error' ? 'error.main' : 'grey.400'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {result.status === 'success' && <CheckCircle color="success" />}
                    {result.status === 'error' && <Error color="error" />}
                    {result.status === 'pending' && <CircularProgress size={20} />}
                    
                    <Typography variant="subtitle1" fontWeight="bold">
                      {result.name}
                    </Typography>
                  </Box>
                  
                  {result.message && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {result.message}
                    </Typography>
                  )}
                  
                  {result.data && (
                    <Box sx={{ mt: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                      <Typography variant="caption" component="pre" sx={{ fontFamily: 'monospace' }}>
                        {JSON.stringify(result.data, null, 2)}
                      </Typography>
                    </Box>
                  )}
                </Paper>
              ))}
            </Stack>
            
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Debug Instructions:
              </Typography>
              <Typography variant="body2" component="div">
                1. Open browser console (F12) for detailed logs<br />
                2. Check Supabase Dashboard → Database → Functions<br />
                3. Verify save_user_api_key function exists in public schema<br />
                4. Check if "Exposed via API" is enabled for the function<br />
                5. If RPC fails but direct insert works, use direct insert as fallback
              </Typography>
            </Box>
          </>
        )}
      </Paper>
    </Container>
  )
}

export default ApiKeyTest