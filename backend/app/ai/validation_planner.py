from typing import Dict, Any, List
from app.ai.schemas import ValidationExecutionPlan, ValidationStep

class ValidationPlanner:
    """
    Determines what needs to be asserted and what risks are present based on the context.
    """
    def __init__(self):
        pass

    def plan_validations(
        self, 
        context_data: Dict[str, Any], 
        steps: List[Dict[str, Any]], 
        expected_flow: str = "", 
        acceptance_criteria: str = ""
    ) -> Dict[str, Any]:
        """
        Dynamically analyzes steps against context to plan required validations.
        """
        validation_steps = []
        
        for step in steps:
            action = step.get('action', '').upper()
            step_num = step.get('step_number', 0)
            validations = []

            if action == 'NAVIGATE':
                validations.extend(['URL Validation', 'HTTP 200', 'Screenshot Capture'])
            
            elif action == 'CLICK':
                validations.extend(['Element Visible', 'Element Clickable'])
                # If clicking a link or a button that looks like navigation
                selector = step.get('selector', '').lower()
                if 'a[' in selector or 'href' in selector or selector.startswith('a.') or selector.startswith('a:'):
                    validations.append('URL Changed')
                elif 'submit' in selector or 'save' in selector:
                    validations.append('Form Validation')
                    validations.append('API Response Validation')
                
                # Check context to see if it triggers network
                validations.append('Screenshot Capture')

            elif action == 'FILL':
                validations.extend(['Element Visible', 'Element Enabled', 'Text Validation'])
                
            elif action == 'ASSERT_VISIBLE':
                validations.extend(['Element Visible', 'DOM Validation'])
                
            elif action == 'ASSERT_URL':
                validations.extend(['URL Validation', 'HTTP Status Validation'])
                
            elif action == 'SCREENSHOT':
                validations.extend(['Screenshot Capture'])

            # Global validations applied to critical flows based on criteria
            if 'accessibility' in acceptance_criteria.lower():
                validations.append('Accessibility Validation')
                
            if 'performance' in acceptance_criteria.lower() and action in ['NAVIGATE', 'CLICK']:
                validations.append('Performance Validation')

            # De-duplicate
            validations = list(dict.fromkeys(validations))

            validation_steps.append(ValidationStep(
                step_number=step_num,
                action=action,
                validations=validations
            ))

        plan = ValidationExecutionPlan(
            plan_title="Dynamic Execution Plan",
            steps=validation_steps
        )
        
        return plan.model_dump()
