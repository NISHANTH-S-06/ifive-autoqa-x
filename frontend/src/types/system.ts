export interface SystemHealth {
  status: 'ok' | 'degraded';
  environment: string;
  safe_mode: boolean;
  debug: boolean;
  production_execution_enabled: boolean;
  real_target_execution_enabled: boolean;
  tls_verification_enabled: boolean;
  database: { ready: boolean; migrations_current: boolean; immutable_triggers_installed: boolean };
  storage: Record<string, boolean>;
  worker: { active_count: number; heartbeat_ok: boolean };
  queue: { queued: number; running: number; terminal: number };
  frontend: { available: boolean };
  disk: { warning: boolean; free_mb: number };
  playwright: { installed: boolean; chromium_available: boolean };
}

export interface BackupSummary {
  backup_id: string;
  file_count: number;
  total_bytes?: number;
  manifest_sha256?: string;
  valid?: boolean;
}

export interface CleanupSummary {
  dry_run: boolean;
  candidate_files: number;
  candidate_bytes: number;
  deleted_files: number;
  deleted_bytes: number;
  records_removed: Record<string, number>;
  categories: Record<string, number>;
  protected: Record<string, boolean>;
}

