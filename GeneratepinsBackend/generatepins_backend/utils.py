import re
import http.client

from .constants import PREFIX_LIST


def phone_number_(value: str, name: str):
    if type(value) != str:
        raise ValueError(
            ": The parameter '{}' is not a string. You gave us the value: {}".
            format(name, value))

    if re.search(r'[a-zA-Z]+$', value):
        raise ValueError(
            ": The parameter '{}' is not a valid phone-number. You gave us the value: {}"
            .format(name, value))
    else:
        return value


phone_number_.__schema__ = {'type': 'string', 'format': 'phone-number'}


def validate_phone_number(phone_number):
    first_three = phone_number[:3]

    if first_three not in PREFIX_LIST and first_three != "+23":
        response = {"status": "error", "msg": "Pass in a valid phone-number"}
        return {"valid": False, "data": (response, http.client.OK)}

    if not (len(phone_number) == 11 or len(phone_number) == 14):

        response = {
            "status": "error",
            "msg": "The lenth of number passed is invalid"
        }
        return {"valid": False, "data": (response, http.client.OK)}

    if first_three == "+23":
        phone_number = "0" + phone_number[4:]
        temp_three = phone_number[:3]
        if temp_three not in PREFIX_LIST:
            response = {
                "status": "error",
                "msg": "Pass in a valid Phone Number"
            }
            return {"valid": False, "data": (response, http.client.OK)}

    return {"valid": True, "data": phone_number}
