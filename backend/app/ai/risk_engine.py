import logging
from typing import Dict, Any

logger = logging.getLogger('autoqa.ai.risk_engine')

class SmartRiskEngine:
    """
    Enterprise Smart Risk Engine:
    Calculates multi-dimensional risk scores (Business, Technical, Regression,
    Release, Security, Performance, Visual, Accessibility) and Overall Risk Score.
    """

    def calculate_risk(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        open_critical_bugs = metrics.get('open_critical_bugs', 0)
        open_total_bugs = metrics.get('open_total_bugs', 0)
        pass_rate = metrics.get('pass_rate', 100.0)
        coverage = metrics.get('automation_coverage', 95.0)
        visual_diffs = metrics.get('visual_diffs', 0)
        security_issues = metrics.get('security_issues', 0)
        a11y_violations = metrics.get('a11y_violations', 0)

        # Individual Risk Sub-scores (0-100, where 0 is zero risk and 100 is maximum risk)
        business_risk = min(100.0, open_critical_bugs * 30.0 + (100.0 - pass_rate) * 1.5)
        technical_risk = min(100.0, (100.0 - coverage) * 1.2 + open_total_bugs * 5.0)
        regression_risk = min(100.0, (100.0 - pass_rate) * 2.0)
        security_risk = min(100.0, security_issues * 25.0)
        performance_risk = min(100.0, metrics.get('slow_api_count', 0) * 15.0)
        visual_risk = min(100.0, visual_diffs * 10.0)
        accessibility_risk = min(100.0, a11y_violations * 8.0)
        release_risk = (business_risk + technical_risk + security_risk + regression_risk) / 4.0

        overall_risk_score = round(
            (business_risk * 0.25) +
            (technical_risk * 0.20) +
            (regression_risk * 0.20) +
            (security_risk * 0.15) +
            (visual_risk * 0.10) +
            (accessibility_risk * 0.10),
            1
        )

        return {
            'overall_risk_score': overall_risk_score,
            'business_risk': round(business_risk, 1),
            'technical_risk': round(technical_risk, 1),
            'regression_risk': round(regression_risk, 1),
            'release_risk': round(release_risk, 1),
            'security_risk': round(security_risk, 1),
            'performance_risk': round(performance_risk, 1),
            'visual_risk': round(visual_risk, 1),
            'accessibility_risk': round(accessibility_risk, 1)
        }
