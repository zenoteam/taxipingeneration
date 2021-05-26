import logging
from datetime import datetime, timedelta

import jwt
from parse import parse
from generatepins_backend.constants import SECRETS

logger = logging.getLogger(__name__)


def encode_token(payload, secret):
    return jwt.encode(payload, secret, algorithm='HS256')


def decode_token(token, secret):
    return jwt.decode(token, secret, algoritms='HS256')


def generate_token_header(payload1, secret):
    """
    Generate a token header base on the username. Sign using the private key.
    """
    payload = {
        'id': payload1['id'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=2),
        'jti': '{0}-{1}'.format(payload1['id'],
                                int(datetime.utcnow().timestamp()))
    }

    # indicate that user is a (super) admin
    if 'admin' in payload1:
        if payload1['admin'] is not None:
            payload['admin'] = payload1['admin']

    token = encode_token(payload, secret)
    token = token.decode('utf8')
    return f'Bearer {token}'


def validate_token_header(header, secret):
    """
    Validate that a token header is correct

    If correct, it returns the payload, if not, it
    returns None
    """
    if not header:
        logger.info('No header')
        return None

    # Retrieve the Bearer token
    parse_result = parse('Bearer {}', header)
    if not parse_result:
        logger.info(f'Wrong format for header "{header}"')
        return None
    token = parse_result[0]
    try:
        decoded_token = decode_token(token.encode('utf8'), secret)
    except jwt.exceptions.DecodeError:
        logger.warning(f'Error decoding header "{header}". '
                       'This may be key mismatch or wrong key')
        return None
    except jwt.exceptions.ExpiredSignatureError:
        logger.error(f'Authentication header has expired')
        return None

    # Check expiry is in the token
    if 'exp' not in decoded_token:
        logger.warning('Token does not have expiry (exp)')
        return None

    # Check username is in the token
    if 'id' not in decoded_token:
        logger.warning('Token does not have user id')
        return None

    logger.info('Header successfully validated')
    return decoded_token
