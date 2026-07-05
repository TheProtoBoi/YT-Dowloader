# YT-Downloader

I made a quick and simple version of `yt-dlp` so you don't have to type out or remember complex terminal commands every time you want to download something.

---

##  How to Use (Windows 10 / 11)

You don't need to install anything. The `.zip` file comes bundled with everything you need.

1. **Download and Extract:** Download the project `.zip` file and extract it completely.
2. **Launch:** Open the extracted folder, navigate into the `Windows` folder, and run the executable.
3. **Download:** Paste your YouTube video or playlist URL.
4. **Name Your Tracks:** Name the folder or playlist. The app automatically updates the metadata tags so your files look great and work perfectly on MP3 players!
   * **Track Names:** You can manually change individual track names or leave it blank to automatically use the YouTube video title.
   * **Artist Name:** Change the artist manually, or leave it blank to automatically use the name of the YouTube channel that uploaded it.
5. **Choose Your Format:** Select whether you want standard video or audio.
6. **AMV Support for Portable Players:** If you want a video to work on a cheap or legacy MP3 player, select the **AMV** file type. *Note: This process takes a bit longer because it converts the video container and downsamples the framerate to a smooth 16 fps.*

Once the download is complete, your files will be neatly organized inside your system's default **Videos** or **Music** folders based on the format you picked!

---

##  Running on Linux

To use the Linux build, you must have `ffmpeg` installed on your system to handle file merging and conversions. 

Open your terminal and run the appropriate command for your distribution:

* **Ubuntu / Debian / Mint / Pop!_OS:**
  ```bash
  sudo apt update && sudo apt install ffmpeg
