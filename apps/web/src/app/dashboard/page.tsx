'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  Settings,
  History,
  MessageSquare,
  Home,
  Sparkles,
  Zap,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('summarize');

  const navItems = [
    { id: 'home', icon: Home, label: 'Home', href: '/' },
    { id: 'summarize', icon: Play, label: 'Summarize', href: '/dashboard' },
    { id: 'chat', icon: MessageSquare, label: 'Q&A Chat', href: '/dashboard/chat' },
    { id: 'history', icon: History, label: 'History', href: '/dashboard/history' },
    { id: 'settings', icon: Settings, label: 'Settings', href: '/dashboard/settings' },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: 0 }}
        animate={{ x: sidebarOpen ? 0 : -280 }}
        transition={{ type: 'spring', damping: 20 }}
        className="fixed left-0 top-0 h-full w-72 glass border-r border-border z-50"
      >
        <div className="flex flex-col h-full p-6">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">AI Summarizer</h1>
              <p className="text-xs text-muted-foreground">Multi-Agent System</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {navItems.map((item) => (
              <Link key={item.id} href={item.href}>
                <motion.button
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActiveView(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeView === item.id
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                      : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </motion.button>
              </Link>
            ))}
          </nav>

          {/* Bottom Section */}
          <div className="pt-6 border-t border-border">
            <Card className="bg-gradient-mesh">
              <CardHeader className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-accent-400" />
                  <p className="text-sm font-semibold">Pro Tip</p>
                </div>
                <p className="text-xs text-muted-foreground">
                  Enable Research Mode for fact-checked summaries with citations
                </p>
              </CardHeader>
            </Card>
          </div>
        </div>
      </motion.aside>

      {/* Sidebar Toggle Button */}
      <motion.button
        initial={{ x: 0 }}
        animate={{ x: sidebarOpen ? 280 : 0 }}
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed left-2 top-4 z-50 w-10 h-10 rounded-lg glass glass-hover flex items-center justify-center"
      >
        {sidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
      </motion.button>

      {/* Main Content */}
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarOpen ? 'ml-72' : 'ml-0'
        } overflow-y-auto`}
      >
        <div className="p-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h2 className="text-4xl font-bold mb-2">
              {activeView === 'summarize' && 'Video Summarizer'}
              {activeView === 'chat' && 'Q&A Chat'}
              {activeView === 'history' && 'Your History'}
              {activeView === 'settings' && 'Settings'}
            </h2>
            <p className="text-muted-foreground">
              {activeView === 'summarize' &&
                'Transform YouTube videos into intelligent summaries with AI agents'}
              {activeView === 'chat' && 'Ask questions about any video you ve summarized'}
              {activeView === 'history' && 'View and manage your past summaries'}
              {activeView === 'settings' && 'Configure your AI models and preferences'}
            </p>
          </motion.div>

          {/* Content Area - Placeholder for now */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              <Card glowing className="p-8">
                <CardHeader>
                  <CardTitle>Enter YouTube URL</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <input
                        type="text"
                        placeholder="https://www.youtube.com/watch?v=..."
                        className="w-full px-4 py-3 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
                      />
                    </div>

                    {/* Summary Mode Selector */}
                    <div>
                      <label className="block text-sm font-medium mb-3">Summary Mode</label>
                      <div className="grid grid-cols-2 gap-3">
                        {['Quick', 'Standard', 'Deep Research', 'Educational'].map((mode) => (
                          <button
                            key={mode}
                            className="px-4 py-3 rounded-lg glass glass-hover text-sm font-medium transition-all"
                          >
                            {mode}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Agent Options */}
                    <div>
                      <label className="block text-sm font-medium mb-3">Enable Features</label>
                      <div className="space-y-2">
                        {[
                          'Fact Checking',
                          'Web Research',
                          'Citations & Timestamps',
                          'Translation',
                        ].map((feature) => (
                          <label
                            key={feature}
                            className="flex items-center gap-3 px-4 py-2 rounded-lg glass-hover cursor-pointer"
                          >
                            <input type="checkbox" className="w-4 h-4 rounded" defaultChecked />
                            <span className="text-sm">{feature}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <Button size="lg" variant="glow" className="w-full">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Start Processing
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Results Placeholder */}
              <Card glowing className="p-8">
                <CardHeader>
                  <CardTitle>Summary Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-muted-foreground">
                    <Play className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>No video processed yet. Enter a URL above to get started.</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Agent Activity */}
              <Card glowing>
                <CardHeader>
                  <CardTitle className="text-lg">Agent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-center py-8 text-muted-foreground">
                      <Zap className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">Agents idle</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Backend Selector */}
              <Card glowing>
                <CardHeader>
                  <CardTitle className="text-lg">Backend</CardTitle>
                </CardHeader>
                <CardContent>
                  <select className="w-full px-4 py-2 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none">
                    <option>Python / FastAPI</option>
                    <option>Node.js / Express</option>
                    <option>Go / Fiber</option>
                    <option>Rust / Actix</option>
                    <option>Ruby / Rails</option>
                  </select>
                  <div className="mt-3 flex items-center gap-2 text-sm text-success">
                    <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                    <span>Connected</span>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <Card glowing>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="text-2xl font-bold gradient-text">0</div>
                    <div className="text-xs text-muted-foreground">Videos Summarized</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold gradient-text">0</div>
                    <div className="text-xs text-muted-foreground">Questions Asked</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold gradient-text">0</div>
                    <div className="text-xs text-muted-foreground">Summaries Exported</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
