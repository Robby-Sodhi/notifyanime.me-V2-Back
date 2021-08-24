import requests
from constants import client_id, client_secret

def parse_response(response):
    if (response.status_code != 200):
        return None
    response = response.json()
    try:
        access_token = response["access_token"]
        refresh_token = response["refresh_token"]
        token_type = response["token_type"]
    except KeyError:
        return None
    if (token_type != "Bearer"):
        return None
    return {"access_token": access_token, "refresh_token": refresh_token , "token_type": token_type}

def get_watch_list(access_token):
    response = requests.get("https://api.myanimelist.net/v2/users/@me/animelist?fields=broadcast,status,synopsis,alternative_titles,id,my_list_status,num_episodes&limit=1000&nsfw=1", headers={"Authorization": f"Bearer {access_token}"})
    if (response.status_code != 200):
        return None
    return response.json()



def refresh_access_token(session_key, refresh_token, db):
    response = requests.post("https://myanimelist.net/v1/oauth2/token",  data={"client_id": client_id, "client_secret": client_secret, "grant_type": "refresh_token", "refresh_token": refresh_token})
    response = parse_response(response)
    if (not response):
        return
    db.write_mal_auth_details(session_key, response["access_token"], response["refresh_token"])



def authenticate_user(session_key, auth_token, code_challenge, db):
    response = requests.post("https://myanimelist.net/v1/oauth2/token",  data={"client_id": client_id, "client_secret": client_secret, "grant_type": "authorization_code", "code_verifier": code_challenge, "code": auth_token})
    response = parse_response(response)
    if (not response):
        return False

    db.write_mal_auth_details(session_key, response["access_token"], response["refresh_token"])
    return True
def update_episode(access_token, show_id, num_ep):
    response = requests.put(f'https://api.myanimelist.net/v2/anime/{show_id}/my_list_status', data={"num_watched_episodes": num_ep}, headers={"Authorization": f"Bearer {access_token}"})
    if (response.status_code != 200):
        return False
    return True
