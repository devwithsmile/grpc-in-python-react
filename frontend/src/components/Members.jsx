import React, { useState, useEffect } from 'react';
import { Users, Plus, Trash2, UserPlus, Mail, Phone } from 'lucide-react';
import api from '../services/api';
import { PageHeader, FormWrapper, SearchBar, DataTable, FormField, FormActions, ConfirmationModal, EmptyMembers, EmptySearch } from './common';
import { useFormValidation } from '../hooks/useFormValidation';
import { useToast } from '../hooks/useToast';
import { useConfirmationModal } from '../hooks/useModal';

const Members = () => {
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
  } = useFormValidation('member', { name: '', email: '', phone: '' });
  
  // Toast notifications
  const { showError, showSuccess } = useToast();
  
  // Confirmation modal
  const { isOpen, config, openConfirmation, closeConfirmation, handleConfirm } = useConfirmationModal();

  // Load members on component mount
  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const data = await api.getMembers();
      setMembers(data);
    } catch (err) {
      console.error('Error loading members:', err);
      showError('Failed to load members. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form data
    const validation = validateFormData(formData, members);
    if (!validation.isValid) {
      return;
    }

    try {
      setLoading(true);
      const createdMember = await api.createMember(validation.data);
      setMembers([...members, createdMember]);
      resetForm();
      setShowAddForm(false);
      showSuccess('Member created successfully!');
    } catch (err) {
      console.error('Error creating member:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 400) {
        showError('Invalid member data. Please check your input.');
      } else if (err.status === 409) {
        showError('A member with this email already exists.');
      } else {
        showError('Failed to create member. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (member) => {
    openConfirmation({
      title: "Delete Member",
      message: `Are you sure you want to delete "${member.name}" (${member.email})? This action cannot be undone.`,
      confirmText: "Delete Member",
      cancelText: "Cancel",
      type: "danger",
      onConfirm: () => handleDelete(member.id)
    });
  };

  const handleDelete = async (id) => {
    try {
      setLoading(true);
      await api.deleteMember(id);
      setMembers(members.filter(member => member.id !== id));
      showSuccess('Member deleted successfully!');
    } catch (err) {
      console.error('Error deleting member:', err);
      if (err.type === 'network') {
        showError('Network error: Unable to connect to server');
      } else if (err.status === 404) {
        showError('Member not found.');
      } else {
        showError('Failed to delete member. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    handleFieldChange(e.target.name, e.target.value);
  };

  const handleFieldBlurEvent = (e) => {
    handleFieldBlur(e.target.name, members);
  };

  const filteredMembers = members.filter(member =>
    member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    member.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (member.phone && member.phone.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleResetForm = () => {
    resetForm();
    setShowAddForm(false);
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <PageHeader
        icon={Users}
        title="Library Members"
        description="Manage your library's member database"
        buttonText="Add New Member"
        buttonIcon={UserPlus}
        onButtonClick={() => setShowAddForm(!showAddForm)}
      />

      {/* Add Member Form */}
      <FormWrapper
        isVisible={showAddForm}
        title="Add New Member"
        icon={UserPlus}
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid-responsive">
            <FormField
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter member's full name"
              required
              error={formErrors.name}
            />
            <FormField
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter email address"
              required
              error={formErrors.email}
            />
            <FormField
              label="Phone Number (Optional)"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleInputChange}
              onBlur={handleFieldBlurEvent}
              placeholder="Enter phone number"
              error={formErrors.phone}
            />
          </div>
          
          <FormActions
            submitText="Add Member"
            submitIcon={UserPlus}
            onCancel={handleResetForm}
            loading={loading}
            loadingText="Adding Member..."
          />
        </form>
      </FormWrapper>

      {/* Search Bar */}
      <SearchBar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        placeholder="Search members by name, email, or phone..."
        filteredCount={filteredMembers.length}
        totalCount={members.length}
      />

      {/* Members Grid */}
      <DataTable
        title="Members Directory"
        icon={Users}
        totalCount={members.length}
        loading={loading}
        loadingType="skeleton-grid"
        emptyStateComponent={
          searchTerm ? (
            <EmptySearch 
              searchTerm={searchTerm} 
              onClearSearch={() => setSearchTerm('')} 
            />
          ) : (
            <EmptyMembers onAddMember={() => setShowAddForm(true)} />
          )
        }
      >
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
                      onClick={() => handleDeleteClick(member)}
                      className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200"
                      title="Delete member"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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

export default Members; 