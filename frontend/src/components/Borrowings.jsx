import React, { useState, useEffect } from 'react';
import { BookOpenCheck, Plus, Search, Calendar, BookOpen, Users, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

const Borrowings = () => {
  const [borrowings, setBorrowings] = useState([]);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [newBorrowing, setNewBorrowing] = useState({ bookId: '', memberId: '', dueDate: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [borrowingsData, booksData, membersData] = await Promise.all([
        api.getBorrowings(),
        api.getBooks(),
        api.getMembers()
      ]);
      setBorrowings(borrowingsData);
      setBooks(booksData);
      setMembers(membersData);
      setError('');
    } catch (err) {
      setError('Failed to load data');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newBorrowing.bookId || !newBorrowing.memberId || !newBorrowing.dueDate) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      const createdBorrowing = await api.borrowBook(newBorrowing);
      setBorrowings([...borrowings, createdBorrowing]);
      setNewBorrowing({ bookId: '', memberId: '', dueDate: '' });
      setShowAddForm(false);
      setError('');
    } catch (err) {
      setError('Failed to create borrowing');
      console.error('Error creating borrowing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (bookId, memberId) => {
    try {
      setLoading(true);
      await api.returnBook(bookId, memberId);
      // Update the borrowing status
      setBorrowings(borrowings.map(b => 
        b.bookId === bookId && b.memberId === memberId 
          ? { ...b, status: 'returned', returnedAt: new Date().toISOString() }
          : b
      ));
      setError('');
    } catch (err) {
      setError('Failed to return book');
      console.error('Error returning book:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setNewBorrowing({
      ...newBorrowing,
      [e.target.name]: e.target.value
    });
  };

  const filteredBorrowings = borrowings.filter(borrowing => {
    const book = books.find(b => b.id === borrowing.bookId);
    const member = members.find(m => m.id === borrowing.memberId);
    
    return (
      (book && book.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (member && member.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      borrowing.status.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const resetForm = () => {
    setNewBorrowing({ bookId: '', memberId: '', dueDate: '' });
    setShowAddForm(false);
    setError('');
  };

  const getBookTitle = (bookId) => {
    const book = books.find(b => b.id === bookId);
    return book ? book.title : 'Unknown Book';
  };

  const getMemberName = (memberId) => {
    const member = members.find(m => m.id === memberId);
    return member ? member.name : 'Unknown Member';
  };

  const getStatusBadge = (status, dueDate) => {
    const isOverdue = new Date(dueDate) < new Date() && status === 'borrowed';
    
    if (isOverdue) {
      return <span className="badge badge-error">Overdue</span>;
    }
    
    switch (status) {
      case 'borrowed':
        return <span className="badge badge-info">Borrowed</span>;
      case 'returned':
        return <span className="badge badge-success">Returned</span>;
      default:
        return <span className="badge badge-warning">{status}</span>;
    }
  };

  const getDaysRemaining = (dueDate) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return `${Math.abs(diffDays)} days overdue`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else {
      return `${diffDays} days remaining`;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <BookOpenCheck className="w-6 h-6 mr-3 text-purple-600" />
            Book Borrowings
          </h2>
          <p className="text-gray-600 mt-1">Track all book loans and returns</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-primary mt-4 sm:mt-0"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Borrowing
        </button>
      </div>

      {/* Add Borrowing Form */}
      {showAddForm && (
        <div className="card animate-slide-up">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Plus className="w-5 h-5 mr-2 text-purple-600" />
              New Book Borrowing
            </h3>
          </div>
          
          <div className="card-body">
            {error && (
              <div className="message message-error mb-6">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid-responsive">
                <div>
                  <label className="form-label">Select Book</label>
                  <select
                    name="bookId"
                    value={newBorrowing.bookId}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  >
                    <option value="">Choose a book...</option>
                    {books.map(book => (
                      <option key={book.id} value={book.id}>
                        {book.title} by {book.author}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Select Member</label>
                  <select
                    name="memberId"
                    value={newBorrowing.memberId}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  >
                    <option value="">Choose a member...</option>
                    {members.map(member => (
                      <option key={member.id} value={member.id}>
                        {member.name} ({member.email})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Due Date</label>
                  <input
                    type="date"
                    name="dueDate"
                    value={newBorrowing.dueDate}
                    onChange={handleInputChange}
                    className="form-input"
                    min={new Date().toISOString().split('T')[0]}
                    required
                  />
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex-1"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Creating Borrowing...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Borrowing
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search borrowings by book title, member name, or status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {filteredBorrowings.length} of {borrowings.length} borrowings
          </span>
        </div>
      </div>

      {/* Borrowings Grid */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <BookOpenCheck className="w-5 h-5 mr-2 text-purple-600" />
              Borrowing Records
            </h3>
            <div className="text-sm text-gray-500">
              Total: {borrowings.length} borrowings
            </div>
          </div>
        </div>
        
        <div className="card-body">
          {loading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-500">Loading borrowings...</p>
            </div>
          ) : filteredBorrowings.length === 0 ? (
            <div className="empty-state">
              <BookOpenCheck className="empty-state-icon" />
              <p className="empty-state-text">
                {searchTerm ? 'No borrowings found matching your search.' : 'No borrowings recorded yet.'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="btn-primary mt-4"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Borrowing
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredBorrowings.map((borrowing) => (
                <div key={`${borrowing.bookId}-${borrowing.memberId}`} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-elevated transition-all duration-200">
                  {/* Header with Status */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg flex items-center justify-center">
                        <BookOpen className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{getBookTitle(borrowing.bookId)}</h4>
                        <p className="text-sm text-gray-500">Borrowed by {getMemberName(borrowing.memberId)}</p>
                      </div>
                    </div>
                    {getStatusBadge(borrowing.status, borrowing.dueDate)}
                  </div>

                  {/* Details */}
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center space-x-3 text-sm">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">
                        Due: {new Date(borrowing.dueDate).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-sm">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">
                        {getDaysRemaining(borrowing.dueDate)}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="text-xs text-gray-500">
                      ID: {borrowing.id || `${borrowing.bookId}-${borrowing.memberId}`}
                    </div>
                    {borrowing.status === 'borrowed' && (
                      <button
                        onClick={() => handleReturn(borrowing.bookId, borrowing.memberId)}
                        className="btn-secondary text-sm px-4 py-2"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Return Book
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Borrowings; 