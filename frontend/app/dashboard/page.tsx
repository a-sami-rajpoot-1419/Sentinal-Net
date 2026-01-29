'use client'

import { useEffect, useState } from 'react'
import { getAPIClient, AgentPerformance } from '@/lib/api'
import ProtectedRoute from '@/components/ProtectedRoute'

function Dashboard() {
  const [agents, setAgents] = useState<AgentPerformance[]>([])
  const [weights, setWeights] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const api = getAPIClient()
        const [agentsData, weightsData] = await Promise.all([
          api.getReputations(),
          api.getWeights(),
        ])
        setAgents(agentsData)
        setWeights(weightsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Consensus Dashboard</h1>
        <p className="text-gray-400">Real-time monitoring of agent predictions and weights</p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="glass p-4 rounded-lg border-l-4 border-red-500 bg-red-500/10">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Agent Performance Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent) => (
          <div key={agent.agent_name} className="glass p-6 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm capitalize">{agent.agent_name}</h3>
              <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-300">
                Active
              </span>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Accuracy</span>
                <span className="font-semibold">{(agent.accuracy * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700/50 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-400 to-purple-500 h-2 rounded-full transition-all"
                  style={{ width: `${agent.accuracy * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-2 text-xs text-gray-400">
              <div className="flex justify-between">
                <span>Predictions</span>
                <span>{agent.total_predictions}</span>
              </div>
              <div className="flex justify-between">
                <span>Correct</span>
                <span>{agent.correct_predictions}</span>
              </div>
              <div className="flex justify-between">
                <span>Confidence</span>
                <span>{agent.confidence_avg.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Weight</span>
                <span className="font-semibold text-blue-300">{agent.current_weight.toFixed(2)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Weights Table */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Current Agent Weights (RWPV)</h2>
        <div className="space-y-3">
          {Object.entries(weights).map(([agentName, weight]) => (
            <div key={agentName} className="flex items-center justify-between">
              <span className="capitalize text-sm">{agentName}</span>
              <div className="flex items-center gap-4">
                <div className="w-32 bg-gray-700/50 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min((weight / 5) * 100, 100)}%` }}
                  />
                </div>
                <span className="font-semibold w-12 text-right">{weight.toFixed(3)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Status Info */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-lg font-bold mb-4">System Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Backend</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400 pulse" />
              <span>Connected</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Database</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400 pulse" />
              <span>Online</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Agents</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              <span>{agents.length} Active</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Last Update</div>
            <div className="text-gray-300 mt-1">Just now</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  )
}
