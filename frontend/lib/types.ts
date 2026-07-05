export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface UploadedFile {
  id: string;
  filename: string;
  file_type: "pdf" | "csv" | "xlsx";
  size_bytes: number;
  status: "uploaded" | "ingested" | "failed";
  uploaded_at: string;
}

export interface PlanStep {
  step_id: string;
  agent: "rag" | "data_analysis" | "python_exec" | "report" | "forecast" | "mail";
  instruction: string;
  depends_on: string[];
  status: "pending" | "running" | "done" | "failed";
}

export interface AgentStatusEvent {
  agent: string;
  status: string;
}

export interface Citation {
  source_file: string;
  page: number;
  chunk_index: number;
  snippet: string;
}

export interface ArtifactRef {
  id: string;
  title: string;
  type: string;
  mime_type: string;
}

export interface FinalPayload {
  content: string;
  citations: Citation[];
  artifacts: ArtifactRef[];
}

export interface ChatTurn {
  id: string;
  question: string;
  streamingAnswer: string;
  finalPayload: FinalPayload | null;
  plan: PlanStep[];
  agentStatuses: AgentStatusEvent[];
  isStreaming: boolean;
  error: string | null;
}
