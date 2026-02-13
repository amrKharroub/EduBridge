import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { usePageTitle } from '../../../context/PageTitleContext';
import CommunityFileList from '../components/CommunityFileList';
import type { CommunityFileItem } from '../components/CommunityFileList';
import BreadcrumbNav from '../components/BreadcrumbNav';
import type { BreadcrumbItem } from '../components/BreadcrumbNav';

// Mock community data – files and folders shared with everyone
const rootCommunityItems: CommunityFileItem[] = [
  {
    id: 'c1',
    name: 'Machine Learning Fundamentals',
    type: 'folder',
    owner: 'Dr. Michael Roberts',
    description: 'Lecture slides, datasets, and assignments covering supervised and unsupervised learning.',
    modified: '1 hour ago',
    size: '--',
  },
  {
    id: 'c2',
    name: 'Linear Algebra Notes.pdf',
    type: 'file',
    owner: 'Prof. Linda Martinez',
    description: 'Comprehensive notes on matrices, eigenvalues, eigenvectors, and vector spaces.',
    modified: 'Yesterday',
    size: '3.6 MB',
  },
  {
    id: 'c3',
    name: 'Data Structures & Algorithms',
    type: 'folder',
    owner: 'James Anderson',
    description: 'Implementation examples, complexity analysis, and practice problems for common data structures.',
    modified: '2 days ago',
    size: '--',
  },
  {
    id: 'c4',
    name: 'Database Systems Overview',
    type: 'file',
    owner: 'Dr. Sophia Lee',
    description: 'Introduction to relational databases, ER modeling, normalization, and SQL queries.',
    modified: 'Feb 10',
    size: '2.1 MB',
  },
];

const folderContents: Record<string, CommunityFileItem[]> = {
  'c1': [
    {
      id: 'c1-1',
      name: 'Lecture 01 - Introduction to ML.pdf',
      type: 'file',
      owner: 'Dr. Michael Roberts',
      description: 'Overview of machine learning concepts, types of learning, and real-world applications.',
      modified: '1 hour ago',
      size: '5.4 MB',
    },
    {
      id: 'c1-2',
      name: 'Assignments',
      type: 'folder',
      owner: 'Dr. Michael Roberts',
      description: 'Homework exercises including regression, classification, and clustering tasks.',
      modified: '1 hour ago',
      size: '--',
    },
  ],
  'c3': [
    {
      id: 'c3-1',
      name: 'Sorting Algorithms Cheat Sheet.pdf',
      type: 'file',
      owner: 'James Anderson',
      description: 'Quick reference for Bubble, Merge, Quick, and Heap sort with time and space complexity.',
      modified: '2 days ago',
      size: '420 KB',
    },
    {
      id: 'c3-2',
      name: 'Practice Problems',
      type: 'folder',
      owner: 'James Anderson',
      description: 'Coding exercises on linked lists, stacks, queues, trees, and graphs.',
      modified: '2 days ago',
      size: '--',
    },
  ],
};


const Community = () => {
  const { setTitle } = usePageTitle();

  useEffect(() => {
    setTitle('Community');
  }, [setTitle]);

  // Breadcrumb state
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([
    { id: 'root', name: 'Community' },
  ]);

  // Current folder ID (root = null)
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [items, setItems] = useState<CommunityFileItem[]>(rootCommunityItems);

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
        setItems(rootCommunityItems);
      } else {
        setCurrentFolderId(item.id);
        setItems(folderContents[item.id] || []);
      }
    }
  };

  const handleDownload = (fileId: string) => {
    console.log('Download file:', fileId);
    // TODO: implement actual download
  };

  return (
    <Box>
      <BreadcrumbNav items={breadcrumbs} onNavigate={handleBreadcrumbClick} />
      <CommunityFileList
        files={items}
        onFolderClick={handleFolderClick}
        onDownload={handleDownload}
      />
    </Box>
  );
};

export default Community;