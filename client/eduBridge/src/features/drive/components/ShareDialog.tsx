import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Box,
  Chip,
  Typography,
} from '@mui/material';

interface ShareDialogProps {
  open: boolean;
  onClose: () => void;
  itemName: string;
  onShare: (emails: string[], shareWithEveryone: boolean) => void;
}

const ShareDialog: React.FC<ShareDialogProps> = ({
  open,
  onClose,
  itemName,
  onShare,
}) => {
  const [emailInput, setEmailInput] = useState('');
  const [emails, setEmails] = useState<string[]>([]);
  const [shareWithEveryone, setShareWithEveryone] = useState(false);

  const handleAddEmail = () => {
    if (emailInput.trim() && isValidEmail(emailInput.trim())) {
      setEmails([...emails, emailInput.trim()]);
      setEmailInput('');
    }
  };

  const handleDeleteEmail = (emailToDelete: string) => {
    setEmails(emails.filter((email) => email !== emailToDelete));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddEmail();
    }
  };

  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleShare = () => {
    onShare(emails, shareWithEveryone);
    // Reset state
    setEmails([]);
    setEmailInput('');
    setShareWithEveryone(false);
    onClose();
  };

  const handleCancel = () => {
    setEmails([]);
    setEmailInput('');
    setShareWithEveryone(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleCancel} maxWidth="sm" fullWidth>
      <DialogTitle>Share "{itemName}"</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Add people and groups
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Enter email address"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <Button variant="outlined" onClick={handleAddEmail}>
              Add
            </Button>
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {emails.map((email) => (
              <Chip
                key={email}
                label={email}
                onDelete={() => handleDeleteEmail(email)}
                size="small"
              />
            ))}
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={shareWithEveryone}
                onChange={(e) => setShareWithEveryone(e.target.checked)}
              />
            }
            label="Share with everyone"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel}>Cancel</Button>
        <Button
          onClick={handleShare}
          variant="contained"
          disabled={emails.length === 0 && !shareWithEveryone}
        >
          Share
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ShareDialog;