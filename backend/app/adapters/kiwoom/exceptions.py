class KiwoomAdapterError(Exception):
    pass


class KiwoomAuthError(KiwoomAdapterError):
    pass


class KiwoomRequestError(KiwoomAdapterError):
    pass


class KiwoomConfigurationError(KiwoomAdapterError):
    pass