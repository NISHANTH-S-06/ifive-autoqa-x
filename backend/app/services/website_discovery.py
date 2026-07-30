import json
import logging
import subprocess
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

logger = logging.getLogger('autoqa.website_discovery')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
QA_ROOT = PROJECT_ROOT / 'qa'
DISCOVERY_SCRIPT = QA_ROOT / 'discovery.mjs'

class DiscoveryElement(BaseModel):
    id: str = ""
    tag: str
    text: str = ""
    href: str = ""
    src: str = ""
    type: str = ""
    name: str = ""
    placeholder: str = ""
    testId: str = ""
    role: str = ""
    ariaLabel: str = ""
    className: str = ""
    visible: bool = True

class NavigationMap(BaseModel):
    title: str = ""
    url: str = ""
    stats: Dict[str, Any] = {}
    menus: List[DiscoveryElement] = []
    buttons: List[DiscoveryElement] = []
    forms: List[DiscoveryElement] = []
    tables: List[DiscoveryElement] = []
    cards: List[DiscoveryElement] = []
    dialogs: List[DiscoveryElement] = []
    tabs: List[DiscoveryElement] = []
    dropdowns: List[DiscoveryElement] = []
    inputs: List[DiscoveryElement] = []
    links: List[DiscoveryElement] = []
    images: List[DiscoveryElement] = []
    tree: Dict[str, Any] = {}
    elements: List[DiscoveryElement] = []
    error: Optional[str] = None

def scan_website(url: str) -> NavigationMap:
    """
    Launch a headless Playwright instance via Node.js to scan the target URL
    and return a structured NavigationMap of available interactive elements.
    """
    if not DISCOVERY_SCRIPT.is_file():
        logger.error("Discovery script not found at %s", DISCOVERY_SCRIPT)
        return NavigationMap(error="Discovery engine is not available locally.")

    try:
        command = ['node', str(DISCOVERY_SCRIPT), url]
        result = subprocess.run(
            command,
            cwd=QA_ROOT,
            capture_output=True,
            text=True,
            timeout=35
        )

        if result.returncode != 0 or not result.stdout.strip():
            logger.error("Discovery failed: %s", result.stderr)
            try:
                err_data = json.loads(result.stderr)
                return NavigationMap(error=err_data.get('error', 'Unknown discovery error'))
            except Exception:
                return NavigationMap(error="Failed to scan website. Playwright execution error.")

        json_line = next((line for line in reversed(result.stdout.splitlines()) if line.startswith('{')), None)
        
        if not json_line:
            return NavigationMap(error="Invalid discovery output format")

        data = json.loads(json_line)
        if 'error' in data:
            return NavigationMap(error=data['error'])

        # Aggregate elements list for backward compatibility
        all_elements = []
        for category in ['menus', 'buttons', 'forms', 'tables', 'cards', 'dialogs', 'tabs', 'dropdowns', 'inputs', 'links']:
            if category in data and isinstance(data[category], list):
                all_elements.extend([DiscoveryElement(**item) for item in data[category]])

        data['elements'] = all_elements
        return NavigationMap(**data)

    except subprocess.TimeoutExpired:
        logger.error("Discovery script timed out for %s", url)
        return NavigationMap(error="Website scan timed out. The site might be unreachable.")
    except Exception as e:
        logger.exception("Unexpected error in scan_website")
        return NavigationMap(error=str(e))
