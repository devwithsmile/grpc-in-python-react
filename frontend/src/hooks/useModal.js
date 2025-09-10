import { useState, useCallback } from 'react';

export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);
  const [modalData, setModalData] = useState(null);

  const openModal = useCallback((data = null) => {
    setModalData(data);
    setIsOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsOpen(false);
    setModalData(null);
  }, []);

  const toggleModal = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    modalData,
    openModal,
    closeModal,
    toggleModal
  };
};

export const useConfirmationModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [config, setConfig] = useState({
    title: "Confirm Action",
    message: "",
    confirmText: "Confirm",
    cancelText: "Cancel",
    type: "danger",
    onConfirm: null,
    onCancel: null
  });

  const openConfirmation = useCallback((modalConfig) => {
    setConfig({
      title: "Confirm Action",
      message: "",
      confirmText: "Confirm",
      cancelText: "Cancel",
      type: "danger",
      onConfirm: null,
      onCancel: null,
      ...modalConfig
    });
    setIsOpen(true);
  }, []);

  const closeConfirmation = useCallback(() => {
    setIsOpen(false);
    if (config.onCancel) {
      config.onCancel();
    }
  }, [config]);

  const handleConfirm = useCallback(() => {
    if (config.onConfirm) {
      config.onConfirm();
    }
    setIsOpen(false);
  }, [config]);

  return {
    isOpen,
    config,
    openConfirmation,
    closeConfirmation,
    handleConfirm
  };
};
