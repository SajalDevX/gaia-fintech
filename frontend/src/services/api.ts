import axios from 'axios';
import type { AnalysisResult, WebSocketMessage } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export class AnalysisAPI {
  static async analyzeCompany(companyName: string): Promise<AnalysisResult> {
    const response = await api.post('/api/analyze', { company_name: companyName });
    return response.data;
  }

  static async getAnalysisStatus(analysisId: string): Promise<any> {
    const response = await api.get(`/api/analysis/${analysisId}/status`);
    return response.data;
  }

  static connectWebSocket(
    analysisId: string,
    onMessage: (message: WebSocketMessage) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void
  ): WebSocket {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/${analysisId}`);

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        onMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    ws.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      onClose?.(event);
    };

    return ws;
  }
}

export default api;
