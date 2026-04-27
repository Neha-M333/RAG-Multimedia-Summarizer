/**
 * API Client for GlassVault Backend
 * Connects React frontend to FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface Document {
  id: number;
  file_name: string;
  file_type: string;
  upload_date: string;
  processed: boolean;
  metadata?: any;
}

export interface VideoGenerationOptions {
  language?: string;
  target_duration?: number;
  include_subtitles?: boolean;
}

export interface VideoResult {
  success: boolean;
  video_path?: string;
  thumbnail_path?: string;
  duration?: number;
  file_size?: number;
  language?: string;
  error?: string;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: Source[];
  confidence?: string;
  complexity?: string;
}

export interface Source {
  content: string;
  metadata: {
    file_name?: string;
    [key: string]: any;
  };
  relevance_score?: number;
}

export interface UploadResponse {
  id: number;
  file_name: string;
  file_type: string;
  chunks: number;
  summary?: string;
  keywords?: string[];
  status: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  confidence?: string;
  complexity?: string;
}

export interface Analytics {
  documents: {
    total: number;
    by_type: Record<string, number>;
    total_size_mb: number;
  };
  chat: {
    total_messages: number;
    avg_response_time: number;
  };
  performance: {
    cache_hit_rate: number;
    queries_executed: number;
  };
}

// API Client Class
class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; database: string; documents: number }> {
    return this.request('/health');
  }

  // Document Management
  async uploadFile(
    file: File,
    options: {
      generateSummary?: boolean;
      extractKeywords?: boolean;
    } = {}
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const queryParams = new URLSearchParams({
      generate_summary: String(options.generateSummary ?? true),
      extract_keywords: String(options.extractKeywords ?? false),
    });

    const response = await fetch(
      `${this.baseURL}/upload?${queryParams}`,
      {
        method: 'POST',
        body: formData, // Do NOT include Content-Type here for FormData
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  async getDocuments(): Promise<Document[]> {
    return this.request('/documents');
  }

  async getDocument(id: number): Promise<Document & { chunks: any[] }> {
    return this.request(`/documents/${id}`);
  }

  async deleteDocument(id: number): Promise<{ status: string }> {
    return this.request(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Chat
  async sendMessage(
    message: string,
    sessionId: string,
    options: {
      language?: string;
      topK?: number;
    } = {}
  ): Promise<ChatResponse> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        language: options.language || 'English',
        top_k: options.topK || 5,
      }),
    });
  }

  async translateText(
    text: string,
    targetLanguage: string,
    sourceLanguage: string = 'auto'
  ): Promise<{ translated_text: string; source_language: string; target_language: string }> {
    return this.request('/translate', {
      method: 'POST',
      body: JSON.stringify({
        text,
        target_language: targetLanguage,
        source_language: sourceLanguage,
      }),
    });
  }

  async getChatHistory(
    sessionId: string,
    limit: number = 50
  ): Promise<{ session_id: string; messages: ChatMessage[] }> {
    return this.request(`/chat/history/${sessionId}?limit=${limit}`);
  }

  // Summarization
  async summarizeDocument(
    documentId: number,
    options: {
      style?: string;
      language?: string;
      targetLength?: number;
    } = {}
  ): Promise<{
    summary: string;
    style: string;
    word_count: number;
    compression_ratio: number;
  }> {
    return this.request('/summarize', {
      method: 'POST',
      body: JSON.stringify({
        document_id: documentId,
        style: options.style || 'executive',
        language: options.language || 'English',
        target_length: options.targetLength || 300,
      }),
    });
  }

  // Analytics
  async getAnalytics(): Promise<Analytics> {
    return this.request('/analytics');
  }

  // Video Generation
  async generateVideo(
    documentId: number,
    options: VideoGenerationOptions = {}
  ): Promise<VideoResult> {
    const formData = new FormData();
    formData.append('document_id', documentId.toString());
    formData.append('language', options.language || 'english');
    formData.append('target_duration', (options.target_duration || 60).toString());
    formData.append('include_subtitles', (options.include_subtitles !== false).toString());

    const response = await fetch(`${this.baseURL}/generate-video`, {
      method: 'POST',
      body: formData, // Do NOT include Content-Type header for FormData
    });

    if (!response.ok) {
      throw new Error(`Video generation failed: ${response.statusText}`);
    }

    return response.json();
  }

  getVideoUrl(filename: string): string {
    return `${this.baseURL}/videos/${filename}`;
  }
}

// Export singleton instance
export const api = new APIClient(API_BASE_URL);

// React Query Hooks (optional, but recommended)
export const queryKeys = {
  documents: ['documents'] as const,
  document: (id: number) => ['documents', id] as const,
  chatHistory: (sessionId: string) => ['chat', 'history', sessionId] as const,
  analytics: ['analytics'] as const,
};
