import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Link,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useState } from "react";

const SignupPage = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange =
    (field: keyof typeof form) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({
        ...prev,
        [field]: event.target.value,
      }));
    };

  const handleSignup = () => {
    if (!form.email || !form.password) return;

    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    // Mock signup → auto login
    login();
    navigate("/drive");
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
    >
      <Paper sx={{ p: 4, width: 420 }}>
        <Typography variant="h5" mb={2}>
          Create Account
        </Typography>

        <TextField
          fullWidth
          label="Full Name"
          margin="normal"
          value={form.name}
          onChange={handleChange("name")}
        />

        <TextField
          fullWidth
          label="Email"
          margin="normal"
          value={form.email}
          onChange={handleChange("email")}
        />

        <TextField
          fullWidth
          label="Password"
          type="password"
          margin="normal"
          value={form.password}
          onChange={handleChange("password")}
        />

        <TextField
          fullWidth
          label="Confirm Password"
          type="password"
          margin="normal"
          value={form.confirmPassword}
          onChange={handleChange("confirmPassword")}
        />

        <Button
          variant="contained"
          fullWidth
          sx={{ mt: 2 }}
          onClick={handleSignup}
        >
          Sign Up
        </Button>

        <Typography variant="body2" mt={2} textAlign="center">
          Already have an account?{" "}
          <Link
            component="button"
            variant="body2"
            onClick={() => navigate("/login")}
          >
            Login
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
};

export default SignupPage;
