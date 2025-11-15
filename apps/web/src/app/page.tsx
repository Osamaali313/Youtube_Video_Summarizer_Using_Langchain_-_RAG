'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import ParticleGalaxy from '@/components/3d/ParticleGalaxy';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Sparkles,
  Zap,
  Brain,
  MessageSquare,
  FileText,
  Layers,
  ArrowRight,
  Check,
} from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'Multi-Agent Intelligence',
    description:
      'Powered by LangGraph with specialized agents for extraction, summarization, fact-checking, and research.',
    color: 'text-primary-400',
  },
  {
    icon: Sparkles,
    title: 'Smart Summarization',
    description:
      'Multiple summary modes: Quick, Detailed, Research-backed, and Educational notes tailored to your needs.',
    color: 'text-accent-400',
  },
  {
    icon: MessageSquare,
    title: 'Interactive Q&A',
    description:
      'Ask questions about any video with RAG-powered context-aware responses and source citations.',
    color: 'text-cta-400',
  },
  {
    icon: Zap,
    title: 'Real-time Processing',
    description:
      'Watch agents work in real-time with live activity visualization and progress tracking.',
    color: 'text-primary-400',
  },
  {
    icon: FileText,
    title: 'Multi-format Export',
    description:
      'Export to PDF, Markdown, JSON, or Notion-ready format with timestamps and citations.',
    color: 'text-accent-400',
  },
  {
    icon: Layers,
    title: 'Multiple Backends',
    description:
      'Choose from Python, Node.js, Go, Rust, or Ruby backends - each optimized for different use cases.',
    color: 'text-cta-400',
  },
];

const workflows = [
  'Extract YouTube transcript',
  'Analyze content with AI agents',
  'Generate smart summaries',
  'Fact-check claims',
  'Add citations & timestamps',
  'Export in your format',
];

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <ParticleGalaxy />

      {/* Hero Section */}
      <section className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-5xl mx-auto"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8"
          >
            <Sparkles className="w-4 h-4 text-accent-400" />
            <span className="text-sm font-medium">Powered by LangGraph Multi-Agent System</span>
          </motion.div>

          {/* Main Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-6xl md:text-8xl font-bold mb-6 leading-tight"
          >
            Transform YouTube Videos
            <br />
            <span className="gradient-text">Into Intelligence</span>
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto"
          >
            AI-powered video summarization with multi-agent workflows. Extract insights,
            ask questions, and export knowledge - all powered by state-of-the-art LangGraph agents.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link href="/dashboard">
              <Button size="xl" variant="glow" className="group">
                Start Summarizing
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button size="xl" variant="glass">
              View Demo
            </Button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-3 gap-8 mt-20 max-w-2xl mx-auto"
          >
            <div>
              <div className="text-4xl font-bold gradient-text">9+</div>
              <div className="text-sm text-muted-foreground mt-1">AI Agents</div>
            </div>
            <div>
              <div className="text-4xl font-bold gradient-text">5</div>
              <div className="text-sm text-muted-foreground mt-1">Backend Options</div>
            </div>
            <div>
              <div className="text-4xl font-bold gradient-text">200+</div>
              <div className="text-sm text-muted-foreground mt-1">AI Models</div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 px-6 py-32 bg-gradient-to-b from-transparent to-background/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold mb-4">
              Powerful <span className="gradient-text">Features</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to extract, analyze, and understand video content with AI
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card glowing className="h-full">
                  <CardHeader>
                    <feature.icon className={`w-12 h-12 mb-4 ${feature.color}`} />
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 px-6 py-32">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
            <p className="text-xl text-muted-foreground">
              Six simple steps powered by intelligent AI agents
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workflows.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass rounded-lg p-6 flex items-start gap-4 glass-hover"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{step}</p>
                </div>
                <Check className="w-5 h-5 text-success flex-shrink-0" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center"
        >
          <Card glowing className="p-12 bg-gradient-mesh">
            <CardContent className="space-y-8">
              <h2 className="text-5xl font-bold">
                Ready to Get <span className="gradient-text">Started?</span>
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                No credit card required. Start summarizing YouTube videos with AI agents in seconds.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/dashboard">
                  <Button size="xl" variant="glow">
                    Launch App
                    <Zap className="w-5 h-5" />
                  </Button>
                </Link>
                <Button size="xl" variant="outline">
                  View Documentation
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-12 border-t border-border">
        <div className="max-w-7xl mx-auto text-center text-muted-foreground">
          <p>Built with Next.js, LangGraph, and cutting-edge AI technology</p>
          <p className="mt-2 text-sm">
            Supports OpenRouter & Google AI Studio | Multiple backend options
          </p>
        </div>
      </footer>
    </main>
  );
}
