# Gdansk_Airport

### 📹: Scrape Video
This repository contains a Python script that allows you to capture live video and corresponding image frames from the Gdansk Airport live feed available at [Gdansk Airport Webcams](https://www.airport.gdansk.pl/lotnisko/kamery-internetowe-p30.html).
Before running the script, make sure you have `ffmpeg` installed and available in your system's PATH.
```bash
sudo apt install ffmpeg
```

The `capture_video.py` script is designed to perform the following:
- Capture live video from the Gdansk Airport live feed (multiple live feeds).
- Extract image frames at specified intervals from the video stream.
- Save the video and image frames to a directory structured as `data/[current_date]/(PPS3 or WestPier)`, where `[current_date]` is the date when the script is run, in GMT+1 time.
- Generate a CSV file named `frame_info.csv` with timestamps (in GMT+1) and Frame_ID for each captured frame.
- If the script is executed multiple times on the same date, the new videos/images will be added and the new frame data will be appended to the existing `frame_info.csv` file without overwriting the previous data.

This ensures that all captures within the same day are consolidated in one place, making it easy to reference and manage the captured data.

To capture the video and corresponding image frames, run the `capture_video.py` script with the desired frame interval and record duration.

Example command:
```bash
python3 capture_video.py --frame_interval 10 --record_duration 60
```
For more information and available options, you can use the help command:
```bash
python3 capture_video.py --help
```
---

### ⛈️: Fetch Weather Info
`live_weather.py` calls API managed by [Open-Meteo](https://open-meteo.com/en/docs#latitude=54.3781&longitude=18.4682&current=temperature_2m,relative_humidity_2m,rain,snowfall,cloud_cover&hourly=&timezone=Europe%2FBerlin) to get relevant weather information in real-time.

---

### 🕙: Generate Time Series Data
`generate_time_series.py` produces time-series-data from live-stream video in the following format:
| Date(YYYYMMDD) | Hour | Minute | Seconds | Time Normalized | Track ID | Obj Class | Centroid_x | Centroid_y | Temp (C) 2m | Humidity (%) 2m | Rain (mm) | Showers (mm) | Cloud Cover (%) |
|----------------|------|--------|---------|-----------------|----------|-----------|------------|------------|-------------|-----------------|-----------|--------------|-----------------|

