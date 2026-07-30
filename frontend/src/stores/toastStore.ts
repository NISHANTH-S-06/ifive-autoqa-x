import { useState, useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
}

type ToastListener = (toasts: ToastMessage[]) => void;

let toastsState: ToastMessage[] = [];
const listeners = new Set<ToastListener>();

export const toast = {
  show: (type: ToastType, message: string, title?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    toastsState = [...toastsState, { id, type, message, title }];
    listeners.forEach(listener => listener(toastsState));

    setTimeout(() => {
      toast.dismiss(id);
    }, 4000);
  },
  success: (message: string, title?: string) => toast.show('success', message, title),
  error: (message: string, title?: string) => toast.show('error', message, title),
  warning: (message: string, title?: string) => toast.show('warning', message, title),
  info: (message: string, title?: string) => toast.show('info', message, title),

  dismiss: (id: string) => {
    toastsState = toastsState.filter(t => t.id !== id);
    listeners.forEach(listener => listener(toastsState));
  }
};

export function useToasts() {
  const [toasts, setToasts] = useState<ToastMessage[]>(toastsState);

  useEffect(() => {
    listeners.add(setToasts);
    return () => {
      listeners.delete(setToasts);
    };
  }, []);

  return { toasts, dismiss: toast.dismiss };
}
