'use client'

import { useEffect, useState } from 'react'
import { getAPIClient } from '@/lib/api'

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const api = getAPIClient()
        const history = await api.getPredictionHistory(50)
        setPredictions(history)
      } catch (error) {
        console.error('Failed to fetch predictions:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Prediction History</h1>
        <p className="text-gray-400">View all consensus predictions and agent votes</p>
      </div>

      {loading ? (
        <div className="glass p-8 rounded-lg text-center">
          <div className="spinner">Loading predictions...</div>
        </div>
      ) : predictions.length === 0 ? (
        <div className="glass p-8 rounded-lg text-center">
          <p className="text-gray-400">No predictions yet. Start making predictions from the API.</p>
        </div>
      ) : (
        <div className="glass p-6 rounded-lg overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Sample ID</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Predicted Class</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Confidence</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((pred, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4">{pred.sample_id}</td>
                  <td className="py-3 px-4 font-semibold text-blue-300">{pred.predicted_class}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-700/50 rounded h-1.5">
                        <div
                          className="bg-green-400 h-1.5 rounded transition-all"
                          style={{ width: `${pred.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">
                        {(pred.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-500 text-xs">
                    {new Date(pred.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
