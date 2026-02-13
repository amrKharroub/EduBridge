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
import ShareIcon from '@mui/icons-material/Share';
import InfoIcon from '@mui/icons-material/Info';
import CodeIcon from '@mui/icons-material/Code';
import EmbedDialog from './EmbedDialog';

export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  owner: string;
  modified: string;
  size: string;
  description?: string;
  tags?: string;
}

interface FileListProps {
  files: FileItem[];
  onFolderClick: (folderId: string, folderName: string) => void;
  onDownload?: (fileId: string) => void;
  onShare?: (file: FileItem) => void;
  onDetails?: (file: FileItem) => void;
}

const FileList: React.FC<FileListProps> = ({
  files,
  onFolderClick,
  onDownload,
  onShare,
  onDetails,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);

  // Inside FileList component, add state:
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [embedFile, setEmbedFile] = useState<FileItem | null>(null);

  const handleEmbedClick = (file: FileItem) => {
    setEmbedFile(file);
    setEmbedDialogOpen(true);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, file: FileItem) => {
    setAnchorEl(event.currentTarget);
    setSelectedFile(file);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedFile(null);
  };

  const handleShare = () => {
    if (selectedFile && onShare) {
      onShare(selectedFile);
    }
    handleMenuClose();
  };

  const handleDetails = () => {
    if (selectedFile && onDetails) {
      onDetails(selectedFile);
    }
    handleMenuClose();
  };

  return (
    <>
      <TableContainer component={Paper} elevation={2}>
        <Table sx={{ minWidth: 650 }} aria-label="file list">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Owner</TableCell>
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
        <MenuItem onClick={handleShare}>
          <ListItemIcon>
            <ShareIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share</ListItemText>
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

export default FileList;