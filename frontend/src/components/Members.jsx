import React, { useState, useEffect } from 'react';
import { Users, Plus, Trash2, Edit, Search, UserPlus, Mail, Phone, Calendar } from 'lucide-react';
import api from '../services/api';

const Members = () => {
  const [members, setMembers] = useState([]);
  const [newMember, setNewMember] = useState({ name: '', email: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Load members on component mount
  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const data = await api.getMembers();
      setMembers(data);
      setError('');
    } catch (err) {
      setError('Failed to load members');
      console.error('Error loading members:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newMember.name || !newMember.email) {
      setError('Please fill in at least name and email');
      return;
    }

    try {
      setLoading(true);
      const createdMember = await api.createMember(newMember);
      setMembers([...members, createdMember]);
      setNewMember({ name: '', email: '', phone: '' });
      setShowAddForm(false);
      setError('');
    } catch (err) {
      setError('Failed to create member');
      console.error('Error creating member:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this member?')) return;

    try {
      setLoading(true);
      await api.deleteMember(id);
      setMembers(members.filter(member => member.id !== id));
      setError('');
    } catch (err) {
      setError('Failed to delete member');
      console.error('Error deleting member:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setNewMember({
      ...newMember,
      [e.target.name]: e.target.value
    });
  };

  const filteredMembers = members.filter(member =>
    member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    member.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (member.phone && member.phone.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const resetForm = () => {
    setNewMember({ name: '', email: '', phone: '' });
    setShowAddForm(false);
    setError('');
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Users className="w-6 h-6 mr-3 text-green-600" />
            Library Members
          </h2>
          <p className="text-gray-600 mt-1">Manage your library's member database</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-primary mt-4 sm:mt-0"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Add New Member
        </button>
      </div>

      {/* Add Member Form */}
      {showAddForm && (
        <div className="card animate-slide-up">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <UserPlus className="w-5 h-5 mr-2 text-green-600" />
              Add New Member
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
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    name="name"
                    value={newMember.name}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter member's full name"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={newMember.email}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter email address"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Phone Number (Optional)</label>
                  <input
                    type="tel"
                    name="phone"
                    value={newMember.phone}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter phone number"
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
                      Adding Member...
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Member
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
            placeholder="Search members by name, email, or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {filteredMembers.length} of {members.length} members
          </span>
        </div>
      </div>

      {/* Members Grid */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Users className="w-5 h-5 mr-2 text-green-600" />
              Members Directory
            </h3>
            <div className="text-sm text-gray-500">
              Total: {members.length} members
            </div>
          </div>
        </div>
        
        <div className="card-body">
          {loading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-500">Loading members...</p>
            </div>
          ) : filteredMembers.length === 0 ? (
            <div className="empty-state">
              <Users className="empty-state-icon" />
              <p className="empty-state-text">
                {searchTerm ? 'No members found matching your search.' : 'No members registered yet.'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="btn-primary mt-4"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Register Your First Member
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMembers.map((member) => (
                <div key={member.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-elevated transition-all duration-200 group">
                  {/* Member Avatar and Info */}
                  <div className="flex items-start space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                      {getInitials(member.name)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors duration-200">
                        {member.name}
                      </h4>
                      <p className="text-sm text-gray-500">Member ID: {member.id}</p>
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center space-x-3 text-sm">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">{member.email}</span>
                    </div>
                    {member.phone && (
                      <div className="flex items-center space-x-3 text-sm">
                        <Phone className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700">{member.phone}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                      <span className="badge badge-success">Active</span>
                    </div>
                    <button
                      onClick={() => handleDelete(member.id)}
                      className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200"
                      title="Delete member"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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

export default Members; 