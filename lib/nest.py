import hashlib, json, os, re, requests, yaml

class Nest:

    def __init__(self, auth_data):
        self.auth_data = auth_data
        self.nest_api_url = 'https://developer-api.nest.com/?auth={0}'

    def get_data(self):
        access_token = self.auth_data['access_token']

        # http GET on Nest API
        nest_response = requests.get(self.nest_api_url.format(access_token))

        # check the response
        try:
            nest_response.raise_for_status()
        except Exception as e:
            print("nest.get_data exception: '{:s}'".format(str(e)))
            return None

        # return JSON-formatted data
        return nest_response.json()



def generate_authorization_file(nest_id, nest_secret, auth_out_file):
    # generate a random state string
    pynest_state = hashlib.md5(os.urandom(32)).hexdigest()

    # build the authorization URL
    authorization_url = 'https://home.nest.com/login/oauth2?client_id={0}&state={1}'

    # prompt the user to authorize
    print("Navigate to the authorization URL:")
    print(authorization_url.format(nest_id, pynest_state))

    # get access PIN code from user
    access_pin_input = raw_input("\n>> Enter Access Token: ")
    access_pin = "".join(access_pin_input.upper().split())

    # validate the token
    regex_match = re.match(r"[A-Z0-9]+$", access_pin)
    if (not regex_match):
        print("Invalid format on token '{:s}'! Expected only characters A-Z, 0-9".format(access_pin))
        return

    print("Got Access PIN: '{:s}', retrieving Access Token...".format(access_pin))

    # build the access token URL
    access_token_url = 'https://api.home.nest.com/oauth2/access_token'
    access_token_data = {
        'code': access_pin,
        'client_id': nest_id,
        'client_secret': nest_secret,
        'grant_type': 'authorization_code'
    }

    token_response = requests.post(access_token_url, data=access_token_data)
    print("Received Access Token URL Response:")
    print token_response.content
    try:
        # raise exception if the token request results in error
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']
    except Exception as e:
        raise e

    # if access token obtained, save the data
    authorization_file_data = {
        'pynest_state': pynest_state,
        #'nest_client_id' : nest_id,
        #'nest_client_secret': nest_secret,
        'access_token': access_token,
    }

    with open(auth_out_file, 'w') as outfile:
        yaml.dump(authorization_file_data, outfile, default_flow_style=False)


