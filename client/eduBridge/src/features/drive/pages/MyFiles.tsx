import { useState, useEffect } from 'react';
import { Box, Fab, Tooltip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { usePageTitle } from '../../../context/PageTitleContext';
import FileList from '../components/FileList';
import type { FileItem } from '../components/FileList';
import BreadcrumbNav from '../components/BreadcrumbNav';
import type { BreadcrumbItem } from '../components/BreadcrumbNav';
import UploadDialog from '../components/UploadDialog';
import type { NewItemData } from '../components/UploadDialog';
import ShareDialog from '../components/ShareDialog';
import FileDetailsDialog from '../components/FileDetailsDialog';

// Mock file system with owner, description, tags
const rootFiles: FileItem[] = [
  {
    id: '1',
    name: 'Project Proposal.pdf',
    type: 'file',
    owner: 'me',
    modified: 'Today 10:30',
    size: '2.3 MB',
    description: 'Initial draft of Q2 project proposal',
    tags: 'work, proposal',
  },
  {
    id: '2',
    name: 'chemistry Notes.md',
    type: 'file',
    owner: 'me',
    modified: 'Yesterday',
    size: '124 KB',
    description: 'Notes from sprint planning and retro',
    tags: 'meeting',
  },
  {
    id: '3',
    name: 'math lessons',
    type: 'folder',
    owner: 'me',
    modified: '2 days ago',
    size: '--',
    description: 'Images, icons, and logos',
    tags: 'assets',
  },
  {
    id: '4',
    name: 'Presentation.pptx',
    type: 'file',
    owner: 'John',
    modified: 'Mar 12',
    size: '5.1 MB',
    description: 'Final version for client review',
    tags: 'client',
  },
  {
    id: '5',
    name: 'Archive',
    type: 'folder',
    owner: 'me',
    modified: 'Mar 10',
    size: '--',
    description: 'Old projects and backups',
    tags: 'archive',
  },
];

const folderContents: Record<string, FileItem[]> = {
  '3': [
    {
      id: '3-1',
      name: 'Logo.png',
      type: 'file',
      owner: 'me',
      modified: '2 days ago',
      size: '1.2 MB',
      description: 'Company logo in PNG format',
      tags: 'logo',
    },
    {
      id: '3-2',
      name: 'Icons',
      type: 'folder',
      owner: 'me',
      modified: '2 days ago',
      size: '--',
      description: 'SVG icon set',
      tags: 'icons',
    },
  ],
  '5': [
    {
      id: '5-1',
      name: 'old_report.pdf',
      type: 'file',
      owner: 'me',
      modified: 'Mar 9',
      size: '890 KB',
      description: 'Quarterly report from 2024',
      tags: 'old',
    },
  ],
  '3-2': [
    {
      id: '3-2-1',
      name: 'favicon.ico',
      type: 'file',
      owner: 'me',
      modified: '2 days ago',
      size: '15 KB',
      description: 'Browser favicon',
      tags: 'icon',
    },
  ],
};

const MyFiles = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('My Drive');
  }, [setTitle]);

  // Breadcrumb state
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([
    { id: 'root', name: 'My Drive' },
  ]);

  // Current folder ID (root = null)
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [files, setFiles] = useState<FileItem[]>(rootFiles);

  // Dialog states
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);

  const handleFolderClick = (folderId: string, folderName: string) => {
    setCurrentFolderId(folderId);
    setFiles(folderContents[folderId] || []);
    setBreadcrumbs([...breadcrumbs, { id: folderId, name: folderName }]);
  };

  const handleBreadcrumbClick = (item: BreadcrumbItem) => {
    const index = breadcrumbs.findIndex((b) => b.id === item.id);
    if (index !== -1) {
      const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
      setBreadcrumbs(newBreadcrumbs);
      if (item.id === 'root') {
        setCurrentFolderId(null);
        setFiles(rootFiles);
      } else {
        setCurrentFolderId(item.id);
        setFiles(folderContents[item.id] || []);
      }
    }
  };

  const handleDownload = (fileId: string) => {
    console.log('Download file:', fileId);
    // TODO: implement actual download
  };

  const handleShare = (file: FileItem) => {
    setSelectedFile(file);
    setShareDialogOpen(true);
  };

  const handleShareSubmit = (emails: string[], shareWithEveryone: boolean) => {
    console.log('Share:', {
      file: selectedFile?.name,
      emails,
      shareWithEveryone,
    });
    // TODO: implement actual sharing
  };

  const handleDetails = (file: FileItem) => {
    setSelectedFile(file);
    setDetailsDialogOpen(true);
  };

  const handleCreateItem = (data: NewItemData) => {
    const newItem: FileItem = {
      id: `new-${Date.now()}`,
      name: data.name,
      type: data.type,
      owner: 'me',
      modified: 'Just now',
      size: data.type === 'folder' ? '--' : data.file ? `${(data.file.size / 1024).toFixed(1)} KB` : '0 KB',
      description: data.description || undefined,
      tags: data.tags || undefined,
    };

    if (currentFolderId) {
      if (!folderContents[currentFolderId]) {
        folderContents[currentFolderId] = [];
      }
      folderContents[currentFolderId].push(newItem);
      setFiles([...folderContents[currentFolderId]]);
    } else {
      rootFiles.push(newItem);
      setFiles([...rootFiles]);
    }
  };

  return (
    <Box sx={{ position: 'relative', minHeight: 'calc(100vh - 64px)' }}>
      <BreadcrumbNav items={breadcrumbs} onNavigate={handleBreadcrumbClick} />
      <FileList
        files={files}
        onFolderClick={handleFolderClick}
        onDownload={handleDownload}
        onShare={handleShare}
        onDetails={handleDetails}
      />

      <Tooltip title="Create new file or folder" placement="left">
        <Fab
          color="primary"
          aria-label="add"
          onClick={() => setUploadDialogOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
          }}
        >
          <AddIcon />
        </Fab>
      </Tooltip>

      <UploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onSubmit={handleCreateItem}
      />

      <ShareDialog
        open={shareDialogOpen}
        onClose={() => setShareDialogOpen(false)}
        itemName={selectedFile?.name || ''}
        onShare={handleShareSubmit}
      />

      <FileDetailsDialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        file={selectedFile}
      />
    </Box>
  );
};

export default MyFiles;