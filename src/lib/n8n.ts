/**
 * n8n API 연동 유틸리티
 * n8n 워크플로우 실행 상태 및 노드별 실행 결과 조회
 */

export interface N8nWorkflowExecution {
  id: string
  workflowId: string
  mode: 'manual' | 'trigger' | 'webhook'
  finished: boolean
  retryOf?: string
  retrySuccessId?: string
  startedAt: string
  stoppedAt?: string
  status: 'success' | 'error' | 'waiting' | 'running'
  data?: {
    resultData?: {
      runData?: Record<string, N8nNodeExecution[]>
    }
  }
}

export interface N8nNodeExecution {
  startTime: number
  executionTime: number
  source: Array<{
    previousNode: string
  }>
  data?: {
    main?: Array<Array<{
      json: any
      binary?: any
    }>>
  }
  error?: {
    message: string
    description?: string
    context?: any
  }
}

export interface N8nWorkflow {
  id: string
  name: string
  active: boolean
  nodes: N8nNode[]
  connections: any
  createdAt: string
  updatedAt: string
}

export interface N8nNode {
  id: string
  name: string
  type: string
  typeVersion: number
  position: [number, number]
  parameters: any
}

export interface WorkflowExecutionSummary {
  workflowId: string
  workflowName: string
  lastExecution?: {
    id: string
    status: 'success' | 'error' | 'waiting' | 'running'
    startedAt: string
    stoppedAt?: string
    duration?: number
  }
  nodeExecutions: NodeExecutionStatus[]
  totalExecutions: number
  successRate: number
}

export interface NodeExecutionStatus {
  nodeName: string
  nodeType: string
  status: 'success' | 'error' | 'skipped' | 'running' | 'waiting'
  executionTime?: number
  itemsProcessed?: number
  error?: string
  lastExecutedAt?: string
}

/**
 * n8n API 클라이언트
 */
class N8nClient {
  private baseUrl: string
  private apiKey: string

  constructor(baseUrl?: string, apiKey?: string) {
    this.baseUrl = baseUrl || import.meta.env.VITE_N8N_URL || 'http://localhost:5678'
    this.apiKey = apiKey || import.meta.env.VITE_N8N_API_KEY || ''
  }

  private async fetch(endpoint: string, options?: RequestInit) {
    const url = `${this.baseUrl}/api/v1${endpoint}`

    const headers: Record<string, string> = {
      'X-N8N-API-KEY': this.apiKey,
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`n8n API 오류: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 워크플로우 목록 조회
   */
  async getWorkflows(): Promise<{ data: N8nWorkflow[] }> {
    return this.fetch('/workflows')
  }

  /**
   * 특정 워크플로우 조회
   */
  async getWorkflow(workflowId: string): Promise<N8nWorkflow> {
    return this.fetch(`/workflows/${workflowId}`)
  }

  /**
   * 워크플로우 실행 내역 조회
   */
  async getExecutions(workflowId?: string, limit = 20): Promise<{ data: N8nWorkflowExecution[] }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(workflowId && { workflowId }),
    })
    return this.fetch(`/executions?${params}`)
  }

  /**
   * 특정 실행 상세 조회
   */
  async getExecution(executionId: string): Promise<N8nWorkflowExecution> {
    return this.fetch(`/executions/${executionId}`)
  }

  /**
   * 워크플로우별 실행 통계 생성
   */
  async getWorkflowExecutionSummary(workflowId: string, limit = 10): Promise<WorkflowExecutionSummary> {
    const [workflow, executionsResult] = await Promise.all([
      this.getWorkflow(workflowId),
      this.getExecutions(workflowId, limit),
    ])

    const executions = executionsResult.data || []
    const lastExecution = executions[0]

    // 노드별 실행 상태 분석
    const nodeExecutions: NodeExecutionStatus[] = []

    if (lastExecution?.data?.resultData?.runData) {
      const runData = lastExecution.data.resultData.runData

      for (const [nodeName, nodeRuns] of Object.entries(runData)) {
        const node = workflow.nodes.find(n => n.name === nodeName)
        const lastRun = nodeRuns[nodeRuns.length - 1]

        nodeExecutions.push({
          nodeName,
          nodeType: node?.type || 'unknown',
          status: lastRun.error ? 'error' : 'success',
          executionTime: lastRun.executionTime,
          itemsProcessed: lastRun.data?.main?.[0]?.length || 0,
          error: lastRun.error?.message,
          lastExecutedAt: new Date(lastRun.startTime).toISOString(),
        })
      }
    }

    // 성공률 계산
    const successCount = executions.filter(e => e.status === 'success').length
    const successRate = executions.length > 0 ? (successCount / executions.length) * 100 : 0

    return {
      workflowId,
      workflowName: workflow.name,
      lastExecution: lastExecution ? {
        id: lastExecution.id,
        status: lastExecution.status,
        startedAt: lastExecution.startedAt,
        stoppedAt: lastExecution.stoppedAt,
        duration: lastExecution.stoppedAt
          ? new Date(lastExecution.stoppedAt).getTime() - new Date(lastExecution.startedAt).getTime()
          : undefined,
      } : undefined,
      nodeExecutions,
      totalExecutions: executions.length,
      successRate,
    }
  }

  /**
   * 모든 활성 워크플로우의 실행 통계 조회
   */
  async getAllWorkflowsSummary(limit = 10): Promise<WorkflowExecutionSummary[]> {
    const workflowsResult = await this.getWorkflows()
    const workflows = workflowsResult.data || []
    const activeWorkflows = workflows.filter(w => w.active)

    const summaries = await Promise.all(
      activeWorkflows.map(w => this.getWorkflowExecutionSummary(w.id, limit))
    )

    return summaries
  }
}

export const n8nClient = new N8nClient()
