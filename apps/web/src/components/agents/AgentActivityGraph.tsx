'use client';

import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  FileText,
  Search,
  CheckCircle2,
  Link as LinkIcon,
  Globe,
  Loader2,
  ChevronRight,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  icon: any;
  progress?: number;
  result?: string;
  duration?: number;
}

interface AgentActivityGraphProps {
  agents?: Agent[];
  isProcessing?: boolean;
}

const defaultAgents: Agent[] = [
  {
    id: 'extractor',
    name: 'Extractor Agent',
    status: 'idle',
    icon: FileText,
    progress: 0,
  },
  {
    id: 'summarizer',
    name: 'Summarizer Agent',
    status: 'idle',
    icon: Brain,
    progress: 0,
  },
  {
    id: 'research',
    name: 'Research Agent',
    status: 'idle',
    icon: Search,
    progress: 0,
  },
  {
    id: 'fact_checker',
    name: 'Fact-Checker Agent',
    status: 'idle',
    icon: CheckCircle2,
    progress: 0,
  },
  {
    id: 'citation',
    name: 'Citation Agent',
    status: 'idle',
    icon: LinkIcon,
    progress: 0,
  },
];

export default function AgentActivityGraph({
  agents = defaultAgents,
  isProcessing = false,
}: AgentActivityGraphProps) {
  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'running':
        return 'text-accent-400 bg-accent-400/20 border-accent-400/30';
      case 'completed':
        return 'text-success bg-success/20 border-success/30';
      case 'error':
        return 'text-error bg-error/20 border-error/30';
      default:
        return 'text-muted-foreground bg-muted/20 border-muted/30';
    }
  };

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'error':
        return <span className="text-xs">!</span>;
      default:
        return null;
    }
  };

  return (
    <Card glowing className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Globe className="w-5 h-5 text-accent-400" />
            Agent Activity
          </CardTitle>
          {isProcessing && (
            <div className="flex items-center gap-2 text-xs text-accent-400">
              <div className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
              Processing
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className={`relative p-4 rounded-lg border ${getStatusColor(
                  agent.status
                )} transition-all duration-300`}
              >
                {/* Connection Line */}
                {index < agents.length - 1 && (
                  <div className="absolute left-8 top-full w-0.5 h-3 bg-border" />
                )}

                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div
                    className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                      agent.status === 'running' ? 'bg-gradient-accent' : 'bg-muted/50'
                    }`}
                  >
                    <agent.icon
                      className={`w-5 h-5 ${
                        agent.status === 'running'
                          ? 'text-white animate-pulse'
                          : 'text-muted-foreground'
                      }`}
                    />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">{agent.name}</p>
                      {getStatusIcon(agent.status)}
                    </div>

                    {/* Progress Bar */}
                    {agent.status === 'running' && agent.progress !== undefined && (
                      <div className="mt-2">
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${agent.progress}%` }}
                            transition={{ duration: 0.5 }}
                            className="h-full bg-gradient-accent"
                          />
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {agent.progress}% complete
                        </p>
                      </div>
                    )}

                    {/* Result */}
                    {agent.result && (
                      <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                        {agent.result}
                      </p>
                    )}

                    {/* Duration */}
                    {agent.duration && agent.status === 'completed' && (
                      <p className="text-xs text-success mt-1">{agent.duration}ms</p>
                    )}
                  </div>

                  {/* Chevron */}
                  {agent.status === 'completed' && (
                    <ChevronRight className="w-4 h-4 text-success flex-shrink-0" />
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {!isProcessing && agents.every((a) => a.status === 'idle') && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8 text-muted-foreground"
            >
              <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Agents are ready</p>
              <p className="text-xs mt-1">Start processing to see agent activity</p>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
