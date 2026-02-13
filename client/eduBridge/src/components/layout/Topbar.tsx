import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { useAuthStore } from "@features/auth/store/authStore";

const Topbar = () => {
  const { logout } = useAuthStore();

  return (
    <AppBar position="fixed" sx={{ zIndex: 1201 }}>
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        <Typography variant="h6">Drive App</Typography>

        <Button color="inherit" onClick={logout}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Topbar;
