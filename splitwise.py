from splitwise import Splitwise
key="mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X"
consumer_secret="y2wdKYyD7KsU5wlQcarVYrg0K9tvbeEnorFqVQzO"

sObj = Splitwise(key,consumer_secret)
url, secret = sObj.getAuthorizeURL()

# params[:oauth_verifier] is CP6OtM9npWa1JWQUfZ7M

secret='7PVEVbWpMA8csLJSQcLRnGcFvygNi1Lt1pC6TUUe'
session ={}
session['access_token'] = 'mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X'
sObj.setAccessToken(session['access_token'])
sObj.getFriends()
url, secret = sObj.getAuthorizeURL()

sObj = sObj = Splitwise(key,consumer_secret, api_key=secret)
current = sObj.getCurrentUser()