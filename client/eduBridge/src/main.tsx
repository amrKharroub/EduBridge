import React from 'react';
import ReactDOM from 'react-dom/client';
import { CssBaseline } from '@mui/material';
import { ThemeProvider } from './theme/ThemeContext'; // our custom provider
import App from './app/App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
