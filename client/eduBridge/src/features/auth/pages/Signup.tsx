import React, { useState, useEffect  } from 'react';
import {
  TextField,
  Button,
  Typography,
  Link,
  Box,
  Grid,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AuthLayout from '../../../components/layout/AuthLayout';
import { usePageTitle } from '../../../context/PageTitleContext';


interface FormData {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  dob: string;
}

interface Touched {
  username: boolean;
  email: boolean;
  firstName: boolean;
  lastName: boolean;
  password: boolean;
  dob: boolean;
}

const Signup = () => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    password: '',
    dob: '',
  });

  const [touched, setTouched] = useState<Touched>({
    username: false,
    email: false,
    firstName: false,
    lastName: false,
    password: false,
    dob: false,
  });

  const [submitted, setSubmitted] = useState(false);

  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('EduBridge');
  }, [setTitle]);

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

    setTouched({
      username: true,
      email: true,
      firstName: true,
      lastName: true,
      password: true,
      dob: true,
    });

    const hasError = Object.values(formData).some((val) => isFieldEmpty(val));
    if (hasError) return;

    console.log('Signup:', formData);
  };

  return (
    <AuthLayout>
      <Typography
        component="h1"
        variant="h5"
        align="center"
        sx={{ mb: 1 }} // reduced bottom margin
      >
        Sign Up
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate>
        {/* Username - dense & small */}
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          id="username"
          label="Username"
          name="username"
          autoComplete="username"
          autoFocus
          value={formData.username}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('username')}
          helperText={showError('username') ? 'Username is required' : ' '}
        />
        {/* Email - dense & small */}
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          id="email"
          label="Email Address"
          name="email"
          autoComplete="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('email')}
          helperText={showError('email') ? 'Email is required' : ' '}
        />
        {/* First & Last Name side by side */}
        <Grid container spacing={1}>
        <Grid size={{ xs: 6 }}>
            <TextField
            margin="dense"
            required
            fullWidth
            size="small"
            id="firstName"
            label="First Name"
            name="firstName"
            autoComplete="given-name"
            value={formData.firstName}
            onChange={handleChange}
            onBlur={handleBlur}
            error={showError('firstName')}
            helperText={showError('firstName') ? 'Required' : ' '}
            />
        </Grid>
        <Grid size={{ xs: 6 }}>
            <TextField
            margin="dense"
            required
            fullWidth
            size="small"
            id="lastName"
            label="Last Name"
            name="lastName"
            autoComplete="family-name"
            value={formData.lastName}
            onChange={handleChange}
            onBlur={handleBlur}
            error={showError('lastName')}
            helperText={showError('lastName') ? 'Required' : ' '}
            />
        </Grid>
        </Grid>
        {/* Password - dense & small */}
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="password"
          label="Password"
          type="password"
          id="password"
          autoComplete="new-password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('password')}
          helperText={showError('password') ? 'Password is required' : ' '}
        />
        {/* Date of Birth - dense & small */}
        <TextField
          margin="dense"
          required
          fullWidth
          size="small"
          name="dob"
          label="Date of Birth"
          type="date"
          id="dob"
          InputLabelProps={{ shrink: true }}
          value={formData.dob}
          onChange={handleChange}
          onBlur={handleBlur}
          error={showError('dob')}
          helperText={showError('dob') ? 'Date of birth is required' : ' '}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 2, mb: 1 }} // reduced top margin
        >
          Sign Up
        </Button>
        <Box display="flex" justifyContent="flex-end">
          <Link component={RouterLink} to="/login" variant="body2">
            {'Already have an account? Sign In'}
          </Link>
        </Box>
      </Box>
    </AuthLayout>
  );
};

export default Signup;