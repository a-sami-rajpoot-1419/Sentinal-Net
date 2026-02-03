'use client'

import React, { ReactNode } from 'react'
import Link from 'next/link'
import { AuthProvider } from '@/contexts/AuthContext'
import UserMenu from '@/components/auth/UserMenu'
import './globals.css'

interface RootLayoutProps {
  children: ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Sentinel-Net Dashboard</title>
        <meta name="description" content="Real-time ML consensus prediction dashboard" />
      </head>
      <body>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="glass border-b border-white/10 sticky top-0 z-50">
              <nav className="container h-16 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500" />
                  <span className="font-bold text-lg gradient-text">Sentinel-Net</span>
                </Link>

                <div className="flex items-center gap-8">
                <Link
                  href="/dashboard"
                  className="text-sm text-gray-300 hover:text-white transition-smooth"
                >
                  Dashboard
                </Link>
                <Link
                  href="/predictions"
                  className="text-sm text-gray-300 hover:text-white transition-smooth"
                >
                  Predictions
                </Link>
                <Link
                  href="/agents"
                  className="text-sm text-gray-300 hover:text-white transition-smooth"
                >
                  Agents
                </Link>
                <Link
                  href="/docs"
                  className="text-sm text-gray-300 hover:text-white transition-smooth"
                >
                  📚 Docs
                </Link>
                <Link
                  href="/settings"
                  className="text-sm text-gray-300 hover:text-white transition-smooth"
                >
                  Settings
                </Link>
                
                {/* User Menu */}
                <UserMenu />
              </div>
            </nav>
          </header>

          {/* Main Content */}
          <main className="flex-1 container py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t border-white/10 py-6 text-center text-sm text-gray-400">
            <p>&copy; 2026 Sentinel-Net. RWPV Consensus Engine with Multi-Agent ML.</p>
          </footer>
        </div>
        </AuthProvider>
      </body>
    </html>
  )
}
