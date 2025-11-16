'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download,
  FileText,
  FileJson,
  FileCode,
  Copy,
  Check,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { exportSummary, copyToClipboard, exportAsMarkdown } from '@/lib/export';
import type { Summary } from '@/lib/stores/appStore';

interface ExportMenuProps {
  summary: Summary;
  onExport?: () => void;
}

export default function ExportMenu({ summary, onExport }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleExport = (format: 'markdown' | 'json' | 'text' | 'notion' | 'obsidian') => {
    exportSummary(summary, format);
    setIsOpen(false);
    onExport?.();
  };

  const handleCopy = async () => {
    const markdown = exportAsMarkdown(summary);
    const success = await copyToClipboard(markdown);

    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const exportOptions = [
    {
      format: 'markdown' as const,
      icon: FileText,
      label: 'Markdown',
      description: 'Standard .md format',
      color: 'text-primary-400',
    },
    {
      format: 'json' as const,
      icon: FileJson,
      label: 'JSON',
      description: 'Structured data',
      color: 'text-accent-400',
    },
    {
      format: 'text' as const,
      icon: FileText,
      label: 'Plain Text',
      description: 'Simple .txt file',
      color: 'text-muted-foreground',
    },
    {
      format: 'notion' as const,
      icon: FileCode,
      label: 'Notion',
      description: 'Import to Notion',
      color: 'text-cta-400',
    },
    {
      format: 'obsidian' as const,
      icon: FileCode,
      label: 'Obsidian',
      description: 'Vault-ready format',
      color: 'text-primary-400',
    },
  ];

  return (
    <div className="relative">
      <Button
        variant="glass"
        size="default"
        onClick={() => setIsOpen(!isOpen)}
        className="gap-2"
      >
        <Download className="w-4 h-4" />
        Export
        <ChevronDown
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </Button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40"
            />

            {/* Menu */}
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ type: 'spring', duration: 0.3 }}
              className="absolute right-0 mt-2 w-72 z-50"
            >
              <Card className="glass border border-border overflow-hidden">
                <div className="p-2 space-y-1">
                  {/* Copy to Clipboard */}
                  <button
                    onClick={handleCopy}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted/50 transition-colors text-left"
                  >
                    {copied ? (
                      <Check className="w-5 h-5 text-success" />
                    ) : (
                      <Copy className="w-5 h-5 text-accent-400" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        {copied ? 'Copied!' : 'Copy to Clipboard'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Markdown format
                      </p>
                    </div>
                  </button>

                  <div className="border-t border-border my-2" />

                  {/* Export Options */}
                  {exportOptions.map((option) => (
                    <button
                      key={option.format}
                      onClick={() => handleExport(option.format)}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted/50 transition-colors text-left"
                    >
                      <option.icon className={`w-5 h-5 ${option.color}`} />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{option.label}</p>
                        <p className="text-xs text-muted-foreground">
                          {option.description}
                        </p>
                      </div>
                      <Download className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100" />
                    </button>
                  ))}
                </div>
              </Card>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
