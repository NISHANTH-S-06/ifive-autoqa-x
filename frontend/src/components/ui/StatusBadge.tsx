import React from 'react';
import { 
  FileText, Clock, CheckCircle2, XCircle, HelpCircle, 
  Layers, PlayCircle, Check, AlertTriangle, AlertCircle, Key, ShieldAlert
} from 'lucide-react';

export type StatusType = 
  | 'DRAFT' 
  | 'IN_REVIEW' 
  | 'APPROVED' 
  | 'REJECTED' 
  | 'NEED_CLARITY' 
  | 'QUEUED' 
  | 'RUNNING' 
  | 'PASS'
  | 'PASSED'
  | 'FAIL'
  | 'FAILED'
  | 'BLOCKED' 
  | 'PASS_WITH_WARNINGS'
  | 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION'
  | 'PENDING_SAFE_EPHEMERAL_INPUT'
  | string;

interface StatusBadgeProps {
  status: StatusType;
  label?: string;
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, label, size = 'md' }: StatusBadgeProps) {
  const raw = String(status || '').trim();
  const normStatus = raw.toUpperCase();

  const getStatusConfig = () => {
    switch (normStatus) {
      case 'DRAFT':
        return { className: 'badge-draft', icon: FileText, text: 'Draft' };
      case 'IN_REVIEW':
        return { className: 'badge-in_review', icon: Clock, text: 'In Review' };
      case 'APPROVED':
        return { className: 'badge-approved', icon: CheckCircle2, text: 'Approved' };
      case 'REJECTED':
        return { className: 'badge-rejected', icon: XCircle, text: 'Rejected' };
      case 'NEED_CLARITY':
        return { className: 'badge-need_clarity', icon: HelpCircle, text: 'Needs Clarification' };
      case 'QUEUED':
        return { className: 'badge-queued', icon: Layers, text: 'Queued' };
      case 'RUNNING':
        return { className: 'badge-running', icon: PlayCircle, text: 'Running' };
      case 'PASS':
      case 'PASSED':
        return { className: 'badge-pass', icon: Check, text: 'Passed' };
      case 'FAIL':
      case 'FAILED':
        return { className: 'badge-fail', icon: XCircle, text: 'Failed' };
      case 'BLOCKED':
        return { className: 'badge-blocked', icon: AlertCircle, text: 'Blocked' };
      case 'PASS_WITH_WARNINGS':
        return { className: 'badge-pass_with_warnings', icon: AlertTriangle, text: 'Passed with Warnings' };
      case 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION':
        return { className: 'badge-in_review', icon: ShieldAlert, text: 'Pending Authorization' };
      case 'PENDING_SAFE_EPHEMERAL_INPUT':
        return { className: 'badge-queued', icon: Key, text: 'Runtime Credential Required' };
      default:
        return { className: 'badge-draft', icon: FileText, text: raw || 'Unknown' };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <span 
      className={`badge ${config.className}`}
      style={{
        fontSize: size === 'sm' ? '0.7rem' : '0.75rem',
        padding: size === 'sm' ? '0.15rem 0.45rem' : '0.2rem 0.6rem',
        maxWidth: '220px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
      }}
      title={raw !== config.text ? `Raw Status: ${raw}` : undefined}
      data-testid={`status-badge-${normStatus.toLowerCase()}`}
    >
      <Icon size={size === 'sm' ? 11 : 13} style={{ flexShrink: 0 }} />
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {label || config.text}
      </span>
    </span>
  );
}
