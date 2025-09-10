import React from 'react';
import LoadingIndicator, { SkeletonTable, SkeletonGrid } from './LoadingIndicator';
import EmptyState from './EmptyState';

const DataTable = ({ 
  title, 
  icon: Icon, 
  totalCount, 
  loading, 
  emptyStateIcon: EmptyStateIcon, 
  emptyStateText, 
  onEmptyStateAction, 
  emptyStateActionText, 
  emptyStateActionIcon: EmptyStateActionIcon,
  children,
  className = "card",
  loadingType = "spinner", // spinner, skeleton-table, skeleton-grid
  emptyStateComponent: CustomEmptyState
}) => {
  const renderLoadingState = () => {
    if (loadingType === "skeleton-table") {
      return <SkeletonTable rows={5} columns={4} />;
    }
    if (loadingType === "skeleton-grid") {
      return <SkeletonGrid items={6} className="p-6" />;
    }
    return <LoadingIndicator type="spinner" message="Loading..." className="p-12" />;
  };

  const renderEmptyState = () => {
    if (CustomEmptyState) {
      // If CustomEmptyState is a JSX element, render it directly
      // If it's a component, render it as a component
      return React.isValidElement(CustomEmptyState) ? CustomEmptyState : <CustomEmptyState />;
    }
    
    return (
      <EmptyState
        icon={EmptyStateIcon}
        title={emptyStateText}
        action={onEmptyStateAction}
        actionText={emptyStateActionText}
        actionIcon={EmptyStateActionIcon}
        className="p-12"
      />
    );
  };

  return (
    <div className={className}>
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            {Icon && <Icon className="w-5 h-5 mr-2" />}
            {title}
          </h3>
          <div className="text-sm text-gray-500">
            Total: {totalCount} items
          </div>
        </div>
      </div>
      
      <div className="overflow-hidden">
        {loading ? (
          renderLoadingState()
        ) : totalCount === 0 ? (
          renderEmptyState()
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default DataTable;
