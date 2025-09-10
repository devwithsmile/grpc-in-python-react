import React from 'react';

const PageHeader = ({ 
  icon: Icon, 
  title, 
  description, 
  buttonText, 
  onButtonClick, 
  buttonIcon: ButtonIcon,
  buttonClassName = "btn-primary mt-4 sm:mt-0"
}) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Icon className="w-6 h-6 mr-3" />
          {title}
        </h2>
        <p className="text-gray-600 mt-1">{description}</p>
      </div>
      <button
        onClick={onButtonClick}
        className={buttonClassName}
      >
        {ButtonIcon && <ButtonIcon className="w-4 h-4 mr-2" />}
        {buttonText}
      </button>
    </div>
  );
};

export default PageHeader;
