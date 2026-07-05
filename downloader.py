import os
import sys
import glob
import yt_dlp
import threading
import subprocess
from datetime import datetime
import traceback
import customtkinter as ctk
from mutagen.easyid3 import EasyID3

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Custom Media Downloader Engine")
        self.geometry("560x900") 
        self.resizable(False, False)

        self.search_results_map = {}
        self.result_buttons = []

        # Main Title
        self.title_label = ctk.CTkLabel(self, text="⚙️ Advanced Media Engine & Search", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=12)

        # YOUTUBE SEARCH PANEL
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", padx=40, pady=(0, 15))

        self.search_label = ctk.CTkLabel(self.search_frame, text="🔍 Search YouTube:", font=ctk.CTkFont(weight="bold"))
        self.search_label.pack(anchor="w", padx=15, pady=(5, 2))

        # Search Mode Selection Toggle
        self.search_mode_toggle = ctk.CTkSegmentedButton(self.search_frame, values=["Videos", "Playlists", "By Channel"])
        self.search_mode_toggle.pack(fill="x", padx=15, pady=(0, 8))
        self.search_mode_toggle.set("Videos")

        self.search_row = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_row.pack(fill="x", padx=15, pady=(0, 5))

        # Placeholder text dynamically shifts hints based on selection
        self.search_input = ctk.CTkEntry(self.search_row, width=320, placeholder_text="Type text or @channelname...")
        self.search_input.pack(side="left", padx=(0, 10))
        
        self.search_btn = ctk.CTkButton(self.search_row, text="Search", width=110, command=self.start_search_thread)
        self.search_btn.pack(side="right")

        self.results_label = ctk.CTkLabel(self.search_frame, text="Click a Search Result to Load URL:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray")
        self.results_label.pack(anchor="w", padx=15, pady=(5, 0))

        # Scrollable Results Panel 
        self.results_scroll_frame = ctk.CTkScrollableFrame(self.search_frame, width=430, height=140)
        self.results_scroll_frame.pack(pady=(2, 12), padx=15, fill="x")
        
        self.no_results_label = ctk.CTkLabel(self.results_scroll_frame, text="(No search results loaded yet)", text_color="gray")
        self.no_results_label.pack(pady=20)

        # 1. URL Input Field
        self.url_label = ctk.CTkLabel(self, text="Target YouTube Video or Playlist URL:", font=ctk.CTkFont(weight="bold"))
        self.url_label.pack(anchor="w", padx=40)
        self.url_input = ctk.CTkEntry(self, width=480, placeholder_text="https://www.youtube.com/...")
        self.url_input.pack(pady=(2, 10))

        # 2. File Renaming / Directory Field
        self.playlist_label = ctk.CTkLabel(self, text="Custom Folder Name / Album Name:", font=ctk.CTkFont(weight="bold"))
        self.playlist_label.pack(anchor="w", padx=40)
        self.playlist_input = ctk.CTkEntry(self, width=480, placeholder_text="e.g., Favorites, Chill Beats")
        self.playlist_input.pack(pady=(2, 10))

        # --- METADATA OVERRIDE FIELDS ---
        self.meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.meta_frame.pack(fill="x", padx=40, pady=5)

        self.title_override_label = ctk.CTkLabel(self.meta_frame, text="Custom File & Track Title (Optional):", font=ctk.CTkFont(weight="bold"))
        self.title_override_label.grid(row=0, column=0, sticky="w", pady=2)
        self.title_override_input = ctk.CTkEntry(self.meta_frame, width=230, placeholder_text="Leave blank for original title")
        self.title_override_input.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(0, 10))

        self.artist_override_label = ctk.CTkLabel(self.meta_frame, text="Custom Track Artist (Optional):", font=ctk.CTkFont(weight="bold"))
        self.artist_override_label.grid(row=0, column=1, sticky="w", pady=2)
        self.artist_override_input = ctk.CTkEntry(self.meta_frame, width=230, placeholder_text="e.g., Custom Artist")
        self.artist_override_input.grid(row=1, column=1, sticky="w", pady=(0, 10))

        # --- FORMAT SELECTIONS ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(fill="x", padx=40, pady=5)

        self.format_label = ctk.CTkLabel(self.settings_frame, text="Download Format:", font=ctk.CTkFont(weight="bold"))
        self.format_label.grid(row=0, column=0, sticky="w", pady=2)
        
        self.format_menu = ctk.CTkComboBox(self.settings_frame, values=["MP3 (Audio)", "FLAC (Lossless)", "WAV (Audio)", "M4A (Audio)", "MP4 (Video)", "MP4 (320x240 Legacy Video)", "AMV (Cheap MP3 Player Video)"], width=230, command=self.toggle_quality_menu)
        self.format_menu.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(0, 10))
        self.format_menu.set("MP3 (Audio)")

        self.quality_label = ctk.CTkLabel(self.settings_frame, text="Video Quality (If MP4):", font=ctk.CTkFont(weight="bold"))
        self.quality_label.grid(row=0, column=1, sticky="w", pady=2)
        self.quality_menu = ctk.CTkComboBox(self.settings_frame, values=["Best Available", "1080p", "720p", "480p"], width=230)
        self.quality_menu.grid(row=1, column=1, sticky="w", pady=(0, 10))
        self.quality_menu.set("Best Available")

        self.thumbnail_switch = ctk.CTkSwitch(self, text="Embed Original Artwork / Thumbnail Image")
        self.thumbnail_switch.pack(anchor="w", padx=40, pady=5)
        self.thumbnail_switch.select() 

        self.download_btn = ctk.CTkButton(self, text="Execute Processing Engine", command=self.start_download_thread, font=ctk.CTkFont(size=15, weight="bold"), height=40)
        self.download_btn.pack(pady=15, fill="x", padx=40)

        self.status_label = ctk.CTkLabel(self, text="System Standby", text_color="gray", font=ctk.CTkFont(weight="bold"), wraplength=480)
        self.status_label.pack(pady=5)

    def toggle_quality_menu(self, choice):
        if choice == "MP4 (Video)":
            self.quality_menu.configure(state="normal")
        else:
            self.quality_menu.configure(state="disabled")

    def start_search_thread(self):
        query = self.search_input.get().strip()
        if not query:
            self.status_label.configure(text="⚠️ Please type a query or channel identifier!", text_color="orange")
            return
        self.search_btn.configure(state="disabled", text="Searching...")
        self.status_label.configure(text="🔍 Querying YouTube servers...", text_color="#3b8ed0")
        
        mode = self.search_mode_toggle.get()
        threading.Thread(target=self.run_youtube_search, args=(query, mode)).start()

    def run_youtube_search(self, query, mode):
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'extract_flat': True, 
            'skip_download': True,
            'extractor_args': {'youtube': {'player_client': ['web_safari', 'android']}}
        }

        # FIX: Handle "By Channel" mode differently by constructing a clean playlist tab link
        if mode == "By Channel":
            # Strip spaces to convert names like "Lofi Girl" into a handle if it lacks an @ symbol
            clean_channel = query if query.startswith("@") else f"@{query.replace(' ', '')}"
            search_target = f"https://www.youtube.com/{clean_channel}/playlists"
            self.status_label.configure(text=f"🔍 Reading channel: {clean_channel}...", text_color="#3b8ed0")
        elif mode == "Playlists":
            ydl_opts['extractor_args']['youtube']['search_type'] = 'playlist'
            search_target = f"ytsearch10:{query}"
        else:
            search_target = f"ytsearch10:{query}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_data = ydl.extract_info(search_target, download=False)
                if 'entries' in search_data and search_data['entries']:
                    self.populate_search_ui(search_data, mode)
                else:
                    raise Exception("No results found on this target link.")
        except Exception as e:
            for btn in self.result_buttons:
                btn.destroy()
            self.result_buttons.clear()
            self.no_results_label.configure(text="No entries found")
            self.no_results_label.pack(pady=20)
            self.status_label.configure(text=f"❌ Problem: {str(e).splitlines()[0][:60]}", text_color="red")
            print(traceback.format_exc())
        finally:
            self.search_btn.configure(state="normal", text="Search")
            
    def populate_search_ui(self, search_data, mode):
        self.no_results_label.pack_forget()
        for btn in self.result_buttons:
            btn.destroy()
        self.result_buttons.clear()

        new_map = {}
        first_string = None

        for index, entry in enumerate(search_data['entries'], start=1):
            if entry:
                title = entry.get('title', 'Unknown Title')
                creator = entry.get('uploader', entry.get('channel', entry.get('playlist_uploader', 'Unknown Creator')))
                
                if mode in ["Playlists", "By Channel"]:
                    url = f"https://www.youtube.com/playlist?list={entry.get('id')}"
                    meta_str = f" [Playlist • by {creator}]"
                else:
                    url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                    duration = entry.get('duration', None)
                    time_str = f" {int(duration)//60}:{int(duration)%60:02d}" if duration else "0:00"
                    meta_str = f" [{time_str} • by {creator}]"

                menu_display_string = f"{index}. {title}{meta_str}"
                
                new_map[menu_display_string] = url
                if not first_string:
                    first_string = menu_display_string

                row_btn = ctk.CTkButton(
                    self.results_scroll_frame, 
                    text=menu_display_string, 
                    anchor="w", 
                    fg_color="transparent", 
                    text_color="white",
                    hover_color="#2b2b2b",
                    height=28,
                    command=lambda s=menu_display_string: self.select_search_result(s)
                )
                row_btn.pack(fill="x", pady=2, padx=5)
                self.result_buttons.append(row_btn)

        self.search_results_map = new_map
        if first_string:
            self.select_search_result(first_string)
        self.status_label.configure(text="✅ Search results loaded successfully!", text_color="green")

    def select_search_result(self, selected_string):
        target_url = self.search_results_map.get(selected_string)
        if target_url:
            self.url_input.delete(0, 'end')
            self.url_input.insert(0, target_url)
            
            for btn in self.result_buttons:
                if btn.cget("text") == selected_string:
                    btn.configure(fg_color="#1f538d") 
                else:
                    btn.configure(fg_color="transparent")

            self.status_label.configure(text="🔗 Selected URL loaded into download field!", text_color="green")

    def start_download_thread(self):
        threading.Thread(target=self.run_downloader).start()

    def run_downloader(self):
        url = self.url_input.get().strip()
        folder_name = self.playlist_input.get().strip()
        chosen_format = self.format_menu.get()
        chosen_quality = self.quality_menu.get()
        title_override = self.title_override_input.get().strip()
        artist_override = self.artist_override_input.get().strip()

        if not url or not folder_name:
            self.status_label.configure(text="❌ Error: Target URL and Folder fields required!", text_color="red")
            return

        self.download_btn.configure(state="disabled")
        self.status_label.configure(text="📥 Step 1: Downloading source target...", text_color="#3b8ed0")

        is_video = "Video" in chosen_format or "AMV" in chosen_format
        save_folder = "Videos" if is_video else "Music"
        output_dir = os.path.join(os.environ['USERPROFILE'], save_folder, folder_name)
        os.makedirs(output_dir, exist_ok=True)

        if getattr(sys, 'frozen', False):
            self.base_folder = os.path.dirname(sys.argv[0])
        else:
            self.base_folder = os.path.dirname(os.path.abspath(__file__))
        self.base_folder = os.path.abspath(self.base_folder)

        if title_override:
            name_template = f"{title_override} - %(playlist_index)s.%(ext)s"
        else:
            name_template = "%(title)s.%(ext)s"

        ydl_opts = {
            'outtmpl': os.path.join(output_dir, name_template),
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': self.base_folder, 
            'extractor_args': {'youtube': {'player_client': ['web_safari', 'android']}}
        }

        if chosen_format in ["AMV (Cheap MP3 Player Video)", "MP4 (320x240 Legacy Video)"]:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['outtmpl'] = os.path.join(output_dir, "raw_source_temp_%(playlist_index)s.%(ext)s")
        elif chosen_format == "MP4 (Video)":
            ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best'
            if chosen_quality == "1080p":
                ydl_opts['format'] = 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/best'
            elif chosen_quality == "720p":
                ydl_opts['format'] = 'bv*[height<=720][ext=mp4]+ba[ext=m4a]/best'
            elif chosen_quality == "480p":
                ydl_opts['format'] = 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/best'
            ydl_opts['merge_output_format'] = 'mp4'
            if self.thumbnail_switch.get() == 1:
                ydl_opts['postprocessors'] = [{'key': 'FFmpegMetadata'}]
        else:
            codec_map = {"MP3 (Audio)": "mp3", "FLAC (Lossless)": "flac", "WAV (Audio)": "wav", "M4A (Audio)": "m4a"}
            target_codec = codec_map.get(chosen_format, "mp3")
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': target_codec,
                'preferredquality': '320' if target_codec == 'mp3' else '0',
            }]
            if self.thumbnail_switch.get() == 1:
                ydl_opts['writethumbnail'] = True
                ydl_opts['postprocessors'].append({'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'})
                ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info:
                    downloaded_paths = [ydl.prepare_filename(e) for e in info['entries'] if e]
                else:
                    downloaded_paths = [ydl.prepare_filename(info)]

            ffmpeg_path = os.path.join(self.base_folder, "ffmpeg.exe")

            if chosen_format == "MP4 (320x240 Legacy Video)":
                self.status_label.configure(text="📟 Step 2: Downscaling video to 320x240 H.264...", text_color="orange")
                search_pattern = os.path.join(output_dir, "raw_source_temp_*.*")
                found_files = glob.glob(search_pattern)

                if found_files:
                    for idx, temp_file_path in enumerate(found_files, start=1):
                        sanitized_title = f"{title_override}_{idx}" if title_override else f"Converted_Video_{idx}"
                        sanitized_title = "".join([c for c in sanitized_title if c.isalpha() or c.isdigit() or c in " .-_()"])
                        final_mp4_output = os.path.join(output_dir, f"{sanitized_title}.mp4")

                        cmd = [
                            ffmpeg_path, "-y", "-i", temp_file_path,
                            "-vf", "scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2",
                            "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-ac", "2", "-ar", "44100", "-b:a", "128k",
                            final_mp4_output
                        ]
                        
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        subprocess.run(cmd, startupinfo=startupinfo, check=True)
                        os.remove(temp_file_path)
                else:
                    raise FileNotFoundError("Could not locate raw download files.")

            elif chosen_format == "AMV (Cheap MP3 Player Video)":
                self.status_label.configure(text="📟 Step 2: Custom scaling & hardware remuxing...", text_color="orange")
                search_pattern = os.path.join(output_dir, "raw_source_temp_*.*")
                found_files = glob.glob(search_pattern)

                if found_files:
                    for idx, temp_file_path in enumerate(found_files, start=1):
                        sanitized_title = f"{title_override}_{idx}" if title_override else f"Converted_Video_{idx}"
                        sanitized_title = "".join([c for c in sanitized_title if c.isalpha() or c.isdigit() or c in " .-_()"])
                        
                        avi_temp_output = os.path.join(output_dir, f"{sanitized_title}.avi")
                        final_amv_output = os.path.join(output_dir, f"{sanitized_title}.amv")

                        cmd = [
                            ffmpeg_path, "-y", "-i", temp_file_path,
                            "-c:v", "msmpeg4v3", "-b:v", "256k",
                            "-s", "160x120", "-r", "16",
                            "-c:a", "libmp3lame", "-ac", "1", "-ar", "22050", "-b:a", "64k",
                            avi_temp_output
                        ]
                        
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        subprocess.run(cmd, startupinfo=startupinfo, check=True)
                        
                        if os.path.exists(avi_temp_output):
                            if os.path.exists(final_amv_output):
                                os.remove(final_amv_output)
                            os.rename(avi_temp_output, final_amv_output)
                        os.remove(temp_file_path)
                else:
                    raise FileNotFoundError("Could not locate raw download files.")

            elif chosen_format == "MP3 (Audio)":
                self.status_label.configure(text="🏷️ Injecting custom track metadata tags...", text_color="orange")
                for file_path in downloaded_paths:
                    base, _ = os.path.splitext(file_path)
                    final_audio_path = base + ".mp3"
                    if os.path.exists(final_audio_path):
                        try:
                            audio = EasyID3(final_audio_path)
                            audio['album'] = folder_name
                            if title_override: audio['title'] = title_override
                            if artist_override: audio['artist'] = artist_override
                            audio.save()
                        except Exception:
                            pass

            self.status_label.configure(text=f"✅ Success! Check {save_folder}\\{folder_name}", text_color="green")
            self.url_input.delete(0, 'end')
            
        except Exception as err:
            err_msg = str(err).split('\n')[0]
            self.status_label.configure(text=f"❌ Error: {err_msg[:80]}...", text_color="red")
            print(traceback.format_exc())
        finally:
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()