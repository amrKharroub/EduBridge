import React, { useState } from 'react';
import { Box, Toolbar } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import TopBar from './TopBar';
import Sidebar from './Sidebar';

const drawerWidth = 240;

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  const handleDrawerClose = () => {
    setIsClosing(true);
    setMobileOpen(false);
    setIsClosing(false);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Fixed Top Bar */}
      <TopBar onMenuClick={handleDrawerToggle} showMenuButton={isMobile} />

      {/* Sidebar - responsive */}
      <Sidebar
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerClose}
        variant={isMobile ? 'temporary' : 'permanent'}
      />

      {/* Main content - pushes right when drawer is permanent */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar /> {/* Spacer to push content below fixed AppBar */}
        {children}
      </Box>
    </Box>
  );
};

export default DashboardLayout;