from typing import Dict, Union, List

def parse_description(description: str) -> Dict[str, Union[str, List[str], bool, float, int]]:
    """
    Parses a multi-line description string into a dictionary.
    
    Args:
        description (str): The multi-line string to parse.
    
    Returns:
        Dict[str, Union[str, List[str], bool, float, int]]: The parsed data.
    """
    data = {}
    current_key = None
    multiline_keys = {'Description', 'Unique Features', 'Reasons To Book', 'Loyalty Program',
                     'Ships In Fleet', 'Accommodation Overview', 'Cabin Types', 'Deck Plans',
                     'Dining Venues', 'Entertainment & Activities', 'Health & Fitness',
                     'Accessibility & Special Needs', 'Itinerary Details', 'Available Fares'}
    
    for line in description.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if ': ' in line:
            key, value = line.split(': ', 1)
            key = key.strip()
            value = value.strip()
            if key in multiline_keys:
                data[key] = value
                current_key = key
            else:
                # Attempt to convert to appropriate type
                if value.lower() == 'true':
                    data[key] = True
                elif value.lower() == 'false':
                    data[key] = False
                else:
                    try:
                        # Attempt to convert to float or int
                        if '.' in value:
                            data[key] = float(value)
                        else:
                            data[key] = int(value)
                    except ValueError:
                        data[key] = value
        else:
            if current_key and isinstance(data.get(current_key), str):
                data[current_key] += ' ' + line.strip()
    
    return data 