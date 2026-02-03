'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function DocsPage() {
  const [expandedSection, setExpandedSection] = useState<string | null>('overview')

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-indigo-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Sentinel Net</h1>
          <p className="text-xl text-gray-300">
            Consensus-Based Ensemble Learning System
          </p>
        </div>

        {/* Navigation */}
        <div className="mb-8 flex gap-4">
          <Link
            href="/dashboard"
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            Back to Dashboard
          </Link>
        </div>

        {/* Documentation Sections */}
        <div className="space-y-4">
          {/* Overview */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('overview')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">📊 System Overview</h2>
              <span className="text-gray-400">{expandedSection === 'overview' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'overview' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <p>
                  Sentinel Net is a consensus-based ensemble learning system that combines predictions from multiple machine learning models to create robust classifications. The system uses weighted voting to determine the final prediction, with weights dynamically adjusted based on prediction accuracy.
                </p>
                <div className="bg-slate-800/50 p-4 rounded border-l-4 border-blue-500">
                  <h3 className="text-white font-semibold mb-2">Key Components:</h3>
                  <ul className="list-disc list-inside space-y-1">
                    <li><strong>Agents:</strong> Multiple ML models (Naive Bayes, SVM, Random Forest, Logistic Regression)</li>
                    <li><strong>Consensus Engine:</strong> Combines agent predictions using weighted voting</li>
                    <li><strong>RWPV System:</strong> Reward/Penalty Weight Update mechanism that adapts weights</li>
                    <li><strong>Dashboard:</strong> Real-time monitoring of agent performance and system status</li>
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Agents Explanation */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('agents')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">🤖 Agents</h2>
              <span className="text-gray-400">{expandedSection === 'agents' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'agents' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <p>
                  The system uses four independent machine learning agents, each trained on the same dataset but using different algorithms. Each agent provides predictions with confidence scores.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Naive Bayes</h4>
                    <p className="text-sm mt-1">Probabilistic classifier based on Bayes' theorem with independence assumptions</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Support Vector Machine (SVM)</h4>
                    <p className="text-sm mt-1">Finds optimal hyperplane for classification with strong margins</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Random Forest</h4>
                    <p className="text-sm mt-1">Ensemble of decision trees voting for the final classification</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Logistic Regression</h4>
                    <p className="text-sm mt-1">Statistical model for binary/multiclass classification</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Consensus Voting */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('consensus')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">🗳️ Consensus Voting</h2>
              <span className="text-gray-400">{expandedSection === 'consensus' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'consensus' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <p>
                  Consensus voting combines predictions from all agents using weighted voting. Each agent's vote is multiplied by its current weight, and the class with the highest total weight wins.
                </p>
                <div className="bg-slate-800/50 p-4 rounded border-l-4 border-green-500 mt-4">
                  <h3 className="text-white font-semibold mb-3">Voting Formula:</h3>
                  <code className="text-green-300 text-sm block mb-2">
                    Final Class = argmax(Σ weight[agent_i] × prediction[agent_i])
                  </code>
                  <p className="text-xs text-gray-400 mt-2">
                    The consensus confidence is calculated as the maximum weighted vote divided by the sum of all votes
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* RWPV System */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('rwpv')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">⚖️ RWPV Weight System</h2>
              <span className="text-gray-400">{expandedSection === 'rwpv' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'rwpv' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <p>
                  Reward/Penalty Weight Update (RWPV) is an adaptive system that adjusts agent weights based on their prediction accuracy. Correct predictions increase weights, incorrect predictions decrease them.
                </p>
                <div className="bg-slate-800/50 p-4 rounded mt-4 space-y-3">
                  <div className="border-l-4 border-green-500 pl-3">
                    <h4 className="text-green-300 font-semibold">Reward (Correct Prediction)</h4>
                    <p className="text-sm">weight = weight × (1 + α)</p>
                    <p className="text-xs text-gray-400">Agent weight increased by factor α (typically 0.05)</p>
                  </div>
                  <div className="border-l-4 border-red-500 pl-3">
                    <h4 className="text-red-300 font-semibold">Penalty (Wrong Prediction)</h4>
                    <p className="text-sm">weight = weight × (1 - β)</p>
                    <p className="text-xs text-gray-400">Agent weight decreased by factor β (typically 0.02)</p>
                  </div>
                  <div className="border-l-4 border-yellow-500 pl-3">
                    <h4 className="text-yellow-300 font-semibold">Minority Reward</h4>
                    <p className="text-sm">Agents who voted correctly in minority get small reward</p>
                    <p className="text-xs text-gray-400">Encourages diverse predictions</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Dashboard Guide */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('dashboard')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">📈 Dashboard Metrics</h2>
              <span className="text-gray-400">{expandedSection === 'dashboard' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'dashboard' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <p>
                  The dashboard displays real-time metrics pulled directly from the database, showing the actual performance of agents and the evolution of their weights.
                </p>
                <div className="space-y-3 mt-4">
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Agent Performance</h4>
                    <p className="text-sm mt-1">Shows accuracy, total predictions, correct predictions, and current weight for each agent</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Consensus Logs</h4>
                    <p className="text-sm mt-1">Recent prediction history with agent predictions, weights, and final consensus decision</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">Weights History</h4>
                    <p className="text-sm mt-1">Track how agent weights evolve over time based on prediction accuracy</p>
                  </div>
                  <div className="bg-slate-800/50 p-3 rounded">
                    <h4 className="text-blue-300 font-semibold">System Status</h4>
                    <p className="text-sm mt-1">Real-time connectivity status and number of active agents</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Technical Architecture */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('architecture')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">🏗️ Architecture</h2>
              <span className="text-gray-400">{expandedSection === 'architecture' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'architecture' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <div className="bg-slate-800/50 p-4 rounded">
                  <h4 className="text-white font-semibold mb-3">System Stack:</h4>
                  <ul className="space-y-2 text-sm">
                    <li><strong>Backend:</strong> FastAPI (Python) with async HTTP REST API</li>
                    <li><strong>Database:</strong> Supabase PostgreSQL for persistence and logging</li>
                    <li><strong>Frontend:</strong> Next.js 14 with React for real-time UI updates</li>
                    <li><strong>Auth:</strong> JWT-based authentication with Supabase</li>
                    <li><strong>ML Models:</strong> scikit-learn for all agent implementations</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 p-4 rounded mt-4">
                  <h4 className="text-white font-semibold mb-3">Data Flow:</h4>
                  <ol className="space-y-2 text-sm list-decimal list-inside">
                    <li>User submits features or text for classification</li>
                    <li>Backend sends features to all 4 agents simultaneously</li>
                    <li>Agents return individual predictions with confidence scores</li>
                    <li>Consensus engine applies weighted voting</li>
                    <li>Results logged to database with weights and metrics</li>
                    <li>Dashboard fetches real-time data to display system state</li>
                  </ol>
                </div>
              </div>
            )}
          </div>

          {/* Getting Started */}
          <div className="glass p-6 rounded-lg border border-white/20">
            <button
              onClick={() => toggleSection('started')}
              className="w-full flex items-center justify-between hover:opacity-80 transition"
            >
              <h2 className="text-2xl font-bold text-white">🚀 Getting Started</h2>
              <span className="text-gray-400">{expandedSection === 'started' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'started' && (
              <div className="mt-4 text-gray-300 space-y-4">
                <ol className="list-decimal list-inside space-y-3">
                  <li>
                    <strong>Dashboard:</strong> Visit the{' '}
                    <Link href="/dashboard" className="text-blue-400 hover:underline">
                      Dashboard
                    </Link>{' '}
                    to see real-time agent performance and consensus predictions
                  </li>
                  <li>
                    <strong>Agents Page:</strong> Check individual agent statistics and accuracy metrics
                  </li>
                  <li>
                    <strong>Make Predictions:</strong> Use the prediction endpoint to classify new samples
                  </li>
                  <li>
                    <strong>Monitor Logs:</strong> View consensus logs and weight history in the dashboard
                  </li>
                </ol>
                <div className="bg-blue-900/30 p-4 rounded border-l-4 border-blue-500 mt-4">
                  <p className="text-sm">
                    <strong>Tip:</strong> Refresh the dashboard to see updated metrics. The system continuously learns and adapts weights based on prediction accuracy.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-white/20 text-center text-gray-400">
          <p>Sentinel Net - Consensus-Based Ensemble Learning System</p>
          <p className="text-sm mt-2">Built with FastAPI, Next.js, and Supabase</p>
        </div>
      </div>
    </div>
  )
}
