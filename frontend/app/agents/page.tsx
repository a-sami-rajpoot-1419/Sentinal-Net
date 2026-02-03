"use client";

import { useEffect, useState } from "react";
import { getAPIClient, AgentInfo } from "@/lib/api";

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const api = getAPIClient();
        const agentsList = await api.listAgents();
        setAgents(agentsList);
      } catch (error) {
        console.error("Failed to fetch agents:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">ML Agents</h1>
        <p className="text-gray-400">
          Overview of all available ML models in the ensemble
        </p>
      </div>

      {loading ? (
        <div className="glass p-8 rounded-lg text-center">
          <div className="spinner">Loading agents...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent) => {
            const agentName = agent.agent_name || agent.name || "Unknown";
            const isTrained = agent.is_trained ?? agent.trained ?? false;

            return (
              <div key={agentName} className="glass p-6 rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold capitalize">{agentName}</h2>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      isTrained
                        ? "bg-green-500/20 text-green-300"
                        : "bg-yellow-500/20 text-yellow-300"
                    }`}
                  >
                    {isTrained ? "Trained" : "Not Trained"}
                  </span>
                </div>

                {agent.accuracy !== undefined && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Accuracy</span>
                      <span className="font-semibold text-blue-300">
                        {(agent.accuracy * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700/50 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
                        style={{ width: `${agent.accuracy * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                {agent.total_predictions !== undefined && (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Total Predictions</div>
                      <div className="text-xl font-bold text-purple-300">
                        {agent.total_predictions}
                      </div>
                    </div>
                  </div>
                )}

                <div className="text-xs text-gray-500 italic">
                  {agentName === "naive_bayes" &&
                    "Simple probabilistic classifier based on Bayes theorem"}
                  {agentName === "svm" &&
                    "Support Vector Machine with RBF kernel for non-linear separation"}
                  {agentName === "random_forest" &&
                    "Ensemble of decision trees for robust predictions"}
                  {agentName === "logistic_regression" &&
                    "Linear classifier using logistic function"}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Architecture Info */}
      <div className="glass p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Ensemble Architecture</h2>
        <div className="space-y-4 text-sm text-gray-300">
          <p>
            All agents are trained on the same preprocessed dataset with TF-IDF
            vectorization (1000 dimensions) + 4 engineered features (1004 total
            dimensions).
          </p>
          <p>
            During prediction, all 4 agents vote independently on the class. The
            RWPV consensus engine aggregates votes using dynamic weights based
            on historical performance.
          </p>
          <p>
            Weights are adjusted in real-time based on prediction accuracy:
            <br />
            • Reward correct predictions: weight × 1.05
            <br />
            • Penalty wrong predictions: weight × 0.90
            <br />
            • Reward minority correct: weight × 1.15
            <br />• Bounds: [0.1, 5.0]
          </p>
        </div>
      </div>
    </div>
  );
}
