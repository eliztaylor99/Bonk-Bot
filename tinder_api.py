import requests
import json
OFFLINE = False
headers = {
    
}

def like_person(s_number, id):
    if OFFLINE:
        return

    params = (
        ('locale', 'en'),
    )

    data = {"s_number": s_number}

    response = requests.post('https://api.gotinder.com/like/{0}'.format(id), headers=headers, params=params, data=data)
    if response.status_code != 200:
        print("Error liking status code: {0}".format(response.status_code))
    else:
        print("Liked")

def pass_person(s_number, id):
    if OFFLINE:
        return
    params = (
        ('locale', 'en'),
        ('s_number', '{0}'.format(s_number)),
    )

    response = requests.get('https://api.gotinder.com/pass/{0}'.format(id), headers=headers, params=params)
    if response.status_code != 200:
        print("Error passing status code: {0}".format(response.status_code))
    else:
        print("Passed")

def get_suggestions():
    if OFFLINE:            
        with open('matches.json') as f:
            data = json.load(f)
            return data

    headers = {
        'authority': 'api.gotinder.com',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'x-supported-image-formats': 'jpeg',
        'persistent-device-id': '3e7e0586-aa25-48a8-bdd3-13b8f258f758',
        'tinder-version': '2.88.1',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'user-session-id': '2584babf-ae58-4484-af76-720f91195e67',
        'accept': 'application/json',
        'app-session-time-elapsed': '198914',
        'x-auth-token': '9853fd35-b4c8-4ec8-9924-0d0e312a7251',
        'user-session-time-elapsed': '199026',
        'platform': 'web',
        'app-session-id': '59f5062c-ef0b-477d-bb1b-c864e77954af',
        'app-version': '1028801',
        'origin': 'https://tinder.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://tinder.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('locale', 'en'),
    )

    response = requests.get('https://api.gotinder.com/v2/recs/core', headers=headers, params=params)
    print("Getting new recommendations")
    
    saveToFile = False
    if saveToFile:
        with open('matches.json', 'w') as outfile:
            json.dump(response.json(), outfile)
    return response.json()

def getMatches():

    params = (
        ('locale', 'en'),
        ('count', '60'),
        ('message', '1'),
        ('is_tinder_u', 'false'),
    )

    response = requests.get('https://api.gotinder.com/v2/matches', headers=headers, params=params)    
    if response.status_code != 200:
        print("Error getting matches status code: {0}".format(response.status_code))
    else:
        print("got matches")
    return response.json()



def getMessages(match_id):
    if OFFLINE:            
        with open('matches.json') as f:
            data = json.load(f)
            return data

    params = (
        ('locale', 'en'),
        ('count', '100'),
    )

    response = requests.get('https://api.gotinder.com/v2/matches/{0}/messages'.format(match_id), headers=headers, params=params)    
    if response.status_code != 200:
        print("error getting messages")                
    saveToFile = True
    if saveToFile:
        with open('messages.json', 'w') as outfile:
            json.dump(response.json(), outfile)
    return response.json()

def getProfileFromID(id):
    if OFFLINE:            
        with open('profile.json') as f:
            data = json.load(f)
            return data
    print("downloading profile")


    params = (
        ('locale', 'en'),
    )

    response = requests.get('https://api.gotinder.com/user/{0}'.format(id), headers=headers, params=params)
    if response.status_code != 200:
        print("error getting profile")
    saveToFile = True
    if saveToFile:
        with open('profile.json', 'w') as outfile:
            json.dump(response.json(), outfile)
    return response.json()

def sendMessage(match_id, message):

    params = (
        ('locale', 'en'),
    )

    data = {"message": message, "matchId": match_id}
    
    data = {
        "match": None,
        "matchId": match_id,
        "message": "hi from discord",
        "otherId": "60c435fcb92eb1010041e3dd",
        "sessionId": "dc5c062f-1106-48e0-8d2c-faab3a052fd9",
        "tempMessageId": 0.1764613556218222,
        "userId": "60c2db8cd821c401008981df"
    }
    response = requests.post('https://api.gotinder.com/user/matches/{0}'.format(match_id), headers=headers, params=params, data=data)
    if response.status_code != 200:
        print("error sending message")
    print(response.json())

    #NB. Original query string below. It seems impossible to parse and
    #reproduce query strings 100% accurately so the one below is given
    #in case the reproduced version is not "correct".
    # response = requests.post('https://api.gotinder.com/user/matches/60c2db8cd821c401008981df60c435fcb92eb1010041e3dd?locale=en', headers=headers, data=data)