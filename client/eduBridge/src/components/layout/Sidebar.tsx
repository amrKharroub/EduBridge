import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import FolderIcon from '@mui/icons-material/Folder';
import PeopleIcon from '@mui/icons-material/People';
import PublicIcon from '@mui/icons-material/Public';
import ChatIcon from '@mui/icons-material/Chat';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 240;

// Main navigation items
const mainMenuItems = [
  { text: 'My files', icon: <FolderIcon />, path: '/drive/my-files' },
  { text: 'Shared with me', icon: <PeopleIcon />, path: '/drive/shared' },
  { text: 'Community', icon: <PublicIcon />, path: '/drive/community' },
  { text: 'Chat', icon: <ChatIcon />, path: '/drive/chat' },
];

// Settings item (bottom)
const settingsMenuItem = { text: 'Settings', icon: <SettingsIcon />, path: '/drive/settings' };

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  variant: 'permanent' | 'temporary';
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, variant }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      <Toolbar /> {/* Spacer for top bar */}
      
      {/* Main navigation items */}
      <List sx={{ flexGrow: 1 }}>
        {mainMenuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (variant === 'temporary') onClose();
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Divider before settings */}
      <Divider />

      {/* Settings at bottom */}
      <List sx={{ mb: 1 }}>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === settingsMenuItem.path}
            onClick={() => {
              navigate(settingsMenuItem.path);
              if (variant === 'temporary') onClose();
            }}
          >
            <ListItemIcon>{settingsMenuItem.icon}</ListItemIcon>
            <ListItemText primary={settingsMenuItem.text} />
          </ListItemButton>
        </ListItem>
      </List>
    </Drawer>
  );
};

export default Sidebar;