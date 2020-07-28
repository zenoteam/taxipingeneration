import http.client
import requests
from datetime import datetime, timedelta
from flask_restplus import Namespace, Resource, fields
from generatepins_backend.models import GeneratepinModel
from generatepins_backend.db import db
from generatepins_backend.pin_generator import gen_digits

api_namespace = Namespace('api', description='API operations')

SEND_PIN_MSG_URL = "http://165.22.116.11:7058/api/messages/genpin/"
ADD_PIN = "http://165.22.116.11:7062/api/addpin/"
CONFIRM_URL = "http://165.22.116.11:7042/api/confirm/"


# Input and output formats for Generatepins

checkpin_parser = api_namespace.parser()
checkpin_parser.add_argument('username', type=str, required=True,
                             help='username')
checkpin_parser.add_argument('pin', type=str, required=True,
                             help='The Pin sent to user')
checkpin_parser.add_argument('otp', type=bool, required=False,
                             help='indicates if it is am otp gen')

genpin_parser = api_namespace.parser()
genpin_parser.add_argument('username', type=str, required=True,
                           help='username')
genpin_parser.add_argument('admin', type=str, required=True,
                           help='username')
genpin_parser.add_argument('phone_number', type=str, required=True,
                           help='user phone number')
genpin_parser.add_argument('email', type=str, required=False,
                           help='user email')

model = {
    'id': fields.Integer(),
    'admin': fields.String(),
    'username': fields.String(),
    'expiry_time': fields.DateTime(),
    'pin': fields.String()
}
genpin_model = api_namespace.model('Generate Pin', model)


@api_namespace.route('/genpin/')
class GenPin(Resource):

    @api_namespace.doc('Pin Generator')
    @api_namespace.expect(genpin_parser)
    def post(self):
        '''
        Creates A Pin that gives users the ability to create new_passowrd
        '''
        args = genpin_parser.parse_args()

        # Generate Four digits pin
        pin = gen_digits()
        expiry_time = datetime.utcnow() + timedelta(minutes=10)
        username = args['username']
        admin = args['admin']

        user = GeneratepinModel(
            username=username,
            admin=admin,
            pin=pin,
            expiry_time=expiry_time
        )

        phone_num = args['phone_number']

        email = args['email']

        db.session.add(user)
        db.session.commit()
        if email:
            data = {
                'username': username,
                'recieverNo': phone_num,
                'pin': pin,
                'recieverEmail': email
            }
        else:
            data = {
                'username': username,
                'recieverNo': phone_num,
                'pin': pin
            }

        requests.post(url=SEND_PIN_MSG_URL, data=data)
        result = api_namespace.marshal(user, genpin_model)

        return result, http.client.CREATED


@api_namespace.route('/checkpin/')
class CheckPin(Resource):

    @api_namespace.doc('Authenticates User provided Pin')
    @api_namespace.expect(checkpin_parser)
    def post(self):
        '''
        Authenticates the Pin
        '''
        args = checkpin_parser.parse_args()

        # Search for the user
        user = (GeneratepinModel
                .query
                .filter(GeneratepinModel.admin == args['username'])
                .order_by(GeneratepinModel.expiry_time.desc())
                .first())
        if not user:
            return '', http.client.UNAUTHORIZED

        if user.pin != args['pin']:
            return '', http.client.TOO_MANY_REQUESTS

        if user.expiry_time < datetime.utcnow():
            return {'result': False}, http.client.UNAUTHORIZED

        if user.used:
            return '', http.client.UNAUTHORIZED

        if args['otp']:
            data = {
                'usernamemain': user.username
            }
            r = requests.put(url=CONFIRM_URL, data=data)
            if r.status_code != http.client.OK:
                return '', http.client.INTERNAL_SERVER_ERROR

        # Turn Pin to used
        user.used = True

        db.session.add(user)
        db.session.commit()

        result = api_namespace.marshal(user, genpin_model)

        return result, http.client.OK
