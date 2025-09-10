import React, { useState, useEffect } from 'react';
import { BookOpenCheck, Plus, Calendar, BookOpen, Clock, CheckCircle } from 'lucide-react';
import api from '../services/api';
import { PageHeader, FormWrapper, SearchBar, DataTable, FormField, FormActions, ConfirmationModal, EmptyBorrowings, EmptySearch } from './common';
import { useFormValidation } from '../hooks/useFormValidation';
import { useToast } from '../hooks/useToast';
import { useConfirmationModal } from '../hooks/useModal';

const Borrowings = () => {
  const [borrowings, setBorrowings] = useState([]);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Form validation
  const {
    data: formData,
    errors: formErrors,
    handleFieldChange,
    handleFieldBlur,
    validateFormData,
    resetForm
  } = useFormValidation('borrowing', { bookId: '', memberId: '', dueDate: '' });
  
  // Toast notifications
  const { showError, showSuccess } = useToast();
  
  // Confirmation modal
  const { isOpen, config, openConfirmation, closeConfirmation, handleConfirm } = useConfirmationModal();

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
    } catch (err) {
      console.error('Error loading data:', err);
      showError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form data
    const validation = validateFormData(formData);
    if (!validation.isValid) {
      return;
    }

    try {
      setLoading(true);
      const createdBorrowing = await api.borrowBook(validation.data);
      setBorrowings([...borrowings, createdBorrowing]);
      resetForm();
      setShowAddForm(false);
      showSuccess('Book borrowing created successfully!');
    } catch (err) {
      console.error('Error creating borrowing:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 400) {
        showError('Invalid borrowing data. Please check your input.');
      } else if (err.status === 409) {
        showError('This book is already borrowed.');
      } else {
        showError('Failed to create borrowing. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReturnClick = (borrowing) => {
    const bookTitle = getBookTitle(borrowing.book_id);
    const memberName = getMemberName(borrowing.member_id);
    
    openConfirmation({
      title: "Return Book",
      message: `Are you sure you want to mark "${bookTitle}" as returned by ${memberName}?`,
      confirmText: "Return Book",
      cancelText: "Cancel",
      type: "info",
      onConfirm: () => handleReturn(borrowing.book_id, borrowing.member_id)
    });
  };

  const handleReturn = async (bookId, memberId) => {
    try {
      setLoading(true);
      await api.returnBook(bookId, memberId);
      // Update the borrowing status
      setBorrowings(borrowings.map(b => 
        b.book_id === bookId && b.member_id === memberId 
          ? { ...b, is_returned: true, return_date: new Date().toISOString() }
          : b
      ));
      showSuccess('Book returned successfully!');
    } catch (err) {
      console.error('Error returning book:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 404) {
        showError('Borrowing record not found.');
      } else {
        showError('Failed to return book. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    handleFieldChange(e.target.name, e.target.value);
  };

  const handleFieldBlurEvent = (e) => {
    handleFieldBlur(e.target.name);
  };

  const filteredBorrowings = borrowings.filter(borrowing => {
    const book = books.find(b => b.id === borrowing.book_id);
    const member = members.find(m => m.id === borrowing.member_id);
    
    return (
      (book && book.title && book.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (member && member.name && member.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (borrowing.is_returned !== undefined && borrowing.is_returned.toString().toLowerCase().includes(searchTerm.toLowerCase())) ||
      (borrowing.status && borrowing.status.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  });

  const handleResetForm = () => {
    resetForm();
    setShowAddForm(false);
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
    if (!dueDate) return 'No due date';
    
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
      <PageHeader
        icon={BookOpenCheck}
        title="Book Borrowings"
        description="Track all book loans and returns"
        buttonText="New Borrowing"
        buttonIcon={Plus}
        onButtonClick={() => setShowAddForm(!showAddForm)}
      />

      {/* Add Borrowing Form */}
      <FormWrapper
        isVisible={showAddForm}
        title="New Book Borrowing"
        icon={Plus}
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid-responsive">
            <FormField
              label="Select Book"
              name="bookId"
              type="select"
              value={formData.bookId}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Choose a book..."
              required
              error={formErrors.bookId}
              options={books.map(book => ({
                value: book.id,
                label: `${book.title} by ${book.author}`
              }))}
            />
            <FormField
              label="Select Member"
              name="memberId"
              type="select"
              value={formData.memberId}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Choose a member..."
              required
              error={formErrors.memberId}
              options={members.map(member => ({
                value: member.id,
                label: `${member.name} (${member.email})`
              }))}
            />
            <FormField
              label="Due Date"
              name="dueDate"
              type="date"
              value={formData.dueDate}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              required
              min={new Date().toISOString().split('T')[0]}
              error={formErrors.dueDate}
            />
          </div>
          
          <FormActions
            submitText="Create Borrowing"
            submitIcon={Plus}
            onCancel={handleResetForm}
            loading={loading}
            loadingText="Creating Borrowing..."
          />
        </form>
      </FormWrapper>

      {/* Search Bar */}
      <SearchBar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        placeholder="Search borrowings by book title, member name, or status..."
        filteredCount={filteredBorrowings.length}
        totalCount={borrowings.length}
      />

      {/* Borrowings Grid */}
      <DataTable
        title="Borrowing Records"
        icon={BookOpenCheck}
        totalCount={borrowings.length}
        loading={loading}
        loadingType="skeleton-grid"
        emptyStateComponent={
          searchTerm ? (
            <EmptySearch 
              searchTerm={searchTerm} 
              onClearSearch={() => setSearchTerm('')} 
            />
          ) : (
            <EmptyBorrowings onCreateBorrowing={() => setShowAddForm(true)} />
          )
        }
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredBorrowings.map((borrowing) => (
            <div key={`${borrowing.book_id}-${borrowing.member_id}`} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-elevated transition-all duration-200">
              {/* Header with Status */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{getBookTitle(borrowing.book_id)}</h4>
                    <p className="text-sm text-gray-500">Borrowed by {getMemberName(borrowing.member_id)}</p>
                  </div>
                </div>
                {getStatusBadge(borrowing.is_returned ? 'returned' : 'borrowed', borrowing.due_date)}
              </div>

              {/* Details */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center space-x-3 text-sm">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-700">
                    Due: {borrowing.due_date ? new Date(borrowing.due_date).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-700">
                    {getDaysRemaining(borrowing.due_date)}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="text-xs text-gray-500">
                  ID: {borrowing.id || `${borrowing.book_id}-${borrowing.member_id}`}
                </div>
                    {!borrowing.is_returned && (
                      <button
                        onClick={() => handleReturnClick(borrowing)}
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
      </DataTable>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={isOpen}
        onClose={closeConfirmation}
        onConfirm={handleConfirm}
        title={config.title}
        message={config.message}
        confirmText={config.confirmText}
        cancelText={config.cancelText}
        type={config.type}
        isLoading={loading}
      />
    </div>
  );
};

export default Borrowings; 