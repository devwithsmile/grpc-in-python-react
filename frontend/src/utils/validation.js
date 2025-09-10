// Validation utility functions
export const validationRules = {
  // Book validation rules
  book: {
    title: {
      required: true,
      minLength: 3,
      maxLength: 200,
      trim: true,
      pattern: /^[a-zA-Z0-9\s\-.,'&()]+$/,
      message: 'Title must be 3-200 characters and contain only letters, numbers, spaces, and common punctuation'
    },
    author: {
      required: true,
      minLength: 2,
      maxLength: 100,
      trim: true,
      pattern: /^[a-zA-Z\s\-.,'&()]+$/,
      message: 'Author name must be 2-100 characters and contain only letters, spaces, and common punctuation'
    },
    isbn: {
      required: true,
      pattern: /^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$/,
      message: 'Please enter a valid ISBN-10 or ISBN-13 format'
    }
  },
  
  // Member validation rules
  member: {
    name: {
      required: true,
      minLength: 2,
      maxLength: 100,
      trim: true,
      pattern: /^[a-zA-Z\s\-.,'&()]+$/,
      message: 'Name must be 2-100 characters and contain only letters, spaces, and common punctuation'
    },
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Please enter a valid email address'
    },
    phone: {
      required: false,
      pattern: /^[\+]?[1-9][\d]{0,15}$/,
      message: 'Please enter a valid phone number'
    }
  },
  
  // Borrowing validation rules
  borrowing: {
    bookId: {
      required: true,
      message: 'Please select a book'
    },
    memberId: {
      required: true,
      message: 'Please select a member'
    },
    dueDate: {
      required: true,
      minDate: new Date().toISOString().split('T')[0],
      message: 'Due date must be today or later'
    }
  }
};

// Validation functions
export const validateField = (value, rules) => {
  const errors = [];
  
  // Trim whitespace if required
  if (rules.trim && typeof value === 'string') {
    value = value.trim();
  }
  
  // Required validation
  if (rules.required && (!value || value === '')) {
    errors.push(`${rules.message || 'This field is required'}`);
    return { isValid: false, errors, value };
  }
  
  // Skip other validations if field is empty and not required
  if (!value || value === '') {
    return { isValid: true, errors: [], value };
  }
  
  // Min length validation
  if (rules.minLength && value.length < rules.minLength) {
    errors.push(`${rules.message || `Minimum length is ${rules.minLength} characters`}`);
  }
  
  // Max length validation
  if (rules.maxLength && value.length > rules.maxLength) {
    errors.push(`${rules.message || `Maximum length is ${rules.maxLength} characters`}`);
  }
  
  // Pattern validation
  if (rules.pattern && !rules.pattern.test(value)) {
    errors.push(rules.message || 'Invalid format');
  }
  
  // Min date validation
  if (rules.minDate && new Date(value) < new Date(rules.minDate)) {
    errors.push(rules.message || `Date must be ${rules.minDate} or later`);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    value: rules.trim ? value : value
  };
};

// Validate entire form
export const validateForm = (data, formType) => {
  const rules = validationRules[formType];
  if (!rules) {
    return { isValid: true, errors: {}, data };
  }
  
  const errors = {};
  const sanitizedData = {};
  let isValid = true;
  
  Object.keys(rules).forEach(field => {
    const fieldRules = rules[field];
    const fieldValue = data[field];
    const validation = validateField(fieldValue, fieldRules);
    
    if (!validation.isValid) {
      errors[field] = validation.errors;
      isValid = false;
    }
    
    sanitizedData[field] = validation.value;
  });
  
  return { isValid, errors, data: sanitizedData };
};

// Check for duplicates
export const checkDuplicate = (value, field, existingItems, currentId = null) => {
  if (!value || !existingItems) return false;
  
  return existingItems.some(item => 
    item.id !== currentId && 
    item[field] && 
    item[field].toLowerCase() === value.toLowerCase()
  );
};

// Sanitize data
export const sanitizeData = (data, formType) => {
  const rules = validationRules[formType];
  if (!rules) return data;
  
  const sanitized = {};
  
  Object.keys(data).forEach(key => {
    const value = data[key];
    const fieldRules = rules[key];
    
    if (fieldRules && fieldRules.trim && typeof value === 'string') {
      sanitized[key] = value.trim();
    } else {
      sanitized[key] = value;
    }
  });
  
  return sanitized;
};
