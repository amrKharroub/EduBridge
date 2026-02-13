import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  IconButton,
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import type { ChatSession } from '../../../types/chatType';
import { formatDistanceToNow } from 'date-fns';

interface ChatListProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
}

const ChatList: React.FC<ChatListProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}) => {
  // Sort by updatedAt descending
  const sortedSessions = [...sessions].sort(
    (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
  );

  return (
    <Paper
      elevation={2}
      sx={{
        width: 280,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="subtitle1" fontWeight="bold">
          Chats
        </Typography>
        <IconButton size="small" onClick={onNewSession} color="primary">
          <AddIcon />
        </IconButton>
      </Box>

      {/* Chat list */}
      <List sx={{ flex: 1, overflowY: 'auto', p: 1 }}>
        {sortedSessions.length === 0 ? (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No chats yet
            </Typography>
          </Box>
        ) : (
          sortedSessions.map((session) => (
            <ListItem
              key={session.id}
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                >
                  <DeleteOutlineIcon fontSize="small" />
                </IconButton>
              }
              sx={{ mb: 0.5 }}
            >
              <ListItemButton
                selected={activeSessionId === session.id}
                onClick={() => onSelectSession(session.id)}
                sx={{ borderRadius: 1 }}
              >
                <ListItemText
                  primary={
                    <Typography variant="body2" noWrap sx={{ maxWidth: 180 }}>
                      {session.title}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {formatDistanceToNow(session.updatedAt, { addSuffix: true })}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))
        )}
      </List>
    </Paper>
  );
};

export default ChatList;