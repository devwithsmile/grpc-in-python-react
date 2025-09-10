import React from 'react';
import { Search } from 'lucide-react';

const SearchBar = ({ 
  searchTerm, 
  onSearchChange, 
  placeholder, 
  filteredCount, 
  totalCount,
  className = "flex flex-col sm:flex-row gap-4"
}) => {
  return (
    <div className={className}>
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="form-input pl-10"
        />
      </div>
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">
          {filteredCount} of {totalCount} items
        </span>
      </div>
    </div>
  );
};

export default SearchBar;
