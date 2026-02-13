import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  Link,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AuthLayout from '../../../components/layout/AuthLayout';

const ResetPassword = () => {
  const navigate = useNavigate();
  const [code, setCode] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setError('');

    if (!code.trim()) {
      setError('Please enter the verification code');
      return;
    }

    // Mock API call – verify code
    try {
      // Simulate network request
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      // Mock validation: code should be 8 characters alphanumeric
      if (code.length === 8 && /^[A-Z0-9]+$/.test(code)) {
        setSuccess(true);
        // In a real app, you'd redirect to set new password page
        setTimeout(() => navigate('/login'), 3000);
      } else {
        setError('Invalid code. Please check your email and try again.');
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    }
  };

  return (
    <AuthLayout>
      <Typography component="h1" variant="h5" align="center" gutterBottom>
        Reset Password
      </Typography>
      {success ? (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Alert severity="success" sx={{ mb: 2 }}>
            Code verified successfully! Redirecting to login...
          </Alert>
          <Typography variant="body2" color="text.secondary">
            You can now{' '}
            <Link component={RouterLink} to="/login">
              login
            </Link>{' '}
            with your new password.
          </Typography>
        </Box>
      ) : (
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter the 8-character verification code sent to your email address.
          </Typography>
          <TextField
            margin="dense"
            required
            fullWidth
            size="small"
            id="code"
            label="Verification Code"
            name="code"
            autoComplete="off"
            autoFocus
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            error={submitted && !!error}
            helperText={submitted && error ? error : 'e.g., 54J43V9V'}
            inputProps={{ maxLength: 8, style: { textTransform: 'uppercase' } }}
            sx={{ mb: 2 }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 1, mb: 2 }}
          >
            Verify Code
          </Button>
          <Box display="flex" justifyContent="center">
            <Link component={RouterLink} to="/login" variant="body2">
              Back to Login
            </Link>
          </Box>
        </Box>
      )}
    </AuthLayout>
  );
};

export default ResetPassword;