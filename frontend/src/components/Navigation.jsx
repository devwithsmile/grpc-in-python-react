import React from 'react';
import { BookOpen, Users, BookOpenCheck, BarChart3 } from 'lucide-react';

const Navigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { 
      id: 'books', 
      label: 'Books', 
      icon: BookOpen, 
      description: 'Manage library collection',
      color: 'blue' 
    },
    { 
      id: 'members', 
      label: 'Members', 
      icon: Users, 
      description: 'Member management',
      color: 'green' 
    },
    { 
      id: 'borrowings', 
      label: 'Borrowings', 
      icon: BookOpenCheck, 
      description: 'Track loans & returns',
      color: 'purple' 
    }
  ];

  const getColorClasses = (color, isActive) => {
    const baseClasses = "transition-all duration-200 ease-in-out";
    
    if (isActive) {
      switch (color) {
        case 'blue':
          return `${baseClasses} bg-blue-50 border-blue-500 text-blue-700`;
        case 'green':
          return `${baseClasses} bg-green-50 border-green-500 text-green-700`;
        case 'purple':
          return `${baseClasses} bg-purple-50 border-purple-500 text-purple-700`;
        default:
          return `${baseClasses} bg-blue-50 border-blue-500 text-blue-700`;
      }
    } else {
      return `${baseClasses} bg-white border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50 hover:border-gray-300`;
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 shadow-subtle">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 sm:flex-none px-6 py-4 border-b-2 font-medium text-sm
                  flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-3
                  rounded-t-lg transition-all duration-200 hover:shadow-sm
                  ${getColorClasses(tab.color, isActive)}
                `}
              >
                <div className="flex items-center space-x-2">
                  <Icon className={`w-5 h-5 ${isActive ? 'animate-bounce-subtle' : ''}`} />
                  <span className="font-semibold">{tab.label}</span>
                </div>
                <span className={`text-xs ${isActive ? 'opacity-100' : 'opacity-0'} transition-opacity duration-200`}>
                  {tab.description}
                </span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default Navigation; 