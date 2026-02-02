"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  BookOpen,
  Code,
  Users,
  Briefcase,
  ArrowRight,
  FileText,
  Download,
} from "lucide-react";

const docSections = [
  {
    id: "overview",
    title: "System Overview",
    description:
      "High-level introduction to Sentinel-Net and its core capabilities",
    icon: BookOpen,
    color: "from-blue-500 to-cyan-500",
    path: "/docs/overview",
    available: true,
  },
  {
    id: "users",
    title: "For End Users",
    description: "Simple explanations, privacy commitments, and FAQs",
    icon: Users,
    color: "from-green-500 to-emerald-500",
    path: "/docs/users",
    available: true,
  },
  {
    id: "developers",
    title: "For Developers",
    description:
      "API reference, setup guides, deployment, and extending the system",
    icon: Code,
    color: "from-purple-500 to-pink-500",
    path: "/docs/developers",
    available: true,
  },
  {
    id: "researchers",
    title: "For Researchers",
    description:
      "Benchmarks, research opportunities, datasets, and academic access",
    icon: BookOpen,
    color: "from-orange-500 to-red-500",
    path: "/docs/researchers",
    available: true,
  },
  {
    id: "business",
    title: "For Business Stakeholders",
    description:
      "ROI analysis, market opportunities, competitive positioning, and roadmap",
    icon: Briefcase,
    color: "from-indigo-500 to-blue-500",
    path: "/docs/business",
    available: true,
  },
  {
    id: "architecture",
    title: "System Architecture",
    description:
      "Complete technical design, ML models, consensus algorithm, and data flow",
    icon: FileText,
    color: "from-teal-500 to-cyan-500",
    path: "/docs/architecture",
    available: true,
  },
];

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="inline-block px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-sm font-semibold text-blue-300 mb-4">
            📚 Complete Documentation
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Sentinel-Net Documentation
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Choose your role to access tailored documentation and resources. All
            guides are available in HTML and PDF formats.
          </p>
        </motion.div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12"
        >
          <a href="/docs/overview" className="group">
            <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-blue-500/50 transition-all">
              <div className="flex items-center gap-3 mb-2">
                <FileText size={18} className="text-blue-400" />
                <span className="text-sm font-semibold text-gray-300">
                  Quick Start
                </span>
              </div>
              <p className="text-xs text-gray-500">5-minute introduction</p>
            </div>
          </a>
          <a href="/docs/developers" className="group">
            <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-purple-500/50 transition-all">
              <div className="flex items-center gap-3 mb-2">
                <Code size={18} className="text-purple-400" />
                <span className="text-sm font-semibold text-gray-300">
                  API Reference
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Full endpoint documentation
              </p>
            </div>
          </a>
          <a href="/docs/architecture" className="group">
            <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-teal-500/50 transition-all">
              <div className="flex items-center gap-3 mb-2">
                <Briefcase size={18} className="text-teal-400" />
                <span className="text-sm font-semibold text-gray-300">
                  Architecture
                </span>
              </div>
              <p className="text-xs text-gray-500">System design details</p>
            </div>
          </a>
        </motion.div>

        {/* Documentation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {docSections.map((section, idx) => {
            const Icon = section.icon;
            return (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Link href={section.path}>
                  <div className="group h-full p-6 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-white/20 hover:bg-slate-800/70 transition-all cursor-pointer">
                    <div
                      className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${section.color} mb-4 group-hover:scale-110 transition-transform`}
                    >
                      <Icon size={24} className="text-white" />
                    </div>

                    <h3 className="text-lg font-semibold text-white mb-2">
                      {section.title}
                    </h3>

                    <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                      {section.description}
                    </p>

                    <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                      <div className="flex items-center gap-2">
                        <span className="inline-block w-2 h-2 rounded-full bg-green-500"></span>
                        <span className="text-xs text-gray-500">Available</span>
                      </div>
                      <ArrowRight
                        size={16}
                        className="text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all"
                      />
                    </div>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>

        {/* Download All Docs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-xl text-center"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Download size={20} className="text-blue-400" />
            <h3 className="text-lg font-semibold text-white">
              Download All Documentation
            </h3>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Get PDF versions of all documentation for offline viewing
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors">
              📄 Download All PDFs
            </button>
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold rounded-lg transition-colors">
              📋 View Online
            </button>
          </div>
        </motion.div>

        {/* Navigation Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-16 pt-8 border-t border-slate-700 flex justify-between items-center"
        >
          <Link href="/">
            <span className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
              ← Back to Home
            </span>
          </Link>
          <div className="text-xs text-gray-500">
            Last updated: February 2, 2026
          </div>
        </motion.div>
      </div>
    </div>
  );
}
