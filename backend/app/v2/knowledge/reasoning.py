"""Knowledge Reasoning and Pattern Matcher for Version 2.0 (In-Memory Only)."""
from typing import Dict, Any, List, Optional


class PatternMatcher:
    def __init__(self):
        self._patterns = [
            {"id": "pat-auth", "keywords": ["login", "auth", "signin", "password"], "module": "Authentication", "suggested_steps": ["NAVIGATE /login", "FILL username", "FILL password", "CLICK Submit"]},
            {"id": "pat-sales", "keywords": ["sales", "order", "so", "customer"], "module": "Sales", "suggested_steps": ["NAVIGATE /sales/orders", "FILL customer_name", "CLICK Create", "ASSERT Toast"]},
            {"id": "pat-purch", "keywords": ["purchase", "po", "vendor", "goods"], "module": "Purchase", "suggested_steps": ["NAVIGATE /purchase/orders", "FILL vendor_name", "CLICK Create", "ASSERT Toast"]},
            {"id": "pat-inv", "keywords": ["stock", "item", "inventory", "sku"], "module": "Inventory", "suggested_steps": ["NAVIGATE /inventory/items", "FILL item_code", "CLICK Stock Entry", "ASSERT Qty"]},
            {"id": "pat-fin", "keywords": ["invoice", "payment", "ledger", "receipt"], "module": "Finance", "suggested_steps": ["NAVIGATE /finance/invoices", "FILL amount", "CLICK Post Invoice", "ASSERT Receipt"]},
        ]

    def match_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        query_lower = query.lower()
        for p in self._patterns:
            if any(kw in query_lower for kw in p["keywords"]):
                return p
        return None


class KnowledgeQueryEngine:
    def __init__(self):
        self.pattern_matcher = PatternMatcher()

    def query_knowledge(self, task_description: str) -> Dict[str, Any]:
        pattern = self.pattern_matcher.match_pattern(task_description)
        if pattern:
            return {
                "matched": True,
                "module": pattern["module"],
                "suggested_steps": pattern["suggested_steps"],
                "confidence": 90.0,
            }
        return {
            "matched": False,
            "module": "General",
            "suggested_steps": ["NAVIGATE /", "FILL form", "CLICK submit", "ASSERT success"],
            "confidence": 60.0,
        }


class ExecutionHistoryAnalyzer:
    def analyze_history(self, history_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(history_records)
        if total == 0:
            return {"pass_rate": 100.0, "flakiness_index": 0.0}

        passed = sum(1 for r in history_records if r.get("verdict") == "PASSED")
        return {
            "total_runs": total,
            "passed_runs": passed,
            "pass_rate": round((passed / total) * 100.0, 1),
            "flakiness_index": round((1.0 - (passed / total)) * 10.0, 2),
        }


class SuggestionEngine:
    def __init__(self):
        self.history_analyzer = ExecutionHistoryAnalyzer()

    def generate_suggestions(self, failure_context: Dict[str, Any]) -> List[str]:
        return [
            "Verify element render visibility before clicking.",
            "Use resilient data-testid or text-based locator (e.g. button:has-text('Submit')).",
            "Increase explicit wait timeout for dynamic API response.",
        ]
