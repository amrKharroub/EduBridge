import React, { useState, useEffect } from 'react';
import {
  TextField,
  Button,
  Typography,
  Link,
  Box,
  Divider,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AuthLayout from '../../../components/layout/AuthLayout';
import { usePageTitle } from '../../../context/PageTitleContext';

// Simple Google SVG icon
const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24">
    <path
      fill="currentColor"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="currentColor"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="currentColor"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
    />
    <path
      fill="currentColor"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
    />
  </svg>
);

interface FormData {
  email: string;
  password: string;
}

interface Touched {
  email: boolean;
  password: boolean;
}

const Login = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('EduBridge');
  }, [setTitle]);

  const [formData, setFormData] = useState<FormData>({ email: '', password: '' });
  const [touched, setTouched] = useState<Touched>({ email: false, password: false });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
  };

  const isFieldEmpty = (value: string) => value.trim() === '';
  const showError = (field: keyof FormData) =>
    (touched[field] || submitted) && isFieldEmpty(formData[field]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTouched({ email: true, password: true });

    if (isFieldEmpty(formData.email) || isFieldEmpty(formData.password)) return;
    console.log('Login:', formData);
  };

  const handleGoogleSignIn = () => {
    console.log('Continue with Google');
    // TODO: integrate Google OAuth
  };

  return (
    <AuthLayout>
      {/* Welcome header */}
      <Typography
        component="h1"
        variant="h4"
        align="center"
        sx={{ fontWeight: 500, mb: 0.5 }}
      >
        Welcome back
      </Typography>
      <Typography
        variant="body2"
        align="center"
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Sign in to your account
      </Typography>


      {/* Email/Password Form */}
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 0 }}>
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          id="email"
          label="Email Address"
          name="email"
          autoComplete="email"
          autoFocus
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('email')}
          helperText={showError('email') ? 'Email is required' : ' '}
        />
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="password"
          label="Password"
          type="password"
          id="password"
          autoComplete="current-password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('password')}
          helperText={showError('password') ? 'Password is required' : ' '}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 2, mb: 1.5 }}
        >
          Sign In
        </Button>
        
        {/* Google Sign-In Button */}
        <Divider sx={{ my: 2.5 }}>or</Divider>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<GoogleIcon />}
          onClick={handleGoogleSignIn}
          sx={{
            py: 1.2,
            color: 'text.primary',
            borderColor: 'divider',
            '&:hover': { borderColor: 'text.primary' },
          }}
        >
          Continue with Google
        </Button>

        <Box display="flex" justifyContent="flex-end">
          <Link component={RouterLink} to="/signup" variant="body2">
            {"Don't have an account? Sign Up"}
          </Link>
        </Box>
      </Box>
    </AuthLayout>
  );
};

export default Login;