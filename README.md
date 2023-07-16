# ListenBrainz_to_SubSonic
Pulls ListenBrainz generated playlists for a given user and creates the playlist in a subsonic library

This requires the following packages:
thefuzz
hashlib
urllib
json
re

Additionally, credentials are stored in a file in the same directory (.subsonic_creds). An example has been provided.

How it works:
If you scrobble to ListenBrainz from Airsonic, it generates a playlist every week of recomendations. This script gets the latest one and then uses fuzzy matching to find the closest match (if possible) and create a playlist from that. Because it might recommend songs you don't have (or don't have any more), it averages four different fuzz scores on the top Subsonic result and only adds it if it's over a 75% match. In my experimentation, this tends to be pretty good but can occasionally grab alternative versions of songs by the same artist. IE, it would occasionally grab "Artist - Song (John Peel Session)" over "Artist - Song" with no good explanation because the Subsonic search system is not well documented. I may return to this in the future and add a condition to go pull additional Subsonic search results and compare them to find the "best" match, but the intended goal of not pulling a random unintended song by the completely wrong band is working.
