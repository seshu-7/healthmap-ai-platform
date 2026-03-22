import React from 'react';

interface State {
  hasError: boolean;
  errorMessage: string;
}

interface Props {
  children: React.ReactNode;
}

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false, errorMessage: '' };

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      errorMessage: error?.message || 'Unknown frontend error',
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('UI crash captured by ErrorBoundary', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ maxWidth: 900, margin: '48px auto', padding: 20 }}>
          <div className="card" style={{ borderLeft: '4px solid var(--danger)' }}>
            <h2 style={{ margin: 0, fontSize: 20 }}>UI error occurred</h2>
            <p style={{ marginTop: 10, color: 'var(--text-secondary)' }}>
              The app hit a runtime error. Reload the page; if this continues, share the error text below.
            </p>
            <div style={{
              marginTop: 12,
              padding: 12,
              borderRadius: 8,
              background: '#fef2f2',
              color: 'var(--danger)',
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
              fontSize: 13,
              wordBreak: 'break-word',
            }}>
              {this.state.errorMessage}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
