import React from 'react';
import { ToggleButton, ToggleButtonGroup, Box } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import QuizIcon from '@mui/icons-material/Quiz';

export type AgentType = 'general' | 'quiz';

interface AgentSelectorProps {
  agent: AgentType;
  onChange: (agent: AgentType) => void;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({ agent, onChange }) => {
  const handleChange = (
    _event: React.MouseEvent<HTMLElement>,
    newAgent: AgentType | null,
  ) => {
    if (newAgent) {
      onChange(newAgent);
    }
  };

  return (
    <ToggleButtonGroup
      value={agent}
      exclusive
      onChange={handleChange}
      size="small"
      color="primary"
      sx={{ mr: 1 }}
    >
      <ToggleButton value="general">
        <ChatIcon sx={{ mr: 0.5, fontSize: 18 }} />
        General
      </ToggleButton>
      <ToggleButton value="quiz">
        <QuizIcon sx={{ mr: 0.5, fontSize: 18 }} />
        Quiz
      </ToggleButton>
    </ToggleButtonGroup>
  );
};

export default AgentSelector;