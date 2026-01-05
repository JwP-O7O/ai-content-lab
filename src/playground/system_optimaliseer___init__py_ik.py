import functools
import threading
import json

_config = None
_config_lock = threading.Lock()

@functools.lru_cache(maxsize=1)
def get_config():
    global _config
    with _config_lock:
        if _config is None:
            try:
                with open("config.json", "r") as f:
                    _config = json.load(f)
            except FileNotFoundError:
                print("Error: Config file not found. Using default.")
                _config = {"default_setting": "default_value"}
            except json.JSONDecodeError as e:
                print(f"Error decoding config file: {e}")
                _config = {"default_setting": "default_value"}
    return _config

if __name__ == '__main__':
    config = get_config()
    print(config)
    config2 = get_config()
    print(config2)