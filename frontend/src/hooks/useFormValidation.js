import { useState, useCallback } from 'react';
import { validateForm, validateField, checkDuplicate, sanitizeData, validationRules } from '../utils/validation';

export const useFormValidation = (formType, initialData = {}) => {
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validateFieldValue = useCallback((field, value, existingItems = [], currentId = null) => {
    const validation = validateField(value, validationRules[formType]?.[field]);
    
    // Check for duplicates if applicable
    if (validation.isValid && existingItems && field !== 'dueDate') {
      const isDuplicate = checkDuplicate(value, field, existingItems, currentId);
      if (isDuplicate) {
        validation.isValid = false;
        validation.errors.push(`${field} already exists`);
      }
    }
    
    return validation;
  }, [formType]);

  const handleFieldChange = useCallback((field, value) => {
    setData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  }, [errors]);

  const handleFieldBlur = useCallback((field, existingItems = [], currentId = null) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    
    const value = data[field];
    const validation = validateFieldValue(field, value, existingItems, currentId);
    
    setErrors(prev => ({
      ...prev,
      [field]: validation.isValid ? null : validation.errors
    }));
  }, [data, validateFieldValue]);

  const validateFormData = useCallback((formData = data, existingItems = [], currentId = null) => {
    const sanitized = sanitizeData(formData, formType);
    const validation = validateForm(sanitized, formType);
    
    // Check for duplicates
    if (validation.isValid && existingItems) {
      const duplicateErrors = {};
      Object.keys(sanitized).forEach(field => {
        if (field !== 'dueDate' && validationRules[formType]?.[field]) {
          const isDuplicate = checkDuplicate(sanitized[field], field, existingItems, currentId);
          if (isDuplicate) {
            duplicateErrors[field] = [`${field} already exists`];
            validation.isValid = false;
          }
        }
      });
      
      if (!validation.isValid) {
        validation.errors = { ...validation.errors, ...duplicateErrors };
      }
    }
    
    setErrors(validation.errors);
    return validation;
  }, [data, formType]);

  const resetForm = useCallback((newData = {}) => {
    setData(newData);
    setErrors({});
    setTouched({});
  }, []);

  const setFieldError = useCallback((field, error) => {
    setErrors(prev => ({ ...prev, [field]: error }));
  }, []);

  const clearFieldError = useCallback((field) => {
    setErrors(prev => ({ ...prev, [field]: null }));
  }, []);

  return {
    data,
    errors,
    touched,
    handleFieldChange,
    handleFieldBlur,
    validateFormData,
    resetForm,
    setFieldError,
    clearFieldError,
    setData,
    setErrors
  };
};
