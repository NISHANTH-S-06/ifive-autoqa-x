import logging
from typing import Dict, Any, List

logger = logging.getLogger('autoqa.ai.website_discovery')

STANDARD_MODULE_PATTERNS = {
    'Authentication': ['login', 'signin', 'signup', 'register', 'auth', 'password', 'oauth'],
    'Dashboard': ['dashboard', 'home', 'overview', 'summary', 'analytics', 'kpi'],
    'Sales': ['sales', 'order', 'quotation', 'invoice', 'customer', 'deal', 'opportunity'],
    'Purchase': ['purchase', 'vendor', 'supplier', 'po', 'procurement', 'receipt'],
    'Inventory': ['inventory', 'stock', 'warehouse', 'item', 'product', 'sku', 'asset'],
    'HRMS': ['hrms', 'employee', 'attendance', 'leave', 'payroll', 'hr', 'staff', 'salary'],
    'CRM': ['crm', 'lead', 'contact', 'pipeline', 'ticket', 'client', 'account'],
    'Finance': ['finance', 'accounting', 'ledger', 'tax', 'bank', 'payment', 'expense', 'billing'],
    'Reports': ['report', 'analytics', 'export', 'audit', 'chart', 'log', 'stat'],
    'Masters': ['master', 'category', 'unit', 'type', 'group', 'definition', 'attribute'],
    'Settings': ['setting', 'config', 'user', 'role', 'permission', 'system', 'profile', 'admin']
}

class WebsiteDiscoveryEngine:
    """
    Enterprise AI Website Discovery Engine:
    Parses scanned UI maps, classifies elements into Module Trees,
    and extracts multi-step User Journeys into Flow Graphs.
    """

    def discover(self, scanned_data: Dict[str, Any]) -> Dict[str, Any]:
        title = scanned_data.get('title', 'Target Application')
        url = scanned_data.get('url', '')
        menus = scanned_data.get('menus', [])
        links = scanned_data.get('links', [])
        buttons = scanned_data.get('buttons', [])
        forms = scanned_data.get('forms', [])
        tables = scanned_data.get('tables', [])

        # 1. AI Module Classification & Module Tree Building
        modules_found: Dict[str, List[Dict[str, Any]]] = {}

        all_text_elements = menus + links + buttons
        for elem in all_text_elements:
            txt = (elem.get('text', '') + ' ' + elem.get('href', '')).lower()
            matched = False
            for mod_name, patterns in STANDARD_MODULE_PATTERNS.items():
                if any(p in txt for p in patterns):
                    if mod_name not in modules_found:
                        modules_found[mod_name] = []
                    modules_found[mod_name].append(elem)
                    matched = True
                    break
            if not matched and len(txt.strip()) > 2:
                if 'Custom Modules' not in modules_found:
                    modules_found['Custom Modules'] = []
                modules_found['Custom Modules'].append(elem)

        module_tree = {
            'name': title,
            'root_url': url,
            'modules': [
                {
                    'module_name': mod,
                    'count': len(items),
                    'components': items[:10]
                }
                for mod, items in modules_found.items()
            ]
        }

        # 2. AI Flow Discovery (Flow Graph Generation)
        nodes = [{'id': 'node_root', 'label': f'Entry Point ({title})', 'url': url, 'type': 'PAGE'}]
        edges = []

        # Identify Navigation Flow & User Journeys
        for idx, (mod, items) in enumerate(modules_found.items()):
            mod_node_id = f'node_mod_{idx}'
            nodes.append({
                'id': mod_node_id,
                'label': f'{mod} Module',
                'type': 'MODULE',
                'item_count': len(items)
            })
            edges.append({
                'source': 'node_root',
                'target': mod_node_id,
                'action': 'NAVIGATE',
                'label': f'Access {mod}'
            })

        # Identify Multi-step Forms & Wizards
        if forms:
            form_node_id = 'node_forms_wizard'
            nodes.append({
                'id': form_node_id,
                'label': 'Multi-Step Form / Data Entry Flow',
                'type': 'WIZARD',
                'form_count': len(forms)
            })
            edges.append({
                'source': 'node_root',
                'target': form_node_id,
                'action': 'SUBMIT',
                'label': 'Execute Data Entry Workflow'
            })

        flow_graph = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'nodes': nodes,
            'edges': edges,
            'journeys': [
                {'name': 'Primary Navigation Journey', 'steps': ['Entry Point', 'Module Selection', 'Form Execution', 'Data Verification']},
                {'name': 'Authentication Journey', 'steps': ['Login Screen', 'Credential Submission', 'Role Redirection', 'Dashboard Loading']}
            ]
        }

        return {
            'status': 'discovery_complete',
            'url': url,
            'title': title,
            'module_tree': module_tree,
            'flow_graph': flow_graph
        }
