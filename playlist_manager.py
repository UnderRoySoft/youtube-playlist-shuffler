import random
from googleapiclient.errors import HttpError
import time

class PlaylistManager:
    """
    Manages YouTube playlist operations: fetching, shuffling, creating
    """
    def __init__(self, youtube_service):
        # Store the authenticated YouTube API service
        self.youtube = youtube_service

    def get_user_playlists(self):
        """
        Fetch all playlists owned by the authenticated user
        Returns: List of dictionaries with playlist info
        """
        try:
            # API call to get user's playlists
            request = self.youtube.playlists().list(
                part="snippet,contentDetails",  # What data to include
                mine=True,                      # Only user's playlists
                maxResults=50                   # Maximum playlists to fetch
            )
            response = request.execute()

            # Process the response into a cleaner format
            playlists = []
            for item in response['items']:
                playlists.append({
                    'id': item['id'],                                      # Playlist ID for API calls
                    'title': item['snippet']['title'],                     # Display name
                    'video_count': item['contentDetails']['itemCount']     # Number of videos
                })
            return playlists
        
        except HttpError as e:
            # Handle API errores gracefully
            print(f"Error fetching playlists: {e}")
            return[]
        
    def get_playlist_videos(self, playlist_id):
        """
        Get all videos from a specific playlist
        Args: playlist_id - YouTube playlist ID
        Returns: List of video dictionaries
        """
        videos = []
        next_page_token = None  # For pagination (playlists can have 100+ videos)

        try:
            # Keep fetching until we get all videos
            while True:
                request = self.youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,               # Max per request
                    pageToken=next_page_token   # For next page of results
                )
                response = request.execute()

                # Extract video information from each item
                for item in response['items']:
                    videos.append({
                        'video_id': item['snippet']['resourceId']['videoId'],   # Unique video ID
                        'title': item['snippet']['title']                       # Video title
                    })

                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break   # No more pages, exit loop

        except HttpError as e:
            print(f"Error fetching videos: {e}")

        return videos
    
    # How to verify this works:
    # The test script below will show if these methods work correctly

    def shuffle_videos(self, videos):
        """
        Randomize the order of videos in a playlist
        Args: videos - list of video dictionaries
        Returns: new list with videos in random order
        """
        shuffled = videos.copy() # Create copy to avoid modifying original
        random.shuffle(shuffled) # Randomize order in-place
        return shuffled
    
        # How to verify: Check that returned list has same videos but different order

    def create_new_playlist(self, title, description=""):
        """
        Create a new empty playlist on YouTube
        Args: title - name for the playlist, description - optional description
        Returns: playlist ID if successful, None if failed
        """
        try:
            # API call to create new playlist
            request = self.youtube.playlists().insert(
                part="snippet,status", # Include title/description and privacy settings
                body={
                    "snippet":{
                        "title":title,
                        "description":description
                    },
                    "status":{
                        "privacyStatus":"private" # Create as private by default
                    }
                }
            )
            response = request.execute()
            return response['id'] # Return the new playlist's ID
        
        except HttpError as e:
            print(f"Error creating playlist: {e}")
            return None
        
        # How to verify: Check your YouTube account - new playlist should appear

    def add_videos_to_playlist(self, playlist_id, video_ids, max_retries=3):
        """
        Add multiple videos to an existing playlist
        Args: playlist_id - target playlist ID, video_ids - list of video IDs to add
        Returns: tuple (successful_count, failed_videos)
        """
        added_count = 0
        failed_videos = []

        for i, video_id in enumerate(video_ids):
            success = False
        
            # Try adding each video with retries
            for attempt in range(max_retries):
                try:
                    request = self.youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
                    request.execute()
                    added_count += 1
                    success = True
                    print(f"Added video {i+1}/{len(video_ids)}")
                    break  # Success, no need to retry
                
                except HttpError as e:
                    error_code = e.resp.status if hasattr(e, 'resp') else 'unknown'
                    print(f"Attempt {attempt+1}/{max_retries} failed for video {i+1}: {error_code}")
                
                    if attempt < max_retries - 1:  # Not the last attempt
                        time.sleep(1)  # Wait 1 second before retry
                    else:
                        # All retries failed
                        failed_videos.append({
                            'video_id': video_id,
                            'error': str(e),
                            'position': i+1
                        })
                        print(f"Failed to add video {i+1} after {max_retries} attempts")
        
            # Small delay between videos to avoid rate limits
            if success:
                time.sleep(0.1)  # 100ms delay
    
        return added_count, failed_videos
    
        # How to verify: Check the target playlist - should contain the added videos