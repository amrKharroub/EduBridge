import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Divider,
  Chip,
} from '@mui/material';
import type { FileItem } from './FileList';

interface FileDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  file: FileItem | null;
}

const FileDetailsDialog: React.FC<FileDetailsDialogProps> = ({
  open,
  onClose,
  file,
}) => {
  if (!file) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>File Details</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Name
            </Typography>
            <Typography variant="body1">{file.name}</Typography>
          </Box>
          <Divider />
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Type
            </Typography>
            <Typography variant="body1">
              {file.type === 'folder' ? 'Folder' : 'File'}
            </Typography>
          </Box>
          <Divider />
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Owner
            </Typography>
            <Typography variant="body1">{file.owner}</Typography>
          </Box>
          <Divider />
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Size
            </Typography>
            <Typography variant="body1">{file.size}</Typography>
          </Box>
          <Divider />
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Modified
            </Typography>
            <Typography variant="body1">{file.modified}</Typography>
          </Box>
          {file.description && (
            <>
              <Divider />
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body1">{file.description}</Typography>
              </Box>
            </>
          )}
          {file.tags && (
            <>
              <Divider />
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Tags
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                  {file.tags.split(',').map((tag) => (
                    <Chip
                      key={tag}
                      label={tag.trim()}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            </>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default FileDetailsDialog;