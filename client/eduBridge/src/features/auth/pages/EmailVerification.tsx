import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Alert, CircularProgress } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AuthLayout from '../../../components/layout/AuthLayout';

const EmailVerification = () => {
  const { key } = useParams<{ key: string }>();
  const navigate = useNavigate();
  const [verifying, setVerifying] = useState(true);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Simulate API call to verify email
    const verifyEmail = async () => {
      try {
        // TODO: Replace with actual API call
        await new Promise((resolve) => setTimeout(resolve, 1500));
        // Mock success – in real app, send key to backend
        if (key && key.length > 5) {
          setVerified(true);
        } else {
          setError('Invalid verification link');
        }
      } catch (err) {
        setError('Verification failed. Please try again.');
      } finally {
        setVerifying(false);
      }
    };
    verifyEmail();
  }, [key]);

  const handleContinue = () => {
    navigate('/drive/my-files');
  };

  return (
    <AuthLayout>
      <Box sx={{ textAlign: 'center', py: 2 }}>
        {verifying ? (
          <>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography variant="h6">Verifying your email...</Typography>
          </>
        ) : verified ? (
          <>
            <CheckCircleIcon color="success" sx={{ fontSize: 64, mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Email Verified!
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Your email has been successfully verified. You can now access all features.
            </Typography>
            <Button variant="contained" onClick={handleContinue}>
              Go to My Drive
            </Button>
          </>
        ) : (
          <>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error || 'Verification failed'}
            </Alert>
            <Button variant="outlined" onClick={() => navigate('/login')}>
              Back to Login
            </Button>
          </>
        )}
      </Box>
    </AuthLayout>
  );
};

export default EmailVerification;