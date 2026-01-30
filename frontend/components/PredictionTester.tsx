'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Loader2 } from 'lucide-react'
import { getAPIClient } from '@/lib/api'

interface PredictionResult {
  prediction: string
  confidence: number
  agent_votes: {
    [key: string]: {
      vote: string
      confidence: number
    }
  }
  message: string
}

export default function PredictionTester() {
  const [smsText, setSmsText] = useState('')
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!smsText.trim()) {
      setError('Please enter SMS text to classify')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const api = getAPIClient()
      const classificationResult = await api.classify(smsText)
      setResult(classificationResult)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to classify message. Ensure backend is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <motion.form onSubmit={handleClassify} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Enter SMS Message:
          </label>
          <textarea
            value={smsText}
            onChange={(e) => setSmsText(e.target.value)}
            placeholder="Paste an SMS message here to classify it as SPAM or HAM..."
            className="w-full p-4 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            disabled={loading}
          />
        </div>

        <motion.button
          whileHover={{ scale: loading ? 1 : 1.02 }}
          whileTap={{ scale: loading ? 1 : 0.98 }}
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            loading
              ? 'bg-slate-700 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white'
          }`}
        >
          {loading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              Classifying...
            </>
          ) : (
            <>
              <Send size={20} />
              Classify Message
            </>
          )}
        </motion.button>
      </motion.form>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm"
        >
          ⚠️ {error}
        </motion.div>
      )}

      {/* Result Display */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Main Prediction */}
          <div
            className={`p-6 rounded-lg border-2 ${
              result.prediction === 'SPAM'
                ? 'bg-red-500/10 border-red-500/50'
                : 'bg-green-500/10 border-green-500/50'
            }`}
          >
            <div className="text-sm font-medium text-gray-400 mb-2">FINAL CLASSIFICATION</div>
            <div className="flex items-baseline gap-3">
              <span
                className={`text-4xl font-bold ${
                  result.prediction === 'SPAM' ? 'text-red-400' : 'text-green-400'
                }`}
              >
                {result.prediction}
              </span>
              <span className="text-2xl font-semibold text-gray-300">
                {(result.confidence * 100).toFixed(1)}% confident
              </span>
            </div>
          </div>

          {/* Individual Agent Votes */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Agent Votes (Consensus Ensemble):</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(result.agent_votes).map(([agent, vote], idx) => (
                <motion.div
                  key={agent}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="p-4 bg-slate-800 border border-slate-600 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-300 capitalize">
                      {agent.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${
                        vote.vote === 'SPAM'
                          ? 'bg-red-500/30 text-red-300'
                          : 'bg-green-500/30 text-green-300'
                      }`}
                    >
                      {vote.vote}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          vote.vote === 'SPAM'
                            ? 'bg-red-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${vote.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-400 w-12 text-right">
                      {(vote.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Original Message */}
          <div className="p-4 bg-slate-800/50 border border-slate-600 rounded-lg">
            <div className="text-xs font-medium text-gray-400 mb-2">ORIGINAL MESSAGE</div>
            <p className="text-gray-200 text-sm break-words">{result.message}</p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
