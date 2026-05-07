class FlagSwitchError(Exception):
    pass


class InvalidApiKeyError(FlagSwitchError):
    pass


class EnvironmentNotFoundError(FlagSwitchError):
    pass


class FlagSwitchConnectionError(FlagSwitchError):
    pass
