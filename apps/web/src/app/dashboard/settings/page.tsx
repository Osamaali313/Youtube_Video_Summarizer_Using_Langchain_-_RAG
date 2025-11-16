'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Key,
  Shield,
  Server,
  Zap,
  Save,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Globe,
  Database,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/lib/stores/appStore';

export default function SettingsPage() {
  const { apiKeys, setApiKeys, settings, updateSettings } = useAppStore();
  const [showOpenRouter, setShowOpenRouter] = useState(false);
  const [showGoogleAI, setShowGoogleAI] = useState(false);
  const [tempKeys, setTempKeys] = useState({
    openrouter: apiKeys.openrouter || '',
    googleAi: apiKeys.googleAi || '',
  });
  const [saved, setSaved] = useState(false);

  const handleSaveKeys = () => {
    setApiKeys({
      openrouter: tempKeys.openrouter,
      googleAi: tempKeys.googleAi,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleFeatureToggle = (feature: string) => {
    updateSettings({
      features: {
        ...settings.features,
        [feature]: !settings.features[feature as keyof typeof settings.features],
      },
    });
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex-1 ml-72 overflow-y-auto">
        <div className="p-8 max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="text-4xl font-bold mb-2">Settings</h2>
            <p className="text-muted-foreground">
              Configure your API keys, backend, and preferences
            </p>
          </motion.div>

          {/* API Keys Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card glowing>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center">
                    <Key className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle>API Keys</CardTitle>
                    <CardDescription>
                      Securely store your AI provider API keys
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* OpenRouter */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <Globe className="w-4 h-4 text-primary-400" />
                      OpenRouter API Key
                    </label>
                    <a
                      href="https://openrouter.ai/keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-accent-400 hover:text-accent-300"
                    >
                      Get API Key →
                    </a>
                  </div>
                  <div className="relative">
                    <input
                      type={showOpenRouter ? 'text' : 'password'}
                      value={tempKeys.openrouter}
                      onChange={(e) =>
                        setTempKeys({ ...tempKeys, openrouter: e.target.value })
                      }
                      placeholder="sk-or-..."
                      className="w-full px-4 py-3 pr-12 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all font-mono text-sm"
                    />
                    <button
                      onClick={() => setShowOpenRouter(!showOpenRouter)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showOpenRouter ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Access to 200+ AI models including GPT-4, Claude, Llama, and more
                  </p>
                </div>

                {/* Google AI Studio */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-accent-400" />
                      Google AI Studio API Key
                    </label>
                    <a
                      href="https://makersuite.google.com/app/apikey"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-accent-400 hover:text-accent-300"
                    >
                      Get API Key →
                    </a>
                  </div>
                  <div className="relative">
                    <input
                      type={showGoogleAI ? 'text' : 'password'}
                      value={tempKeys.googleAi}
                      onChange={(e) =>
                        setTempKeys({ ...tempKeys, googleAi: e.target.value })
                      }
                      placeholder="AIza..."
                      className="w-full px-4 py-3 pr-12 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all font-mono text-sm"
                    />
                    <button
                      onClick={() => setShowGoogleAI(!showGoogleAI)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showGoogleAI ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Gemini Pro and Gemini Flash models for fast, efficient processing
                  </p>
                </div>

                {/* Security Notice */}
                <div className="flex items-start gap-3 glass p-4 rounded-lg border border-accent-500/30">
                  <Shield className="w-5 h-5 text-accent-400 flex-shrink-0 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-accent-400 mb-1">
                      Secure Storage
                    </p>
                    <p className="text-muted-foreground text-xs">
                      API keys are encrypted and stored locally in your browser. They
                      are never sent to our servers.
                    </p>
                  </div>
                </div>

                {/* Save Button */}
                <Button
                  size="lg"
                  variant="glow"
                  onClick={handleSaveKeys}
                  className="w-full"
                >
                  {saved ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 mr-2" />
                      Saved Successfully
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" />
                      Save API Keys
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Backend Selection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card glowing>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-accent flex items-center justify-center">
                    <Server className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle>Backend Configuration</CardTitle>
                    <CardDescription>
                      Choose your preferred backend service
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    {
                      id: 'python',
                      name: 'Python / FastAPI',
                      description: 'Full LangGraph support',
                      recommended: true,
                    },
                    {
                      id: 'nodejs',
                      name: 'Node.js / Express',
                      description: 'LangGraph.js implementation',
                    },
                    { id: 'go', name: 'Go / Fiber', description: 'High performance' },
                    { id: 'rust', name: 'Rust / Actix', description: 'Ultra-fast' },
                  ].map((backend) => (
                    <button
                      key={backend.id}
                      onClick={() => updateSettings({ backend: backend.id as any })}
                      className={`p-4 rounded-lg border-2 transition-all text-left ${
                        settings.backend === backend.id
                          ? 'border-primary-500 bg-primary-500/10'
                          : 'border-border glass-hover'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <p className="font-medium">{backend.name}</p>
                        {backend.recommended && (
                          <span className="text-xs px-2 py-1 rounded bg-accent-400/20 text-accent-400">
                            Recommended
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {backend.description}
                      </p>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Default Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card glowing>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-cta flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle>Default Preferences</CardTitle>
                    <CardDescription>
                      Set your default summary mode and features
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Default Mode */}
                <div className="space-y-3">
                  <label className="text-sm font-medium">Default Summary Mode</label>
                  <div className="grid grid-cols-2 gap-3">
                    {['quick', 'standard', 'research', 'educational'].map((mode) => (
                      <button
                        key={mode}
                        onClick={() => updateSettings({ defaultMode: mode as any })}
                        className={`px-4 py-3 rounded-lg text-sm font-medium transition-all capitalize ${
                          settings.defaultMode === mode
                            ? 'bg-primary-500/20 border-2 border-primary-500 text-primary-400'
                            : 'glass glass-hover border border-border'
                        }`}
                      >
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Feature Toggles */}
                <div className="space-y-3">
                  <label className="text-sm font-medium">Enabled Features</label>
                  <div className="space-y-2">
                    {[
                      { id: 'factChecking', label: 'Fact Checking', icon: CheckCircle2 },
                      { id: 'webResearch', label: 'Web Research', icon: Globe },
                      { id: 'citations', label: 'Citations & Timestamps', icon: Database },
                      { id: 'translation', label: 'Translation Support', icon: Globe },
                    ].map((feature) => (
                      <label
                        key={feature.id}
                        className="flex items-center justify-between p-4 rounded-lg glass-hover cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <feature.icon className="w-5 h-5 text-accent-400" />
                          <span className="text-sm font-medium">{feature.label}</span>
                        </div>
                        <input
                          type="checkbox"
                          checked={
                            settings.features[
                              feature.id as keyof typeof settings.features
                            ]
                          }
                          onChange={() => handleFeatureToggle(feature.id)}
                          className="w-5 h-5 rounded accent-primary-500"
                        />
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Danger Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="border-error/30">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-error/20 flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-error" />
                  </div>
                  <div>
                    <CardTitle className="text-error">Danger Zone</CardTitle>
                    <CardDescription>
                      Irreversible actions - proceed with caution
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full border-error text-error">
                  Clear All Summaries
                </Button>
                <Button variant="outline" className="w-full border-error text-error">
                  Reset All Settings
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
