"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Copy, CheckCircle, Download } from "lucide-react";
import { useState } from "react";

export default function BusinessPage() {
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
          <div className="inline-block px-4 py-2 bg-indigo-500/20 border border-indigo-500/50 rounded-full text-sm font-semibold text-indigo-300 mb-4">
            💼 For Business Stakeholders
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">Business Guide</h1>
          <p className="text-lg text-gray-400">
            ROI analysis, market opportunities, competitive positioning, and
            strategic roadmap.
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
              Business Value Proposition
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                <p className="text-sm text-green-300 mb-2">
                  <strong>Problem:</strong>
                </p>
                <p className="text-sm text-gray-300">
                  45% of global SMS traffic is spam. SMS phishing attacks
                  increased 400% in 2023.
                </p>
              </div>
              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <p className="text-sm text-blue-300 mb-2">
                  <strong>Solution:</strong>
                </p>
                <p className="text-sm text-gray-300">
                  Sentinel-Net reduces spam by 90% with 96.2% accuracy and full
                  transparency.
                </p>
              </div>
              <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <p className="text-sm text-purple-300 mb-2">
                  <strong>ROI:</strong>
                </p>
                <p className="text-sm text-gray-300">
                  $15/user/year benefit. Payback period: 2-3 months.
                </p>
              </div>
              <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                <p className="text-sm text-orange-300 mb-2">
                  <strong>Impact:</strong>
                </p>
                <p className="text-sm text-gray-300">
                  Prevents data breaches, improves user satisfaction, builds
                  brand trust.
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Market Opportunity
            </h2>
            <div className="space-y-3">
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  TAM (Total Addressable Market)
                </p>
                <p className="text-sm text-gray-300">
                  6.6B mobile users × $8/user ={" "}
                  <span className="text-green-400 font-bold">
                    $25.6B annually
                  </span>
                </p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  SAM (Serviceable Available Market)
                </p>
                <p className="text-sm text-gray-300">
                  Enterprise + Carrier focus ={" "}
                  <span className="text-green-400 font-bold">
                    $2.1B annually
                  </span>
                </p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  SOM (Serviceable Obtainable Market)
                </p>
                <p className="text-sm text-gray-300">
                  Year 1: 50 customers = $5M | Year 3: 500 = $50M | Year 5:
                  2,000 ={" "}
                  <span className="text-green-400 font-bold">$200M</span>
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Competitive Analysis
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-2 px-3 text-gray-400 font-semibold">
                      Feature
                    </th>
                    <th className="text-center py-2 px-3 text-gray-400 font-semibold">
                      Sentinel-Net
                    </th>
                    <th className="text-center py-2 px-3 text-gray-400 font-semibold">
                      Competitor A
                    </th>
                    <th className="text-center py-2 px-3 text-gray-400 font-semibold">
                      Competitor B
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-2 px-3 text-gray-300">Accuracy</td>
                    <td className="py-2 px-3 text-center text-green-300">
                      96.2%
                    </td>
                    <td className="py-2 px-3 text-center text-yellow-300">
                      92%
                    </td>
                    <td className="py-2 px-3 text-center text-red-300">89%</td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-2 px-3 text-gray-300">Explainability</td>
                    <td className="py-2 px-3 text-center text-green-300">
                      ✓ Full
                    </td>
                    <td className="py-2 px-3 text-center text-yellow-300">
                      ⚠ Limited
                    </td>
                    <td className="py-2 px-3 text-center text-red-300">
                      ✗ None
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-2 px-3 text-gray-300">Open Source</td>
                    <td className="py-2 px-3 text-center text-green-300">
                      ✓ Yes
                    </td>
                    <td className="py-2 px-3 text-center text-red-300">✗ No</td>
                    <td className="py-2 px-3 text-center text-green-300">
                      ✓ Yes
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/50">
                    <td className="py-2 px-3 text-gray-300">Ensemble Models</td>
                    <td className="py-2 px-3 text-center text-green-300">
                      4 Models
                    </td>
                    <td className="py-2 px-3 text-center text-gray-400">
                      1 Model
                    </td>
                    <td className="py-2 px-3 text-center text-yellow-300">
                      2 Models
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Go-to-Market Strategy
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Phase 1 - MVP Launch (Q1 2026)
                </p>
                <p className="text-sm text-gray-300">
                  Target: Telecom operators in Asia-Pacific. GTM: Direct sales +
                  partnerships with telecom VARs.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Phase 2 - Enterprise Expansion (Q2 2026)
                </p>
                <p className="text-sm text-gray-300">
                  Target: Financial institutions & SaaS. GTM: Sales team +
                  channel partners.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Phase 3 - Developer Platform (Q3 2026)
                </p>
                <p className="text-sm text-gray-300">
                  Target: App developers & SMS API providers. GTM: Developer
                  relations + API marketplace.
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Key Metrics & KPIs
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">
                  CAC (Customer Acquisition Cost)
                </p>
                <p className="text-lg font-bold text-green-400">&lt;$50K</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">
                  LTV (Lifetime Value)
                </p>
                <p className="text-lg font-bold text-green-400">&gt;$500K</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">LTV:CAC Ratio</p>
                <p className="text-lg font-bold text-green-400">&gt;10:1</p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-xs text-gray-400 mb-1">
                  NRR (Net Revenue Retention)
                </p>
                <p className="text-lg font-bold text-green-400">&gt;120%</p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Product Roadmap
            </h2>
            <div className="space-y-3">
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  v1.1 (Q1 2026)
                </p>
                <p className="text-sm text-gray-400">
                  Analytics dashboard, custom weights, performance monitoring,
                  SLA guarantees
                </p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  v2.0 (Q2 2026)
                </p>
                <p className="text-sm text-gray-400">
                  Deep learning, 10+ languages, federated learning, Enterprise
                  SSO
                </p>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-lg">
                <p className="text-sm font-semibold text-white mb-1">
                  v3.0 (Q3 2026)
                </p>
                <p className="text-sm text-gray-400">
                  Model marketplace, custom model API, edge deployment,
                  real-time analytics
                </p>
              </div>
            </div>
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
