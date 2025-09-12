import { supabase } from '../lib/supabase'

export interface ApiKeyData {
  provider: string
  keyType: string
  keyName: string
  keyValue: string
  isTestMode: boolean
}

export class ApiKeyService {
  /**
   * Test if RPC function exists and is accessible
   */
  static async testRpcFunction() {
    try {
      console.log('Testing RPC function availability...')
      
      // Try to call with minimal parameters
      const { data, error } = await supabase.rpc('save_user_api_key', {
        p_user_id: '00000000-0000-0000-0000-000000000000',
        p_provider: 'test',
        p_key_type: 'test',
        p_key_name: 'test',
        p_key_value: 'test',
        p_is_test_mode: true
      })

      if (error) {
        console.error('RPC test failed:', error)
        return { success: false, error }
      }

      console.log('RPC test successful:', data)
      return { success: true, data }
    } catch (err) {
      console.error('RPC test exception:', err)
      return { success: false, error: err }
    }
  }

  /**
   * Save API key using direct table insert as fallback
   */
  static async saveApiKeyDirect(userId: string, keyData: ApiKeyData) {
    try {
      console.log('Attempting direct table insert...')
      
      // Encode the value as base64
      const encodedValue = btoa(keyData.keyValue)
      
      const { data, error } = await supabase
        .from('user_api_keys')
        .upsert({
          user_id: userId,
          provider: keyData.provider,
          key_type: keyData.keyType,
          key_name: keyData.keyName,
          encrypted_value: encodedValue,
          is_test_mode: keyData.isTestMode,
          is_active: true,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'user_id,provider,key_type,key_name'
        })
        .select()
        .single()

      if (error) {
        console.error('Direct insert failed:', error)
        return { success: false, error }
      }

      console.log('Direct insert successful:', data)
      return { success: true, data }
    } catch (err) {
      console.error('Direct insert exception:', err)
      return { success: false, error: err }
    }
  }

  /**
   * Save API key with multiple fallback strategies
   */
  static async saveApiKey(userId: string, keyData: ApiKeyData) {
    console.group('🔑 Saving API Key')
    console.log('User ID:', userId)
    console.log('Key Data:', { ...keyData, keyValue: '***' })

    // Strategy 1: Try RPC with standard parameter names (alphabetical order)
    try {
      console.log('Strategy 1: RPC with p_ prefix (alphabetical order)...')
      const { data, error } = await supabase.rpc('save_user_api_key', {
        p_is_test_mode: keyData.isTestMode,
        p_key_name: keyData.keyName,
        p_key_type: keyData.keyType,
        p_key_value: keyData.keyValue,
        p_provider: keyData.provider,
        p_user_id: userId
      })

      if (!error) {
        console.log('✅ Strategy 1 successful:', data)
        console.groupEnd()
        return { success: true, data, method: 'rpc_standard' }
      }
      console.error('Strategy 1 failed:', error)
    } catch (err) {
      console.error('Strategy 1 exception:', err)
    }

    // Strategy 2: Try RPC without p_ prefix
    try {
      console.log('Strategy 2: RPC without prefix...')
      const { data, error } = await supabase.rpc('save_user_api_key', {
        user_id: userId,
        provider: keyData.provider,
        key_type: keyData.keyType,
        key_name: keyData.keyName,
        key_value: keyData.keyValue,
        is_test_mode: keyData.isTestMode
      })

      if (!error) {
        console.log('✅ Strategy 2 successful:', data)
        console.groupEnd()
        return { success: true, data, method: 'rpc_no_prefix' }
      }
      console.error('Strategy 2 failed:', error)
    } catch (err) {
      console.error('Strategy 2 exception:', err)
    }

    // Strategy 3: Direct table insert
    try {
      console.log('Strategy 3: Direct table insert...')
      const result = await this.saveApiKeyDirect(userId, keyData)
      if (result.success) {
        console.log('✅ Strategy 3 successful')
        console.groupEnd()
        return { ...result, method: 'direct_insert' }
      }
    } catch (err) {
      console.error('Strategy 3 exception:', err)
    }

    console.error('❌ All strategies failed')
    console.groupEnd()
    return { 
      success: false, 
      error: 'Failed to save API key using all available methods',
      method: 'none'
    }
  }

  /**
   * Get API keys for a user
   */
  static async getApiKeys(userId: string, mode?: 'test' | 'live') {
    try {
      let query = supabase
        .from('user_api_keys')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      if (mode !== undefined) {
        query = query.eq('is_test_mode', mode === 'test')
      }

      const { data, error } = await query

      if (error) {
        console.error('Failed to fetch API keys:', error)
        return { success: false, error }
      }

      return { success: true, data }
    } catch (err) {
      console.error('Exception fetching API keys:', err)
      return { success: false, error: err }
    }
  }

  /**
   * Delete an API key
   */
  static async deleteApiKey(userId: string, keyId: string) {
    try {
      // First try RPC
      try {
        const { data, error } = await supabase.rpc('delete_user_api_key', {
          p_user_id: userId,
          p_key_id: keyId
        })

        if (!error) {
          return { success: true, data, method: 'rpc' }
        }
      } catch (err) {
        console.warn('RPC delete failed, trying direct delete:', err)
      }

      // Fallback to direct delete
      const { error } = await supabase
        .from('user_api_keys')
        .delete()
        .eq('id', keyId)
        .eq('user_id', userId)

      if (error) {
        console.error('Failed to delete API key:', error)
        return { success: false, error }
      }

      return { success: true, method: 'direct' }
    } catch (err) {
      console.error('Exception deleting API key:', err)
      return { success: false, error: err }
    }
  }
}

// Export for debugging in browser console
if (typeof window !== 'undefined') {
  (window as any).ApiKeyService = ApiKeyService
}