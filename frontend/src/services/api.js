// API service for communicating with the REST backend
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = BACKEND_URL;
  }

  // Generic HTTP request method
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Books API
  async createBook(bookData) {
    return this.request('/books', {
      method: 'POST',
      body: JSON.stringify(bookData),
    });
  }

  async getBooks() {
    return this.request('/books');
  }

  async getBook(id) {
    return this.request(`/books/${id}`);
  }

  async updateBook(id, bookData) {
    return this.request(`/books/${id}`, {
      method: 'PUT',
      body: JSON.stringify(bookData),
    });
  }

  async deleteBook(id) {
    return this.request(`/books/${id}`, {
      method: 'DELETE',
    });
  }

  // Members API
  async createMember(memberData) {
    return this.request('/members', {
      method: 'POST',
      body: JSON.stringify(memberData),
    });
  }

  async getMembers() {
    return this.request('/members');
  }

  async getMember(id) {
    return this.request(`/members/${id}`);
  }

  async updateMember(id, memberData) {
    return this.request(`/members/${id}`, {
      method: 'PUT',
      body: JSON.stringify(memberData),
    });
  }

  async deleteMember(id) {
    return this.request(`/members/${id}`, {
      method: 'DELETE',
    });
  }

  // Borrowings API
  async borrowBook(borrowingData) {
    return this.request('/borrowings', {
      method: 'POST',
      body: JSON.stringify(borrowingData),
    });
  }

  async returnBook(bookId, memberId) {
    return this.request(`/borrowings/return`, {
      method: 'POST',
      body: JSON.stringify({ book_id: bookId, member_id: memberId }),
    });
  }

  async getBorrowings() {
    return this.request('/borrowings');
  }

  async getMemberBorrowings(memberId) {
    return this.request(`/borrowings/member/${memberId}`);
  }
}

export default new ApiService(); 