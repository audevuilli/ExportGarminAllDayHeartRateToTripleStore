'''
downloadGarminAllDayHeartRate -- Login to Garmin Connect and download a ZIP file that 
                                 contains, among other things, all day heart rate data.

This code is heavily based on https://github.com/La0/garmin-uploader.
In particular: https://github.com/La0/garmin-uploader/blob/master/garmin_uploader/api.py

@author:     Robert Henschel
@copyright:  2019. All rights reserved.
@license:    GNU General Public License, version 2
'''

import requests
import re
import argparse

URL_HOSTNAME = 'https://connect.garmin.com/modern/auth/hostname'
URL_LOGIN = 'https://sso.garmin.com/sso/login'
URL_POST_LOGIN = 'https://connect.garmin.com/modern/'
URL_PROFILE = 'https://connect.garmin.com/modern/proxy/userprofile-service/socialProfile/'
URL_HOST_SSO = 'sso.garmin.com'
URL_HOST_CONNECT = 'connect.garmin.com'
URL_SSO_SIGNIN = 'https://sso.garmin.com/sso/signin'


# Instantiate the parser
parser = argparse.ArgumentParser()

# Required argument
parser.add_argument('UserName', type=str,
                    help='Garmin.com user name.')
parser.add_argument('Password', type=str,
                    help='Garmin.com password.')
parser.add_argument('Day', type=str,
                    help='Which day to download, in format: YYYY-MM-DD.')
args = parser.parse_args()

# Parse arguments
username  = getattr(args, 'UserName')
password  = getattr(args, 'Password')
day       = getattr(args, 'Day')

# Use a valid Browser user agent
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/50.0', 
})

# Request sso hostname
sso_hostname = None
resp = session.get(URL_HOSTNAME)
if not resp.ok:
    raise Exception('Invalid SSO first request status code {}'.format(resp.status_code))  
sso_hostname = resp.json().get('host')

# Load login page to get login ticket
# Full parameters we have to maintain from Firebug
params = {
    'clientId': 'GarminConnect',
    'connectLegalTerms': 'true',
    'consumeServiceTicket': 'false',
    'createAccountShown': 'true',
    'cssUrl': 'https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css', 
    'displayNameShown': 'false',
    'embedWidget': 'false',
    'gauthHost': 'https://sso.garmin.com/sso',
    'generateExtraServiceTicket': 'true',
    'generateNoServiceTicket': 'false',
    'generateTwoExtraServiceTickets': 'false',
    'globalOptInChecked': 'false',
    'globalOptInShown': 'true',
    'id': 'gauth-widget',
    'initialFocus': 'true',
    'locale': 'fr',
    'locationPromptShown': 'true',
    'mobile': 'false',
    'openCreateAccount': 'false',
    'privacyStatementUrl': 'https://www.garmin.com/fr/privacy/connect/', 
    'redirectAfterAccountCreationUrl': 'https://connect.garmin.com/modern/',
    'redirectAfterAccountLoginUrl': 'https://connect.garmin.com/modern/', 
    'rememberMeChecked': 'false',
    'rememberMeShown': 'true',
    'service': 'https://connect.garmin.com/modern/',
    'showPassword': 'true',
    'source': 'https://connect.garmin.com/signin/',
    'webhost': sso_hostname,
}
res = session.get(URL_LOGIN, params=params)
if res.status_code != 200:
    raise Exception('No login form')

# Lookup CSRF token
csrf = re.search(r'<input type="hidden" name="_csrf" value="(\w+)" />', res.content.decode('utf-8')) 
if csrf is None:
    raise Exception('No CSRF token')
csrf_token = csrf.group(1)
#print('Found CSRF token {}'.format(csrf_token))

# Login/Password with login ticket
data = {
  'embed': 'false',
  'username': username,
  'password': password,
  '_csrf': csrf_token,
}
headers = {
  'Host': URL_HOST_SSO,
  'Referer': URL_SSO_SIGNIN,
}
res = session.post(URL_LOGIN, params=params, data=data, headers=headers)
if not res.ok:
    raise Exception('Authentification failed.')

# Check we have sso guid in cookies
if 'GARMIN-SSO-GUID' not in session.cookies:
    raise Exception('Missing Garmin auth cookie')

# Try to find the full post login url in response
regex = 'var response_url(\s+)= (\"|\').*?ticket=(?P<ticket>[\w\-]+)(\"|\')' 
params = {}
matches = re.search(regex, res.text)
if not matches:
    raise Exception('Missing service ticket')
params['ticket'] = matches.group('ticket')
#print('Found service ticket {}'.format(params['ticket']))

# Second auth step
# Needs a service ticket from previous response
headers = {
    'Host': URL_HOST_CONNECT,
}
res = session.get(URL_POST_LOGIN, params=params, headers=headers)
if res.status_code != 200 and not res.history:
    raise Exception('Second auth step failed.')

# Check login
res = session.get(URL_PROFILE)
if not res.ok:
    raise Exception("Login check failed.")
garmin_user = res.json()
print('Logged in as {}'.format(garmin_user['fullName']))

# Download daily summary zip file and save to file
res = session.get("https://connect.garmin.com/modern/proxy/download-service/files/wellness/"+str(day))
if not res.ok:
    raise Exception("Retrieving 'daily summary ZIP file' failed.")
f = open(str(day)+".zip", "wb")
f.write(res.content)
f.close()
#print("Done!")


