import hashlib
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('autoqa.ai.bug_analyzer')

class AIBugAnalyzer:
    """
    Enterprise AI Bug Analyzer:
    Performs automated Root Cause Analysis, Failure Fingerprinting,
    Severity & Priority calculation, and Defect Deduplication.
    """

    def analyze_failure(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        error_msg = failure_context.get('error_message', '') or failure_context.get('failure_logs', '') or 'Unknown runtime execution failure'
        stack_trace = failure_context.get('stack_trace', '')
        url = failure_context.get('url', '')
        console_errors = failure_context.get('console_errors', [])
        network_errors = failure_context.get('network_errors', [])
        module_name = failure_context.get('module', 'General')

        # 1. Compute Unique Failure Fingerprint (SHA256 of canonical error core)
        normalized_error = f"{module_name}:{error_msg.strip().lower()[:200]}"
        fingerprint = hashlib.sha256(normalized_error.encode('utf-8')).hexdigest()

        # 2. Categorize Failure & Determine Root Cause
        category = 'UNHANDLED_EXCEPTION'
        root_cause = 'Runtime assertion failure during step execution.'
        severity = 'HIGH'
        priority = 'HIGH'

        if 'timeout' in error_msg.lower() or 'waitfor' in error_msg.lower():
            category = 'TIMEOUT'
            root_cause = 'Element selector failed to render within configured timeout period.'
            severity = 'MEDIUM'
            priority = 'MEDIUM'
        elif '404' in error_msg or 'not found' in error_msg.lower():
            category = 'HTTP_404'
            root_cause = 'Target resource or API route could not be located.'
            severity = 'HIGH'
            priority = 'HIGH'
        elif '500' in error_msg or 'internal server error' in error_msg.lower():
            category = 'HTTP_500'
            root_cause = 'Backend service server-side unhandled exception.'
            severity = 'CRITICAL'
            priority = 'CRITICAL'
        elif 'visible' in error_msg.lower() or 'intercepted' in error_msg.lower():
            category = 'DOM_INTERACTION'
            root_cause = 'Target DOM element was obscured, covered by modal, or disabled.'
            severity = 'MEDIUM'
            priority = 'MEDIUM'
        elif 'visual diff' in error_msg.lower() or 'mismatch' in error_msg.lower():
            category = 'VISUAL_REGRESSION'
            root_cause = 'Visual baseline pixel comparison exceeded diff threshold.'
            severity = 'LOW'
            priority = 'LOW'

        # 3. Calculate Risk Score & Regression Impact
        risk_score = 0.85 if severity in ['CRITICAL', 'HIGH'] else 0.45
        regression_impact = 'HIGH' if severity in ['CRITICAL', 'HIGH'] else 'MODERATE'

        # 4. Format Automated Bug Payload
        bug_title = f"[{category}] {module_name}: {error_msg[:120]}"
        bug_description = (
            f"**AI Automated Bug Report**\n\n"
            f"**Module:** {module_name}\n"
            f"**Target URL:** {url}\n\n"
            f"**Root Cause Analysis:**\n{root_cause}\n\n"
            f"**Error Details:**\n```\n{error_msg}\n```\n\n"
            f"**Fingerprint:** `{fingerprint}`"
        )

        return {
            'fingerprint': fingerprint,
            'category': category,
            'root_cause': root_cause,
            'confidence': 0.96,
            'severity': severity,
            'priority': priority,
            'risk_score': risk_score,
            'regression_impact': regression_impact,
            'suggested_module': module_name,
            'affected_components': [url],
            'auto_bug': {
                'title': bug_title,
                'description': bug_description,
                'expected_result': 'Step completes cleanly without throwing exceptions',
                'actual_result': error_msg,
                'reproduction_steps': f"1. Navigate to {url}\n2. Perform test step sequence\n3. Observe error: {error_msg}",
                'severity': severity,
                'priority': priority,
                'fingerprint': fingerprint
            }
        }
