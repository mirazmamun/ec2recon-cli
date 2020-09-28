from typing import Optional, Dict
def print_dict(dct: Dict[str, str], indent: int = 28):
    """Return pretty print of dictionary

    Args:
        dct (dict): dictionary
        indent (int, optional): Left indent. Defaults to 50.
    """
    strings = list([])
    for k, v in dct.items():
        strings.append(f"{' ' * indent}{k} : {v}")
    return "\n".join(strings)

def print_dict_list(lst: list, indent: int = 50):
    """Return pretty print of dictionary

    Args:
        dct (dict): dictionary
        indent (int, optional): Left indent. Defaults to 50.
    """
    strings = list([])
    for v in lst:
        strings.append(print_dict({ v.get('Key'): v.get('Value') }))
    return "\n".join(strings)