# src/dialogllm/utils/state_manager.py

class StateManager:
    def __init__(self):
        self._state = {}

    def get_state(self, key):
        return self._state.get(key)

    def set_state(self, key, value):
        self._state[key] = value

    def clear_state(self, key):
        if key in self._state:
            del self._state[key]