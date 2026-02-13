import React, { useState } from 'react';
import { TextField, IconButton, Paper } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        borderRadius: 2,
      }}
    >
      <TextField
        fullWidth
        multiline
        maxRows={4}
        placeholder="Type your message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
        size="small"
        variant="outlined"
      />
      <IconButton
        color="primary"
        onClick={handleSend}
        disabled={!message.trim() || disabled}
        sx={{ alignSelf: 'flex-end' }}
      >
        <SendIcon />
      </IconButton>
    </Paper>
  );
};

export default ChatInput;