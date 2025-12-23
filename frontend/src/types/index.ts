export interface Company {
  name: string;
  ticker?: string;
  industry?: string;
}

export interface ESGScores {
  environmental: number;
  social: number;
  governance: number;
  overall: number;
}

export interface SDGImpact {
  goal: number;
  title: string;
  score: number;
  impact: 'positive' | 'negative' | 'neutral';
  evidence: string[];
}

export interface GreenwashingAlert {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  description: string;
  evidence: string[];
  confidence: number;
}

export interface AgentStatus {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'completed' | 'debating';
  currentTask?: string;
  progress: number;
  findings?: string[];
  avatar?: string;
}

export interface DebateMessage {
  agentId: string;
  agentName: string;
  message: string;
  timestamp: Date;
  stance: 'support' | 'challenge' | 'neutral';
}

export interface AnalysisResult {
  company: Company;
  esgScores: ESGScores;
  sdgImpacts: SDGImpact[];
  greenwashingAlerts: GreenwashingAlert[];
  agents: AgentStatus[];
  debate: DebateMessage[];
  analysisDate: Date;
  confidence: number;
}

export interface WebSocketMessage {
  type: 'agent_update' | 'debate_message' | 'analysis_complete' | 'error';
  data: any;
}

export const SDG_GOALS = [
  { number: 1, title: 'No Poverty', color: '#E5243B' },
  { number: 2, title: 'Zero Hunger', color: '#DDA63A' },
  { number: 3, title: 'Good Health', color: '#4C9F38' },
  { number: 4, title: 'Quality Education', color: '#C5192D' },
  { number: 5, title: 'Gender Equality', color: '#FF3A21' },
  { number: 6, title: 'Clean Water', color: '#26BDE2' },
  { number: 7, title: 'Clean Energy', color: '#FCC30B' },
  { number: 8, title: 'Decent Work', color: '#A21942' },
  { number: 9, title: 'Innovation', color: '#FD6925' },
  { number: 10, title: 'Reduced Inequality', color: '#DD1367' },
  { number: 11, title: 'Sustainable Cities', color: '#FD9D24' },
  { number: 12, title: 'Responsible Consumption', color: '#BF8B2E' },
  { number: 13, title: 'Climate Action', color: '#3F7E44' },
  { number: 14, title: 'Life Below Water', color: '#0A97D9' },
  { number: 15, title: 'Life on Land', color: '#56C02B' },
  { number: 16, title: 'Peace & Justice', color: '#00689D' },
  { number: 17, title: 'Partnerships', color: '#19486A' },
];
