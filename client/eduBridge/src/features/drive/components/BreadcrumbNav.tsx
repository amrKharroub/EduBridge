import React from 'react';
import { Breadcrumbs, Link, Typography } from '@mui/material';

export interface BreadcrumbItem {
  id: string;
  name: string;
}

interface BreadcrumbNavProps {
  items: BreadcrumbItem[];
  onNavigate: (item: BreadcrumbItem) => void;
}

const BreadcrumbNav: React.FC<BreadcrumbNavProps> = ({ items, onNavigate }) => {
  return (
    <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return isLast ? (
          <Typography key={item.id} color="text.primary">
            {item.name}
          </Typography>
        ) : (
          <Link
            key={item.id}
            component="button"
            variant="body1"
            onClick={() => onNavigate(item)}
            sx={{ cursor: 'pointer' }}
          >
            {item.name}
          </Link>
        );
      })}
    </Breadcrumbs>
  );
};

export default BreadcrumbNav;