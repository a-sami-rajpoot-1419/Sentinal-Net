"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Download, Copy, CheckCircle } from "lucide-react";
import { useState } from "react";

export default function UsersPage() {
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
          <div className="inline-block px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-full text-sm font-semibold text-green-300 mb-4">
            👥 For End Users
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            User Guide: Understanding Sentinel-Net
          </h1>
          <p className="text-lg text-gray-400">
            Simple explanations of how to use Sentinel-Net and what your results
            mean.
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
              Understanding Your Classification Results
            </h2>
            <div className="space-y-4 text-gray-300">
              <p>
                When you send an SMS to Sentinel-Net, you'll receive a clear
                result showing:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <h3 className="font-semibold text-red-300 mb-2">🚫 SPAM</h3>
                  <p className="text-sm">
                    Likely to be a scam, phishing attempt, or unwanted
                    promotional message. Be cautious clicking any links.
                  </p>
                </div>
                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <h3 className="font-semibold text-green-300 mb-2">✓ HAM</h3>
                  <p className="text-sm">
                    Legitimate message from a real person or trusted service.
                    Safe to read and respond to.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              What Do These Percentages Mean?
            </h2>
            <div className="space-y-3 text-gray-300">
              <p className="mb-4">
                Each result includes confidence percentages. Here's what they
                mean:
              </p>
              <div className="bg-slate-900/50 p-4 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Confidence Score: 95%
                </p>
                <p className="text-sm">
                  This means the system is 95% confident in its decision. Higher
                  percentages = more reliable predictions.
                </p>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-lg">
                <p className="font-semibold text-white mb-2">What's Good?</p>
                <ul className="text-sm space-y-1">
                  <li>
                    • <span className="text-green-400">90-100%:</span> Very
                    confident - trust this result
                  </li>
                  <li>
                    • <span className="text-yellow-400">70-89%:</span> Confident
                    - likely correct
                  </li>
                  <li>
                    • <span className="text-red-400">Below 70%:</span> Less
                    certain - use with caution
                  </li>
                </ul>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Privacy & Data Safety
            </h2>
            <div className="space-y-4 text-gray-300">
              <div className="flex gap-3">
                <span className="text-green-400 font-bold">✓</span>
                <div>
                  <p className="font-semibold text-white">No Data Storage</p>
                  <p className="text-sm">
                    Your SMS text is never saved. It's analyzed and then deleted
                    immediately.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-green-400 font-bold">✓</span>
                <div>
                  <p className="font-semibold text-white">
                    Encrypted Transmission
                  </p>
                  <p className="text-sm">
                    All messages are encrypted when sent between your device and
                    our servers.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-green-400 font-bold">✓</span>
                <div>
                  <p className="font-semibold text-white">
                    GDPR & CCPA Compliant
                  </p>
                  <p className="text-sm">
                    We comply with international privacy laws. You have the
                    right to delete your data anytime.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-green-400 font-bold">✓</span>
                <div>
                  <p className="font-semibold text-white">
                    No Third-Party Sharing
                  </p>
                  <p className="text-sm">
                    Your data is never sold or shared with any third parties.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Frequently Asked Questions
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Q: Is the system always right?
                </p>
                <p className="text-sm text-gray-400">
                  A: No system is perfect. Sentinel-Net is 96.2% accurate on
                  average, but occasional mistakes happen. It's designed to
                  catch the vast majority of spam.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Q: Can I report a misclassification?
                </p>
                <p className="text-sm text-gray-400">
                  A: Yes! Feedback helps the system improve. Every time you mark
                  a result as incorrect, we use that to refine our models.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Q: Why does it take 200ms sometimes?
                </p>
                <p className="text-sm text-gray-400">
                  A: Sentinel-Net runs 4 ML models in parallel to ensure
                  accuracy. 200ms is still very fast for such thorough analysis.
                </p>
              </div>
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-semibold text-white mb-2">
                  Q: What data do you keep?
                </p>
                <p className="text-sm text-gray-400">
                  A: We only keep: your classification (spam/ham), confidence
                  score, and timestamp. Never the actual message text.
                </p>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">
              Tips for Best Results
            </h2>
            <ol className="space-y-3 text-gray-300">
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white text-sm">
                  1
                </span>
                <span>
                  <strong>Use complete messages:</strong> Longer messages help
                  the system understand context better
                </span>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white text-sm">
                  2
                </span>
                <span>
                  <strong>Watch for red flags:</strong> URLs, offers, urgency -
                  these are common spam indicators
                </span>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white text-sm">
                  3
                </span>
                <span>
                  <strong>Trust the consensus:</strong> When multiple models
                  agree, it's more reliable
                </span>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white text-sm">
                  4
                </span>
                <span>
                  <strong>Report misclassifications:</strong> Your feedback
                  helps improve accuracy for everyone
                </span>
              </li>
            </ol>
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
