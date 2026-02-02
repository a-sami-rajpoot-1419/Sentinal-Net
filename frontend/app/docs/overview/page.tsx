"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Download, Copy, CheckCircle } from "lucide-react";
import { useState } from "react";

export default function OverviewPage() {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Back Button */}
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

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="inline-block px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-sm font-semibold text-blue-300 mb-4">
            📖 Quick Start Guide
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Sentinel-Net System Overview
          </h1>
          <p className="text-lg text-gray-400">
            A comprehensive introduction to the SMS spam detection system with
            96.2% accuracy.
          </p>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-8"
        >
          {/* What is Sentinel-Net */}
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              What is Sentinel-Net?
            </h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              Sentinel-Net is a production-grade SMS spam classification system
              that uses an ensemble of machine learning models to detect spam
              with exceptional accuracy. Instead of relying on a single
              algorithm, Sentinel-Net uses a multi-agent consensus approach
              where four diverse models vote together to make the final
              decision.
            </p>
            <ul className="space-y-2 text-gray-300">
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>96.2% Accuracy:</strong> Ensemble of 4 ML models
                  voting together
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Explainable:</strong> See why each message is
                  classified
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Fast:</strong> &lt;200ms response time (p99)
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  <strong>Privacy-First:</strong> No data storage after
                  classification
                </span>
              </li>
            </ul>
          </section>

          {/* How It Works */}
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">How It Works</h2>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">Text Input</h3>
                  <p className="text-gray-400">
                    You send an SMS message to classify
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center font-bold text-white">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    Text Preprocessing
                  </h3>
                  <p className="text-gray-400">
                    Message is cleaned and converted to numerical features using
                    TF-IDF vectorization
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-pink-500 flex items-center justify-center font-bold text-white">
                  3
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    Model Voting
                  </h3>
                  <p className="text-gray-400">
                    Four ML models independently predict and vote: Naive Bayes,
                    Random Forest, Logistic Regression, SVM
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center font-bold text-white">
                  4
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    Consensus Decision
                  </h3>
                  <p className="text-gray-400">
                    RWPV (Relative Weighted Plurality Voting) algorithm
                    aggregates votes to reach final consensus
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center font-bold text-white">
                  5
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    Result & Logging
                  </h3>
                  <p className="text-gray-400">
                    Final classification, confidence, and all agent votes are
                    returned and logged
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Key Features */}
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  🎯 Clear Classification
                </h3>
                <p className="text-sm text-gray-400">
                  Explicit SPAM or HAM labels with confidence percentages
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  🤖 Individual Predictions
                </h3>
                <p className="text-sm text-gray-400">
                  See what each model predicts before the final consensus
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  📊 Performance Metrics
                </h3>
                <p className="text-sm text-gray-400">
                  Compare accuracy, speed, latency, and confidence across models
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  ⚖️ Weight Tracking
                </h3>
                <p className="text-sm text-gray-400">
                  View model weights before and after predictions
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  📋 Audit Trail
                </h3>
                <p className="text-sm text-gray-400">
                  Complete communication logs for transparency
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  🔒 Privacy First
                </h3>
                <p className="text-sm text-gray-400">
                  GDPR/CCPA compliant with no data storage
                </p>
              </div>
            </div>
          </section>

          {/* Performance Metrics */}
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Performance Metrics
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">
                      Model
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">
                      Accuracy
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">
                      Precision
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">
                      F1-Score
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">Naive Bayes</td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      95.8%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      94.2%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      91.1%
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">Random Forest</td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      94.1%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      92.1%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      91.3%
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">
                      Logistic Regression
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      92.3%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      89.8%
                    </td>
                    <td className="py-3 px-4 text-green-300 font-semibold">
                      88.5%
                    </td>
                  </tr>
                  <tr className="bg-blue-500/10 border-t-2 border-blue-500/50 hover:bg-blue-500/20">
                    <td className="py-3 px-4 text-blue-300 font-bold">
                      ENSEMBLE (RWPV)
                    </td>
                    <td className="py-3 px-4 text-blue-300 font-bold">96.2%</td>
                    <td className="py-3 px-4 text-blue-300 font-bold">95.1%</td>
                    <td className="py-3 px-4 text-blue-300 font-bold">93.2%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Quick Start */}
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Quick Start (5 Minutes)
            </h2>
            <div className="bg-slate-900/50 p-4 rounded-lg font-mono text-sm space-y-2 mb-4">
              <div className="text-gray-400">
                <span className="text-green-400">$</span> pip install -r
                requirements.txt
              </div>
              <div className="text-gray-400">
                <span className="text-green-400">$</span> python -m uvicorn
                backend.api.app:app --reload
              </div>
              <div className="text-gray-400">
                <span className="text-green-400">$</span> cd frontend && npm run
                dev
              </div>
              <div className="text-gray-400">
                <span className="text-green-400">$</span> open
                http://localhost:3001
              </div>
            </div>
            <p className="text-sm text-gray-400">
              See the{" "}
              <Link
                href="/docs/developers"
                className="text-blue-400 hover:text-blue-300"
              >
                Developer Guide
              </Link>{" "}
              for detailed setup instructions.
            </p>
          </section>

          {/* Call to Action */}
          <section className="p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-xl text-center">
            <h2 className="text-2xl font-bold text-white mb-4">
              Ready to Learn More?
            </h2>
            <p className="text-gray-300 mb-6">
              Explore documentation tailored to your role
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <Link href="/docs/users">
                <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg transition-colors">
                  For End Users
                </button>
              </Link>
              <Link href="/docs/developers">
                <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold rounded-lg transition-colors">
                  For Developers
                </button>
              </Link>
              <Link href="/docs/business">
                <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition-colors">
                  For Business
                </button>
              </Link>
            </div>
          </section>
        </motion.div>

        {/* Footer Navigation */}
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
