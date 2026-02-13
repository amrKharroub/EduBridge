import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Snackbar,
  Alert,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface EmbedDialogProps {
  open: boolean;
  onClose: () => void;
  fileName: string;
  fileId: string;
}

const EmbedDialog: React.FC<EmbedDialogProps> = ({ open, onClose, fileName, fileId }) => {
  const [copied, setCopied] = React.useState(false);

  // Mock embed code – replace with your actual embed URL pattern
  const embedCode = `<iframe src="https://edubridge.app/embed/${fileId}" width="100%" height="500" frameborder="0"></iframe>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(embedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Embed "{fileName}"</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Embed code"
              multiline
              rows={4}
              value={embedCode}
              fullWidth
              InputProps={{ readOnly: true }}
              variant="outlined"
            />
            <Button
              variant="outlined"
              startIcon={<ContentCopyIcon />}
              onClick={handleCopy}
              sx={{ alignSelf: 'flex-start' }}
            >
              Copy to clipboard
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={copied}
        autoHideDuration={2000}
        onClose={() => setCopied(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" variant="filled" sx={{ width: '100%' }}>
          Embed code copied!
        </Alert>
      </Snackbar>
    </>
  );
};

export default EmbedDialog;