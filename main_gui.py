import sys
import os
from api_test import authenticate_youtube
from playlist_manager import PlaylistManager
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class YouTubeShufflerGUI:
    """
    Main GUI class for the YouTube Playlist Shuffler application
    """
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Shuffler - by UnderRoySoft")
        self.root.geometry("600x500")   # Set window size

        # Initialize variables to store application state
        self.youtube_service = None     # Will hold authenticated YouTube API service
        self.playlist_manager = None    # Will hold PlaylistManager instance
        self.user_playlists = []        # Will store user's playlists

        self.create_widgets()           # Build the GUI

    def create_widgets(self):
        """
        Create and arrange all GUI components
        """
        # Main container frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # === AUTHENTICATION SECTION ===
        # Group authentication controls in a labeled frame
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="5")
        auth_frame.grid(row=0, column=0, columnspan=2,sticky=(tk.W, tk.E), pady=(0, 10))

        # Button to start authentication process
        self.auth_button = ttk.Button(auth_frame, text="Connect to YouTube",
                                    command=self.authenticate)
        self.auth_button.grid(row=0, column=0, padx=(0, 10))

        # Label to show connection  status
        self.status_label = ttk.Label(auth_frame, text="Not connected")
        self.status_label.grid(row=0, column=1)

        # === PLAYLIST SELECTION SECTION ===
        playlist_frame = ttk.LabelFrame(main_frame, text="Select Playlist", padding="5")
        playlist_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Dropdown to select playlist
        self.playlist_var = tk.StringVar() # Variable to store selected playlist
        self.playlist_combo = ttk.Combobox(playlist_frame, textvariable=self.playlist_var,
                                           state="readonly", width="50")
        self.playlist_combo.grid(row=0, column=0, padx=(0, 10))

        # Button to load user's playlists
        self.load_playlists_button = ttk.Button(playlist_frame, text="Load Playlists",
                                                command=self.load_playlists, state="disabled")
        self.load_playlists_button.grid(row=0, column=1)

        # === NEW PLAYLIST SETTINGS SECTION ===
        new_playlist_frame = ttk.LabelFrame(main_frame, text="New Playlist Settings", padding=5)
        new_playlist_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Label and text entry for new playlist name
        ttk.Label(new_playlist_frame, text="New Playlist Name:").grid(row=0, column=0, sticky=tk.W)
        self.new_playlist_entry = ttk.Entry(new_playlist_frame, width=40)
        self.new_playlist_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E,), pady=(5, 0))

        # === ACTION SECTION ===
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        # Main action button
        self.shuffle_button = ttk.Button(action_frame, text="Shuffle & Create Playlist",
                                         command=self.shuffle_and_create, state="disabled")
        self.shuffle_button.grid(row=0, column=0)
        
        # === PROGRESS AND LOG SECTION ===
        # Progress bar for showing ongoing operations
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Text area for logging messages
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.log_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # === CONFIGURE GRID WEIGHTS FOR RESIZING ===
        # Make window resizable properly
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)    # Log area should expand

    def log_message(self, message):
        """
        Add a message to the log area with timestamp
        Args: message - text to display
        """
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)       # Scroll to bottom
        self.root.update_idletasks()    # Update GUI immediately

    # === PLACEHOLDER METHODS (TO BE IMPLEMENTED) ===
    def authenticate(self):
        """Authenticate with YouTube API"""
        def auth_thread():
            try:
                self.progress.start()
                self.log_message("Connecting to YouTube...")

                self.youtube_service = authenticate_youtube()
                self.playlist_manager = PlaylistManager(self.youtube_service)

                self.progress.stop()
                self.status_label.config(text="Connected")
                self.load_playlists_button.config(state="normal")
                self.log_message("Succesfully connected to YouTube!")

            except Exception as e:
                self.progress.stop()
                self.status_label.config(text="Connection failed")
                self.log_message(f"Authentication failed:{str(e)}")
                messagebox.showerror("Error", f"Authentication failed: {str(e)}")

        # Run in separate thread to prevent GUI freezing
        threading.Thread(target=auth_thread, daemon=True).start()

    def load_playlists(self):
        """Load user playlists"""
        def load_thread():
            try:
                self.progress.start()
                self.log_message("Loading playlists...")

                self.user_playlists = self.playlist_manager.get_user_playlists()

                # Update combo box
                playlist_names = [f"{p['title']} ({p['video_count']} videos)"
                                  for p in self.user_playlists]
                
                self.playlist_combo['values'] = playlist_names

                if playlist_names:
                    self.playlist_combo.current(0)
                    self.shuffle_button.config(state="normal")
                    self.log_message(f"Loaded {len(playlist_names)} playlists")
                else:
                    self.log_message("No playlists found")

                self.progress.stop()

            except Exception as e:
                self.progress.stop()
                self.log_message(f"Error loading playlists: {str(e)}")
                messagebox.showerror("Error", f"Failed to load playlists: {str(e)}")

        threading.Thread(target=load_thread, daemon=True).start()

    def shuffle_and_create(self):
        """Main shuffle and create functionality"""
        if not self.playlist_var.get():
            messagebox.showwarning("Warning", "Please select a playlist")
            return
        
        new_name = self.new_playlist_entry.get().strip()
        if not new_name:
            messagebox.showwarning("Warning", "Please enter a name for the new playlist")
            return

        def shuffle_thread():
            try:
                self.progress.start()

                # Get selected playlist
                selected_index = self.playlist_combo.current()
                selected_playlist = self.user_playlists[selected_index]

                self.log_message(f"Getting videos from '{selected_playlist['title']}'...")
                videos = self.playlist_manager.get_playlist_videos(selected_playlist['id'])

                if not videos:
                    self.log_message("No videos found in playlist")
                    return
                
                self.log_message(f"Found {len(videos)} videos. Shuffling...")
                shuffled_videos = self.playlist_manager.shuffle_videos(videos)

                self.log_message("Creating new playlist...")
                new_playlist_id = self.playlist_manager.create_new_playlist(
                    new_name,
                    f"Shuffled version of {selected_playlist['title']}"
                )

                if not new_playlist_id:
                    self.log_message("Failed to create playlist")
                    return
                
                self.log_message("Adding videos to new playlist...")
                video_ids = [v['video_id'] for v in shuffled_videos]
                added_count = self.playlist_manager.add_videos_to_playlist(new_playlist_id, video_ids)

                self.progress.stop()
                self.log_message(f"Success! Added {added_count}/{len(videos)} videos to new playlist")
                messagebox.showinfo("Success", f"Created playlist '{new_name}' with {added_count} videos!")

            except Exception as e:
                self.progress.stop()
                self.log_message(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Operation failed: {str(e)}")

        threading.Thread(target=shuffle_thread, daemon=True).start()

# Run the application when script is executed direclty 
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeShufflerGUI(root)
    root.mainloop()

    # How to verify this works:
    # 1. Run the script - GUI window should appear
    # 2. Window should have all sections: Authentication, Playlist Selection, etc.
    # 3. Buttons should be clickable and show placeholder messages in log
    # 4. Try resizing window - log area should expand/contract
    # 5. All buttons except "Connect to YouTube" should be disabled initially


