from typing import Dict, Any, List
from app.ai.schemas import ExecutionFailure, HealingResponse

class SelfHealingEngine:
    """
    Detects broken selectors/flows and proposes or automatically applies fixes to tests.
    """
    def __init__(self):
        pass

    def _extract_target_text(self, selector: str) -> str:
        """Extract text from a Playwright text selector (e.g. text="Submit")."""
        if 'text=' in selector or 'has-text' in selector:
            parts = selector.split('"')
            if len(parts) > 1:
                return parts[1].strip()
        return ""

    def heal_test_step(self, failure_data: ExecutionFailure) -> Dict[str, Any]:
        """
        Uses heuristic matching on the current DOM to find a replacement for a broken selector.
        """
        original_selector = failure_data.selector or ""
        current_dom = failure_data.current_dom
        
        healed_selector = None
        strategy_used = "FAILED"
        confidence_score = 0
        success = False
        
        # 1. Attempt to match by exact text if it's a button or link
        target_text = self._extract_target_text(original_selector).lower()
        
        if not target_text and original_selector.startswith('#'):
            # It was an ID selector. Let's see if there's a new ID that is very similar (e.g. -v2)
            # This is simplified for production determinism
            target_id_base = original_selector.replace('#', '')
            
            all_elements = current_dom.get('buttons', []) + current_dom.get('inputs', []) + current_dom.get('links', [])
            for el in all_elements:
                el_id = el.get('id', '')
                if el_id and target_id_base in el_id:
                    healed_selector = f"#{el_id}"
                    strategy_used = "PARTIAL_ID_MATCH"
                    confidence_score = 80
                    success = True
                    break
                    
        elif target_text:
            # We have text to search for
            # Look in buttons and links
            all_clickables = current_dom.get('buttons', []) + current_dom.get('links', [])
            for el in all_clickables:
                el_text = str(el.get('text', '')).lower()
                if target_text == el_text:
                    tag = el.get('tag', 'button')
                    if el.get('id'):
                        healed_selector = f"#{el['id']}"
                    elif el.get('testId'):
                        healed_selector = f"{tag}[data-testid=\"{el['testId']}\"]"
                    else:
                        healed_selector = f"{tag}:has-text(\"{el['text']}\")"
                        
                    strategy_used = "EXACT_TEXT_MATCH"
                    confidence_score = 90
                    success = True
                    break

        if not success:
            strategy_used = "NO_MATCH_FOUND"
            confidence_score = 0
            
        response = HealingResponse(
            original_selector=original_selector,
            healed_selector=healed_selector,
            strategy_used=strategy_used,
            confidence_score=confidence_score,
            success=success
        )
        return response.model_dump()
