import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';

const getDesignTokens = (mode: 'light' | 'dark'): ThemeOptions => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          primary: { main: '#1976d2' },
          secondary: { main: '#dc004e' },
          background: { default: '#f5f5f5', paper: '#fff' },
        }
      : {
          primary: { main: '#90caf9' },
          secondary: { main: '#f48fb1' },
          background: { default: '#121212', paper: '#1e1e1e' },
        }),
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

export const createAppTheme = (mode: 'light' | 'dark') =>
  createTheme(getDesignTokens(mode));