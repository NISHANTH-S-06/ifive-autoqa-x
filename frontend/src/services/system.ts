import { apiGet, apiMutation } from './api';
import type { BackupSummary, CleanupSummary, SystemHealth } from '../types/system';

export const fetchSystemHealth = () => apiGet<SystemHealth>('/api/system/health');
export const fetchBackups = () => apiGet<BackupSummary[]>('/api/system/backups');
export const createBackup = (confirmation: string) => apiMutation<BackupSummary>('POST', '/api/system/backups', { confirmation });
export const previewCleanup = () => apiGet<CleanupSummary>('/api/system/cleanup-preview');
export const applyCleanup = (confirmation: string) => apiMutation<CleanupSummary>('POST', '/api/system/cleanup', { confirmation });

