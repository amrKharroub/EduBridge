import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import HistoryIcon from '@mui/icons-material/History';
import { usePageTitle } from '../../../context/PageTitleContext';
import ChatMessage from '../components/ChatMessage';
import type { Message } from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import QuizChatInput from '../components/QuizChatInput';
import AgentSelector from '../components/AgentSelector';
import type { AgentType } from '../components/AgentSelector';
import type { ChatSession } from '../../../types/chatType';
import type { QuizData } from '../components/QuizCard';

// Mock responses
const mockGeneralResponses = [
  "According to Active Learning Strategies, low-stakes quizzes improve long-term memory retention because they involve retrieval practice, which requires students to actively recall information rather than passively review it. This strengthens memory and enhances understanding. \n \n Two main examples are Think-Pair-Share and Retrieval Practice as two active learning techniques.",
];

const generateMockQuiz = (prompt: string, documents: string[]): QuizData => ({
  id: `quiz-${Date.now()}`,
  title: "Quiz: Geometry  Basics",//`Quiz: ${prompt.substring(0, 40)}${prompt.length > 40 ? '…' : ''}`,
  documentSource: documents,
  questions: [
    {
      id: 'q1',
      question: 'What is the sum of the interior angles of a triangle?',
      options: ['90°', '180°', '270°', '360°'],
    },
    {
      id: 'q2',
      question: 'Which formula is used to calculate the area of a circle?',
      options: ['πr²', '2πr', 'πd', 'r²/2'],
    },
    {
      id: 'q3',
      question: 'What is the name of a quadrilateral with exactly one pair of parallel sides?',
      options: ['Rectangle', 'Trapezoid', 'Rhombus', 'Square'],
    },
    {
      id: 'q4',
      question: 'In a right triangle, what is the side opposite the right angle called?',
      options: ['Adjacent', 'Opposite', 'Hypotenuse', 'Median'],
    },
    {
      id: 'q5',
      question: 'If two angles are complementary, what is their sum?',
      options: ['45°', '90°', '180°', '360°'],
    },
  ],
});

// Create default welcome message
const createWelcomeMessage = (): Message => ({
  id: `welcome-${Date.now()}`,
  type: 'text',
  text: "Hello! I'm your EduBridge assistant. How can I help you today?",
  sender: 'agent',
  timestamp: new Date(),
});

// Create new session
const createNewSession = (agentMode: AgentType = 'general'): ChatSession => ({
  id: `session-${Date.now()}`,
  title: 'New Chat',
  agentMode,
  messages: [createWelcomeMessage()],
  createdAt: new Date(),
  updatedAt: new Date(),
});

const Chat = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('Chat');
  }, [setTitle]);

  // Session state
  const [sessions, setSessions] = useState<ChatSession[]>([
    createNewSession('general'),
  ]);
  const [activeSessionId, setActiveSessionId] = useState<string>(sessions[0].id);

  // Chat history dropdown
  const [historyAnchorEl, setHistoryAnchorEl] = useState<null | HTMLElement>(null);
  const historyOpen = Boolean(historyAnchorEl);

  // Typing indicator
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get active session
  const activeSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession.messages]);

  // Helper: update session with functional state
  const updateSession = (sessionId: string, updater: (session: ChatSession) => ChatSession) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? updater(s) : s))
    );
  };

  // Add message to active session (using functional update)
  const addMessage = (message: Message) => {
    updateSession(activeSessionId, (session) => ({
      ...session,
      messages: [...session.messages, message],
      updatedAt: new Date(),
    }));
  };

  // Update session title
  const updateSessionTitle = (sessionId: string, title: string) => {
    updateSession(sessionId, (session) => ({ ...session, title }));
  };

  // Update session agent mode
  const updateSessionAgentMode = (sessionId: string, agentMode: AgentType) => {
    updateSession(sessionId, (session) => ({ ...session, agentMode }));
  };

  // Handle general message send
  const handleGeneralSend = (text: string) => {
    // Auto-rename if first user message and title is still "New Chat"
    if (
      activeSession.title === 'New Chat' &&
      activeSession.messages.filter((m) => m.sender === 'user').length === 0
    ) {
      const newTitle = text.length > 30 ? `${text.substring(0, 27)}…` : text;
      updateSessionTitle(activeSessionId, newTitle);
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'text',
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    addMessage(userMessage);

    setIsTyping(true);
    setTimeout(() => {
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        type: 'text',
        text: mockGeneralResponses[Math.floor(Math.random() * mockGeneralResponses.length)],
        sender: 'agent',
        timestamp: new Date(),
      };
      addMessage(agentMessage);
      setIsTyping(false);
    }, 1500);
  };

  // Handle quiz send
  const handleQuizSend = (prompt: string, documents: string[]) => {
    // Auto-rename if needed
    if (activeSession.title === 'New Chat') {
      const newTitle = `Quiz: ${documents[0]?.substring(0, 20) || 'Untitled'}…`;
      updateSessionTitle(activeSessionId, newTitle);
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'text',
      text: `[Quiz Request]\nDocuments: ${documents.join(', ')}\n\n${prompt}`,
      sender: 'user',
      timestamp: new Date(),
    };
    addMessage(userMessage);

    setIsTyping(true);
    setTimeout(() => {
      const quiz = generateMockQuiz(prompt, documents);
      const quizMessage: Message = {
        id: `quiz-${Date.now()}`,
        type: 'quiz',
        quiz,
        sender: 'agent',
        timestamp: new Date(),
      };
      addMessage(quizMessage);
      setIsTyping(false);
    }, 2000);
  };

  // Switch agent mode
  const handleAgentModeChange = (newMode: AgentType) => {
    if (newMode === activeSession.agentMode) return;

    updateSessionAgentMode(activeSessionId, newMode);

    const systemMessage: Message = {
      id: `system-${Date.now()}`,
      type: 'text',
      text:
        newMode === 'general'
          ? 'Switched to General Assistant. How can I help?'
          : 'Switched to Quiz Generator. Select documents and describe the quiz you need.',
      sender: 'agent',
      timestamp: new Date(),
    };
    addMessage(systemMessage);
  };

  // Create new session
  const handleNewSession = () => {
    const newSession = createNewSession(activeSession?.agentMode || 'general');
    setSessions((prev) => [...prev, newSession]);
    setActiveSessionId(newSession.id);
    setHistoryAnchorEl(null); // close dropdown
  };

  // Delete session
  const handleDeleteSession = (sessionId: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      const remaining = sessions.filter((s) => s.id !== sessionId);
      if (remaining.length > 0) {
        setActiveSessionId(remaining[0].id);
      } else {
        const newSession = createNewSession('general');
        setSessions([newSession]);
        setActiveSessionId(newSession.id);
      }
    }
    setHistoryAnchorEl(null);
  };

  // Select session
  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setHistoryAnchorEl(null);
  };

  // Sort sessions for dropdown (most recent first)
  const sortedSessions = [...sessions].sort(
    (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header with title + controls */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
          pb: 1,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="h5" noWrap sx={{ maxWidth: '60%' }}>
          {activeSession?.title || 'Chat'}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* History dropdown */}
          <Button
            variant="outlined"
            size="small"
            startIcon={<HistoryIcon />}
            onClick={(e) => setHistoryAnchorEl(e.currentTarget)}
            aria-controls={historyOpen ? 'chat-history-menu' : undefined}
            aria-expanded={historyOpen ? 'true' : undefined}
          >
            History
          </Button>
          {/* New chat button */}
          <Button
            variant="contained"
            size="small"
            startIcon={<AddIcon />}
            onClick={handleNewSession}
          >
            New Chat
          </Button>
        </Box>

        {/* History dropdown menu */}
        <Menu
          id="chat-history-menu"
          anchorEl={historyAnchorEl}
          open={historyOpen}
          onClose={() => setHistoryAnchorEl(null)}
          MenuListProps={{ dense: true }}
          sx={{ maxHeight: 400 }}
        >
          {sortedSessions.length === 0 ? (
            <MenuItem disabled>No chats</MenuItem>
          ) : (
            sortedSessions.map((session) => (
              <MenuItem key={session.id} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box
                  sx={{ display: 'flex', alignItems: 'center', flex: 1 }}
                  onClick={() => handleSelectSession(session.id)}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <ChatIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={session.title}
                    secondary={session.updatedAt.toLocaleDateString()}
                    primaryTypographyProps={{ noWrap: true, sx: { maxWidth: 200 } }}
                  />
                </Box>
                <IconButton
                  edge="end"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSession(session.id);
                  }}
                >
                  <DeleteOutlineIcon fontSize="small" />
                </IconButton>
              </MenuItem>
            ))
          )}
          <Divider />
          <MenuItem onClick={handleNewSession}>
            <ListItemIcon sx={{ minWidth: 36 }}>
              <AddIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Start new chat" />
          </MenuItem>
        </Menu>
      </Box>

      {/* Chat area */}
      <Paper
        elevation={2}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          bgcolor: 'background.default',
          minHeight: 0,
        }}
      >
        {/* Messages */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {activeSession?.messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isTyping && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Paper
                elevation={1}
                sx={{
                  p: 1.5,
                  backgroundColor: (theme) =>
                    theme.palette.mode === 'light' ? 'grey.100' : 'grey.800',
                  borderRadius: '18px 18px 18px 4px',
                }}
              >
                <Typography variant="body2">...</Typography>
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input area */}
        <Box
          sx={{
            p: 2,
            bgcolor: 'background.paper',
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AgentSelector
              agent={activeSession?.agentMode || 'general'}
              onChange={handleAgentModeChange}
            />
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
              {activeSession?.agentMode === 'general'
                ? 'General assistance'
                : 'Generate quizzes from documents'}
            </Typography>
          </Box>

          {activeSession?.agentMode === 'general' ? (
            <ChatInput onSendMessage={handleGeneralSend} disabled={isTyping} />
          ) : (
            <QuizChatInput onSendMessage={handleQuizSend} disabled={isTyping} />
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default Chat;