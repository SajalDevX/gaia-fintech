import axios from 'axios';
import type { AgentStatus } from '../types';

// @ts-ignore - Vite env
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
// @ts-ignore - Vite env
const WS_BASE_URL = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalysisStartResponse {
  analysis_id: string;
  status: string;
  ticker: string;
  message: string;
  websocket_url: string;
  estimated_duration: number;
  created_at: string;
}

export interface BlockchainStatus {
  chain_length: number;
  total_transactions: number;
  smart_contracts: number;
  triggered_contracts: number;
  pending_transactions: number;
  is_valid: boolean;
}

export class AnalysisAPI {
  /**
   * Start a new analysis for a company
   */
  static async startAnalysis(ticker: string, companyName?: string): Promise<AnalysisStartResponse> {
    const response = await api.post('/api/v1/analyze', {
      ticker: ticker.toUpperCase(),
      company_name: companyName,
      include_satellite: true,
      include_sentiment: true,
      include_supply_chain: true,
      debate_rounds: 3
    });
    return response.data;
  }

  /**
   * Get the status of an ongoing analysis
   */
  static async getAnalysisStatus(analysisId: string): Promise<any> {
    const response = await api.get(`/api/v1/analyze/${analysisId}`);
    return response.data;
  }

  /**
   * Get the full results of a completed analysis
   */
  static async getAnalysisResults(analysisId: string): Promise<any> {
    const response = await api.get(`/api/v1/analyze/${analysisId}/results`);
    return response.data;
  }

  /**
   * Connect to WebSocket for real-time analysis updates
   */
  static connectWebSocket(
    analysisId: string,
    onMessage: (message: any) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void
  ): WebSocket {
    const ws = new WebSocket(`${WS_BASE_URL}/api/v1/analyze/ws/${analysisId}`);

    ws.onopen = () => {
      console.log('WebSocket connected for analysis:', analysisId);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
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

  /**
   * Get blockchain status
   */
  static async getBlockchainStatus(): Promise<BlockchainStatus> {
    const response = await api.get('/api/v1/blockchain/status');
    return response.data;
  }

  /**
   * Get audit trail for a company
   */
  static async getAuditTrail(ticker: string): Promise<any> {
    const response = await api.get(`/api/v1/blockchain/audit/${ticker.toUpperCase()}`);
    return response.data;
  }

  /**
   * Verify blockchain integrity
   */
  static async verifyBlockchain(): Promise<any> {
    const response = await api.get('/api/v1/blockchain/verify');
    return response.data;
  }
}

// Map backend agents to frontend display
export const GAIA_AGENTS: AgentStatus[] = [
  {
    id: 'sentinel',
    name: 'Sentinel',
    role: 'Environmental Monitoring',
    status: 'idle',
    progress: 0,
    avatar: '🛡️',
  },
  {
    id: 'veritas',
    name: 'Veritas',
    role: 'Supply Chain Verification',
    status: 'idle',
    progress: 0,
    avatar: '🔍',
  },
  {
    id: 'pulse',
    name: 'Pulse',
    role: 'Sentiment Analysis',
    status: 'idle',
    progress: 0,
    avatar: '📊',
  },
  {
    id: 'regulus',
    name: 'Regulus',
    role: 'Regulatory Compliance',
    status: 'idle',
    progress: 0,
    avatar: '⚖️',
  },
  {
    id: 'impact',
    name: 'Impact',
    role: 'SDG Quantification',
    status: 'idle',
    progress: 0,
    avatar: '🎯',
  },
  {
    id: 'nexus',
    name: 'NEXUS',
    role: 'Financial Inclusion',
    status: 'idle',
    progress: 0,
    avatar: '🌐',
  },
  {
    id: 'orchestrator',
    name: 'Orchestrator',
    role: 'Adversarial Debate',
    status: 'idle',
    progress: 0,
    avatar: '🧠',
  },
];

export default api;
