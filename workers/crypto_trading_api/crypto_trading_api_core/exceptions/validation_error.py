from rest_framework.exceptions import APIException
from rest_framework import status


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    choices = None

    def __init__(self, detail=None, code=None, choices=None):
        APIException.__init__(self, detail, code)
        self.choices = choices

        details = {'detail': self.detail,
                   'choices': choices}
        self.detail = details

