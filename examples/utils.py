from typing import Callable, Dict


def merge_dict(new_dict: Dict) -> Callable[[Dict], Dict]:
    def merger(old_dict: Dict) -> Dict:
        return dict(list(old_dict.items()) + list(new_dict.items()))

    return merger
