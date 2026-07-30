import json
import os
import subprocess
import tempfile
import hashlib
from typing import Dict, Any
from app.ai.schemas import AIContextJSON

class AIContextBuilder:
    """
    Responsible for parsing tasks, aggregating historical context, and generating a 
    coherent state for AI test generation.
    """
    def __init__(self):
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'autoqa_ai_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, url: str) -> str:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")

    def build_context(self, url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Builds the context by invoking the playwright script or retrieving from cache.
        """
        cache_path = self._get_cache_path(url)
        
        if not force_refresh and os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        script_path = os.path.join(os.getcwd(), '..', 'qa', 'context_builder.mjs')
        if not os.path.exists(script_path):
            # Fallback path if running from project root
            script_path = os.path.join(os.getcwd(), 'qa', 'context_builder.mjs')

        try:
            result = subprocess.run(
                ['node', script_path, url],
                capture_output=True,
                text=True,
                check=True
            )
            
            # The script outputs the JSON on stdout
            context_data = json.loads(result.stdout)
            
            # Validate with schema
            validated_context = AIContextJSON(**context_data)
            
            # Cache the result
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(validated_context.model_dump(), f)
                
            return validated_context.model_dump()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Context builder script failed: {e.stderr}"
            raise RuntimeError(error_msg)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse context JSON: {str(e)}")
