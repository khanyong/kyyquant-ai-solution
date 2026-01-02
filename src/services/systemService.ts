import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface SystemStatus {
    trading_context: {
        mode: 'REAL' | 'MOCK'
        active_account_no: string
        accounts?: {
            LIVE: string
            MOCK: string
        }
        server_ip: string
    }
    cpu: any
    memory: any
    disk: any
    uptime_seconds: number
    timestamp: number
}

export const systemService = {
    async getStatus(): Promise<SystemStatus> {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/system/status`)
            return response.data
        } catch (error) {
            console.error('Failed to fetch system status:', error)
            throw error
        }
    }
}
