import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material'

import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export type ItemType = 'file' | 'folder';

export interface NewItemData {
  name: string;
  type: ItemType;
  tags: string;
  description: string;
  file?: File; // for file uploads
}

interface UploadDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: NewItemData) => void;
}

const UploadDialog: React.FC<UploadDialogProps> = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState<NewItemData>({
    name: '',
    type: 'folder', // default to folder (no file selection needed)
    tags: '',
    description: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [touched, setTouched] = useState({
    name: false,
    file: false,
  });
  const [submitted, setSubmitted] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (e: SelectChangeEvent<ItemType>) => {
    const newType = e.target.value as ItemType;
    setFormData({ ...formData, type: newType, name: '' });
    setSelectedFile(null);
    setTouched({ name: false, file: false });
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setTouched({ ...touched, [e.target.name]: true });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setFormData({ ...formData, name: file.name });
      setTouched({ ...touched, file: true });
    }
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const isFieldEmpty = (value: string) => value.trim() === '';
  
  const showNameError = () =>
    formData.type === 'folder' &&
    (touched.name || submitted) &&
    isFieldEmpty(formData.name);

  const showFileError = () =>
    formData.type === 'file' &&
    (touched.file || submitted) &&
    !selectedFile;

  const handleSubmit = () => {
    setSubmitted(true);
    
    // Validate based on type
    if (formData.type === 'folder') {
      if (isFieldEmpty(formData.name)) return;
    } else {
      if (!selectedFile) {
        setTouched({ ...touched, file: true });
        return;
      }
    }

    onSubmit({
      ...formData,
      file: selectedFile || undefined,
    });

    // Reset form
    setFormData({ name: '', type: 'folder', tags: '', description: '' });
    setSelectedFile(null);
    setSubmitted(false);
    setTouched({ name: false, file: false });
    onClose();
  };

  const handleCancel = () => {
    setFormData({ name: '', type: 'folder', tags: '', description: '' });
    setSelectedFile(null);
    setSubmitted(false);
    setTouched({ name: false, file: false });
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleCancel} maxWidth="sm" fullWidth>
      <DialogTitle>Create New</DialogTitle>
      <DialogContent dividers>
        <Box component="form" noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Type selector - FIRST */}
          <FormControl fullWidth size="small">
            <InputLabel id="type-label">Type</InputLabel>
            <Select
              labelId="type-label"
              name="type"
              value={formData.type}
              label="Type"
              onChange={handleSelectChange}
            >
              <MenuItem value="folder">Folder</MenuItem>
              <MenuItem value="file">File</MenuItem>
            </Select>
          </FormControl>

          {/* Conditional fields based on type */}
          {formData.type === 'folder' ? (
            // Folder: Name field
            <TextField
              required
              fullWidth
              size="small"
              name="name"
              label="Folder Name"
              value={formData.name}
              onChange={handleChange}
              onBlur={handleBlur}
              error={showNameError()}
              helperText={showNameError() ? 'Folder name is required' : ' '}
            />
          ) : (
            // File: Choose file button
            <Box>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                onClick={handleChooseFile}
                fullWidth
                sx={{ py: 1.5 }}
                color={showFileError() ? 'error' : 'primary'}
              >
                Choose from computer
              </Button>
              {selectedFile && (
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={selectedFile.name}
                    onDelete={() => {
                      setSelectedFile(null);
                      setFormData({ ...formData, name: '' });
                    }}
                    size="small"
                  />
                  <Typography variant="caption" display="block" sx={{ mt: 0.5, color: 'text.secondary' }}>
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </Typography>
                </Box>
              )}
              {showFileError() && (
                <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                  Please select a file
                </Typography>
              )}
            </Box>
          )}

          {/* Tags (comma-separated) */}
          <TextField
            fullWidth
            size="small"
            name="tags"
            label="Tags (comma-separated)"
            value={formData.tags}
            onChange={handleChange}
            placeholder="e.g. work, important"
          />

          {/* Description */}
          <TextField
            fullWidth
            size="small"
            name="description"
            label="Description"
            value={formData.description}
            onChange={handleChange}
            multiline
            rows={3}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">
          Create
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadDialog;