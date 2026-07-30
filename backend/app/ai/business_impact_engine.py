import logging
from typing import Dict, Any

logger = logging.getLogger('autoqa.ai.business_impact')

class BusinessImpactEngine:
    """
    Module 6: Business Impact Engine
    Calculates Business Severity, Revenue Impact, Customer Impact, Compliance Impact,
    Operational Impact, Release Risk, Priority, Fix Complexity, Developer & Testing Effort.
    """

    def evaluate_business_impact(self, defect_data: Dict[str, Any]) -> Dict[str, Any]:
        severity = defect_data.get('severity', 'HIGH').upper()
        module = defect_data.get('module', 'General')

        is_critical_module = module in ['Sales', 'Finance', 'Checkout', 'Auth']

        if severity == 'CRITICAL' or is_critical_module:
            business_severity = 'CRITICAL'
            revenue_impact = 'HIGH'
            customer_impact = 'SEVERE'
            compliance_impact = 'HIGH'
            operational_impact = 'HIGH'
            priority = 'P0'
            fix_complexity = 'COMPLEX'
            developer_effort_hours = 8
            testing_effort_hours = 4
        else:
            business_severity = 'MEDIUM'
            revenue_impact = 'LOW'
            customer_impact = 'MODERATE'
            compliance_impact = 'LOW'
            operational_impact = 'LOW'
            priority = 'P2'
            fix_complexity = 'MODERATE'
            developer_effort_hours = 3
            testing_effort_hours = 2

        return {
            'business_severity': business_severity,
            'revenue_impact': revenue_impact,
            'customer_impact': customer_impact,
            'compliance_impact': compliance_impact,
            'operational_impact': operational_impact,
            'priority': priority,
            'estimated_fix_complexity': fix_complexity,
            'developer_effort_hours': developer_effort_hours,
            'testing_effort_hours': testing_effort_hours
        }
