// lib/api.ts - FIXED with Document Filtering Support

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Document {
  id: number;
  file_name: string;
  file_type: string;
  upload_date: string;
  file_size: number;
  processed: boolean;
  metadata?: any;
  tags?: string[];
}

export interface Summary {
  document_id: number;
  document_name: string;
  file_type: string;
  upload_date: string;
  summary: {
    id: number;
    summary: string;
    language: string;
    created_date: string;
    word_count: number;
  } | null;
  video_name: string | null;
  has_video: boolean;
}

export interface ChatResponse {
  success: boolean;
  answer: string;
  sources: any[];
  session_id: string;
  metadata?: {
    complexity?: string;
    confidence?: string;
    tokens_used?: number;
    query_understanding?: any;
  };
}

export interface UploadOptions {
  generateSummary?: boolean;
  summaryStyle?: string;
  language?: string;
  generateVideo?: boolean;
  includeSubtitles?: boolean;  // ADDED
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async handleResponse(response: Response) {
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      let errorMessage = `Server error (${response.status}): ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
      } catch {
        if (errorText && errorText.length < 200) {
          errorMessage = errorText;
        }
      }
      
      throw new Error(errorMessage);
    }

    const text = await response.text();
    if (!text || text === '') {
      return { success: true };
    }
    
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  async uploadFile(file: File, options: UploadOptions = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('generate_summary', String(options.generateSummary ?? true));
    formData.append('summary_style', options.summaryStyle || 'executive');
    formData.append('language', options.language || 'english');
    formData.append('generate_video', String(options.generateVideo ?? false));
    formData.append('include_subtitles', String(options.includeSubtitles ?? false)); // ADDED

    console.log('📤 Uploading file:', file.name, 'to', `${this.baseURL}/api/upload`);
    console.log('Options:', options);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000);

      const response = await fetch(`${this.baseURL}/api/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log('📥 Response status:', response.status, response.statusText);

      const result = await this.handleResponse(response);
      console.log('✅ Upload successful:', result);
      return result;

    } catch (error: any) {
      console.error('❌ Upload error:', error);
      
      if (error.name === 'AbortError') {
        throw new Error('Upload timeout - file may be too large or server is slow');
      }
      
      if (error.message === 'Failed to fetch') {
        throw new Error(
          'Cannot connect to server. ' +
          'Make sure backend is running on http://localhost:8000 ' +
          'and CORS is enabled.'
        );
      }
      
      throw error;
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      console.log('🔌 Testing connection to:', `${this.baseURL}/api/health`);
      
      const response = await fetch(`${this.baseURL}/api/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('❌ Health check failed:', response.status);
        return false;
      }

      const data = await response.json();
      console.log('✅ Backend is healthy:', data);
      return true;

    } catch (error) {
      console.error('❌ Cannot connect to backend:', error);
      return false;
    }
  }

  async getDocuments(): Promise<Document[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/documents`);
      const data = await this.handleResponse(response);
      return data.documents || [];
    } catch (error: any) {
      console.error('Error fetching documents:', error);
      return [];
    }
  }

  async getDocument(documentId: number): Promise<Document | null> {
    try {
      const response = await fetch(`${this.baseURL}/api/documents/${documentId}`);
      const data = await this.handleResponse(response);
      return data.document;
    } catch (error: any) {
      console.error('Error fetching document:', error);
      return null;
    }
  }

  async deleteDocument(documentId: number): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/documents/${documentId}`, {
      method: 'DELETE',
    });
    await this.handleResponse(response);
  }

  // ✅ FIXED: Added document_id parameter for filtering
  async sendChatMessage(
    message: string,
    sessionId: string,
    language: string = 'English',
    topK: number = 5,
    documentId: number | null = null  // ✅ NEW PARAMETER
  ): Promise<ChatResponse> {
    
    // Build request body
    const requestBody: any = {
      message,
      session_id: sessionId,
      language,
      top_k: topK,
    };

    // ✅ CRITICAL: Only add document_id if it's specified (not null)
    if (documentId !== null) {
      requestBody.document_id = documentId;
      console.log(`🔍 Chat request WITH document filter: document_id = ${documentId}`);
    } else {
      console.log(`🔍 Chat request WITHOUT document filter (searching all documents)`);
    }

    console.log('📤 Chat request body:', requestBody);

    try {
      const response = await fetch(`${this.baseURL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const result = await this.handleResponse(response);
      
      console.log('📥 Chat response:', {
        answer_length: result.answer?.length || 0,
        sources_count: result.sources?.length || 0,
        confidence: result.metadata?.confidence,
      });

      // ✅ VERIFY: Check if sources are from correct document
      if (documentId !== null && result.sources) {
        const verifiedSources = result.sources.filter(
          (source: any) => source.metadata?.document_id === documentId
        );
        
        if (verifiedSources.length !== result.sources.length) {
          console.warn(
            `⚠️ Filtered ${result.sources.length - verifiedSources.length} sources from wrong documents`
          );
          result.sources = verifiedSources;
        }
      }

      return result;

    } catch (error: any) {
      console.error('❌ Chat request failed:', error);
      throw error;
    }
  }

  async getChatHistory(sessionId: string, limit: number = 50) {
    try {
      const response = await fetch(
        `${this.baseURL}/api/history/chats/${sessionId}?limit=${limit}`
      );
      const data = await this.handleResponse(response);
      return data.history || [];
    } catch (error: any) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  }

  async getAllSummaries(): Promise<Summary[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/summaries/all`);
      const data = await this.handleResponse(response);
      return data.summaries || [];
    } catch (error: any) {
      console.error('Error fetching summaries:', error);
      return [];
    }
  }

  async getDocumentSummary(documentId: number) {
    try {
      const response = await fetch(`${this.baseURL}/api/documents/${documentId}/summary`);
      const data = await this.handleResponse(response);
      return data.summary;
    } catch (error: any) {
      console.error('Error fetching summary:', error);
      return null;
    }
  }

  async generateSummary(
    documentId: number,
    style: string = 'executive',
    language: string = 'English',
    targetLength: number = 300
  ) {
    const response = await fetch(`${this.baseURL}/api/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: documentId,
        style,
        language,
        target_length: targetLength,
      }),
    });

    return await this.handleResponse(response);
  }

  async getAnalytics() {
    try {
      const response = await fetch(`${this.baseURL}/api/analytics`);
      const data = await this.handleResponse(response);
      return data.analytics;
    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      return null;
    }
  }

  async listVideos() {
    try {
      const response = await fetch(`${this.baseURL}/api/videos`);
      const data = await this.handleResponse(response);
      return data.videos || [];
    } catch (error: any) {
      console.error('Error listing videos:', error);
      return [];
    }
  }

  getVideoUrl(videoName: string): string {
    return `${this.baseURL}/api/videos/${videoName}`;
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/api/health`);
    return await this.handleResponse(response);
  }
}

export const api = new APIClient(API_URL);
export default api;