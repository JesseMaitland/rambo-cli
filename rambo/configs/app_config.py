class AppConfig:

    def __init__(self, **kwargs):
        self._config = kwargs

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value
