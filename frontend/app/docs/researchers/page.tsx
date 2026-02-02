"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Copy, CheckCircle, Download } from "lucide-react";
import { useState } from "react";

export default function ResearchersPage() {
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
          <div className="inline-block px-4 py-2 bg-orange-500/20 border border-orange-500/50 rounded-full text-sm font-semibold text-orange-300 mb-4">
            🔬 For Researchers
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">Research Guide</h1>
          <p className="text-lg text-gray-400">
            Benchmarks, research opportunities, datasets, and academic
            resources.
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
              Benchmark Results
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">
                      Model
                    </th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">
                      Accuracy
                    </th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">
                      Precision
                    </th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">
                      Recall
                    </th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">
                      F1-Score
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">Naive Bayes</td>
                    <td className="py-3 px-4 text-center text-green-300">
                      95.8%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      94.2%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      88.3%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      91.1%
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">Random Forest</td>
                    <td className="py-3 px-4 text-center text-green-300">
                      94.1%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      92.1%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      90.5%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      91.3%
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50 hover:bg-slate-900/30">
                    <td className="py-3 px-4 text-gray-300">
                      Logistic Regression
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      92.3%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      89.8%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      87.2%
                    </td>
                    <td className="py-3 px-4 text-center text-green-300">
                      88.5%
                    </td>
                  </tr>
                  <tr className="bg-blue-500/10 border-t-2 border-blue-500/50">
                    <td className="py-3 px-4 text-blue-300 font-bold">
                      Ensemble (RWPV)
                    </td>
                    <td className="py-3 px-4 text-center text-blue-300 font-bold">
                      96.2%
                    </td>
                    <td className="py-3 px-4 text-center text-blue-300 font-bold">
                      95.1%
                    </td>
                    <td className="py-3 px-4 text-center text-blue-300 font-bold">
                      91.4%
                    </td>
                    <td className="py-3 px-4 text-center text-blue-300 font-bold">
                      93.2%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Research Opportunities
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  1. Ensemble Methods Optimization
                </p>
                <p className="text-sm text-gray-400">
                  Can we improve beyond 96.2% accuracy? Experiment with dynamic
                  weighting, meta-learners, or stacking.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  2. Adversarial Robustness
                </p>
                <p className="text-sm text-gray-400">
                  Test the ensemble against adversarial SMS samples. Generate
                  attacks and evaluate defense mechanisms.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  3. Feature Importance Analysis
                </p>
                <p className="text-sm text-gray-400">
                  Use SHAP values or permutation importance to identify which
                  text features drive spam detection.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  4. Model Calibration
                </p>
                <p className="text-sm text-gray-400">
                  Analyze if confidence scores are well-calibrated. Create
                  calibration curves and compute ECE (Expected Calibration
                  Error).
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  5. Transfer Learning
                </p>
                <p className="text-sm text-gray-400">
                  Can models trained on English SMS work for other languages?
                  Test multilingual transfer learning.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  6. Temporal Dynamics
                </p>
                <p className="text-sm text-gray-400">
                  How does spam evolution affect model performance over time?
                  Analyze concept drift.
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Dataset Information
            </h2>
            <div className="space-y-3 text-gray-300">
              <p>
                <strong>Name:</strong> SMS Spam Collection UCI
              </p>
              <p>
                <strong>Size:</strong> 5,572 messages (4,827 ham, 745 spam)
              </p>
              <p>
                <strong>Distribution:</strong> 88% ham, 12% spam
              </p>
              <p>
                <strong>Location:</strong> /data/raw/spam.csv
              </p>
              <p>
                <strong>Format:</strong> CSV with label and text columns
              </p>
              <p>
                <strong>Preprocessing:</strong> TF-IDF vectorization, 1000
                features, bigrams
              </p>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Publication Opportunities
            </h2>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span>
                  <strong>ML Conference:</strong> "Ensemble Methods for SMS
                  Classification"
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span>
                  <strong>Security Conference:</strong> "Adversarial Robustness
                  in Text Classification"
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span>
                  <strong>NLP Conference:</strong> "Feature Engineering for Spam
                  Detection"
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span>
                  <strong>Systems Conference:</strong> "Real-Time Spam Detection
                  Systems"
                </span>
              </li>
            </ul>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Academic Access
            </h2>
            <p className="text-gray-300 mb-4">
              Sentinel-Net is open for research use. Access provided subject to
              responsible use:
            </p>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>Full codebase available on GitHub (open source)</span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>
                  Datasets available with appropriate academic licensing
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>Pre-trained models available for research</span>
              </li>
              <li className="flex gap-3">
                <span className="text-green-400">✓</span>
                <span>Collaboration and consulting available</span>
              </li>
            </ul>
            <p className="text-sm text-gray-400 mt-4">
              Contact: research@sentinel-net.io
            </p>
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
