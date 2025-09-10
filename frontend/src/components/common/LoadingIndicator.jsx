import React from 'react';

// Skeleton components for different content types
const SkeletonBox = ({ className = "h-4 bg-gray-200 rounded" }) => (
  <div className={`animate-pulse ${className}`}></div>
);

const SkeletonText = ({ lines = 1, className = "" }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <SkeletonBox 
        key={index} 
        className={`h-4 bg-gray-200 rounded ${index === lines - 1 ? 'w-3/4' : 'w-full'}`} 
      />
    ))}
  </div>
);

const SkeletonCard = ({ className = "" }) => (
  <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
    <div className="flex items-center space-x-4 mb-4">
      <SkeletonBox className="w-12 h-12 bg-gray-200 rounded-full" />
      <div className="flex-1">
        <SkeletonBox className="h-4 w-3/4 mb-2" />
        <SkeletonBox className="h-3 w-1/2" />
      </div>
    </div>
    <SkeletonText lines={2} />
  </div>
);

const SkeletonTable = ({ rows = 5, columns = 4 }) => (
  <div className="overflow-hidden">
    <div className="min-w-full divide-y divide-gray-200">
      {/* Header */}
      <div className="bg-gray-50 px-6 py-3">
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: columns }).map((_, index) => (
            <SkeletonBox key={index} className="h-4 w-20" />
          ))}
        </div>
      </div>
      {/* Rows */}
      <div className="bg-white divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="px-6 py-4">
            <div className="grid grid-cols-4 gap-4">
              {Array.from({ length: columns }).map((_, colIndex) => (
                <SkeletonBox 
                  key={colIndex} 
                  className={`h-4 ${colIndex === 0 ? 'w-3/4' : 'w-full'}`} 
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const SkeletonGrid = ({ items = 6, className = "" }) => (
  <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
    {Array.from({ length: items }).map((_, index) => (
      <SkeletonCard key={index} />
    ))}
  </div>
);

// Main loading indicator component
const LoadingIndicator = ({ 
  type = "spinner", // spinner, skeleton, custom
  message = "Loading...",
  size = "medium", // small, medium, large
  className = ""
}) => {
  const getSpinnerSize = () => {
    switch (size) {
      case 'small':
        return 'w-4 h-4';
      case 'large':
        return 'w-12 h-12';
      default:
        return 'w-8 h-8';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'small':
        return 'text-sm';
      case 'large':
        return 'text-lg';
      default:
        return 'text-base';
    }
  };

  if (type === "spinner") {
    return (
      <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
        <div className={`${getSpinnerSize()} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4`}></div>
        <p className={`text-gray-500 ${getTextSize()}`}>{message}</p>
      </div>
    );
  }

  if (type === "skeleton") {
    return (
      <div className={className}>
        <SkeletonText lines={3} />
      </div>
    );
  }

  return null;
};

// Export individual skeleton components and main component
export { 
  SkeletonBox, 
  SkeletonText, 
  SkeletonCard, 
  SkeletonTable, 
  SkeletonGrid 
};
export default LoadingIndicator;
