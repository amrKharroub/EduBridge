import React from 'react';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import QuizCard from './QuizCard';
import type { QuizData } from './QuizCard';

export interface Message {
  id: string;
  type: 'text' | 'quiz';
  text?: string; // for text messages
  quiz?: QuizData; // for quiz messages
  sender: 'user' | 'agent';
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const theme = useTheme();
  const isUser = message.sender === 'user';

  // User messages are always text bubbles
  if (isUser) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Paper
          elevation={1}
          sx={{
            p: 1.5,
            maxWidth: '70%',
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            borderRadius: '18px 18px 4px 18px',
          }}
        >
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.text}
          </Typography>
          <Typography
            variant="caption"
            sx={{ display: 'block', mt: 0.5, opacity: 0.8 }}
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Typography>
        </Paper>
      </Box>
    );
  }

  // Agent messages: can be text or quiz
  if (message.type === 'quiz' && message.quiz) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
        <QuizCard quiz={message.quiz} />
      </Box>
    );
  }

  // Default text message from agent
  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
      <Paper
        elevation={1}
        sx={{
          p: 1.5,
          maxWidth: '70%',
          backgroundColor: theme.palette.mode === 'light' ? 'grey.100' : 'grey.800',
          color: 'text.primary',
          borderRadius: '18px 18px 18px 4px',
        }}
      >
        <Typography variant="body2">{message.text}</Typography>
        <Typography
          variant="caption"
          sx={{ display: 'block', mt: 0.5, color: 'text.secondary', opacity: 0.8 }}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ChatMessage;