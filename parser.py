import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import xmltodict
import time

import xml.etree.ElementTree as ET
from collections import defaultdict
from tqdm import tqdm

from lxml import etree

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
USERNAME = os.getenv('USERNAME')


def authenticate_spotify():
    token = util.prompt_for_user_token(
        USERNAME,
        scope='playlist-modify-public playlist-modify-private',
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI
    )
    return spotipy.Spotify(auth=token)


def create_playlists(xml_file_path, track_id_name_dict):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    playlists = {}  # Final playlists dictionary

    # Flag to start processing when Playlists section is found
    process_playlists = False
    for elem in root.iter():
        if elem.tag == 'key' and elem.text == 'Playlists':
            process_playlists = True
            print("Playlists section found")  # Debug print
            continue
        
        # Once we're in the Playlists section and find the array tag
        if process_playlists and elem.tag == 'array':
            for plist_dict in elem.findall('dict'):
                playlist_name = None
                playlist_tracks = []
                
                # We use an index to iterate so we can look ahead to the next element
                plist_items = list(plist_dict)
                for i in range(len(plist_items) - 1):  # Adjusted iteration
                    if plist_items[i].tag == 'key' and plist_items[i].text == 'Name':
                        playlist_name = plist_items[i + 1].text  # Name found
                        # print(f"Processing playlist: {playlist_name}")  # Debug print
                    elif plist_items[i].tag == 'key' and plist_items[i].text == 'Playlist Items':
                        track_ids_elem = plist_items[i + 1]
                        for track_id_dict in track_ids_elem.findall('dict'):
                            for track_id_elem in track_id_dict:
                                if track_id_elem.text == 'Track ID':
                                    track_id = track_id_dict.find('integer').text  # Correctly find the integer
                                    track_name = track_id_name_dict.get(track_id)
                                    if track_name:
                                        playlist_tracks.append(track_name)

                if playlist_name and playlist_tracks:  # Add non-empty playlists
                    playlists[playlist_name] = playlist_tracks

            break  # Stop processing after playlists

    print(f"Created {len(playlists)} playlists.")
    
    # Save to JSON file
    filename = "playlists_output.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(playlists_with_artists, f, ensure_ascii=False, indent=4)

    print(f"Playlists saved to {filename}.")

    return playlists


def search_spotify_and_add(playlists_with_artists):
    
    sp_oauth = SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope = 'playlist-modify-public playlist-modify-private'
    )

    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    
    sp = authenticate_spotify()
    not_found_tracks = []  # To keep track of songs not found on Spotify
    
    # Fetch existing playlists to check for duplicates
    existing_playlists = sp.current_user_playlists()
    existing_playlist_names = [playlist['name'] for playlist in existing_playlists['items']]

    for playlist_name, tracks in playlists_with_artists.items():
        
        # Check if the playlist already exists
        if playlist_name in existing_playlist_names:
            print(f"Playlist '{playlist_name}' already exists. Skipping creation.")
            continue  # Skip to the next playlist
            
            
        # Create a new Spotify playlist for each playlist in the dictionary, make it private and add a description
        sp_playlist = sp.user_playlist_create(USERNAME, playlist_name, public=False, description="Sam Fearn copyrighted")

        for track_name, artist_name in tracks:
            try:
                # Search for the track on Spotify
                results = sp.search(q=f"track:{track_name} artist:{artist_name}", type="track", limit=1)

                if results['tracks']['items']:
                    # If found, add the first match to the Spotify playlist
                    spotify_track_id = results['tracks']['items'][0]['id']
                    sp.user_playlist_add_tracks(USERNAME, sp_playlist['id'], [spotify_track_id])
                else:
                    # If not found, note the track and artist name
                    not_found_tracks.append(f"{track_name} by {artist_name}")

                time.sleep(0.5)  # Be respectful to the API's rate limits

            except spotipy.SpotifyException as e:
                if e.http_status == 429:  # Rate limiting
                    print("Rate limit reached. Pausing for a moment...")
                    time.sleep(5)
                else:
                    print(f"An error occurred: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        print(f"Created playlist '{playlist_name}' and attempted to add tracks.")

    # Report tracks not found on Spotify
    if not_found_tracks:
        print("\nThe following tracks were not found on Spotify:")
        for track in not_found_tracks:
            print(track)


################################################################################

def parse_tracks_with_artists(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    track_id_name_artist_dict = {}

    for track_dict in root.findall('.//dict/dict'):
        track_id = None
        track_name = None
        artist_name = None

        elements = list(track_dict)
        for i in range(0, len(elements), 2):
            key = elements[i].text
            value = elements[i+1].text

            if key == 'Track ID':
                track_id = value
            elif key == 'Name':
                track_name = value
            elif key == 'Artist':
                artist_name = value

        if track_id and track_name and artist_name:
            track_id_name_artist_dict[track_id] = (track_name, artist_name)

    print(f"Processed {len(track_id_name_artist_dict)} songs with artist names.")
    return track_id_name_artist_dict


def create_playlists_with_artists(xml_file_path, track_id_name_artist_dict):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    playlists = {}

    process_playlists = False
    for elem in root.iter():
        if elem.tag == 'key' and elem.text == 'Playlists':
            process_playlists = True
            continue
        
        if process_playlists and elem.tag == 'array':
            for plist_dict in elem.findall('dict'):
                playlist_name = None
                playlist_tracks = []
                
                plist_items = list(plist_dict)
                for i in range(len(plist_items) - 1):
                    if plist_items[i].tag == 'key':
                        if plist_items[i].text == 'Name':
                            playlist_name = plist_items[i + 1].text
                        elif plist_items[i].text == 'Playlist Items':
                            track_ids_elem = plist_items[i + 1]
                            for track_id_dict in track_ids_elem.findall('dict'):
                                for track_id_elem in track_id_dict.findall('./integer'):
                                    track_id = track_id_elem.text
                                    track_info = track_id_name_artist_dict.get(track_id)
                                    if track_info:
                                        playlist_tracks.append(track_info)

                if playlist_name and playlist_tracks:
                    playlists[playlist_name] = playlist_tracks

            break

    print(f"Created {len(playlists)} playlists with songs and artists.")

    return playlists

def main():

    track_id_name_artist_dict = parse_tracks_with_artists('Music.xml')

    playlists_with_artists = create_playlists_with_artists('Music.xml', track_id_name_artist_dict)
    
    search_spotify_and_add(playlists_with_artists)
    
if __name__ == "__main__":
    main()
