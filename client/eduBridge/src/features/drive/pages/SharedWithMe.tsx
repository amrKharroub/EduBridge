import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { usePageTitle } from '../../../context/PageTitleContext';
import SharedWithMeFileList from '../components/SharedWithMeFileList';
import type { SharedWithMeFileItem } from '../components/SharedWithMeFileList';
import BreadcrumbNav from '../components/BreadcrumbNav';
import type { BreadcrumbItem } from '../components/BreadcrumbNav';
import FileDetailsDialog from '../components/FileDetailsDialog'; 
import type { FileItem } from '../components/FileList'; 

// Mock shared with me data
const rootSharedItems: SharedWithMeFileItem[] = [
  {
    id: 's1',
    name: 'Lessons Plan 2025.pdf',
    type: 'file',
    sharedBy: 'alice@gmail.com',
    sharedDate: '2 days ago',
    description: 'Detailed project timeline and milestones',
    size: '1.2 MB',
  },
  {
    id: 's2',
    name: 'Material Assets',
    type: 'folder',
    sharedBy: 'bob@gmail.com',
    sharedDate: '5 days ago',
    description: 'UI kits, icons, and wireframes',
  },
  {
    id: 's3',
    name: 'Budget Forecast.xlsx',
    type: 'file',
    sharedBy: 'carol@shcool.com',
    sharedDate: 'Mar 20',
    description: 'Q2 budget breakdown',
    size: '890 KB',
  },
  {
    id: 's4',
    name: 'lessons Recordings',
    type: 'folder',
    sharedBy: 'david@school.com',
    sharedDate: 'Mar 18',
    description: 'Sprint review recordings',
  },
];

const folderContents: Record<string, SharedWithMeFileItem[]> = {
  's2': [
    {
      id: 's2-1',
      name: 'Wireframes.fig',
      type: 'file',
      sharedBy: 'bob@example.com',
      sharedDate: '5 days ago',
      description: 'Homepage and dashboard wireframes',
      size: '3.4 MB',
    },
    {
      id: 's2-2',
      name: 'Icons.zip',
      type: 'file',
      sharedBy: 'bob@example.com',
      sharedDate: '5 days ago',
      description: 'SVG icon set',
      size: '2.1 MB',
    },
  ],
  's4': [
    {
      id: 's4-1',
      name: 'Sprint 12 Review.mp4',
      type: 'file',
      sharedBy: 'david@example.com',
      sharedDate: 'Mar 18',
      description: 'Recording from March 15',
      size: '45 MB',
    },
  ],
};

const SharedWithMe = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('Shared with me');
  }, [setTitle]);

  // Breadcrumb state
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([
    { id: 'root', name: 'Shared with me' },
  ]);

  // Current folder ID (root = null)
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [items, setItems] = useState<SharedWithMeFileItem[]>(rootSharedItems);

  // Details dialog state
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<SharedWithMeFileItem | null>(null);

  const handleFolderClick = (folderId: string, folderName: string) => {
    setCurrentFolderId(folderId);
    setItems(folderContents[folderId] || []);
    setBreadcrumbs([...breadcrumbs, { id: folderId, name: folderName }]);
  };

  const handleBreadcrumbClick = (item: BreadcrumbItem) => {
    const index = breadcrumbs.findIndex((b) => b.id === item.id);
    if (index !== -1) {
      const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
      setBreadcrumbs(newBreadcrumbs);
      if (item.id === 'root') {
        setCurrentFolderId(null);
        setItems(rootSharedItems);
      } else {
        setCurrentFolderId(item.id);
        setItems(folderContents[item.id] || []);
      }
    }
  };

  const handleDownload = (fileId: string) => {
    const item = [...items, ...Object.values(folderContents).flat()].find(
      (f) => f.id === fileId
    );
    console.log(`Download ${item?.type}:`, item?.name);
    // TODO: implement actual download
  };

  const handleCopyToMyDrive = (item: SharedWithMeFileItem) => {
    console.log('Copy to my drive:', item.name);
    // TODO: implement actual copy
  };

  const handleDetails = (item: SharedWithMeFileItem) => {
    setSelectedItem(item);
    setDetailsOpen(true);
  };

  // Convert SharedWithMeFileItem to FileItem for the details dialog
  const convertToFileItem = (item: SharedWithMeFileItem): FileItem => ({
    id: item.id,
    name: item.name,
    type: item.type,
    owner: item.sharedBy,
    modified: item.sharedDate,
    size: item.size || '--',
    description: item.description,
    tags: '', // not used here
  });

  return (
    <Box>
      <BreadcrumbNav items={breadcrumbs} onNavigate={handleBreadcrumbClick} />
      <SharedWithMeFileList
        files={items}
        onFolderClick={handleFolderClick}
        onDownload={handleDownload}
        onCopyToMyDrive={handleCopyToMyDrive}
        onDetails={handleDetails}
      />

      <FileDetailsDialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        file={selectedItem ? convertToFileItem(selectedItem) : null}
      />
    </Box>
  );
};

export default SharedWithMe;