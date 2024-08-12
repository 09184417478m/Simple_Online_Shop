from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE, HTTP_404_NOT_FOUND

class ValueError(APIException):
    status_code = HTTP_406_NOT_ACCEPTABLE
    default_detail = "Invalid credentials"
    default_code = "NOT_ACCEPTABLE"


class NotFound(APIException):
    status_code = HTTP_404_NOT_FOUND
    default_detail = "not found"
    default_code = "NOT_FOUND"

