import os

class ConfigReader:
    _properties = {}

    @classmethod
    def _load_properties(cls):
        if cls._properties:
            return

        # Possible candidate paths for config.properties
        candidate_paths = [
            os.path.join(os.getcwd(), "config.properties"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.properties"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Automation_Testing_POM", "src", "main", "resources", "config.properties"),
            os.path.join(os.getcwd(), "Automation_Testing_POM", "src", "main", "resources", "config.properties"),
            os.path.join(os.getcwd(), "src", "main", "resources", "config.properties"),
        ]

        config_path = None
        for path in candidate_paths:
            if os.path.exists(path):
                config_path = path
                break

        if config_path:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        cls._properties[key.strip()] = value.strip()

    @classmethod
    def get_property(cls, key: str, default: str = "") -> str:
        cls._load_properties()
        return cls._properties.get(key, default)

    # Alias for exact Java compatibility
    getProperty = get_property
