# Add parent directory to Python path so we can import from main folder
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test script to verify playlist management functions
from api_test import authenticate_youtube
from playlist_manager import PlaylistManager

# Step 1: Authenticate and create playlist manager
print("Authenticating with YouTube...")
youtube = authenticate_youtube()
pm = PlaylistManager(youtube)

# Step 2: Test getting user playlists
print("\nTesting playlist fetching...")
playlists = pm.get_user_playlists()

# Display first few playlists for verification
for i, playlist in enumerate(playlists[:3]):    # Show first 3
    print(f"    {i+1}. {playlist['title']} ({playlist['video_count']} videos)")

# Step 3: Test getting videos from first playlist (if exists)
if playlists:
    print(f"\nTesting video fetching from '{playlists[0]['title']}'...")
    videos = pm.get_playlist_videos(playlists[0]['id'])
    print(f"Succesfully fetched {len(videos)} videos")

    # Show first few video titles for verification
    for i, video in enumerate(videos[:3]):
        print(f"    {i+1}. {video['title']}")
else:
    print("No playlists found - create some playlists in YouTube first!")

# How to verify this test works:
# 1. Run this script after authentication works
# 2. Should see your actual YouTube playlists listed
# 3. Should see video titles from your first playlist
# 4. If you get empty results, check your YouTube account has playlists