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
import InfoIcon from '@mui/icons-material/Info';
import CodeIcon from '@mui/icons-material/Code';
import EmbedDialog from './EmbedDialog';

export interface SharedWithMeFileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  sharedBy: string; // email
  sharedDate: string;
  description?: string;
  size?: string; // optional, for display in details
}

interface SharedWithMeFileListProps {
  files: SharedWithMeFileItem[];
  onFolderClick: (folderId: string, folderName: string) => void;
  onDownload?: (fileId: string) => void;
  onCopyToMyDrive?: (item: SharedWithMeFileItem) => void;
  onDetails?: (item: SharedWithMeFileItem) => void;
}

const SharedWithMeFileList: React.FC<SharedWithMeFileListProps> = ({
  files,
  onFolderClick,
  onDownload,
  onCopyToMyDrive,
  onDetails,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedItem, setSelectedItem] = useState<SharedWithMeFileItem | null>(null);
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [embedFile, setEmbedFile] = useState<SharedWithMeFileItem | null>(null);

  const handleEmbedClick = (file: SharedWithMeFileItem) => {
    setEmbedFile(file);
    setEmbedDialogOpen(true);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, item: SharedWithMeFileItem) => {
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

  const handleDetails = () => {
    if (selectedItem && onDetails) {
      onDetails(selectedItem);
    }
    handleMenuClose();
  };

  return (
    <>
      <TableContainer component={Paper} elevation={2}>
        <Table sx={{ minWidth: 650 }} aria-label="shared with me file list">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Shared by</TableCell>
              <TableCell>Shared date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {files.map((file) => (
              <TableRow
                key={file.id}
                sx={{
                  '&:last-child td, &:last-child th': { border: 0 },
                  '&:hover .download-action': {
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
                <TableCell>{file.sharedBy}</TableCell>
                <TableCell>{file.sharedDate}</TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    {/* Download button - hidden by default, appears on row hover */}
                    <Box
                      className="download-action"
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
                      {file.type === 'file' && (
                        <Tooltip title="Embed">
                          <IconButton
                            size="small"
                            onClick={() => handleEmbedClick(file)}
                          >
                            <CodeIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                    <EmbedDialog
                      open={embedDialogOpen}
                      onClose={() => setEmbedDialogOpen(false)}
                      fileName={embedFile?.name || ''}
                      fileId={embedFile?.id || ''}
                    />
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
        <MenuItem onClick={handleDetails}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Details</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default SharedWithMeFileList;