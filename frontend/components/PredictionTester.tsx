'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Loader2, BarChart3 } from 'lucide-react'
import { getAPIClient } from '@/lib/api'

interface PredictionResult {
  prediction_id: string
  classification: string
  confidence: number
  agent_votes: Record<string, any>
  timestamp: string
}

export default function PredictionTester({ onClose }: { onClose: () => void }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState('')

  const handlePredict = async () => {
    if (!text.trim()) {
      setError('Please enter some text to classify')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const api = getAPIClient()
      const response = await api.classify(text)
      setResult(response)
    } catch (err: any) {
      setError(err.message || 'Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 space-y-6">
      {!result ? (
        <>
          <div className="space-y-3">
            <label className="block text-sm font-semibold text-white">Enter SMS Message</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter a message to classify as SPAM or HAM..."
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 min-h-24"
            />
          </div>

          {error && <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">{error}</div>}

          <button
            onClick={handlePredict}
            disabled={loading || !text.trim()}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-white hover:shadow-xl hover:shadow-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            {loading ? 'Classifying...' : 'Classify Message'}
          </button>
        </>
      ) : (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Overall Prediction */}
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Consensus Prediction</h3>
              <span
                className={`px-4 py-2 rounded-full font-bold text-white ${
                  result.classification === 'SPAM'
                    ? 'bg-red-500/30 border border-red-500'
                    : 'bg-green-500/30 border border-green-500'
                }`}
              >
                {result.classification}
              </span>
            </div>
            <div className="text-slate-300 mb-4 text-sm">
              <p className="mb-2">
                <strong>Message:</strong> {text}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="text-sm text-slate-300 mb-2">Confidence Score</div>
                <div className="w-full bg-slate-600 rounded-full h-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${result.confidence * 100}%` }}
                    transition={{ duration: 0.5 }}
                    className={`h-full ${
                      result.confidence > 0.8
                        ? 'bg-gradient-to-r from-green-500 to-green-400'
                        : result.confidence > 0.6
                        ? 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                        : 'bg-gradient-to-r from-orange-500 to-orange-400'
                    }`}
                  ></motion.div>
                </div>
              </div>
              <div className="text-2xl font-bold text-white">{(result.confidence * 100).toFixed(1)}%</div>
            </div>
          </div>

          {/* Individual Agent Votes */}
          <div>
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Individual Agent Predictions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(result.agent_votes).map(([agent, vote]: [string, any]) => (
                <motion.div
                  key={agent}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-slate-700/50 border border-slate-600 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="font-semibold text-white capitalize">{agent.replace(/_/g, ' ')}</div>
                      <div className="text-sm text-slate-400">Agent Prediction</div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-bold ${
                        vote.prediction === 'SPAM'
                          ? 'bg-red-500/30 text-red-300'
                          : 'bg-green-500/30 text-green-300'
                      }`}
                    >
                      {vote.prediction}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Confidence:</span>
                      <span className="text-white font-semibold">{(vote.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Agent Weight:</span>
                      <span className="text-blue-300 font-semibold">{(vote.weight * 100).toFixed(1)}%</span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-600">
                      <div className="text-xs text-slate-400 mb-1">Weight Distribution</div>
                      <div className="w-full bg-slate-600 rounded-full h-2">
                        <div
                          style={{ width: `${vote.weight * 100}%` }}
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                        ></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* How Consensus Works */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-blue-300 mb-2">How This Decision Was Made</h4>
            <p className="text-sm text-slate-300">
              Each of the 4 agents made an independent prediction. The RWPV (Reputation-Weighted Polynomial Voting) algorithm combined these votes by weighing each agent's contribution based on their historical accuracy and reputation. Higher-performing agents have greater influence on the final decision.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => setResult(null)}
              className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold text-white transition-colors"
            >
              Test Another Message
            </button>
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold text-white transition-colors"
            >
              Close
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
