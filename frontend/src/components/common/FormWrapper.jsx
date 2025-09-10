import React from 'react';

const FormWrapper = ({ 
  isVisible, 
  title, 
  icon: Icon, 
  children, 
  error,
  className = "card animate-slide-up"
}) => {
  if (!isVisible) return null;

  return (
    <div className={className}>
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          {Icon && <Icon className="w-5 h-5 mr-2" />}
          {title}
        </h3>
      </div>
      
      <div className="card-body">
        {error && (
          <div className="message message-error mb-6">
            {error}
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default FormWrapper;
