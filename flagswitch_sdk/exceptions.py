class FlagSwitchError(Exception):
    pass


class InvalidApiKeyError(FlagSwitchError):
    pass


class FlagSwitchConnectionError(FlagSwitchError):
    pass
