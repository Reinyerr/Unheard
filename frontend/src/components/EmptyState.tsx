import type { ReactNode } from 'react';
import type { ExperimentStatus } from '../types/research';

type Kind = ExperimentStatus | 'unavailable' | 'choose_language' | 'loading' | 'pending';
export const statusLabels: Record<Kind, string> = {
  completed: 'Saved evidence available', not_tested: 'Not tested', unsupported: 'Unsupported setting',
  technical_error: 'Technical error', incompatible_output: 'Output requires review',
  unavailable: 'Data unavailable', choose_language: 'Choose a language', loading: 'Loading verified data', pending: 'View pending',
};
export default function EmptyState({ kind, title, children, onRetry, retryLabel = 'Reload static data' }: {
  kind: Kind; title?: string; children?: ReactNode; onRetry?: () => void; retryLabel?: string;
}) {
  return <div className={`empty-state empty-state-${kind}`} role={kind === 'technical_error' ? 'alert' : 'status'} aria-live="polite">
    <h3>{title ?? statusLabels[kind]}</h3>
    {children ? <div className="empty-state-description">{children}</div> : null}
    {onRetry ? <button type="button" onClick={onRetry}>{retryLabel}</button> : null}
  </div>;
}
