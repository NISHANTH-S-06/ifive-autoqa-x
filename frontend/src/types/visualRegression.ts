export interface VisualBaseline {
  id: number;
  project_id: number;
  name: string;
  module: string;
  browser: string;
  viewport_width: number;
  viewport_height: number;
  capture_type: string;
  element_selector?: string | null;
  route_path: string;
  image_path: string;
  version: number;
  is_active: boolean;
  ignore_rules_json?: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface VisualBaselineHistory {
  id: number;
  baseline_id: number;
  version: number;
  image_path: string;
  ignore_rules_json?: string | null;
  change_summary?: string | null;
  created_by: number;
  created_at: string;
}

export interface VisualComparisonRun {
  id: number;
  project_id: number;
  run_id?: number | null;
  baseline_id: number;
  baseline_version: number;
  name: string;
  status: 'PASSED' | 'DIFF_DETECTED' | 'FAILED' | 'ERROR';
  browser: string;
  viewport_width: number;
  viewport_height: number;
  module: string;
  capture_type: string;
  diff_percentage: number;
  total_pixels_changed: number;
  layout_shifts: number;
  missing_elements_count: number;
  color_changes_count: number;
  font_changes_count: number;
  icon_changes_count: number;
  alignment_issues_count: number;
  spacing_changes_count: number;
  responsive_changes_count: number;
  ai_classification: 'COSMETIC' | 'MINOR' | 'MEDIUM' | 'CRITICAL';
  ai_confidence_score: number;
  ai_severity: 'COSMETIC' | 'MINOR' | 'MEDIUM' | 'CRITICAL';
  ai_root_cause?: string | null;
  ai_recommendation?: string | null;
  current_image_path: string;
  diff_image_path?: string | null;
  overlay_image_path?: string | null;
  heatmap_image_path?: string | null;
  bounding_box_image_path?: string | null;
  metadata_json?: string | null;
  created_by: number;
  created_at: string;
}

export interface CreateBaselinePayload {
  project_id: number;
  name: string;
  module: string;
  browser: string;
  viewport_width: number;
  viewport_height: number;
  capture_type: string;
  element_selector?: string;
  route_path: string;
  ignore_rules?: Record<string, any>;
  image_base64?: string;
}

export interface ComparePayload {
  project_id: number;
  baseline_id?: number;
  name: string;
  module: string;
  browser: string;
  viewport_width: number;
  viewport_height: number;
  route_path: string;
  capture_type: string;
  run_id?: number;
  ignore_rules?: Record<string, any>;
  image_base64?: string;
}

export interface VisualHistoryFilter {
  project_id?: number;
  module?: string;
  browser?: string;
  severity?: string;
  ai_classification?: string;
  status?: string;
  limit?: number;
  offset?: number;
}
