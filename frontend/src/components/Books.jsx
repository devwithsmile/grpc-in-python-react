import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Bookmark } from 'lucide-react';
import api from '../services/api';
import { PageHeader, FormWrapper, SearchBar, DataTable, FormField, FormActions, ConfirmationModal, EmptyBooks, EmptySearch } from './common';
import { useFormValidation } from '../hooks/useFormValidation';
import { useToast } from '../hooks/useToast';
import { useConfirmationModal } from '../hooks/useModal';

const Books = () => {
  const [books, setBooks] = useState([]);
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
  } = useFormValidation('book', { title: '', author: '', isbn: '' });
  
  // Toast notifications
  const { showError, showSuccess } = useToast();
  
  // Confirmation modal
  const { isOpen, config, openConfirmation, closeConfirmation, handleConfirm } = useConfirmationModal();

  // Load books on component mount
  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const data = await api.getBooks();
      setBooks(data);
    } catch (err) {
      console.error('Error loading books:', err);
      showError('Failed to load books. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form data
    const validation = validateFormData(formData, books);
    if (!validation.isValid) {
      return;
    }

    try {
      setLoading(true);
      const createdBook = await api.createBook(validation.data);
      setBooks([...books, createdBook]);
      resetForm();
      setShowAddForm(false);
      showSuccess('Book created successfully!');
    } catch (err) {
      console.error('Error creating book:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 400) {
        showError('Invalid book data. Please check your input.');
      } else if (err.status === 409) {
        showError('A book with this ISBN already exists.');
      } else {
        showError('Failed to create book. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (book) => {
    openConfirmation({
      title: "Delete Book",
      message: `Are you sure you want to delete "${book.title}" by ${book.author}? This action cannot be undone.`,
      confirmText: "Delete Book",
      cancelText: "Cancel",
      type: "danger",
      onConfirm: () => handleDelete(book.id)
    });
  };

  const handleDelete = async (id) => {
    try {
      setLoading(true);
      await api.deleteBook(id);
      setBooks(books.filter(book => book.id !== id));
      showSuccess('Book deleted successfully!');
    } catch (err) {
      console.error('Error deleting book:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 404) {
        showError('Book not found.');
      } else {
        showError('Failed to delete book. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    handleFieldChange(e.target.name, e.target.value);
  };

  const handleFieldBlurEvent = (e) => {
    handleFieldBlur(e.target.name, books);
  };

  const filteredBooks = books.filter(book =>
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.isbn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleResetForm = () => {
    resetForm();
    setShowAddForm(false);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <PageHeader
        icon={BookOpen}
        title="Library Collection"
        description="Manage your library's book inventory"
        buttonText="Add New Book"
        buttonIcon={Plus}
        onButtonClick={() => setShowAddForm(!showAddForm)}
      />

      {/* Add Book Form */}
      <FormWrapper
        isVisible={showAddForm}
        title="Add New Book"
        icon={Plus}
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid-responsive">
            <FormField
              label="Book Title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter book title"
              required
              error={formErrors.title}
            />
            <FormField
              label="Author"
              name="author"
              value={formData.author}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter author name"
              required
              error={formErrors.author}
            />
            <FormField
              label="ISBN"
              name="isbn"
              value={formData.isbn}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter ISBN (ISBN-10 or ISBN-13)"
              required
              error={formErrors.isbn}
            />
          </div>
          
          <FormActions
            submitText="Add Book"
            submitIcon={Plus}
            onCancel={handleResetForm}
            loading={loading}
            loadingText="Adding Book..."
          />
        </form>
      </FormWrapper>

      {/* Search and Filter Bar */}
      <SearchBar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        placeholder="Search books by title, author, or ISBN..."
        filteredCount={filteredBooks.length}
        totalCount={books.length}
      />

      {/* Books Table */}
      <DataTable
        title="Books Collection"
        icon={Bookmark}
        totalCount={books.length}
        loading={loading}
        loadingType="skeleton-table"
        emptyStateComponent={
          searchTerm ? (
            <EmptySearch 
              searchTerm={searchTerm} 
              onClearSearch={() => setSearchTerm('')} 
            />
          ) : (
            <EmptyBooks onAddBook={() => setShowAddForm(true)} />
          )
        }
      >
        <div className="table-container">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header th">Title</th>
                <th className="table-header th">Author</th>
                <th className="table-header th">ISBN</th>
                <th className="table-header th">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {filteredBooks.map((book) => (
                <tr key={book.id} className="table-row">
                  <td className="table-cell table-cell-primary">
                    <div className="flex items-center">
                      <BookOpen className="w-4 h-4 text-blue-500 mr-2" />
                      {book.title}
                    </div>
                  </td>
                  <td className="table-cell table-cell-secondary">{book.author}</td>
                  <td className="table-cell table-cell-secondary">
                    <code className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">
                      {book.isbn}
                    </code>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleDeleteClick(book)}
                        className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200"
                        title="Delete book"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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

export default Books; 