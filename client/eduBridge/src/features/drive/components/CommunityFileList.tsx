import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Typography,
  Box,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import FolderIcon from '@mui/icons-material/Folder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

export interface CommunityFileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  owner: string;
  description: string;
  modified: string;
  size: string;
}

interface CommunityFileListProps {
  files: CommunityFileItem[];
  onFolderClick: (folderId: string, folderName: string) => void;
  onDownload?: (fileId: string) => void;
  onCopyToMyDrive?: (item: CommunityFileItem) => void;
}

const CommunityFileList: React.FC<CommunityFileListProps> = ({
  files,
  onFolderClick,
  onDownload,
  onCopyToMyDrive,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedItem, setSelectedItem] = useState<CommunityFileItem | null>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, item: CommunityFileItem) => {
    setAnchorEl(event.currentTarget);
    setSelectedItem(item);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedItem(null);
  };

  const handleCopyToMyDrive = () => {
    if (selectedItem && onCopyToMyDrive) {
      onCopyToMyDrive(selectedItem);
    }
    handleMenuClose();
  };

  return (
    <>
      <TableContainer component={Paper} elevation={2}>
        <Table sx={{ minWidth: 650 }} aria-label="community file list">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell sx={{ maxWidth: 300 }}>Description</TableCell>
              <TableCell>Modified</TableCell>
              <TableCell>Size</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {files.map((file) => (
              <TableRow
                key={file.id}
                sx={{
                  '&:last-child td, &:last-child th': { border: 0 },
                  '&:hover .row-actions': {
                    opacity: 1,
                  },
                }}
              >
                <TableCell component="th" scope="row">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {file.type === 'folder' ? (
                      <FolderIcon
                        sx={{ mr: 1, color: 'primary.main', cursor: 'pointer' }}
                        onClick={() => onFolderClick(file.id, file.name)}
                      />
                    ) : (
                      <InsertDriveFileIcon sx={{ mr: 1, color: 'action.active' }} />
                    )}
                    <span
                      style={file.type === 'folder' ? { cursor: 'pointer' } : {}}
                      onClick={
                        file.type === 'folder'
                          ? () => onFolderClick(file.id, file.name)
                          : undefined
                      }
                    >
                      {file.name}
                    </span>
                  </Box>
                </TableCell>
                <TableCell>{file.owner}</TableCell>
                <TableCell sx={{ maxWidth: 300 }}>
                  <Tooltip title={file.description} placement="bottom-start">
                    <Typography
                      variant="body2"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: 300,
                      }}
                    >
                      {file.description}
                    </Typography>
                  </Tooltip>
                </TableCell>
                <TableCell>{file.modified}</TableCell>
                <TableCell>{file.size}</TableCell>
                <TableCell align="right">
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    {/* Download button - hidden by default, appears on row hover */}
                    <Box
                    className="row-actions"
                    sx={{
                        opacity: 0,
                        transition: 'opacity 0.2s',
                        display: 'flex',
                    }}
                    >
                    <Tooltip title={file.type === 'folder' ? 'Download as ZIP' : 'Download'}>
                        <IconButton
                        size="small"
                        onClick={() => onDownload?.(file.id)}
                        >
                        <DownloadIcon />
                        </IconButton>
                    </Tooltip>
                    </Box>

                    {/* More actions menu - always visible */}
                    <Tooltip title="More actions">
                    <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, file)}
                    >
                        <MoreVertIcon />
                    </IconButton>
                    </Tooltip>
                </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleCopyToMyDrive}>
          <ListItemIcon>
            <ContentCopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy to my drive</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default CommunityFileList;