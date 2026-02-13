import React from 'react';
import type { ReactNode } from 'react';
import { Container, Paper, Box, IconButton } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useThemeContext } from '../../theme/ThemeContext';

interface AuthLayoutProps {
  children: ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  const { mode, toggleColorMode } = useThemeContext();

  return (
    <>
      {/* Theme toggle – fixed to viewport far right */}
      <Box
        sx={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 1200, // above everything
        }}
      >
        <IconButton onClick={toggleColorMode} color="inherit">
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
      </Box>

      {/* Centered form */}
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
          }}
        >
          <Paper elevation={3} sx={{ padding: 3, width: '100%' }}>
            {children}
          </Paper>
        </Box>
      </Container>
    </>
  );
};

export default AuthLayout;