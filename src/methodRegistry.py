
import types
from typing import Callable, Dict

class MethodRegistry:
    jump_table: Dict[str, Callable] = {}

    @classmethod
    def register(cls, command: str) -> Callable:

        def decorator(func: Callable) -> Callable:
            cls.jump_table[command] = func
            return func

        return decorator

    @classmethod
    def get_bound_jump_table(cls, self) -> Dict[str, Callable]:
        return {
            command: types.MethodType(func, self)
            for command, func
            in cls.jump_table.items()
        }

