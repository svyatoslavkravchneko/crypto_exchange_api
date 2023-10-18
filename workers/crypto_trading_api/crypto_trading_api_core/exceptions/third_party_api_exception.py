class ThirdPartyApiException(Exception):
    status_code = None
    response = None

    def __init__(self, message, status_code=None, response=None):
        super(ThirdPartyApiException, self).__init__(message)
        self.status_code = status_code
        self.response = response