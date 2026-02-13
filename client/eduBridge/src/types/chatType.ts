import type { Message } from '../features/chat/components/ChatMessage';
import type { AgentType } from '../features/chat/components/AgentSelector';

export interface ChatSession {
  id: string;
  title: string;
  agentMode: AgentType;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}