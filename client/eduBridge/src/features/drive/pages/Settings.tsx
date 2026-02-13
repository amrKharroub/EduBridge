import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  LinearProgress,
  Grid,
  Alert,
} from '@mui/material';
import { usePageTitle } from '../../../context/PageTitleContext';

// ========== Mock Data ==========
const mockStorageUsed = 2.3; // GB
const mockVectorUsed = 1.2; // GB
const TOTAL_STORAGE = 5; // GB

// ========== Change Email Component ==========
interface EmailForm {
  newEmail: string;
  password: string;
}

const ChangeEmailSection = () => {
  const [form, setForm] = useState<EmailForm>({ newEmail: '', password: '' });
  const [touched, setTouched] = useState({ newEmail: false, password: false });
  const [submitted, setSubmitted] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setSuccess(false);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setTouched({ ...touched, [e.target.name]: true });
  };

  const isFieldEmpty = (value: string) => value.trim() === '';
  const showError = (field: keyof EmailForm) =>
    (touched[field] || submitted) && isFieldEmpty(form[field]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    if (isFieldEmpty(form.newEmail) || isFieldEmpty(form.password)) return;
    // TODO: API call
    console.log('Change email:', form);
    setSuccess(true);
    setForm({ newEmail: '', password: '' });
    setSubmitted(false);
    setTouched({ newEmail: false, password: false });
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
        Change Email
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="newEmail"
          label="New Email"
          type="email"
          value={form.newEmail}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('newEmail')}
          helperText={showError('newEmail') ? 'New email is required' : ' '}
          sx={{ mb: 1 }}
        />
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="password"
          label="Current Password"
          type="password"
          value={form.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('password')}
          helperText={showError('password') ? 'Password is required' : ' '}
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" size="small">
          Update Email
        </Button>
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Email update request sent! (Demo)
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

// ========== Change Password Component ==========
interface PasswordForm {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

const ChangePasswordSection = () => {
  const [form, setForm] = useState<PasswordForm>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [touched, setTouched] = useState({
    currentPassword: false,
    newPassword: false,
    confirmPassword: false,
  });
  const [submitted, setSubmitted] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setSuccess(false);
    setError('');
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setTouched({ ...touched, [e.target.name]: true });
  };

  const isFieldEmpty = (value: string) => value.trim() === '';
  const showError = (field: keyof PasswordForm) =>
    (touched[field] || submitted) && isFieldEmpty(form[field]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setError('');

    // Check empty fields
    if (
      isFieldEmpty(form.currentPassword) ||
      isFieldEmpty(form.newPassword) ||
      isFieldEmpty(form.confirmPassword)
    ) {
      return;
    }

    // Check password match
    if (form.newPassword !== form.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    // TODO: API call
    console.log('Change password:', {
      current: form.currentPassword,
      new: form.newPassword,
    });
    setSuccess(true);
    setForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
    setSubmitted(false);
    setTouched({
      currentPassword: false,
      newPassword: false,
      confirmPassword: false,
    });
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
        Change Password
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="currentPassword"
          label="Current Password"
          type="password"
          value={form.currentPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('currentPassword')}
          helperText={showError('currentPassword') ? 'Current password is required' : ' '}
          sx={{ mb: 1 }}
        />
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="newPassword"
          label="New Password"
          type="password"
          value={form.newPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('newPassword')}
          helperText={showError('newPassword') ? 'New password is required' : ' '}
          sx={{ mb: 1 }}
        />
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="confirmPassword"
          label="Confirm New Password"
          type="password"
          value={form.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('confirmPassword') || !!error}
          helperText={
            showError('confirmPassword')
              ? 'Please confirm your password'
              : error || ' '
          }
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" size="small">
          Update Password
        </Button>
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Password updated successfully! (Demo)
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

// ========== Change Username Component ==========
interface UsernameForm {
  username: string;
}

const ChangeUsernameSection = () => {
  const [form, setForm] = useState<UsernameForm>({ username: '' });
  const [touched, setTouched] = useState({ username: false });
  const [submitted, setSubmitted] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ username: e.target.value });
    setSuccess(false);
  };

  const handleBlur = () => {
    setTouched({ username: true });
  };

  const isFieldEmpty = (value: string) => value.trim() === '';
  const showError = (field: keyof UsernameForm) =>
    (touched[field] || submitted) && isFieldEmpty(form[field]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    if (isFieldEmpty(form.username)) return;
    // TODO: API call
    console.log('Change username:', form);
    setSuccess(true);
    setForm({ username: '' });
    setSubmitted(false);
    setTouched({ username: false });
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
        Change Username
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="username"
          label="New Username"
          value={form.username}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('username')}
          helperText={showError('username') ? 'Username is required' : ' '}
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" size="small">
          Update Username
        </Button>
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Username updated to {form.username}! (Demo)
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

// ========== Storage Usage Component ==========
interface StorageProps {
  used: number;
  total: number;
  label: string;
}

const StorageMeter: React.FC<StorageProps> = ({ used, total, label }) => {
  const percentage = (used / total) * 100;
  const formattedUsed = used.toFixed(1);
  const formattedTotal = total.toFixed(0);

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" color="text.secondary">
          {formattedUsed} GB / {formattedTotal} GB
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={percentage}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[700],
        }}
      />
    </Box>
  );
};

// ========== Main Settings Page ==========
const Settings = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('Settings');
  }, [setTitle]);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Settings
      </Typography>

      {/* Storage Overview Cards */}
    <Grid container spacing={3} sx={{ mb: 4 }}>
    <Grid size={{ xs: 12, md: 6 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
            Storage Usage
        </Typography>
        <StorageMeter
            used={mockStorageUsed}
            total={TOTAL_STORAGE}
            label="Drive Storage"
        />
        <Typography variant="caption" color="text.secondary">
            Files, folders, and uploaded documents
        </Typography>
        </Paper>
    </Grid>
    <Grid size={{ xs: 12, md: 6 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
            Vector Store Usage
        </Typography>
        <StorageMeter
            used={mockVectorUsed}
            total={TOTAL_STORAGE}
            label="Vector Storage"
        />
        <Typography variant="caption" color="text.secondary">
            Embeddings and AI-generated vectors
        </Typography>
        </Paper>
    </Grid>
    </Grid>

      {/* Account Settings Sections */}
      <ChangeUsernameSection />
      <ChangeEmailSection />
      <ChangePasswordSection />
    </Box>
  );
};

export default Settings;