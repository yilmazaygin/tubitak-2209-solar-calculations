"""
Utility functions for handling API responses.
Includes truncation for large responses to prevent client-side issues.
"""

from typing import Dict, Any
from .logger import app_logger as logger
from .config_loader import settings

MAX_RECORDS_PER_ARRAY = settings.MAX_RECORDS_PER_ARRAY


def truncate_large_arrays(data: Dict[str, Any], max_records: int = None, keys_to_check: list = None) -> Dict[str, Any]:
    """
    Truncate large arrays in response to prevent client UI freezing.
    Useful for Swagger UI and other web clients that struggle with large JSON responses.
    
    Args:
        data: Response data dictionary
        max_records: Maximum records to keep per array (default: MAX_RECORDS_PER_ARRAY)
        keys_to_check: List of top-level keys to check for arrays (default: ['outputs'])
    
    Returns:
        Truncated data with metadata about truncation
    
    Example:
        >>> data = {'outputs': {'hourly': [1, 2, 3, ...8760 items]}}
        >>> truncated = truncate_large_arrays(data, max_records=1000)
        >>> len(truncated['outputs']['hourly'])
        1000
        >>> '_truncation_warning' in truncated
        True
    """
    if max_records is None:
        max_records = MAX_RECORDS_PER_ARRAY
    
    if keys_to_check is None:
        keys_to_check = ['outputs']
    
    # Work on a copy to avoid modifying original
    result = data.copy()
    truncated = False
    truncation_info = {}
    
    for top_key in keys_to_check:
        if top_key not in result:
            continue
            
        if not isinstance(result[top_key], dict):
            continue
        
        # Make a copy of the nested dict
        result[top_key] = result[top_key].copy()
        
        for key, value in result[top_key].items():
            if isinstance(value, list) and len(value) > max_records:
                original_count = len(value)
                result[top_key][key] = value[:max_records]
                truncated = True
                truncation_info[f"{top_key}.{key}"] = {
                    'original_count': original_count,
                    'returned_count': max_records,
                    'truncated_count': original_count - max_records
                }
                logger.warning(
                    f"Truncated {top_key}.{key} from {original_count} to {max_records} records "
                    f"for client compatibility"
                )
    
    if truncated:
        result['_truncation_warning'] = {
            'message': (
                f'Response truncated to {max_records} records per array for client compatibility. '
                'Use API clients (curl, Python requests, etc.) or download options for full data.'
            ),
            'truncated_arrays': truncation_info
        }
    
    return result


def get_response_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of response structure without the full data.
    Useful for logging and debugging.
    
    Args:
        data: Response data dictionary
    
    Returns:
        Summary dict with keys, types, and sizes
    
    Example:
        >>> data = {'outputs': {'hourly': [1, 2, 3]}, 'inputs': {'lat': 38.447}}
        >>> summary = get_response_summary(data)
        >>> summary
        {'top_level_keys': ['outputs', 'inputs'], 'outputs': {'hourly': {'type': 'list', 'count': 3}}}
    """
    summary = {
        'top_level_keys': list(data.keys())
    }
    
    for key, value in data.items():
        if isinstance(value, dict):
            summary[key] = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    summary[key][sub_key] = {
                        'type': 'list',
                        'count': len(sub_value)
                    }
                elif isinstance(sub_value, dict):
                    summary[key][sub_key] = {
                        'type': 'dict',
                        'keys': list(sub_value.keys())
                    }
                else:
                    summary[key][sub_key] = {
                        'type': type(sub_value).__name__,
                        'value': sub_value if not isinstance(sub_value, (str, bytes)) or len(str(sub_value)) < 100 else f"{str(sub_value)[:100]}..."
                    }
        elif isinstance(value, list):
            summary[key] = {
                'type': 'list',
                'count': len(value)
            }
    
    return summary
