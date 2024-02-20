# Spotify Playlist Parser 🎵

This project provides a Python script that parses XML files containing music library information (such as those exported from iTunes) and creates corresponding playlists in Spotify, automatically populating them with available tracks found on Spotify.


Many thanks to Sam "Disco Inferno" Fearn for his timeless iTunes library for testing of this tool.
## Features 🌟

- Parses music library XML files.
- Creates Spotify playlists based on the XML file's contents.
- Searches Spotify for each track and adds it to the corresponding playlist.
- Skips creating playlists if they already exist in Spotify.
- Saves a summary of created playlists and tracks not found on Spotify.

## Prerequisites 📋

Before you begin, ensure you have met the following requirements:

- Python 3.6+
- A Spotify account
- A Spotify Developer account with an application set up to obtain `client_id`, `client_secret`, and a `redirect_uri`. (See [the official Spotify documentation here](https://developer.spotify.com/documentation/web-api/concepts/apps) for information on how to do this). 

## Installation 🚀

1. Clone this repository:
```bash
git clone https://github.com/yourusername/spotify-playlist-parser.git
```

2. Navigate to the project directory: 
```bash
cd spotify-playlist-parser
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Setup 🛠

1. Rename .env.example to .env and fill in your Spotify application details:
```plaintext
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=your_redirect_uri
USERNAME=your_spotify_username
```

2. Make sure to add the redirect_uri to your Spotify application's whitelist in the Spotify Developer Dashboard.

## Usage 📚
Run the parser with:
```bash
python parser.py
```

## Project Structure
spotify-playlist-parser/
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── parser.py
│
└── data/
    └── example_music_library.xml

## Contributing 🤝
Contributions, issues, and feature requests are welcome! Feel free to check issues page.

## License 📝
Distributed under the MIT License. See LICENSE for more information.


## Acknowledgements 🙏
* To Sam "Disco Inferno" Fearn for his timeless iTunes library for testing of this tool.
* This project uses the Spotipy library for interacting with the Spotify Web API.


## Instructions for parser.py
1. Environment Variables: For security and convenience, store your Spotify API credentials and username in environment variables. You could use a library like python-dotenv to load these from a .env file.

2. Running the Script: After setting up the environment variables, you can run parser.py to start the process. The script will prompt you for authentication with Spotify on the first run.

## Note on Authentication Variables
Ensure you remove or redact sensitive information like SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, and USERNAME from your script before sharing or pushing to a public repository. Instead, load these from environment variables or a configuration file that is not tracked in your version control system.
