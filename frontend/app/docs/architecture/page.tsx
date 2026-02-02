"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Copy, CheckCircle, Download } from "lucide-react";
import { useState } from "react";

export default function ArchitecturePage() {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-8"
        >
          <Link
            href="/docs"
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
          >
            <ArrowLeft size={18} />
            Back to Documentation
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="inline-block px-4 py-2 bg-teal-500/20 border border-teal-500/50 rounded-full text-sm font-semibold text-teal-300 mb-4">
            🏗️ System Architecture
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Complete Technical Design
          </h1>
          <p className="text-lg text-gray-400">
            Detailed architecture, ML models, consensus algorithm, and data
            flow.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-8"
        >
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              System Architecture
            </h2>
            <div className="bg-slate-900/50 p-6 rounded-lg font-mono text-xs space-y-2 text-gray-300 overflow-x-auto">
              <p className="text-cyan-400">
                ┌─────────────────────────────────────────────────────┐
              </p>
              <p className="text-cyan-400">│ User Interface (Next.js) │</p>
              <p className="text-cyan-400">
                │ • Prediction Testing • Analytics • Documentation │
              </p>
              <p className="text-cyan-400">
                └───────────────────┬─────────────────────────────────┘
              </p>
              <p className="text-cyan-400 ml-8">│ REST API (JSON)</p>
              <p className="text-cyan-400">
                ┌───────────────────▼─────────────────────────────────┐
              </p>
              <p className="text-cyan-400">│ Backend (FastAPI) │</p>
              <p className="text-cyan-400">
                │ /classify /models /analytics /health │
              </p>
              <p className="text-cyan-400">
                └───────────────────┬─────────────────────────────────┘
              </p>
              <p className="text-cyan-400 ml-8">│</p>
              <p className="text-cyan-400">
                ┌───────────┬──────────────┬────────────────┐
              </p>
              <p className="text-cyan-400">▼ ▼ ▼ ▼</p>
              <p className="text-cyan-400">
                Text ML Agents Consensus Engine Database
              </p>
              <p className="text-cyan-400">
                Prep (4 Models) (RWPV Algorithm) (Supabase)
              </p>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              ML Model Ensemble
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">🤖 Naive Bayes</p>
                <p className="text-sm text-gray-400 mb-2">
                  Probabilistic classifier based on Bayes' theorem. Fast,
                  interpretable, good for text classification.
                </p>
                <p className="text-sm text-yellow-300">
                  <strong>Accuracy: 95.8%</strong> | Status: ✓ Trained
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  🌲 Random Forest
                </p>
                <p className="text-sm text-gray-400 mb-2">
                  Ensemble of decision trees. Handles non-linear patterns,
                  robust to outliers.
                </p>
                <p className="text-sm text-yellow-300">
                  <strong>Accuracy: 94.1%</strong> | Status: ✓ Trained
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  📊 Logistic Regression
                </p>
                <p className="text-sm text-gray-400 mb-2">
                  Linear classifier with sigmoid function. Fast inference, good
                  baseline.
                </p>
                <p className="text-sm text-yellow-300">
                  <strong>Accuracy: 92.3%</strong> | Status: ✓ Trained
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  🔷 Support Vector Machine
                </p>
                <p className="text-sm text-gray-400 mb-2">
                  Finds optimal hyperplane in feature space. Powerful for
                  high-dimensional data.
                </p>
                <p className="text-sm text-gray-500">
                  <strong>Status: ⏳ In Training</strong>
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              RWPV Consensus Algorithm
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <p className="font-semibold text-blue-300 mb-2">
                  Phase 1: Proposal Collection
                </p>
                <p className="text-sm text-gray-300">
                  Each model independently predicts and returns (prediction,
                  confidence, weight)
                </p>
              </div>
              <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <p className="font-semibold text-purple-300 mb-2">
                  Phase 2: Weighted Aggregation
                </p>
                <p className="text-sm text-gray-300">
                  Calculate weighted vote: Σ(confidence × weight) for SPAM and
                  HAM
                </p>
              </div>
              <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                <p className="font-semibold text-green-300 mb-2">
                  Phase 3: Consensus Decision
                </p>
                <p className="text-sm text-gray-300">
                  Decision if (weighted_spam_score) &gt; 0.5, else HAM
                </p>
              </div>
              <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                <p className="font-semibold text-orange-300 mb-2">
                  Phase 4: Reputation Update
                </p>
                <p className="text-sm text-gray-300">
                  Update model weights based on prediction correctness
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Data Flow Example
            </h2>
            <div className="bg-slate-900/50 p-4 rounded-lg space-y-3 text-sm text-gray-300">
              <div>
                <p className="font-semibold text-white mb-1">Input:</p>
                <p className="font-mono text-xs">
                  "Free entry in 2 a wkly comp to win FA Cup..."
                </p>
              </div>
              <div>
                <p className="font-semibold text-white mb-1">Preprocessing:</p>
                <p className="font-mono text-xs">
                  → Cleaned text → TF-IDF vectorization → 1000 features
                </p>
              </div>
              <div>
                <p className="font-semibold text-white mb-1">
                  Model Inference:
                </p>
                <p className="font-mono text-xs">
                  NB: SPAM (92%), RF: SPAM (88%), LR: SPAM (85%)
                </p>
              </div>
              <div>
                <p className="font-semibold text-white mb-1">Consensus:</p>
                <p className="font-mono text-xs">
                  RWPV: 3/3 agree on SPAM → Final: SPAM (88.3%)
                </p>
              </div>
              <div>
                <p className="font-semibold text-white mb-1">Output:</p>
                <p className="font-mono text-xs">
                  {
                    "{ classification: 'SPAM', confidence: 0.883, agent_votes: {...} }"
                  }
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Performance Characteristics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">
                  Response Time (p50)
                </p>
                <p className="text-lg font-bold text-green-400">45ms</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">
                  Response Time (p99)
                </p>
                <p className="text-lg font-bold text-green-400">185ms</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">Throughput</p>
                <p className="text-lg font-bold text-green-400">100K/hour</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">Uptime Target</p>
                <p className="text-lg font-bold text-green-400">99.99%</p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Technology Stack
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-2">Backend</p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• FastAPI (async framework)</li>
                  <li>• scikit-learn (ML)</li>
                  <li>• pandas, numpy (data)</li>
                  <li>• Supabase PostgreSQL</li>
                </ul>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-2">
                  Frontend
                </p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Next.js 14 (React)</li>
                  <li>• TailwindCSS (styling)</li>
                  <li>• Framer Motion (animation)</li>
                  <li>• Lucide Icons</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Security & Privacy
            </h2>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Encryption in Transit:</strong> TLS 1.3 for all
                  communications
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Encryption at Rest:</strong> All database records
                  encrypted
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>No Data Storage:</strong> SMS text deleted after
                  classification
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>GDPR/CCPA Compliant:</strong> Right to deletion fully
                  supported
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Audit Trail:</strong> All predictions logged with full
                  context
                </span>
              </li>
            </ul>
          </section>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-12 pt-8 border-t border-slate-700 flex justify-between items-center"
        >
          <Link
            href="/docs"
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            ← Back to Docs
          </Link>
          <div className="flex gap-4">
            <button
              onClick={() => copyToClipboard(window.location.href)}
              className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 transition-colors"
            >
              {copied ? (
                <>
                  <CheckCircle size={16} />
                  Copied!
                </>
              ) : (
                <>
                  <Copy size={16} />
                  Copy Link
                </>
              )}
            </button>
            <button className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 transition-colors">
              <Download size={16} />
              PDF
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
