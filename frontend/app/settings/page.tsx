'use client'

import { useState } from 'react'
import { getAPIClient } from '@/lib/api'

export default function SettingsPage() {
  const [isResetting, setIsResetting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const handleResetWeights = async () => {
    if (!confirm('Are you sure you want to reset all agent weights to 1.0?')) {
      return
    }

    setIsResetting(true)
    try {
      const api = getAPIClient()
      await api.resetWeights()
      setSuccessMessage('Weights reset successfully!')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (error) {
      alert('Failed to reset weights: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setIsResetting(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Configure consensus engine parameters</p>
      </div>

      {successMessage && (
        <div className="glass p-4 rounded-lg border-l-4 border-green-500 bg-green-500/10">
          <p className="text-green-300 text-sm">{successMessage}</p>
        </div>
      )}

      {/* RWPV Parameters */}
      <div className="glass p-6 rounded-lg space-y-6">
        <h2 className="text-xl font-bold">RWPV Parameters</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Reward Correct</label>
              <input
                type="number"
                defaultValue="1.05"
                disabled
                className="w-full px-4 py-2 bg-gray-700/30 border border-white/10 rounded-lg text-sm disabled:opacity-50"
              />
              <p className="text-xs text-gray-500 mt-1">Multiplier when agent is correct</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Penalty Wrong</label>
              <input
                type="number"
                defaultValue="0.90"
                disabled
                className="w-full px-4 py-2 bg-gray-700/30 border border-white/10 rounded-lg text-sm disabled:opacity-50"
              />
              <p className="text-xs text-gray-500 mt-1">Multiplier when agent is wrong</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Reward Minority</label>
              <input
                type="number"
                defaultValue="1.15"
                disabled
                className="w-full px-4 py-2 bg-gray-700/30 border border-white/10 rounded-lg text-sm disabled:opacity-50"
              />
              <p className="text-xs text-gray-500 mt-1">Bonus for minority correct predictions</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Weight Range</label>
              <input
                type="text"
                defaultValue="[0.1, 5.0]"
                disabled
                className="w-full px-4 py-2 bg-gray-700/30 border border-white/10 rounded-lg text-sm disabled:opacity-50"
              />
              <p className="text-xs text-gray-500 mt-1">Min/max bounds for weights</p>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-white/10">
          <p className="text-sm text-gray-400 mb-4">
            These parameters are configured during startup and can be changed in the .env file.
          </p>
        </div>
      </div>

      {/* Agent Management */}
      <div className="glass p-6 rounded-lg space-y-6">
        <h2 className="text-xl font-bold">Agent Management</h2>

        <div className="space-y-3">
          <button
            onClick={handleResetWeights}
            disabled={isResetting}
            className="w-full px-4 py-3 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded-lg font-semibold text-red-300 transition-smooth disabled:opacity-50"
          >
            {isResetting ? 'Resetting...' : 'Reset All Weights to 1.0'}
          </button>
          <p className="text-xs text-gray-500">
            Resets all agent weights to their initial value. Use this to start fresh.
          </p>
        </div>
      </div>

      {/* Database Configuration */}
      <div className="glass p-6 rounded-lg space-y-4">
        <h2 className="text-xl font-bold">Database Configuration</h2>
        <div className="space-y-2 text-sm text-gray-300">
          <div>
            <span className="text-gray-400">Provider:</span> Supabase (PostgreSQL)
          </div>
          <div>
            <span className="text-gray-400">Project:</span> jfhbgfpuusvlreucjvmf
          </div>
          <div>
            <span className="text-gray-400">Tables:</span> sessions, consensus_results,
            weight_updates, agent_performance
          </div>
          <div>
            <span className="text-gray-400">RLS:</span> Enabled
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="glass p-6 rounded-lg border border-red-500/20 space-y-4">
        <h2 className="text-xl font-bold text-red-300">Danger Zone</h2>
        <p className="text-sm text-gray-400">
          These actions are irreversible. Please use with caution.
        </p>
        <button
          disabled
          className="px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg font-semibold text-red-300 opacity-50 cursor-not-allowed text-sm"
        >
          Clear All Data (Coming Soon)
        </button>
      </div>
    </div>
  )
}
