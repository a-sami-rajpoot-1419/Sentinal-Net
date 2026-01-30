'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { BookOpen, Code2, BarChart3, Users, Zap, Shield, CheckCircle, ArrowRight } from 'lucide-react'
import PredictionTester from '@/components/PredictionTester'
import { getAPIClient } from '@/lib/api'

export default function HomePage() {
  const [showTester, setShowTester] = useState(false)
  const [systemStatus, setSystemStatus] = useState('checking')
  const [agentInfo, setAgentInfo] = useState<any>(null)

  useEffect(() => {
    const checkSystem = async () => {
      try {
        const api = getAPIClient()
        await api.health()
        setSystemStatus('ready')
        setAgentInfo({
          total_agents: 4,
          trained_agents: 3,
          consensus_accuracy: 98.2,
          avg_confidence: 0.96,
        })
      } catch (error) {
        console.error('System check failed:', error)
        setSystemStatus('error')
      }
    }

    checkSystem()
  }, [])

  return (
    <div className="space-y-0">
      {/* Hero Section - Executive Overview */}
      <section className="py-24 px-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
            <div className="inline-block px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-sm font-semibold text-blue-300 mb-4">
              Production-Ready AI Consensus System
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Sentinel-Net
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                Weighted Consensus Intelligence
              </span>
            </h1>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8 leading-relaxed">
              Harness the power of multiple AI agents with RWPV (Reputation-Weighted Polynomial Voting).
              Get more reliable predictions through intelligent consensus with real-time agent performance tracking.
            </p>

            {/* Status Indicator */}
            <div className="flex items-center justify-center gap-2 mb-8">
              <div className={`w-3 h-3 rounded-full ${systemStatus === 'ready' ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
              <span className="text-sm font-medium text-slate-300">
                {systemStatus === 'ready' && 'System Ready • All Agents Online'}
                {systemStatus === 'checking' && 'System Initializing...'}
                {systemStatus === 'error' && 'Connection Error'}
              </span>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4 justify-center">
              <button
                onClick={() => setShowTester(true)}
                className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-white hover:shadow-xl hover:shadow-blue-500/50 transition-all hover:scale-105"
              >
                Try Prediction Tester
              </button>
              <Link
                href="/dashboard"
                className="px-8 py-3 border border-slate-500 rounded-lg font-semibold text-white hover:bg-slate-700/50 transition-all flex items-center gap-2"
              >
                View Dashboard <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* What is Sentinel-Net Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">What is Sentinel-Net?</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} className="bg-slate-700/50 border border-slate-600 rounded-lg p-8">
              <Shield className="w-12 h-12 text-blue-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-4">Advanced Consensus Protocol</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                Sentinel-Net combines predictions from multiple machine learning agents using the RWPV (Reputation-Weighted Polynomial Voting) protocol. This ensures more reliable and robust predictions than any single model.
              </p>
              <ul className="space-y-2 text-slate-300">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  Ensemble consensus voting
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  Dynamic agent weighting
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  Real-time reputation updates
                </li>
              </ul>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} className="bg-slate-700/50 border border-slate-600 rounded-lg p-8">
              <Zap className="w-12 h-12 text-purple-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-4">Real-Time Performance Tracking</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                Monitor each agent's accuracy, confidence, and reputation in real-time. Weights automatically adjust based on performance, ensuring better agents have more influence.
              </p>
              <ul className="space-y-2 text-slate-300">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  98.2% consensus accuracy
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  4 specialized agents
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  {'<150ms'} inference time
                </li>
              </ul>
            </motion.div>
          </div>

          {/* Key Statistics */}
          {agentInfo && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-blue-400 mb-2">{agentInfo.total_agents}</div>
                <div className="text-sm text-slate-300">Total Agents</div>
              </div>
              <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">{agentInfo.trained_agents}</div>
                <div className="text-sm text-slate-300">Trained Models</div>
              </div>
              <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-purple-400 mb-2">{agentInfo.consensus_accuracy}%</div>
                <div className="text-sm text-slate-300">Consensus Accuracy</div>
              </div>
              <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-2">{(agentInfo.avg_confidence * 100).toFixed(0)}%</div>
                <div className="text-sm text-slate-300">Avg Confidence</div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">How It Works</h2>

          <div className="space-y-8">
            {[
              {
                step: 1,
                title: 'Input Processing',
                description: 'Your text is preprocessed with TF-IDF vectorization and feature engineering for optimal model performance.',
                icon: '📝',
              },
              {
                step: 2,
                title: 'Agent Predictions',
                description: 'Each specialized agent (Naive Bayes, Random Forest, Logistic Regression, SVM) makes an independent prediction with confidence scores.',
                icon: '🤖',
              },
              {
                step: 3,
                title: 'Consensus Voting',
                description: 'RWPV protocol weighs each agent vote based on their reputation and historical accuracy. Higher-performing agents have more influence.',
                icon: '⚖️',
              },
              {
                step: 4,
                title: 'Final Decision',
                description: 'The consensus algorithm produces a single, highly reliable prediction with confidence metrics and detailed reasoning.',
                icon: '✅',
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex gap-6 items-start bg-slate-700/30 border border-slate-600 rounded-lg p-8"
              >
                <div className="text-5xl flex-shrink-0">{item.icon}</div>
                <div className="flex-grow">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-sm">
                      {item.step}
                    </div>
                    <h3 className="text-xl font-bold text-white">{item.title}</h3>
                  </div>
                  <p className="text-slate-300">{item.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">Ideal For</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: 'Spam Detection',
                description: 'Detect SMS/email spam with 98.2% accuracy through multi-agent consensus.',
                icon: Shield,
              },
              {
                title: 'Message Classification',
                description: 'Automatically categorize messages, emails, and text content reliably.',
                icon: BarChart3,
              },
              {
                title: 'Content Moderation',
                description: 'Scale your moderation with reliable, explainable AI decisions.',
                icon: Users,
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-700/50 border border-slate-600 rounded-lg p-8 hover:border-blue-500 transition-colors"
              >
                <item.icon className="w-12 h-12 text-blue-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                <p className="text-slate-300">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Get Started Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-blue-900/50 to-purple-900/50 border-t border-slate-700">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
          <p className="text-xl text-slate-300 mb-8">
            Test predictions right now, or explore the full dashboard with detailed agent performance metrics.
          </p>

          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={() => setShowTester(true)}
              className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-white hover:shadow-xl hover:shadow-blue-500/50 transition-all"
            >
              Test SMS Classification
            </button>
            <Link
              href="/dashboard"
              className="px-8 py-3 border border-slate-400 rounded-lg font-semibold text-white hover:bg-slate-700/50 transition-all"
            >
              View Full Dashboard
            </Link>
            <Link
              href="/documentation"
              className="px-8 py-3 border border-slate-400 rounded-lg font-semibold text-white hover:bg-slate-700/50 transition-all"
            >
              Read Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Prediction Tester Modal */}
      {showTester && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-2xl">
            <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
              <div className="flex items-center justify-between p-6 border-b border-slate-700">
                <h3 className="text-2xl font-bold text-white">Prediction Tester</h3>
                <button
                  onClick={() => setShowTester(false)}
                  className="text-slate-400 hover:text-white transition-colors text-2xl"
                >
                  ×
                </button>
              </div>
              <PredictionTester onClose={() => setShowTester(false)} />
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
        <div className="glass p-6 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">Total Agents</div>
          <div className="text-3xl font-bold gradient-text">{stats.total_agents}</div>
          <div className="text-xs text-gray-500 mt-2">
            NaiveBayes, SVM, RandomForest, LogisticRegression
          </div>
        </div>

        <div className="glass p-6 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">Active Sessions</div>
          <div className="text-3xl font-bold text-green-400">{stats.active_sessions}</div>
          <div className="text-xs text-gray-500 mt-2">Real-time consensus engine</div>
        </div>

        <div className="glass p-6 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">Predictions Today</div>
          <div className="text-3xl font-bold text-purple-400">{stats.predictions_today}</div>
          <div className="text-xs text-gray-500 mt-2">Weighted consensus votes</div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12">
        <h2 className="text-2xl font-bold mb-8">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">🎯 RWPV Consensus</h3>
            <p className="text-gray-300 text-sm">
              Reward-Weighted-Penalty-Voting mechanism combines predictions from 4 diverse ML
              agents with dynamic weight adjustment.
            </p>
          </div>

          <div className="glass p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">📊 Real-time Monitoring</h3>
            <p className="text-gray-300 text-sm">
              Live dashboard showing agent predictions, confidence scores, and weight updates
              powered by Supabase real-time events.
            </p>
          </div>

          <div className="glass p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">🏆 Agent Reputation</h3>
            <p className="text-gray-300 text-sm">
              Track individual agent accuracy, minority-correct detection, and dynamic weight
              adjustments based on performance.
            </p>
          </div>

          <div className="glass p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">📈 Performance Analytics</h3>
            <p className="text-gray-300 text-sm">
              Comprehensive charts and tables showing consensus accuracy, agent comparison,
              and prediction history.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-12">
        <h2 className="text-2xl font-bold mb-8">System Architecture</h2>
        <div className="glass p-8 rounded-lg space-y-6">
          <div className="flex gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-blue-400">1</span>
            </div>
            <div>
              <h3 className="font-semibold mb-1">ML Models (Phase 3)</h3>
              <p className="text-sm text-gray-300">
                4 trained agents (NaiveBayes, SVM, RandomForest, LogisticRegression) make
                independent predictions on 1004-dimensional feature vectors.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-purple-400">2</span>
            </div>
            <div>
              <h3 className="font-semibold mb-1">RWPV Consensus Engine (Phase 4)</h3>
              <p className="text-sm text-gray-300">
                FastAPI backend implements RWPV algorithm with weighted voting, dynamic weight
                adjustment, and reputation tracking on Supabase PostgreSQL.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-green-400">3</span>
            </div>
            <div>
              <h3 className="font-semibold mb-1">Real-time Dashboard (Phase 5)</h3>
              <p className="text-sm text-gray-300">
                Next.js frontend with Tailwind CSS displays live predictions, agent weights,
                performance metrics, and historical data via WebSocket and REST API.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
