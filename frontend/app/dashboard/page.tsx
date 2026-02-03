'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getAPIClient, AgentPerformance } from '@/lib/api'
import ProtectedRoute from '@/components/ProtectedRoute'

function Dashboard() {
  const [agents, setAgents] = useState<AgentPerformance[]>([])
  const [consensusLogs, setConsensuslogs] = useState<any[]>([])
  const [weightsHistory, setWeightsHistory] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const api = getAPIClient()
        const [agentsData, logsData, historyData] = await Promise.all([
          api.getReputations(),
          api.getConsensuslogs(50),
          api.getWeightsHistory(100),
        ])
        setAgents(agentsData)
        setConsensuslogs(logsData?.logs || [])
        setWeightsHistory(historyData)
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
        <div className="text-gray-300">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header with Docs Link */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-gray-400">Real-time agent performance and consensus metrics</p>
        </div>
        <Link
          href="/docs"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition text-sm"
        >
          📚 Learn System
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="glass p-4 rounded-lg border-l-4 border-red-500 bg-red-500/10">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* System Status */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-lg font-bold mb-4">System Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Backend</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span>Connected</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Database</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span>Online</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Agents Active</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-green-400"></div>
              <span>{agents.length}</span>
            </div>
          </div>
          <div>
            <div className="text-gray-400">Last Update</div>
            <div className="text-gray-300 mt-1">Just now</div>
          </div>
        </div>
      </div>

      {/* Agent Performance */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Agent Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent) => (
            <div key={agent.agent_name} className="glass p-6 rounded-lg space-y-3 border border-white/10">
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
                    style={{ width: `${Math.min(agent.accuracy * 100, 100)}%` }}
                  />
                </div>
              </div>

              <div className="space-y-1 text-xs text-gray-400 border-t border-gray-700/50 pt-3">
                <div className="flex justify-between">
                  <span>Total Predictions</span>
                  <span className="text-gray-300">{agent.total_predictions}</span>
                </div>
                <div className="flex justify-between">
                  <span>Correct</span>
                  <span className="text-gray-300">{agent.correct_predictions}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Confidence</span>
                  <span className="text-gray-300">{agent.confidence_avg.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Current Weight</span>
                  <span className="font-semibold text-blue-300">{agent.current_weight.toFixed(3)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Consensus Logs */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Recent Consensus Logs</h2>
        {consensusLogs.length === 0 ? (
          <p className="text-gray-400 text-sm">No consensus logs yet. Make predictions to see logs appear here.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700/50">
                  <th className="text-left py-2 px-3 text-gray-400">Sample ID</th>
                  <th className="text-left py-2 px-3 text-gray-400">Predicted Class</th>
                  <th className="text-left py-2 px-3 text-gray-400">Confidence</th>
                  <th className="text-left py-2 px-3 text-gray-400">Created At</th>
                </tr>
              </thead>
              <tbody>
                {consensusLogs.slice(0, 10).map((log, idx) => (
                  <tr key={idx} className="border-b border-gray-700/30 hover:bg-gray-700/10 transition">
                    <td className="py-2 px-3 text-gray-300">{log.sample_id || 'N/A'}</td>
                    <td className="py-2 px-3">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                        {log.predicted_class}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <span className="text-green-300">{(log.confidence * 100).toFixed(1)}%</span>
                    </td>
                    <td className="py-2 px-3 text-gray-500 text-xs">
                      {log.created_at ? new Date(log.created_at).toLocaleTimeString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Weight Updates History */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Weight Evolution History</h2>
        {!weightsHistory || Object.keys(weightsHistory.by_agent || {}).length === 0 ? (
          <p className="text-gray-400 text-sm">No weight updates yet. Weights will be tracked after predictions.</p>
        ) : (
          <div className="space-y-6">
            {Object.entries(weightsHistory.by_agent || {}).map(([agentName, updates]: [string, any]) => (
              <div key={agentName} className="border-l-2 border-blue-500/50 pl-4">
                <h3 className="font-semibold capitalize mb-3 text-blue-300">{agentName}</h3>
                <div className="space-y-2">
                  {(updates as any[]).slice(-5).map((update, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs bg-gray-800/30 p-2 rounded">
                      <div className="flex-1">
                        <span className="text-gray-400">{update.reason || 'Update'}</span>
                        <span className="text-gray-500 ml-2">
                          {update.previous_weight?.toFixed(3)} → {update.new_weight?.toFixed(3)}
                        </span>
                      </div>
                      <span className="text-gray-500 text-xs">
                        {update.created_at ? new Date(update.created_at).toLocaleTimeString() : ''}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="glass p-4 rounded-lg border-l-4 border-indigo-500 bg-indigo-500/10">
        <p className="text-sm text-gray-300">
          <strong>📌 Tip:</strong> All data is pulled directly from the database. Refresh the page to see updated metrics. Visit the <Link href="/docs" className="text-indigo-400 hover:underline">documentation</Link> to learn how the consensus system works.
        </p>
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
