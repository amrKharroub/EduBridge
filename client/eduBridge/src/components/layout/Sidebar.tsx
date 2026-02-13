import { Drawer, List, ListItemButton, ListItemText } from "@mui/material";
import { useNavigate } from "react-router-dom";

const drawerWidth = 240;

const Sidebar = () => {
  const navigate = useNavigate();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
        },
      }}
    >
      <List>
        <ListItemButton onClick={() => navigate("/drive")}>
          <ListItemText primary="Drive" />
        </ListItemButton>

        <ListItemButton onClick={() => navigate("/community")}>
          <ListItemText primary="Community" />
        </ListItemButton>

        <ListItemButton onClick={() => navigate("/chat")}>
          <ListItemText primary="Chat" />
        </ListItemButton>
      </List>
    </Drawer>
  );
};

export default Sidebar;
