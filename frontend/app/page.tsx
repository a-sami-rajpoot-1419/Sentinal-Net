'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getAPIClient } from '@/lib/api'

export default function HomePage() {
  const [stats, setStats] = useState({
    total_agents: 4,
    active_sessions: 0,
    predictions_today: 0,
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const api = getAPIClient()
        await api.health()
        setStats({
          total_agents: 4,
          active_sessions: 1,
          predictions_today: 0,
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="py-20 text-center">
        <h1 className="text-5xl font-bold mb-6 gradient-text">
          Sentinel-Net Consensus Dashboard
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
          Real-time monitoring of RWPV-weighted consensus predictions from diverse ML agents.
          Track agent performance, weights, and reputation in one unified dashboard.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/dashboard"
            className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold hover:shadow-lg transition-smooth"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/predictions"
            className="px-8 py-3 border border-white/20 rounded-lg font-semibold hover:bg-white/5 transition-smooth"
          >
            View Predictions
          </Link>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
