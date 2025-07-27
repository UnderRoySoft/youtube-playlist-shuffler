# Test script for shuffle and create functionality

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_test import authenticate_youtube
from playlist_manager import PlaylistManager

youtube = authenticate_youtube()
pm = PlaylistManager(youtube)

# Test 1: Get a playlist to work with
print("Getting playlists...")
playlists = pm.get_user_playlists()
if not playlists:
    print("No playlists found! Create on in YouTube first.")
    exit()

# Use the first playlist
test_playlist = playlists[0]
print(f"Using playlist: {test_playlist['title']}")

# Test 2: Get videos from the playlist
print("Getting videos...")
videos = pm.get_playlist_videos(test_playlist['id'])
print(f"Found {len(videos)} videos")

if len(videos) < 2:
    print("Need at least 2 videos to test shuffling!")
    exit()

# Test 3: Test shuffling
print("\nTesting shuffle...")
original_order = [v['title'] for v in videos[:3]] # First 3 titles
shuffled_videos = pm.shuffle_videos(videos)
shuffled_order = [v['title'] for v in shuffled_videos[:3]] # First 3 after shuffle

print ("Original order:", original_order)
print("Shuffled order:", shuffled_order)
print("Shuffle works!" if original_order != shuffled_order else "Order unchanged (might be coincidence)")

# Test 4: Create new playlist (optional - creates actual playlist!)
create_test = input("\nCreate test playlist? (y/n):").lower().strip()
if create_test == 'y':
    test_name = "Test Shuffled Playlist"
    print(f"Creating playlist:{test_name}")
    new_playlist_id = pm.create_new_playlist(test_name, "Created by playlist shuffler test")
    if new_playlist_id:
        print(f"Created playlist with ID: {new_playlist_id}")

        # Test adding a few videos
        test_video_ids = [v['video_id'] for v in shuffled_videos[:3]] # First 3 videos
        print(f"Adding {len(test_video_ids)} videos...")

        added = pm.add_videos_to_playlist(new_playlist_id, test_video_ids)
        print(f"Added {added} videos succesfully!")
        print("Check your YouTube account - new playlist should be there!")
    else:
        print("Failed to create playlist")

# How to verify this test:
# 1. Run script and follow prompts
# 2. Shuffle test should show different order
# 3. If you chose to create playlist, check YouTube for new playlist
# 4. New playlist should contain the test videos  