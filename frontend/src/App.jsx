import React, { useState } from 'react';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Books from './components/Books';
import Members from './components/Members';
import Borrowings from './components/Borrowings';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('books');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'books':
        return <Books />;
      case 'members':
        return <Members />;
      case 'borrowings':
        return <Borrowings />;
      default:
        return <Books />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-fade-in">
          {renderActiveTab()}
        </div>
      </main>
    </div>
  );
}

export default App;
