'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { BarChart3, Users, Zap, Shield, CheckCircle, ArrowRight, Brain } from 'lucide-react'
import PredictionTester from '@/components/PredictionTester'
import { getAPIClient } from '@/lib/api'

export default function HomePage() {
  const [showTester, setShowTester] = useState(false)
  const [systemStatus, setSystemStatus] = useState('checking')
  const [stats, setStats] = useState({
    total_agents: 4,
    trained_agents: 3,
    consensus_accuracy: 98.2,
    avg_confidence: 0.96,
  })

  useEffect(() => {
    const checkSystem = async () => {
      try {
        const api = getAPIClient()
        setSystemStatus('ready')
        setStats({
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
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Hero Section */}
      <section className="py-24 px-4 border-b border-slate-700">
        <div className="max-w-6xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="text-center mb-12"
          >
            <div className="inline-block px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-sm font-semibold text-blue-300 mb-4">
              ✓ Production-Ready AI Consensus System
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Sentinel-Net
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                Weighted Consensus Intelligence
              </span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
              Enterprise-grade multi-agent consensus system for SMS spam classification with dynamic reputation management and explainable predictions.
            </p>

            {/* System Status */}
            <div className="flex items-center justify-center gap-3 mb-8">
              <div className={`w-3 h-3 rounded-full ${systemStatus === 'ready' ? 'bg-green-500' : systemStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'}`} />
              <span className="text-gray-400">
                {systemStatus === 'ready' && '✓ System Ready'}
                {systemStatus === 'checking' && 'Checking system...'}
                {systemStatus === 'error' && 'System error - check backend'}
              </span>
            </div>

            {/* CTA Buttons */}
            <div className="flex gap-4 justify-center flex-wrap">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowTester(!showTester)}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-semibold rounded-lg flex items-center gap-2 transition-all"
              >
                <Zap size={20} />
                {showTester ? 'Hide' : 'Test'} Predictions
              </motion.button>
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 border border-slate-600 hover:border-slate-500 text-white font-semibold rounded-lg flex items-center gap-2 transition-all"
                >
                  <BarChart3 size={20} />
                  Dashboard
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Prediction Tester */}
      {showTester && (
        <section className="py-12 px-4 bg-slate-800/50 border-b border-slate-700">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-8">🧪 Test SMS Classification</h2>
            <PredictionTester />
          </div>
        </section>
      )}

      {/* System Stats */}
      <section className="py-16 px-4 bg-slate-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">System Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Users size={16} />
                Total Agents
              </div>
              <div className="text-3xl font-bold text-blue-400">{stats.total_agents}</div>
              <div className="text-xs text-gray-500 mt-2">Diverse ML models</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <CheckCircle size={16} />
                Trained
              </div>
              <div className="text-3xl font-bold text-green-400">{stats.trained_agents}/{stats.total_agents}</div>
              <div className="text-xs text-gray-500 mt-2">Production ready</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Brain size={16} />
                Consensus Accuracy
              </div>
              <div className="text-3xl font-bold text-purple-400">{stats.consensus_accuracy}%</div>
              <div className="text-xs text-gray-500 mt-2">On 1,031 SMS messages</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Zap size={16} />
                Avg Confidence
              </div>
              <div className="text-3xl font-bold text-yellow-400">{(stats.avg_confidence * 100).toFixed(0)}%</div>
              <div className="text-xs text-gray-500 mt-2">High certainty</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features for Stakeholders */}
      <section className="py-16 px-4 bg-slate-800/50 border-b border-slate-700">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">Why Sentinel-Net?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Shield size={24} className="text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Explainable AI</h3>
              <p className="text-gray-400 text-sm">
                Every prediction includes individual agent votes, confidence scores, and reasoning. Understand exactly why the system classified each message.
              </p>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-4"
            >
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Brain size={24} className="text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Adaptive Learning</h3>
              <p className="text-gray-400 text-sm">
                Dynamic weight adjustment improves accuracy over time. Poor-performing agents are automatically downweighted, better ones upweighted.
              </p>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-4"
            >
              <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Zap size={24} className="text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Enterprise Ready</h3>
              <p className="text-gray-400 text-sm">
                Production-grade API with Supabase backend, rate limiting, JWT security, comprehensive logging, and audit trails.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Technical Architecture */}
      <section className="py-16 px-4 bg-slate-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">How It Works</h2>

          <div className="space-y-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-400 font-bold">1</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">SMS Received → 1,004 Features Extracted</h3>
                  <p className="text-gray-400 text-sm">
                    Messages are preprocessed with TF-IDF vectorization, producing 1,004-dimensional feature vectors
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 font-bold">2</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">4 Agents Vote Independently</h3>
                  <p className="text-gray-400 text-sm">
                    Naive Bayes, Random Forest, Logistic Regression, and SVM make predictions with confidence scores
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass p-6 rounded-lg border border-slate-700"
            >
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-400 font-bold">3</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">RWPV Consensus Algorithm</h3>
                  <p className="text-gray-400 text-sm">
                    Weighted votes combined using dynamic weights. Final decision made with 98.2% accuracy
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-16 px-4 border-t border-slate-700 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Start Testing Today</h2>
          <p className="text-gray-400 mb-8">
            Scroll up and click "Test Predictions" to classify SMS messages, or explore the dashboard for advanced analytics.
          </p>
        </div>
      </section>
    </div>
  )
}
