import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Edit, Search, Filter, Bookmark } from 'lucide-react';
import api from '../services/api';

const Books = () => {
  const [books, setBooks] = useState([]);
  const [newBook, setNewBook] = useState({ title: '', author: '', isbn: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Load books on component mount
  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const data = await api.getBooks();
      setBooks(data);
      setError('');
    } catch (err) {
      setError('Failed to load books');
      console.error('Error loading books:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newBook.title || !newBook.author || !newBook.isbn) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      const createdBook = await api.createBook(newBook);
      setBooks([...books, createdBook]);
      setNewBook({ title: '', author: '', isbn: '' });
      setShowAddForm(false);
      setError('');
    } catch (err) {
      setError('Failed to create book');
      console.error('Error creating book:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this book?')) return;

    try {
      setLoading(true);
      await api.deleteBook(id);
      setBooks(books.filter(book => book.id !== id));
      setError('');
    } catch (err) {
      setError('Failed to delete book');
      console.error('Error deleting book:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setNewBook({
      ...newBook,
      [e.target.name]: e.target.value
    });
  };

  const filteredBooks = books.filter(book =>
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.isbn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const resetForm = () => {
    setNewBook({ title: '', author: '', isbn: '' });
    setShowAddForm(false);
    setError('');
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <BookOpen className="w-6 h-6 mr-3 text-blue-600" />
            Library Collection
          </h2>
          <p className="text-gray-600 mt-1">Manage your library's book inventory</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-primary mt-4 sm:mt-0"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New Book
        </button>
      </div>

      {/* Add Book Form */}
      {showAddForm && (
        <div className="card animate-slide-up">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Plus className="w-5 h-5 mr-2 text-blue-600" />
              Add New Book
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
                  <label className="form-label">Book Title</label>
                  <input
                    type="text"
                    name="title"
                    value={newBook.title}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter book title"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Author</label>
                  <input
                    type="text"
                    name="author"
                    value={newBook.author}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter author name"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">ISBN</label>
                  <input
                    type="text"
                    name="isbn"
                    value={newBook.isbn}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter ISBN"
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
                      Adding Book...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Book
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

      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search books by title, author, or ISBN..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {filteredBooks.length} of {books.length} books
          </span>
        </div>
      </div>

      {/* Books Table */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Bookmark className="w-5 h-5 mr-2 text-blue-600" />
              Books Collection
            </h3>
            <div className="text-sm text-gray-500">
              Total: {books.length} books
            </div>
          </div>
        </div>
        
        <div className="overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-500">Loading books...</p>
            </div>
          ) : filteredBooks.length === 0 ? (
            <div className="empty-state">
              <BookOpen className="empty-state-icon" />
              <p className="empty-state-text">
                {searchTerm ? 'No books found matching your search.' : 'No books in the collection yet.'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="btn-primary mt-4"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Book
                </button>
              )}
            </div>
          ) : (
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
                            onClick={() => handleDelete(book.id)}
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
          )}
        </div>
      </div>
    </div>
  );
};

export default Books; 