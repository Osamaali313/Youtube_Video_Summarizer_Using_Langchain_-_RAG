'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Video, Clock, Link as LinkIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/lib/stores/appStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  citations?: Array<{ time: string; text: string }>;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { currentSummary, incrementStat } = useAppStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          "I'm an AI assistant powered by RAG and LangGraph agents. I can answer questions about the video you've summarized. Once you connect the backend, I'll provide context-aware responses with citations and timestamps.",
        timestamp: Date.now(),
        citations: [
          { time: '2:34', text: 'Relevant section from video' },
          { time: '5:12', text: 'Supporting information' },
        ],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
      incrementStat('totalQuestions');
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const exampleQuestions = [
    'What are the main topics covered?',
    'Can you explain the key points?',
    'What was mentioned at 3:45?',
    'Summarize the conclusion',
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex-1 ml-72 flex flex-col">
        {/* Header */}
        <div className="border-b border-border p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold mb-2">Q&A Chat</h2>
              <p className="text-muted-foreground">
                Ask questions about your summarized videos
              </p>
            </div>
            {currentSummary && (
              <div className="flex items-center gap-3 glass px-4 py-3 rounded-lg">
                <Video className="w-5 h-5 text-accent-400" />
                <div>
                  <p className="text-sm font-medium line-clamp-1">
                    {currentSummary.videoTitle || 'Current Video'}
                  </p>
                  <p className="text-xs text-muted-foreground">Active context</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full space-y-8"
            >
              <div className="text-center space-y-4">
                <div className="w-20 h-20 rounded-full bg-gradient-primary mx-auto flex items-center justify-center">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold">Start a Conversation</h3>
                <p className="text-muted-foreground max-w-md">
                  Ask me anything about the video you've summarized. I'll provide
                  context-aware answers with citations.
                </p>
              </div>

              {/* Example Questions */}
              <div className="space-y-3 w-full max-w-2xl">
                <p className="text-sm font-medium text-muted-foreground">
                  Try asking:
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {exampleQuestions.map((question, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setInput(question)}
                      className="glass glass-hover p-4 rounded-lg text-left text-sm"
                    >
                      {question}
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <>
              <AnimatePresence mode="popLayout">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-primary flex items-center justify-center">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    )}

                    <div
                      className={`max-w-2xl ${
                        message.role === 'user' ? 'order-first' : ''
                      }`}
                    >
                      <Card
                        className={
                          message.role === 'user'
                            ? 'bg-gradient-primary text-white'
                            : 'glass'
                        }
                      >
                        <CardContent className="p-4">
                          <p className="text-sm leading-relaxed">{message.content}</p>

                          {/* Citations */}
                          {message.citations && message.citations.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-border space-y-2">
                              <p className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                                <LinkIcon className="w-3 h-3" />
                                Citations:
                              </p>
                              {message.citations.map((citation, idx) => (
                                <button
                                  key={idx}
                                  className="flex items-center gap-2 text-xs glass px-3 py-2 rounded-lg hover:bg-muted/50 transition-colors w-full text-left"
                                >
                                  <Clock className="w-3 h-3 text-accent-400" />
                                  <span className="font-mono text-accent-400">
                                    {citation.time}
                                  </span>
                                  <span className="text-muted-foreground">
                                    {citation.text}
                                  </span>
                                </button>
                              ))}
                            </div>
                          )}

                          <p className="text-xs text-muted-foreground mt-3">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </p>
                        </CardContent>
                      </Card>
                    </div>

                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                        <User className="w-5 h-5" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing Indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-primary flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <Card className="glass">
                    <CardContent className="p-4">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-accent-400 rounded-full animate-bounce" />
                        <div
                          className="w-2 h-2 bg-accent-400 rounded-full animate-bounce"
                          style={{ animationDelay: '0.2s' }}
                        />
                        <div
                          className="w-2 h-2 bg-accent-400 rounded-full animate-bounce"
                          style={{ animationDelay: '0.4s' }}
                        />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-border p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about the video..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-lg glass border border-border focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all resize-none"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Press Enter to send, Shift+Enter for new line
                </p>
              </div>
              <Button
                size="lg"
                variant="glow"
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className="self-start"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
