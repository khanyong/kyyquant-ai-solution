import React from 'react'
import StrategyDashboard from '@/components/StrategyDashboard'
import { useAuth } from '@/contexts/AuthContext'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AlertCircle, LogIn } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const StrategyPage: React.FC = () => {
  const { user, loading } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">로딩 중...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="container mx-auto p-4 max-w-md">
        <Alert className="mt-8">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            전략 관리 기능을 사용하려면 로그인이 필요합니다.
          </AlertDescription>
        </Alert>
        <div className="mt-4 text-center">
          <Button onClick={() => navigate('/login')}>
            <LogIn className="mr-2 h-4 w-4" />
            로그인하기
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <StrategyDashboard userId={user.id} />
    </div>
  )
}

export default StrategyPage