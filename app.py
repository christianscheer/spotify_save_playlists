import spotipy
import spotipy.util as util
import json
from spotipy.oauth2 import SpotifyClientCredentials
import string
import os
import sys


def get_spotify_token(user_name, client_id, client_secret, redirect_uri):
    scope = "user-library-read playlist-read-private playlist-read-collaborative"
    token = util.prompt_for_user_token(
        user_name, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    return token


def format_item(item):
    track = item["track"]
    spotify_id = track["id"]
    artists = [ai["name"] for ai in track["artists"]]
    name = track["name"]
    return {"spotify_id": spotify_id,
            "artists": artists, "name": name}


def get_saved_tracks(spotify):
    result = []
    chunk_size = 50
    offset = 0
    results = spotify.current_user_saved_tracks(
        limit=chunk_size, offset=offset)
    while results["items"]:
        result.extend([format_item(item) for item in results["items"]])
        number_of_items = len(results["items"])
        offset += number_of_items
        results = spotify.current_user_saved_tracks(
            limit=chunk_size, offset=offset)
    return result


def get_playlist_tracks(spotify, owner_id, playlist_id):
    result = []
    pl = None
    tracks = None

    try:
        pl = spotify.user_playlist(owner_id, playlist_id)
        tracks = pl["tracks"]
        result.extend([format_item(ti) for ti in tracks["items"]])
    except:
        pass

    while tracks and tracks["next"]:
        try:
            tracks = spotify.next(tracks)
            result.extend([format_item(ti) for ti in tracks["items"]])
        except:
            pass

    return result


def get_playlists(spotify):
    chunk_size = 50
    offset = 0
    pls = spotify.current_user_playlists(limit=chunk_size, offset=offset)
    while pls["items"]:
        for pl in pls["items"]:
            playlist_id = pl["id"]
            name = pl["name"]
            owner_id = pl["owner"]["id"]
            tracks = get_playlist_tracks(spotify, owner_id, playlist_id)
            if tracks:
                playlist = {"playlist_id": playlist_id,
                            "name": name,
                            "tracks": tracks}
                yield playlist
        number_of_items = len(pls["items"])
        offset += number_of_items
        pls = spotify.current_user_playlists(
            limit=chunk_size, offset=offset)


def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = "".join(c for c in s if c in valid_chars)
    return filename


def write_to_json(file_name, object):
    with open(file_name, "wt", encoding="utf-8") as outfile:
        json.dump(object, outfile)


if __name__ == "__main__":

    input_valid = len(sys.argv) == 6

    if not input_valid:
        print("invalid arguments!")
        print(
            "expected arguments: [client_id] [client_secret] [redirect_uri] [user_name] [target_folder]")
    else:
        client_id = sys.argv[1]
        client_secret = sys.argv[2]
        redirect_uri = sys.argv[3]
        user_name = sys.argv[4]
        target_folder = sys.argv[5]

        print("using '%s' as client_id." % client_id)
        print("using '%s' as client_secret." % client_secret)
        print("using '%s' as redirect_uri." % redirect_uri)
        print("using '%s' as user_name." % user_name)
        print("using '%s' as target_folder." % target_folder)

        token = get_spotify_token(user_name, client_id,
                                  client_secret, redirect_uri)

        sp = spotipy.Spotify(auth=token)
        sp.trace = False

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        print("getting saved tracks")
        saved_tracks = get_saved_tracks(sp)
        saved_tracks_filename = os.path.join(
            target_folder, "saved_tracks.json")
        write_to_json(saved_tracks_filename, saved_tracks)
        print("wrote saved tracks to %s" % saved_tracks_filename)

        print("getting playlists")
        for pl in get_playlists(sp):
            playlist_filename = os.path.join(
                target_folder, "%s.json") % format_filename(pl["name"])
            write_to_json(playlist_filename, pl)
            print("written playlist to %s" % playlist_filename)
