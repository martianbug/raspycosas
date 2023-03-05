from splitwise import Splitwise
key="mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X"
consumer_secret="y2wdKYyD7KsU5wlQcarVYrg0K9tvbeEnorFqVQzO"
api_key=  'Q9dA1xmaCfXq3AdEhJba564lDlmZXvSY6cNvFAhj'

sObj = Splitwise(key,consumer_secret)
url, secret = sObj.getAuthorizeURL()

# params[:oauth_verifier] is CP6OtM9npWa1JWQUfZ7M

secret='7PVEVbWpMA8csLJSQcLRnGcFvygNi1Lt1pC6TUUe'
oauth_token='mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X'
access_token = sObj.getAccessToken(oauth_token,secret,oauth_verifier)

sObj = Splitwise(key, consumer_secret, api_key=api_key)
# sObj.setAccessToken(acces_token)

#commands
current = sObj.getCurrentUser()
sObj.getFriends()
id = current.id
user = sObj.getUser(id)
sObj.getGroups()