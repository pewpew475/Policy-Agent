/**
 * API service for connecting to the Insurance AI Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ||
                    (process.env.NODE_ENV === 'production'
                      ? '' // Same domain in production (Vercel)
                      : 'http://localhost:8000');

export interface Message {
  text: string;
  isAi: boolean;
  timestamp?: Date;
  documentIds?: string[];
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  document_type: string;
  processing_status: string;
  upload_timestamp: string;
  summary?: string;
  extracted_text?: string;
  page_count?: number;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  response_time: number;
  sources?: string[];
  confidence?: number;
}

export interface APIKeyResponse {
  key_id: string;
  api_key: string;
  name: string;
  description?: string;
  rate_limit: number;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
}

export interface UploadedDocument {
  document_id?: string;
  filename: string;
  status: 'ready' | 'failed';
  text_length?: number;
  page_count?: number;
  error?: string;
}

export interface UploadResponse {
  uploaded_documents: UploadedDocument[];
}

export interface AnalyticsResponse {
  usage_stats: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_response_time: number;
    documents_processed: number;
    api_calls_today: number;
  };
  top_endpoints: Array<{
    endpoint: string;
    count: number;
    avg_response_time: number;
  }>;
  error_rates: {
    "2xx": number;
    "4xx": number;
    "5xx": number;
  };
  response_times: Array<{
    timestamp: string;
    avg_response_time: number;
    request_count: number;
  }>;
  document_types: Record<string, number>;
}

export interface APIKey {
  id: string;
  name: string;
  created_at: string;
  last_used?: string;
  usage_count: number;
  is_active: boolean;
}

export interface SystemHealth {
  status: string;
  version: string;
  services: Record<string, string>;
  uptime?: number;
  avg_response_time_1h?: number;
  requests_1h?: number;
  error_rate_1h?: number;
}

class APIService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Upload a document to the backend
   */
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Upload files separately (no AI processing yet)
   */
  async uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${this.baseURL}/api/frontend/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Send a chat message with optional document context
   */
  async sendChatMessage(message: string, documentIds?: string[]): Promise<ReadableStream<Uint8Array>> {
    const formData = new FormData();
    formData.append('message', message);

    if (documentIds && documentIds.length > 0) {
      formData.append('document_ids', documentIds.join(','));
    }

    const response = await fetch(`${this.baseURL}/api/frontend/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    return response.body;
  }

  /**
   * Parse streaming response from the AI
   */
  async *parseStreamingResponse(stream: ReadableStream<Uint8Array>): AsyncGenerator<string, void, unknown> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              return;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                yield parsed.content;
              }
            } catch {
              // Skip invalid JSON
              continue;
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Generate an API key
   */
  async generateAPIKey(name: string, description?: string, rateLimit?: number): Promise<APIKeyResponse> {
    const response = await fetch(`${this.baseURL}/api/keys/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        description,
        rate_limit: rateLimit || 1000,
      }),
    });

    if (!response.ok) {
      throw new Error(`API key generation failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get analytics dashboard data
   */
  async getAnalytics(days: number = 7): Promise<AnalyticsResponse> {
    const response = await fetch(`${this.baseURL}/api/analytics/dashboard?days=${days}`);

    if (!response.ok) {
      throw new Error(`Analytics fetch failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get system health
   */
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await fetch(`${this.baseURL}/api/analytics/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get list of API keys
   */
  async getAPIKeys(): Promise<APIKey[]> {
    const response = await fetch(`${this.baseURL}/api/keys`);

    if (!response.ok) {
      throw new Error(`API keys fetch failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check if backend is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new APIService();

// Export types and service
export default APIService;
