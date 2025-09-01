import React from 'react';
import { BookOpen, Database, Zap } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 shadow-elevated">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-8">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">
                Library Management
              </h1>
              <p className="text-blue-100 text-sm font-medium mt-1">
                Professional Library Service Platform
              </p>
            </div>
          </div>

          {/* Tech Stack Badges */}
          <div className="hidden md:flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
              <Database className="w-4 h-4 text-blue-200" />
              <span className="text-blue-100 text-sm font-medium">gRPC</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
              <Zap className="w-4 h-4 text-blue-200" />
              <span className="text-blue-100 text-sm font-medium">PostgreSQL</span>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-blue-100 text-sm font-medium">System Online</span>
          </div>
        </div>
      </div>
      
      {/* Subtle bottom border */}
      <div className="h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
    </header>
  );
};

export default Header; 