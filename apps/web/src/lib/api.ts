/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SummarizeRequest {
  videoUrl: string;
  mode: 'quick' | 'standard' | 'research' | 'educational';
  features: {
    factChecking?: boolean;
    webResearch?: boolean;
    citations?: boolean;
    translation?: boolean;
  };
  apiKey?: string;
}

export interface SummarizeResponse {
  id: string;
  videoId: string;
  videoTitle: string;
  videoUrl: string;
  content: string;
  mode: string;
  timestamps?: Array<{ time: string; text: string }>;
  citations?: string[];
  duration?: number;
  error?: string;
}

export interface QuestionRequest {
  summaryId: string;
  question: string;
  conversationHistory?: Array<{ role: string; content: string }>;
}

export interface QuestionResponse {
  answer: string;
  citations?: Array<{ time: string; text: string }>;
  sources?: string[];
}

/**
 * Summarize a YouTube video
 */
export async function summarizeVideo(
  request: SummarizeRequest
): Promise<SummarizeResponse> {
  const response = await fetch(`${API_URL}/api/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to summarize video');
  }

  return response.json();
}

/**
 * Ask a question about a summarized video
 */
export async function askQuestion(request: QuestionRequest): Promise<QuestionResponse> {
  const response = await fetch(`${API_URL}/api/question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to get answer');
  }

  return response.json();
}

/**
 * Stream summarization with Server-Sent Events
 */
export async function* streamSummarize(
  request: SummarizeRequest
): AsyncGenerator<{ agent: string; status: string; data?: any }> {
  const response = await fetch(`${API_URL}/api/summarize/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to start streaming');
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('No response body');
  }

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          yield data;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Health check for backend
 */
export async function healthCheck(): Promise<{ status: string; backend: string }> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  } catch (error) {
    return { status: 'error', backend: 'disconnected' };
  }
}

/**
 * Get available AI models
 */
export async function getAvailableModels(): Promise<string[]> {
  const response = await fetch(`${API_URL}/api/models`);

  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }

  const data = await response.json();
  return data.models || [];
}
