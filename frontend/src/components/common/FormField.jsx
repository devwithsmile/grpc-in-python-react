import React from 'react';
import { AlertCircle } from 'lucide-react';

const FormField = ({ 
  label, 
  name, 
  type = "text", 
  value, 
  onChange, 
  placeholder, 
  required = false, 
  options = null, // For select fields
  min = null, // For date inputs
  className = "",
  error = null, // Validation error
  onBlur = null, // Blur handler for validation
  disabled = false
}) => {
  const hasError = error && error.length > 0;
  const inputClasses = `form-input ${hasError ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''} ${className}`;

  return (
    <div>
      <label className="form-label">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        {type === 'select' ? (
          <select
            name={name}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            className={inputClasses}
            required={required}
            disabled={disabled}
          >
            <option value="">{placeholder}</option>
            {options && options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            className={inputClasses}
            placeholder={placeholder}
            required={required}
            min={min}
            disabled={disabled}
          />
        )}
        {hasError && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <AlertCircle className="h-5 w-5 text-red-500" />
          </div>
        )}
      </div>
      {hasError && (
        <div className="mt-1 text-sm text-red-600">
          {error.map((err, index) => (
            <div key={index}>{err}</div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FormField;
