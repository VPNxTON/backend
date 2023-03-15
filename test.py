from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def test_auth():
    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    assert response.json()['token'] != ''

def test_server_connect():
    address = 'test'

    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    token = response.json()['token']

    response = client.get(f"/api/servers/{address}/connect", headers={'Authorization': token})
    print(response.content)
    assert  'text/*' in response.headers.get('content-type')


def test_add_request():
    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    token = response.json()["token"]

    response = client.post("/api/servers/request",
     json={ "email": "str", "raw_config": "str"},
     headers={'Authorization':token})
    assert response.json() == { "email": "str", "raw_config": "str"}

def test_session_list():
    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    token = response.json()["token"]
    response = client.get("/api/session/list", headers={'Authorization': token})

    assert len(response.json()) >= 0


def test_session_start():
    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    vpn_token = response.json()['vpn_token']
    response = client.post("/api/session/start", json={"vpn_token": vpn_token})
    print(response.json())
    assert response.json()['status'] == 'connected'


def test_session_end():
    wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
    response = client.post("/api/auth/", json={"wallet": wallet})
    vpn_token = response.json()['vpn_token']
    response = client.post("/api/session/end", json={"vpn_token": vpn_token})
    print(response.json())
    assert response.json()['status'] == 'closed'


# def test_session_list():
#     wallet = 'EQD3kE1K40qprNb-3Ndfwm2D3u2UimvlFeUb7-srs_VwB62X'
#     response = client.post("/api/auth/", json={"wallet": wallet})
#     token = response.json()["token"]
#     response = client.get("/api/user/{wallet}/subscriptions", headers={'Authorization': token})
#     assert len(response.json()) >= 0