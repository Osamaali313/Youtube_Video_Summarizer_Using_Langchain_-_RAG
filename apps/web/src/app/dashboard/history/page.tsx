'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Trash2,
  Download,
  Eye,
  Search,
  Filter,
  Calendar,
  Video,
  Star,
  StarOff,
  ExternalLink,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/lib/stores/appStore';

export default function HistoryPage() {
  const { summaries, deleteSummary, setCurrentSummary } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState<string>('all');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const filteredSummaries = summaries.filter((summary) => {
    const matchesSearch =
      summary.videoTitle?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      summary.content?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter =
      filterMode === 'all' || summary.mode === filterMode;

    return matchesSearch && matchesFilter;
  });

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleExport = (summary: any) => {
    // Create markdown export
    const markdown = `# ${summary.videoTitle}\n\n${summary.content}\n\nGenerated: ${new Date(
      summary.createdAt
    ).toLocaleString()}`;

    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary-${summary.id}.md`;
    a.click();
  };

  const modeColors = {
    quick: 'text-accent-400 bg-accent-400/20',
    standard: 'text-primary-400 bg-primary-400/20',
    research: 'text-cta-400 bg-cta-400/20',
    educational: 'text-success bg-success/20',
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex-1 ml-72 flex flex-col">
        {/* Header */}
        <div className="border-b border-border p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold mb-2">Summary History</h2>
              <p className="text-muted-foreground">
                View and manage your saved summaries
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="glass px-4 py-2 rounded-lg">
                <p className="text-sm text-muted-foreground">Total Summaries</p>
                <p className="text-2xl font-bold gradient-text">{summaries.length}</p>
              </div>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search summaries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
            <select
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value)}
              className="px-4 py-3 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none"
            >
              <option value="all">All Modes</option>
              <option value="quick">Quick</option>
              <option value="standard">Standard</option>
              <option value="research">Research</option>
              <option value="educational">Educational</option>
            </select>
          </div>
        </div>

        {/* Summaries List */}
        <div className="flex-1 overflow-y-auto p-6">
          {filteredSummaries.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full space-y-4"
            >
              <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
                <Clock className="w-10 h-10 text-muted-foreground opacity-50" />
              </div>
              <h3 className="text-2xl font-bold">No Summaries Yet</h3>
              <p className="text-muted-foreground text-center max-w-md">
                {searchQuery || filterMode !== 'all'
                  ? 'No summaries match your search criteria'
                  : 'Start by summarizing your first YouTube video'}
              </p>
            </motion.div>
          ) : (
            <div className="space-y-4 max-w-5xl mx-auto">
              <AnimatePresence mode="popLayout">
                {filteredSummaries.map((summary, index) => (
                  <motion.div
                    key={summary.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card glowing className="group">
                      <CardHeader>
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                              <Video className="w-5 h-5 text-accent-400 flex-shrink-0" />
                              <h3 className="font-bold text-lg line-clamp-1">
                                {summary.videoTitle || 'Untitled Video'}
                              </h3>
                            </div>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                {new Date(summary.createdAt).toLocaleDateString()}
                              </div>
                              <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {new Date(summary.createdAt).toLocaleTimeString()}
                              </div>
                              <span
                                className={`px-2 py-1 rounded-md text-xs font-medium ${
                                  modeColors[summary.mode]
                                }`}
                              >
                                {summary.mode}
                              </span>
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => toggleFavorite(summary.id)}
                            >
                              {favorites.has(summary.id) ? (
                                <Star className="w-4 h-4 text-accent-400 fill-accent-400" />
                              ) : (
                                <StarOff className="w-4 h-4" />
                              )}
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setCurrentSummary(summary)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleExport(summary)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => deleteSummary(summary.id)}
                            >
                              <Trash2 className="w-4 h-4 text-error" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                          {summary.content}
                        </p>

                        {/* Video Link */}
                        {summary.videoUrl && (
                          <a
                            href={summary.videoUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-sm text-accent-400 hover:text-accent-300 transition-colors"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Watch on YouTube
                          </a>
                        )}

                        {/* Timestamps Preview */}
                        {summary.timestamps && summary.timestamps.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-border">
                            <p className="text-xs font-medium text-muted-foreground mb-2">
                              Key Timestamps:
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {summary.timestamps.slice(0, 3).map((ts, idx) => (
                                <span
                                  key={idx}
                                  className="text-xs glass px-2 py-1 rounded font-mono text-accent-400"
                                >
                                  {ts.time}
                                </span>
                              ))}
                              {summary.timestamps.length > 3 && (
                                <span className="text-xs text-muted-foreground">
                                  +{summary.timestamps.length - 3} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
