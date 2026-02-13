import { Box, Toolbar } from "@mui/material";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface Props {
  children: React.ReactNode;
}

const Layout = ({ children }: Props) => {
  return (
    <Box sx={{ display: "flex" }}>
      <Topbar />
      <Sidebar />

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
