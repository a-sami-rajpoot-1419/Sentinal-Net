'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowLeft, Copy, CheckCircle, Download } from 'lucide-react'
import { useState } from 'react'

export default function DevelopersPage() {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="mb-8">
          <Link href="/docs" className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
            <ArrowLeft size={18} />
            Back to Documentation
          </Link>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <div className="inline-block px-4 py-2 bg-purple-500/20 border border-purple-500/50 rounded-full text-sm font-semibold text-purple-300 mb-4">
            👨‍💻 For Developers
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">Developer Guide</h1>
          <p className="text-lg text-gray-400">
            Complete API reference, setup, deployment, and extension guidelines.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="space-y-8">
          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Quick Start Setup</h2>
            <div className="bg-slate-900/50 p-4 rounded-lg font-mono text-sm space-y-2 mb-4">
              <div>
                <span className="text-green-400"># 1. Clone and setup backend</span>
              </div>
              <div className="text-gray-400">
                git clone https://github.com/your-org/sentinel-net.git
              </div>
              <div className="text-gray-400">
                cd sentinel-net
              </div>
              <div className="text-gray-400">
                python -m venv .venv
              </div>
              <div className="text-gray-400">
                source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
              </div>
              <div className="text-gray-400">
                pip install -r requirements.txt
              </div>
              <div className="mt-4 text-green-400"># 2. Start backend</div>
              <div className="text-gray-400">
                python -m uvicorn backend.api.app:app --reload
              </div>
              <div className="mt-4 text-green-400"># 3. Start frontend</div>
              <div className="text-gray-400">
                cd frontend && npm install && npm run dev
              </div>
            </div>
            <p className="text-sm text-gray-400">Backend runs on http://localhost:8000, Frontend on http://localhost:3001</p>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">API Reference</h2>
            <div className="space-y-4">
              <div className="p-4 bg-slate-900/50 rounded-lg">
                <p className="font-mono text-sm text-green-400 mb-2">POST /classify/text</p>
                <p className="text-sm text-gray-300 mb-3">Classify an SMS message</p>
                <p className="text-xs text-gray-400 mb-2">Request:</p>
                <div className="bg-black/50 p-2 rounded text-xs font-mono text-gray-300 mb-3 overflow-x-auto">
                  {'{\n  "text": "Free entry in 2 a wkly comp...",\n  "ground_truth": null\n}'}
                </div>
                <p className="text-xs text-gray-400 mb-2">Response:</p>
                <div className="bg-black/50 p-2 rounded text-xs font-mono text-gray-300 overflow-x-auto">
                  {'{\n  "prediction_id": "uuid",\n  "classification": "SPAM",\n  "confidence": 0.883,\n  "agent_votes": {...},\n  "reasoning": {...},\n  "timestamp": "2026-02-02T14:30:45Z"\n}'}
                </div>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Python Client Example</h2>
            <div className="bg-slate-900/50 p-4 rounded-lg font-mono text-sm space-y-2">
              <div className="text-purple-300">import requests</div>
              <div className="text-gray-400">
                <br />
                response = requests.post(
              </div>
              <div className="text-gray-400 ml-4">
                "http://localhost:8000/classify/text",
              </div>
              <div className="text-gray-400 ml-4">
                json={"{"} "text": "Your SMS here" {"}"}
              </div>
              <div className="text-gray-400">
                )
              </div>
              <div className="text-gray-400">
                <br />
                {`result = response.json()`}
              </div>
              <div className="text-gray-400">
                {`print(f"Classification: {result['classification']}`}
              </div>
              <div className="text-gray-400">
                {`print(f"Confidence: {result['confidence']:.1%}`}
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Environment Variables</h2>
            <div className="space-y-2 text-sm text-gray-300 font-mono">
              <p><span className="text-blue-300">SUPABASE_URL</span>=your-supabase-project-url</p>
              <p><span className="text-blue-300">SUPABASE_KEY</span>=your-supabase-api-key</p>
              <p><span className="text-blue-300">LOG_LEVEL</span>=INFO</p>
              <p className="mt-4 text-gray-400">See .env.example for complete configuration</p>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Project Structure</h2>
            <div className="bg-slate-900/50 p-4 rounded-lg font-mono text-xs text-gray-300 space-y-1">
              <p>sentinel-net/</p>
              <p className="ml-4">├── backend/</p>
              <p className="ml-8">│   ├── api/              # FastAPI app</p>
              <p className="ml-8">│   ├── models/           # ML agents</p>
              <p className="ml-8">│   ├── consensus/        # Voting engine</p>
              <p className="ml-8">│   ├── data/             # Data preprocessing</p>
              <p className="ml-8">│   └── database/         # DB operations</p>
              <p className="ml-4">├── frontend/             # Next.js UI</p>
              <p className="ml-4">├── data/                 # Datasets</p>
              <p className="ml-4">└── outputs/              # Models & logs</p>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Testing</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-semibold text-white mb-2">Backend Tests:</p>
                <div className="bg-slate-900/50 p-2 rounded font-mono text-xs text-gray-300">
                  pytest backend/tests/ -v
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold text-white mb-2">Frontend Tests:</p>
                <div className="bg-slate-900/50 p-2 rounded font-mono text-xs text-gray-300">
                  npm test
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold text-white mb-2">API Integration Tests:</p>
                <div className="bg-slate-900/50 p-2 rounded font-mono text-xs text-gray-300">
                  python test_api.py
                </div>
              </div>
            </div>
          </section>

          <section className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-4">Deployment</h2>
            <p className="text-gray-300 mb-4">
              Deploy using Docker and your preferred cloud platform:
            </p>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span><strong>Backend:</strong> AWS Lambda, Google Cloud Run, or Railway</span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span><strong>Frontend:</strong> Vercel, Netlify, or any static host</span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400">•</span>
                <span><strong>Database:</strong> Managed PostgreSQL (Supabase, RDS)</span>
              </li>
            </ul>
          </section>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mt-12 pt-8 border-t border-slate-700 flex justify-between items-center">
          <Link href="/docs" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
            ← Back to Docs
          </Link>
          <div className="flex gap-4">
            <button onClick={() => copyToClipboard(window.location.href)} className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 transition-colors">
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
  )
}
