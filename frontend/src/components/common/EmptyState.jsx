import React from 'react';

const EmptyState = ({ 
  icon: Icon, 
  title, 
  description, 
  action, 
  actionText, 
  actionIcon: ActionIcon,
  className = "",
  size = "medium" // small, medium, large
}) => {
  const getIconSize = () => {
    switch (size) {
      case 'small':
        return 'w-8 h-8';
      case 'large':
        return 'w-16 h-16';
      default:
        return 'w-12 h-12';
    }
  };

  const getTitleSize = () => {
    switch (size) {
      case 'small':
        return 'text-lg';
      case 'large':
        return 'text-2xl';
      default:
        return 'text-xl';
    }
  };

  const getDescriptionSize = () => {
    switch (size) {
      case 'small':
        return 'text-sm';
      case 'large':
        return 'text-lg';
      default:
        return 'text-base';
    }
  };

  return (
    <div className={`text-center py-12 ${className}`}>
      {Icon && (
        <div className={`mx-auto ${getIconSize()} text-gray-400 mb-4`}>
          <Icon className="w-full h-full" />
        </div>
      )}
      <h3 className={`font-medium text-gray-900 ${getTitleSize()} mb-2`}>
        {title}
      </h3>
      {description && (
        <p className={`text-gray-500 ${getDescriptionSize()} mb-6`}>
          {description}
        </p>
      )}
      {action && actionText && (
        <button
          onClick={action}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
        >
          {ActionIcon && <ActionIcon className="w-4 h-4 mr-2" />}
          {actionText}
        </button>
      )}
    </div>
  );
};

// Specific empty state variants
const EmptyBooks = ({ onAddBook }) => (
  <EmptyState
    icon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    )}
    title="No books in the collection yet"
    description="Get started by adding your first book to the library."
    action={onAddBook}
    actionText="Add Your First Book"
    actionIcon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    )}
  />
);

const EmptyMembers = ({ onAddMember }) => (
  <EmptyState
    icon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    )}
    title="No members registered yet"
    description="Start building your library community by registering your first member."
    action={onAddMember}
    actionText="Register Your First Member"
    actionIcon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    )}
  />
);

const EmptyBorrowings = ({ onCreateBorrowing }) => (
  <EmptyState
    icon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    )}
    title="No borrowings recorded yet"
    description="Track book loans and returns by creating your first borrowing record."
    action={onCreateBorrowing}
    actionText="Create Your First Borrowing"
    actionIcon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    )}
  />
);

const EmptySearch = ({ searchTerm, onClearSearch }) => (
  <EmptyState
    icon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    )}
    title={`No results found for "${searchTerm}"`}
    description="Try adjusting your search terms or filters to find what you're looking for."
    action={onClearSearch}
    actionText="Clear Search"
    actionIcon={({ className }) => (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    )}
    size="small"
  />
);

export { EmptyBooks, EmptyMembers, EmptyBorrowings, EmptySearch };
export default EmptyState;
