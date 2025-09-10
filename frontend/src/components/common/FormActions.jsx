import React from 'react';

const FormActions = ({ 
  submitText, 
  submitIcon: SubmitIcon, 
  cancelText = "Cancel", 
  onCancel, 
  loading = false, 
  loadingText, 
  submitClassName = "btn-primary flex-1",
  cancelClassName = "btn-secondary flex-1"
}) => {
  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <button
        type="submit"
        disabled={loading}
        className={submitClassName}
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            {loadingText}
          </>
        ) : (
          <>
            {SubmitIcon && <SubmitIcon className="w-4 h-4 mr-2" />}
            {submitText}
          </>
        )}
      </button>
      <button
        type="button"
        onClick={onCancel}
        className={cancelClassName}
      >
        {cancelText}
      </button>
    </div>
  );
};

export default FormActions;
