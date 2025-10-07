# Multi-Platform Video Downloader API

A powerful Python API for downloading videos from YouTube, TikTok, Instagram, Facebook, and 1500+ other platforms using FastAPI and yt-dlp.

## Features

- Download videos from 1500+ platforms including YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Vimeo, and more
- Get video information without downloading
- Batch download multiple videos
- Support for different video qualities (360p, 480p, 720p, 1080p)
- Audio-only downloads
- Progress tracking for downloads
- RESTful API with automatic documentation

## API Endpoints

- `GET /` - API information and health check
- `POST /video/info` - Get video information
- `POST /video/download` - Download a single video
- `POST /video/batch` - Download multiple videos
- `GET /downloads/{download_id}` - Check download status
- `GET /files/{download_id}` - Download completed video file
- `GET /downloads` - List all downloads
- `GET /platforms` - Get supported platforms list

## Deployment on Render

This project is configured for easy deployment on Render.com.

### Prerequisites

1. A GitHub account
2. A Render.com account
3. Your code pushed to a GitHub repository

### Deployment Steps

1. **Push to GitHub**: Make sure your code is pushed to a GitHub repository

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

3. **Configure Deployment**:
   - **Name**: `video-downloader-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Choose Free or Starter plan

4. **Environment Variables** (Optional):
   - `PORT`: 5000 (automatically set by Render)
   - `PYTHON_VERSION`: 3.11

5. **Deploy**: Click "Create Web Service" and wait for deployment

### Alternative: Using render.yaml

If you prefer using the `render.yaml` configuration file:

1. Push your code with `render.yaml` to GitHub
2. In Render dashboard, select "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect and use the `render.yaml` configuration

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Access the API**:
   - API: http://localhost:5000
   - Interactive docs: http://localhost:5000/docs
   - ReDoc: http://localhost:5000/redoc

## Usage Examples

### Get Video Information
```bash
curl -X POST "https://your-app.onrender.com/video/info" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Download Video
```bash
curl -X POST "https://your-app.onrender.com/video/download" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.youtube.com/watch?v=VIDEO_ID",
       "quality": "720p",
       "format": "best"
     }'
```

### Check Download Status
```bash
curl "https://your-app.onrender.com/downloads/DOWNLOAD_ID"
```

## Supported Platforms

- YouTube
- TikTok
- Instagram
- Facebook
- Twitter/X
- Reddit
- Vimeo
- Dailymotion
- Twitch
- SoundCloud
- Bandcamp
- And 1500+ other platforms

## Notes

- The free tier on Render has limitations on CPU and memory usage
- Downloaded files are stored temporarily and may be cleaned up
- For production use, consider upgrading to a paid plan
- Make sure to respect the terms of service of video platforms

## License

This project is for educational purposes. Please respect the terms of service of video platforms and copyright laws.