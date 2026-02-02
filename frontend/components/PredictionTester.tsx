"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, ArrowLeft } from "lucide-react";
import { getAPIClient } from "@/lib/api";
import EnhancedPredictionDisplay from "./EnhancedPredictionDisplay";

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

export default function PredictionTester() {
  const [smsText, setSmsText] = useState("");
  const [result, setResult] = useState<EnhancedPredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showResult, setShowResult] = useState(false);

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!smsText.trim()) {
      setError("Please enter SMS text to classify");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const api = getAPIClient();
      const response = await api.classify(smsText);
      setResult(response);
      setShowResult(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to classify message. Ensure backend is running on port 8000.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setShowResult(false);
    setTimeout(() => setResult(null), 300);
  };

  return (
    <div className="space-y-6">
      {!showResult ? (
        <>
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
                rows={4}
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
                  ? "bg-slate-700 text-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white"
              }`}
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Analyzing...
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
        </>
      ) : (
        <>
          {/* Back Button */}
          <motion.button
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={handleBack}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
          >
            <ArrowLeft size={18} />
            Back to New Classification
          </motion.button>

          {/* Enhanced Result Display */}
          {result && <EnhancedPredictionDisplay result={result} />}
        </>
      )}
    </div>
  );
}
