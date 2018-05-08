# spotify_save_playlists

This is a python script that I use to save my spotify-playlists into json files.

## Requirements

- spotipy 2.4.4

Spotipy can be installed via pip with the following command:

``` bat
pip install spotipy
```

- a registered spotify app

If you want to use this you need to head to https://beta.developer.spotify.com/dashboard/ and register/create your own spotify app. This is how you obtain/set your own ```client_id```, ```client_secret``` and ```redirect_uri```.

## Usage

``` bat
python app.py [client_id] [client_secret] [redirect_uri] [user_name] [target_folder]
```

```user_name``` is your spotify-user-name.

When you run this for the first time you will be prompted(in the browser) to login with your spotify credentials and give access to your spotify app.