import { Box, Button, TextField, Typography, Paper } from "@mui/material";
import { useAuthStore } from "../store/authStore";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleLogin = () => {
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
      <Paper sx={{ p: 4, width: 400 }}>
        <Typography variant="h5" mb={2}>
          Login
        </Typography>

        <TextField fullWidth label="Email" margin="normal" />
        <TextField fullWidth label="Password" type="password" margin="normal" />

        <Button
          variant="contained"
          fullWidth
          sx={{ mt: 2 }}
          onClick={handleLogin}
        >
          Login
        </Button>
      </Paper>
    </Box>
  );
};

export default LoginPage;
