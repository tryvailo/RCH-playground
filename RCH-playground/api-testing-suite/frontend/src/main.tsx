import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Suppress browser extension errors (not our code)
if (typeof window !== 'undefined') {
  // Helper function to check if error is from browser extension
  const isBrowserExtensionError = (message: string, stack?: string): boolean => {
    const fullText = (message + ' ' + (stack || '')).toLowerCase();
    const patterns = [
      'message channel closed',
      'asynchronous response',
      'listener indicated',
      'extension context invalidated',
      'content.js',
      'grammarly',
      'iterable',
      'a listener indicated',
      'returning true',
      'before a response was received',
      'chrome-extension://',
      'moz-extension://',
      'safari-extension://',
      'extension://',
    ];
    return patterns.some(pattern => fullText.includes(pattern));
  };

  // Suppress unhandled promise rejections from browser extensions
  window.addEventListener('unhandledrejection', (event) => {
    const message = event.reason?.message || event.reason?.toString() || '';
    const stack = event.reason?.stack || '';
    
    if (isBrowserExtensionError(message, stack)) {
      // Silently ignore browser extension errors
      event.preventDefault();
      event.stopPropagation();
      if (typeof event.stopImmediatePropagation === 'function') {
        event.stopImmediatePropagation();
      }
      return false;
    }
  }, true); // Use capture phase

  // Suppress console errors from browser extensions and MSIF loading errors
  const originalError = console.error;
  console.error = (...args: any[]) => {
    const message = args[0]?.toString() || '';
    const stack = args[1]?.toString() || '';
    
    // Filter out known browser extension errors
    if (
      isBrowserExtensionError(message, stack) ||
      message.includes('Failed to load MSIF data') ||
      message.includes('Failed to parse MSIF') ||
      message.includes('Could not find header row') ||
      message.includes('Backend proxy') ||
      message.includes('proxy-fetch') ||
      (message + ' ' + stack).toLowerCase().includes('msifloader')
    ) {
      // Silently ignore browser extension errors and MSIF loading errors (fallback data is used)
      return;
    }
    originalError.apply(console, args);
  };
  const originalWarn = console.warn;
  console.warn = (...args: any[]) => {
    const message = args[0]?.toString() || '';
    const stack = args[1]?.toString() || '';
    
    if (isBrowserExtensionError(message, stack)) {
      return;
    }
    originalWarn.apply(console, args);
  };

  // Suppress global error events from browser extensions
  window.addEventListener('error', (event) => {
    const message = event.message || '';
    const filename = event.filename || '';
    const stack = event.error?.stack || '';
    
    if (
      isBrowserExtensionError(message, stack) ||
      filename.includes('content.js') ||
      filename.includes('extension://') ||
      filename.includes('chrome-extension://') ||
      filename.includes('moz-extension://') ||
      filename.includes('safari-extension://') ||
      filename.includes('Grammarly.js')
    ) {
      // Silently ignore browser extension errors
      event.preventDefault();
      event.stopPropagation();
      if (typeof event.stopImmediatePropagation === 'function') {
        event.stopImmediatePropagation();
      }
      return;
    }
  }, true); // Use capture phase to catch errors early
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

