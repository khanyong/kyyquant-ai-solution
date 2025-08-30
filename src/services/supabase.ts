import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://hznkyaomtrpzcayayayh.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQ5NDU0MzksImV4cCI6MjA0MDUyMTQzOX0.4u3f58dGMME9r69cp7SUkVc5VlVp3TQaS1UqAOXfJdA'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)