import os
import http.client
import requests
from datetime import datetime, timedelta
from flask_restplus import Namespace, Resource, fields, inputs
from sqlalchemy import and_

from generatepins_backend.models import PinGenModel
from generatepins_backend.constants import VALIDATE_EMAIL_DOMAINS
from generatepins_backend.db import db
from generatepins_backend.pin_generator import gen_digits
from generatepins_backend.utils import phone_number_, validate_phone_number

api_namespace = Namespace(name="Pin Generation V1.1",
                          description='Generate Otp and Pins',
                          path="/api/v1.1/")

SEND_PIN_MSG_URL = os.environ.get(
    "SEND_PIN_MSG_URL",
    "http://host.docker.internal:7002/api/me/messageworker/")

# Input and output formats for Generatepins

checkpin_parser = api_namespace.parser()
checkpin_parser.add_argument('phone_number',
                             type=phone_number_,
                             required=False,
                             help='User phone number')
checkpin_parser.add_argument('email',
                             type=inputs.email(check=VALIDATE_EMAIL_DOMAINS),
                             required=False,
                             help='User email')
checkpin_parser.add_argument('pin',
                             type=str,
                             required=True,
                             help='The Pin sent to user')
checkpin_parser.add_argument('type',
                             type=int,
                             required=True,
                             help='0 -> ForgetPassword, 1 -> Normal Gen Pin')

genpin_parser = api_namespace.parser()

genpin_parser.add_argument('phone_number',
                           type=phone_number_,
                           required=False,
                           help='User phone number')
genpin_parser.add_argument('email',
                           type=inputs.email(check=VALIDATE_EMAIL_DOMAINS),
                           required=False,
                           help='user email')

model = {
    'id': fields.Integer(),
    'phone_number': fields.String(),
    'email': fields.String(),
    'expiry_time': fields.DateTime(),
    'type': fields.Integer(),
    'pin': fields.String()
}
genpin_model = api_namespace.model('Generate Pin', model)


@api_namespace.route('/gen-pin/')
class GenPin(Resource):
    @api_namespace.doc('Pin Generator')
    @api_namespace.expect(genpin_parser)
    def post(self):
        '''
        Creates A Pin that gives users the ability to create new_password
        '''
        args = genpin_parser.parse_args()

        # Generate Four digits pin
        expiry_time = datetime.utcnow() + timedelta(minutes=10)

        phone_number = args["phone_number"]
        email: str = args["email"]

        if phone_number:
            check_phone_number = validate_phone_number(args["phone_number"])
            if not check_phone_number["valid"]:
                return check_phone_number["data"]

            phone_number = check_phone_number["data"]

            user = PinGenModel.query.filter(
                PinGenModel.phone_number == phone_number).first()

        elif email:
            email = email.lower()

            user = PinGenModel.query.filter(PinGenModel.email == email).first()

        else:
            response = {
                "status": "error",
                "msg": "No email or phone_number provided"
            }
            return response, http.client.OK

        pin = gen_digits()

        if user:
            if user.count >= 5:
                if datetime.now() - user.expiry_time <= timedelta(days=7):
                    return {
                        "status":
                        "error",
                        "msg":
                        "You have been barred from genrating an otp for 7 days"
                    }, http.client.OK
                else:
                    user.count = 0

            user.count += 1
            user.pin = pin
            user.expiry_time = expiry_time
            user.verified = False
            db.session.add(user)
            db.session.commit()

        else:

            user = PinGenModel(phone_number=phone_number,
                               email=email,
                               pin=pin,
                               type=1,
                               expiry_time=expiry_time)

            db.session.add(user)
            db.session.commit()
        """phone_num = args['phone_number']

        email = args['email']

        data = None

        msg = f""Here is your pin {pin}. Please note it expires in 10 minutes.""
        if email and phone_num:
            data_msg = {
                '_type': 0,
                'email': email,
                'phoneNumber': phone_num,
                'msg': msg,
                'subject': "Your OTP",
                'typeMessage': 'Pin Generation'
            }
        elif phone_num:
            data_msg = {
                '_type': 1,
                'phoneNumber': phone_num,
                'msg': msg,
                'typeMessage': 'Pin Generation'
            }
        elif email:
            data_msg = {
                '_type': 2,
                'email': email,
                'msg': msg,
                'subject': "Your OTP",
                'typeMessage': 'Pin Generation'
            }

        if not data_msg:
            return {
                "msg": "No contact information was provided"
            }, http.client.BAD_REQUEST

        email_str = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")

        auth_service = os.environ.get("AUTH_SERVICE")
        data = {"email": email_str, "password": password}

        res = requests.post(url=auth_service, params=data)
        data = res.json()
        if data.status_code == 200:

            try:
                auth_token = data["Authorized"]

                header = {"Authorization": auth_token}

                res = requests.post(url=SEND_PIN_MSG_URL,
                                    data=data_msg,
                                    headers=header)
                print(res.status_code)
                print(res.json())

            except KeyError:
                print("Could not send email")

        else:
            pass"""

        result = api_namespace.marshal(user, genpin_model)

        response = {"status": "ok", "result": result}

        return response, http.client.CREATED


@api_namespace.route('/forget-pw-pin/')
class Forgetpwpin(Resource):
    @api_namespace.doc('Forget Password Pin')
    @api_namespace.expect(genpin_parser)
    def post(self):
        '''
        Creates A Pin that gives users the ability to recover forgotten password
        '''
        args = genpin_parser.parse_args()

        # Generate Four digits pin
        expiry_time = datetime.utcnow() + timedelta(minutes=10)

        phone_number = args["phone_number"]
        email: str = args["email"]

        if phone_number:
            check_phone_number = validate_phone_number(args["phone_number"])
            if not check_phone_number["valid"]:
                return check_phone_number["data"]

            phone_number = check_phone_number["data"]

            user = PinGenModel.query.filter(
                PinGenModel.phone_number == phone_number).first()

        elif email:
            email = email.lower()

            user = PinGenModel.query.filter(PinGenModel.email == email).first()

        else:
            response = {
                "status": "error",
                "msg": "No email or phone_number provided"
            }
            return response, http.client.OK

        pin = gen_digits()

        if user:
            if user.count >= 5:
                if datetime.now() - user.expiry_time <= timedelta(days=7):
                    return {
                        "msg":
                        "You have been barred from genrating an otp for 7 days"
                    }, http.client.FORBIDDEN
                else:
                    user.count = 0

            user.count += 1
            user.pin = pin
            user.expiry_time = expiry_time
            user.verified = False
            db.session.add(user)
            db.session.commit()

        else:

            user = PinGenModel(phone_number=phone_number,
                               email=email,
                               pin=pin,
                               type=1,
                               expiry_time=expiry_time)

            db.session.add(user)
            db.session.commit()
        """phone_num = args['phone_number']

        email = args['email']

        data = None

        msg = f""Here is your pin {pin}. Please note it expires in 10 minutes.""
        if email and phone_num:
            data_msg = {
                '_type': 0,
                'email': email,
                'phoneNumber': phone_num,
                'msg': msg,
                'subject': "Your OTP",
                'typeMessage': 'Pin Generation'
            }
        elif phone_num:
            data_msg = {
                '_type': 1,
                'phoneNumber': phone_num,
                'msg': msg,
                'typeMessage': 'Pin Generation'
            }
        elif email:
            data_msg = {
                '_type': 2,
                'email': email,
                'msg': msg,
                'subject': "Your OTP",
                'typeMessage': 'Pin Generation'
            }

        if not data_msg:
            return {
                "msg": "No contact information was provided"
            }, http.client.BAD_REQUEST

        email_str = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")

        auth_service = os.environ.get("AUTH_SERVICE")
        login = {"email": email_str, "password": password}

        res = requests.post(url=auth_service, params=login)
        login = res.json()

        auth_token = login["Authorized"]

        header = {"Authorization": auth_token}

        res = requests.post(url=SEND_PIN_MSG_URL,
                            data=data_msg,
                            headers=header)
        print(res.status_code)
        print(res.json())"""

        result = api_namespace.marshal(user, genpin_model)

        response = {"status": "ok", "result": result}

        return response, http.client.CREATED


@api_namespace.route('/check-pin/')
class CheckPin(Resource):
    @api_namespace.doc('Authenticates User provided Pin')
    @api_namespace.expect(checkpin_parser)
    def post(self):
        '''
        Authenticates the Pin
        '''
        args = checkpin_parser.parse_args()

        # Search for the user
        phone_number = args["phone_number"]
        email: str = args["email"]

        if phone_number:
            check_phone_number = validate_phone_number(args["phone_number"])
            if not check_phone_number["valid"]:
                return check_phone_number["data"]

            phone_number = check_phone_number["data"]

            user = PinGenModel.query.filter(
                PinGenModel.phone_number == phone_number).first()

        elif email:
            email = email.lower()

            user = PinGenModel.query.filter(PinGenModel.email == email).first()

        else:
            response = {
                "status": "error",
                "msg": "No email or phone_number provided"
            }
            return response, http.client.OK

        if not user:
            return {
                "status": "error",
                "msg": "Pin was not generated for this user"
            }, http.client.OK

        if user.verified:
            return {
                "status": "error",
                "msg": "Pin has been verified"
            }, http.client.OK

        if user.pin != args['pin']:
            return {"status": "error", "msg": "Pin invalid"}, http.client.OK

        if user.expiry_time < datetime.utcnow():
            return {
                "status": "error",
                "msg": "Pin has expired"
            }, http.client.OK

        user.verified = True
        db.session.add(user)
        db.session.commit()
        """if args["type"] != 0:
            return {"result": True}, http.client.OK

        email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")

        auth_service = os.environ.get("AUTH_SERVICE")
        data = {"email": email, "password": password}

        res = requests.post(url=auth_service, params=data)
        data = res.json()

        auth_token = data["Authorized"]"""

        result = {"status": "ok", "result": True}

        return result, http.client.OK


verify_parser = checkpin_parser.copy()
verify_parser.remove_argument("type")


@api_namespace.route('/verify-pin')
class CheckPin(Resource):
    @api_namespace.doc('Authenticates User provided Pin')
    @api_namespace.expect(verify_parser)
    def post(self):
        """Check if User has verfied his pin
        """

        args = verify_parser.parse_args()

        # Search for the user
        phone_number = args["phone_number"]
        email: str = args["email"]
        pin: str = args["pin"]

        if phone_number:
            check_phone_number = validate_phone_number(args["phone_number"])
            if not check_phone_number["valid"]:
                return check_phone_number["data"]

            phone_number = check_phone_number["data"]

            user = PinGenModel.query.filter(
                and_(PinGenModel.phone_number == phone_number,
                     PinGenModel.pin == pin)).first()

        elif email:
            email = email.lower()

            user = PinGenModel.query.filter(
                and_(PinGenModel.email == email,
                     PinGenModel.pin == pin)).first()

        else:
            response = {
                "status": "error",
                "msg": "No email or phone_number provided"
            }
            return response, http.client.OK

        if not user:
            return {
                "status": "error",
                "msg": "Pin was not generated for this user"
            }, http.client.OK

        if not user.verified:
            return {
                "status": "error",
                "msg": "Pin has not been verifed"
            }, http.client.OK

        return {"status": "ok", "data": True}, http.client.OK
