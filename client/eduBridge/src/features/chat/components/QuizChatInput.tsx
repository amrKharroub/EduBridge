import React, { useState } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Autocomplete,
  Chip,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

// Mock list of available documents (renamed from books)
const mockDocuments = [
  'Mathematics Grade 6.pdf',
  'Algebra Fundamentals.docx',
  'Geometry 101.pdf',
  'World History - 20th Century.pdf',
  'Introduction to Physics.docx',
  'Chemistry Basics.pdf',
  'Literature Anthology Vol.1.pdf',
  'Computer Science Principles.docx',
];

interface QuizChatInputProps {
  onSendMessage: (prompt: string, documents: string[]) => void;
  disabled?: boolean;
}

const QuizChatInput: React.FC<QuizChatInputProps> = ({ onSendMessage, disabled }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);

  const handleSend = () => {
    if (prompt.trim() && selectedDocs.length > 0) {
      onSendMessage(prompt.trim(), selectedDocs);
      setPrompt('');
      // Keep documents selected for next request
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, width: '100%' }}>
      {/* Document selector */}
      <Autocomplete
        multiple
        size="small"
        options={mockDocuments}
        value={selectedDocs}
        onChange={(_event, newValue) => setSelectedDocs(newValue)}
        renderInput={(params: any) => (
          <TextField
            {...params}
            label="Select documents"
            placeholder="Choose documents"
            required
          />
        )}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => (
            <Chip
              label={option}
              size="small"
              {...getTagProps({ index })}
            />
          ))
        }
      />
      {/* Prompt + send */}
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Describe the quiz you want (e.g., '10 multiple choice questions on chapter 3')"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
          size="small"
          variant="outlined"
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!prompt.trim() || selectedDocs.length === 0 || disabled}
          sx={{ alignSelf: 'flex-end' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default QuizChatInput;