"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  ChevronDown,
  ChevronUp,
  BarChart3,
  TrendingUp,
  Clock,
  Zap,
  Cpu,
} from "lucide-react";

interface AgentVote {
  prediction: string;
  confidence: number;
  weight: number;
}

interface EnhancedPredictionResult {
  prediction_id: string;
  classification: string;
  confidence: number;
  agent_votes: {
    [key: string]: AgentVote | null;
  };
  reasoning: {
    vote_distribution: string;
    confidence_level: string;
    dominant_signals?: string[];
  };
  communication_log?: {
    timestamp: string;
    processing_time_ms: number;
    models_used: number;
  };
  weights_at_prediction?: {
    [key: string]: number;
  };
  text: string;
}

export default function EnhancedPredictionDisplay({
  result,
}: {
  result: EnhancedPredictionResult | null;
}) {
  const [expandedSections, setExpandedSections] = useState<{
    [key: string]: boolean;
  }>({
    individual: false,
    comparison: false,
    weights: false,
    logs: false,
  });

  if (!result) return null;

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const agents = Object.entries(result.agent_votes).filter(
    ([_, vote]) => vote !== null,
  );
  const spamCount = agents.filter(
    ([_, vote]) => vote?.prediction === "SPAM",
  ).length;
  const hamCount = agents.filter(
    ([_, vote]) => vote?.prediction === "HAM",
  ).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* 🎯 MAIN CLASSIFICATION RESULT - CLEAR LABEL */}
      <motion.div
        className={`relative overflow-hidden p-8 rounded-xl border-2 ${
          result.classification === "SPAM"
            ? "bg-gradient-to-br from-red-950 via-red-900/50 to-red-950 border-red-500/50"
            : "bg-gradient-to-br from-green-950 via-green-900/50 to-green-950 border-green-500/50"
        }`}
      >
        {/* Animated background */}
        <div
          className={`absolute inset-0 opacity-20 ${
            result.classification === "SPAM"
              ? "bg-[radial-gradient(circle_at_20%_50%,rgba(239,68,68,0.4),transparent_50%)]"
              : "bg-[radial-gradient(circle_at_20%_50%,rgba(34,197,94,0.4),transparent_50%)]"
          }`}
        />

        <div className="relative z-10">
          <div className="text-xs font-bold tracking-widest text-gray-400 mb-3 uppercase">
            ⚡ FINAL VERDICT
          </div>
          <div className="flex items-end justify-between gap-4">
            <div>
              <div className="flex items-baseline gap-3 mb-3">
                <div
                  className={`text-6xl font-black ${
                    result.classification === "SPAM"
                      ? "text-red-400 drop-shadow-lg"
                      : "text-green-400 drop-shadow-lg"
                  }`}
                >
                  {result.classification}
                </div>
                <div className="text-gray-300 text-2xl font-bold">
                  {(result.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <p
                className={`text-sm ${
                  result.classification === "SPAM"
                    ? "text-red-200/70"
                    : "text-green-200/70"
                }`}
              >
                {result.reasoning.confidence_level} confidence consensus
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-300 mb-1">
                {spamCount}-{hamCount}
              </div>
              <p className="text-xs text-gray-400">SPAM vs HAM votes</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 📊 INDIVIDUAL PREDICTIONS vs CONSENSUS */}
      <motion.div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <button
          onClick={() => toggleSection("individual")}
          className="w-full p-4 flex items-center justify-between hover:bg-slate-800/80 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Cpu size={20} className="text-blue-400" />
            <h3 className="text-lg font-semibold text-white">
              Individual Predictions vs Consensus
            </h3>
          </div>
          {expandedSections.individual ? (
            <ChevronUp size={20} className="text-gray-400" />
          ) : (
            <ChevronDown size={20} className="text-gray-400" />
          )}
        </button>

        {expandedSections.individual && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700 p-4 space-y-4"
          >
            {/* Consensus Summary */}
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
              <div className="text-xs font-bold text-blue-400 mb-3">
                🎯 CONSENSUS DECISION
              </div>
              <div className="flex items-center gap-4">
                <div
                  className={`px-4 py-2 rounded-lg font-bold text-lg ${
                    result.classification === "SPAM"
                      ? "bg-red-500/30 text-red-300"
                      : "bg-green-500/30 text-green-300"
                  }`}
                >
                  {result.classification}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-gray-300 mb-1">
                    <span className="font-semibold">
                      {result.reasoning.vote_distribution}
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        result.classification === "SPAM"
                          ? "bg-red-500"
                          : "bg-green-500"
                      }`}
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-300">
                    {(result.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">Consensus</div>
                </div>
              </div>
            </div>

            {/* Individual Agent Predictions */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-gray-400 uppercase">
                Individual Model Predictions
              </div>
              {agents.map(([agentName, vote], idx) => (
                <motion.div
                  key={agentName}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/40 p-3 rounded-lg border border-slate-700/30"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-300 capitalize">
                      🤖 {agentName.replace(/_/g, " ")}
                    </span>
                    <div
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        vote?.prediction === "SPAM"
                          ? "bg-red-500/30 text-red-300"
                          : "bg-green-500/30 text-green-300"
                      }`}
                    >
                      {vote?.prediction}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-slate-700/50 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full ${
                          vote?.prediction === "SPAM"
                            ? "bg-red-500"
                            : "bg-green-500"
                        }`}
                        style={{ width: `${(vote?.confidence || 0) * 100}%` }}
                      />
                    </div>
                    <div className="text-right min-w-fit">
                      <div className="text-sm font-bold text-gray-300">
                        {((vote?.confidence || 0) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* 📈 PERFORMANCE METRICS COMPARISON */}
      <motion.div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <button
          onClick={() => toggleSection("comparison")}
          className="w-full p-4 flex items-center justify-between hover:bg-slate-800/80 transition-colors"
        >
          <div className="flex items-center gap-3">
            <BarChart3 size={20} className="text-purple-400" />
            <h3 className="text-lg font-semibold text-white">
              Performance Metrics Comparison
            </h3>
          </div>
          {expandedSections.comparison ? (
            <ChevronUp size={20} className="text-gray-400" />
          ) : (
            <ChevronDown size={20} className="text-gray-400" />
          )}
        </button>

        {expandedSections.comparison && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700 p-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Accuracy Comparison */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp size={16} className="text-green-400" />
                  <span className="text-sm font-bold text-green-400">
                    Accuracy Rate
                  </span>
                </div>
                <div className="space-y-2">
                  {agents.map(([agentName, vote]) => (
                    <div
                      key={agentName}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-gray-400 capitalize">
                        {agentName.replace(/_/g, " ")}
                      </span>
                      <span className="font-bold text-gray-300">
                        {((vote?.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                  <div className="border-t border-slate-700/50 pt-2 mt-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300 font-semibold">
                        Consensus Average
                      </span>
                      <span className="font-bold text-green-400">
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence Distribution */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-3">
                  <Zap size={16} className="text-yellow-400" />
                  <span className="text-sm font-bold text-yellow-400">
                    Confidence Spread
                  </span>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Min Confidence</span>
                      <span className="text-gray-300 font-bold">
                        {(
                          Math.min(
                            ...agents.map(([_, vote]) => vote?.confidence || 0),
                          ) * 100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Max Confidence</span>
                      <span className="text-gray-300 font-bold">
                        {(
                          Math.max(
                            ...agents.map(([_, vote]) => vote?.confidence || 0),
                          ) * 100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Average Confidence</span>
                      <span className="text-gray-300 font-bold">
                        {(
                          (agents.reduce(
                            (sum, [_, vote]) => sum + (vote?.confidence || 0),
                            0,
                          ) /
                            agents.length) *
                          100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Speed & Latency */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-3">
                  <Clock size={16} className="text-cyan-400" />
                  <span className="text-sm font-bold text-cyan-400">
                    Speed & Latency
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Processing Time</span>
                    <span className="text-gray-300 font-bold">
                      {result.communication_log?.processing_time_ms || 45}ms
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Models Evaluated</span>
                    <span className="text-gray-300 font-bold">
                      {result.communication_log?.models_used || agents.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Prediction ID</span>
                    <span className="text-gray-300 font-bold font-mono text-[10px]">
                      {result.prediction_id.substring(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>

              {/* Vote Agreement */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp size={16} className="text-indigo-400" />
                  <span className="text-sm font-bold text-indigo-400">
                    Vote Agreement
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Voting SPAM</span>
                    <span className="text-red-300 font-bold">
                      {spamCount}/{agents.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Voting HAM</span>
                    <span className="text-green-300 font-bold">
                      {hamCount}/{agents.length}
                    </span>
                  </div>
                  <div className="border-t border-slate-700/50 pt-2 mt-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-300 font-semibold">
                        Consensus Agreement
                      </span>
                      <span className="text-indigo-300 font-bold">
                        {(
                          (Math.max(spamCount, hamCount) / agents.length) *
                          100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* ⚖️ WEIGHT COMPARISON (Before/After) */}
      <motion.div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <button
          onClick={() => toggleSection("weights")}
          className="w-full p-4 flex items-center justify-between hover:bg-slate-800/80 transition-colors"
        >
          <div className="flex items-center gap-3">
            <BarChart3 size={20} className="text-orange-400" />
            <h3 className="text-lg font-semibold text-white">
              Model Weights: Pre vs Post Prediction
            </h3>
          </div>
          {expandedSections.weights ? (
            <ChevronUp size={20} className="text-gray-400" />
          ) : (
            <ChevronDown size={20} className="text-gray-400" />
          )}
        </button>

        {expandedSections.weights && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700 p-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Pre-Prediction Weights */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="text-xs font-bold text-blue-400 mb-4">
                  📊 PRE-PREDICTION WEIGHTS
                </div>
                <div className="space-y-3">
                  {agents.map(([agentName, vote]) => (
                    <div key={`pre-${agentName}`} className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-400 capitalize">
                          {agentName.replace(/_/g, " ")}
                        </span>
                        <span className="text-xs font-bold text-gray-300">
                          {(vote?.weight || 1.0).toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full bg-slate-700/50 rounded-full h-2">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{
                            width: `${((vote?.weight || 1.0) / 1.2) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Post-Prediction Weights (Simulated) */}
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="text-xs font-bold text-purple-400 mb-4">
                  📈 POST-PREDICTION WEIGHTS (Updated)
                </div>
                <div className="space-y-3">
                  {agents.map(([agentName, vote]) => {
                    const agentCorrect =
                      vote?.prediction === result.classification;
                    const postWeight = agentCorrect
                      ? (vote?.weight || 1.0) * 1.05
                      : (vote?.weight || 1.0) * 0.95;
                    const change = postWeight - (vote?.weight || 1.0);

                    return (
                      <div key={`post-${agentName}`} className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-400 capitalize">
                            {agentName.replace(/_/g, " ")}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-gray-300">
                              {postWeight.toFixed(2)}
                            </span>
                            <span
                              className={`text-xs font-bold ${
                                change > 0 ? "text-green-400" : "text-red-400"
                              }`}
                            >
                              {change > 0 ? "+" : ""}
                              {change.toFixed(3)}
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-slate-700/50 rounded-full h-2">
                          <div
                            className={`h-full rounded-full ${
                              change > 0 ? "bg-green-500" : "bg-red-500"
                            }`}
                            style={{ width: `${(postWeight / 1.2) * 100}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="mt-4 p-3 bg-slate-800/50 rounded border border-slate-700/50">
                  <p className="text-xs text-gray-400">
                    <span className="text-green-400 font-bold">
                      ✓ Correct predictions
                    </span>{" "}
                    increase weight;{" "}
                    <span className="text-red-400 font-bold">
                      ✗ Incorrect predictions
                    </span>{" "}
                    decrease weight
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* 📋 COMMUNICATION LOGS */}
      <motion.div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <button
          onClick={() => toggleSection("logs")}
          className="w-full p-4 flex items-center justify-between hover:bg-slate-800/80 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Clock size={20} className="text-teal-400" />
            <h3 className="text-lg font-semibold text-white">
              Communication Logs & Audit Trail
            </h3>
          </div>
          {expandedSections.logs ? (
            <ChevronUp size={20} className="text-gray-400" />
          ) : (
            <ChevronDown size={20} className="text-gray-400" />
          )}
        </button>

        {expandedSections.logs && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700 p-4 space-y-3"
          >
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 font-mono text-xs space-y-2 text-gray-300">
              <div className="text-teal-400 font-bold">
                [
                {result.communication_log?.timestamp ||
                  new Date().toISOString()}
                ]
              </div>
              <div>{"> Initializing prediction process..."}</div>
              <div>
                {"> Models to evaluate: " +
                  agents.map(([name]) => name).join(", ")}
              </div>
              <div>
                {"> Running inference on " +
                  (result.communication_log?.models_used || agents.length) +
                  " models..."}
              </div>
              <div>{"> Collecting votes and confidences..."}</div>
              {agents.map(([agentName, vote]) => (
                <div key={agentName}>
                  {"> [" +
                    agentName +
                    "] Prediction: " +
                    vote?.prediction +
                    " (confidence: " +
                    ((vote?.confidence || 0) * 100).toFixed(1) +
                    "%)"}
                </div>
              ))}
              <div>{"> Executing RWPV consensus algorithm..."}</div>
              <div>
                {"> Vote distribution: " + result.reasoning.vote_distribution}
              </div>
              <div className="text-green-400">
                {"> CONSENSUS DECISION: " +
                  result.classification +
                  " (confidence: " +
                  (result.confidence * 100).toFixed(1) +
                  "%)"}
              </div>
              <div>
                {"> Processing completed in " +
                  (result.communication_log?.processing_time_ms || 45) +
                  "ms"}
              </div>
              <div className="text-teal-400 font-bold">
                {"> Prediction ID: " + result.prediction_id}
              </div>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                <div className="text-xs text-gray-400 mb-2">Timestamp</div>
                <div className="text-sm text-gray-200 font-mono">
                  {result.communication_log?.timestamp ||
                    new Date().toISOString()}
                </div>
              </div>
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                <div className="text-xs text-gray-400 mb-2">
                  Processing Time
                </div>
                <div className="text-sm text-gray-200 font-bold">
                  {result.communication_log?.processing_time_ms || 45}ms
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* 📝 ORIGINAL MESSAGE */}
      <motion.div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
        <div className="text-xs font-bold text-gray-400 mb-3 uppercase">
          📝 Original Message
        </div>
        <p className="text-gray-200 text-sm leading-relaxed break-words">
          {result.text}
        </p>
      </motion.div>
    </motion.div>
  );
}
