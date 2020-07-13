'''
Test the Generatepin operations
'''
from unittest.mock import ANY
import http.client
from freezegun import freeze_time
from faker import Faker
fake = Faker()


@freeze_time('2019-05-07 13:47:34')
def test_create_pin(client):
    new_pin = {
        'username': fake.name(),
        'phone_number': fake.text(13),
        'email': 'tonystark2@gmail.com'
    }
    response = client.post('/api/genpin/', data=new_pin)
    result = response.json

    assert http.client.CREATED == response.status_code

    expected = {
        'id': ANY,
        'username': new_pin['username'],
        'expiry_time': '2019-05-07T13:57:34',
        'pin': ANY
    }
    assert result == expected


def test_checkpin(client):
    new_pin = {
        'username': fake.name(),
        'phone_number': fake.text(13),
        'email': 'tonystark2@gmail.com'
    }
    response = client.post('/api/genpin/', data=new_pin)
    result = response.json

    assert http.client.CREATED == response.status_code

    check_pin = {
        'username': new_pin['username'],
        'pin': result['pin']
    }

    response = client.post('/api/checkpin/', data=check_pin)
    result = response.json
    assert http.client.OK == response.status_code

    expected = {'result': True}
    assert result == expected


'''
def test_expiredpin(client):
    new_pin = {
            'username': fake.name(),
            'phone_number': fake.text(13),
        }
    #result = ''

    response = client.post('/api/genpin/', data=new_pin)
    result = response.json

    assert http.client.CREATED == response.status_code

    check_pin ={
        'username': new_pin['username'],
        'pin': result['pin']
    }

    #time.sleep(33)
    response = client.post('/api/checkpin/', data=check_pin)
    result = response.json
    assert http.client.UNAUTHORIZED == response.status_code

    expected = {'result': False}
    assert result == expected
'''


def test_wrong_pin(client):
    new_pin = {
            'username': fake.name(),
            'phone_number': fake.text(13),
            'email': 'tonystark2@mail.com'
        }
    # result = ''

    response = client.post('/api/genpin/', data=new_pin)

    assert http.client.CREATED == response.status_code

    check_pin = {
        'username': new_pin['username'],
        'pin': '00000'
    }

    response = client.post('/api/checkpin/', data=check_pin)
    # result = response.json
    assert http.client.UNAUTHORIZED == response.status_code


def test_marked_used_pin(client):
    new_pin = {
        'username': fake.name(),
        'phone_number': fake.text(13),
        'email': 'tonystark2@mail.com'
    }
    response = client.post('/api/genpin/', data=new_pin)
    result = response.json

    assert http.client.CREATED == response.status_code

    check_pin = {
        'username': new_pin['username'],
        'pin': result['pin']
    }

    response = client.post('/api/checkpin/', data=check_pin)
    result2 = response.json
    assert http.client.OK == response.status_code

    expected = {'result': True}
    assert result2 == expected

    response = client.post('/api/used/', data=check_pin)
    result = response.json
    assert http.client.OK == response.status_code

    expected = {'result': 'Marked as Used'}
    assert result == expected


def test_used_pin(client):
    new_pin = {
        'username': fake.name(),
        'phone_number': fake.text(13),
        'email': 'tonystark2@mail.com'
    }
    response = client.post('/api/genpin/', data=new_pin)
    result = response.json

    assert http.client.CREATED == response.status_code

    check_pin = {
        'username': new_pin['username'],
        'pin': result['pin']
    }

    response = client.post('/api/used/', data=check_pin)
    result2 = response.json
    assert http.client.OK == response.status_code

    expected = {'result': 'Marked as Used'}
    assert result2 == expected

    response = client.post('/api/checkpin/', data=check_pin)
    result = response.json
    assert http.client.UNAUTHORIZED == response.status_code
