from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import yt_dlp
import os
import json
import uuid
import asyncio
import aiofiles
from datetime import datetime
import re

app = FastAPI(
    title="Multi-Platform Video Downloader API",
    description="A powerful API for downloading videos from YouTube, TikTok, Instagram, Facebook and 1500+ other platforms",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class VideoDownloadRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = "best"
    quality: Optional[str] = "720p"
    audio_only: Optional[bool] = False
    extract_audio: Optional[bool] = False

class VideoInfoRequest(BaseModel):
    url: HttpUrl

class BatchDownloadRequest(BaseModel):
    urls: List[HttpUrl]
    format: Optional[str] = "best"
    quality: Optional[str] = "720p"
    audio_only: Optional[bool] = False

class VideoInfo(BaseModel):
    title: str
    duration: Optional[int]
    uploader: Optional[str]
    view_count: Optional[int]
    upload_date: Optional[str]
    thumbnail: Optional[str]
    description: Optional[str]
    formats: List[Dict[str, Any]]
    platform: str

class DownloadResponse(BaseModel):
    status: str
    message: str
    download_id: Optional[str] = None
    info: Optional[VideoInfo] = None
    download_url: Optional[str] = None

# Global storage for download tasks
download_tasks = {}

class VideoDownloaderService:
    def __init__(self):
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)
    
    def get_ydl_opts(self, format_selector="best", quality="720p", audio_only=False, extract_audio=False):
        """Get yt-dlp options based on requirements"""
        
        if audio_only or extract_audio:
            format_str = "bestaudio/best"
            ext = "mp3"
        else:
            if quality == "1080p":
                format_str = "best[height<=1080]"
            elif quality == "720p":
                format_str = "best[height<=720]"
            elif quality == "480p":
                format_str = "best[height<=480]"
            elif quality == "360p":
                format_str = "best[height<=360]"
            else:
                format_str = format_selector
            ext = "mp4"
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': f'{self.download_dir}/%(title)s_%(id)s.%(ext)s',
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'extractflat': False,
            'writethumbnail': False,
        }
        
        if audio_only or extract_audio:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        return ydl_opts
    
    def extract_platform(self, url: str) -> str:
        """Extract platform name from URL"""
        url = str(url).lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return "YouTube"
        elif 'tiktok.com' in url:
            return "TikTok"
        elif 'instagram.com' in url:
            return "Instagram"
        elif 'facebook.com' in url or 'fb.watch' in url:
            return "Facebook"
        elif 'twitter.com' in url or 'x.com' in url:
            return "Twitter/X"
        else:
            return "Other"
    
    async def get_video_info(self, url: str) -> VideoInfo:
        """Extract video information without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract formats info
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'resolution': fmt.get('resolution', 'N/A'),
                            'filesize': fmt.get('filesize'),
                            'quality': fmt.get('quality')
                        })
                
                return VideoInfo(
                    title=info.get('title', 'Unknown'),
                    duration=info.get('duration'),
                    uploader=info.get('uploader'),
                    view_count=info.get('view_count'),
                    upload_date=info.get('upload_date'),
                    thumbnail=info.get('thumbnail'),
                    description=info.get('description', '')[:500] + "..." if info.get('description') and len(info.get('description', '')) > 500 else info.get('description', ''),
                    formats=formats[:10],  # Limit to first 10 formats
                    platform=self.extract_platform(url)
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract video info: {str(e)}")
    
    async def download_video(self, url: str, format_selector="best", quality="720p", audio_only=False, extract_audio=False) -> Dict[str, Any]:
        """Download video and return file path"""
        download_id = str(uuid.uuid4())
        
        try:
            ydl_opts = self.get_ydl_opts(format_selector, quality, audio_only, extract_audio)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                title = info.get('title', 'Unknown')
                video_id = info.get('id', 'unknown')
                
                # Clean title for filename matching
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
                
                # Look for the file
                downloaded_file = None
                for file in os.listdir(self.download_dir):
                    if video_id in file or safe_title in file:
                        downloaded_file = file
                        break
                
                if downloaded_file:
                    file_path = os.path.join(self.download_dir, downloaded_file)
                    file_size = os.path.getsize(file_path)
                    
                    return {
                        'download_id': download_id,
                        'file_path': file_path,
                        'filename': downloaded_file,
                        'file_size': file_size,
                        'title': title,
                        'platform': self.extract_platform(url)
                    }
                else:
                    raise Exception("Downloaded file not found")
                    
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

# Initialize service
downloader_service = VideoDownloaderService()

@app.get("/")
async def root():
    """API health check and welcome message"""
    return {
        "message": "Multi-Platform Video Downloader API",
        "status": "active",
        "supported_platforms": [
            "YouTube", "TikTok", "Instagram", "Facebook", 
            "Twitter/X", "Reddit", "Vimeo", "Dailymotion",
            "And 1500+ other platforms"
        ],
        "version": "1.0.0",
        "endpoints": {
            "/": "API information",
            "/video/info": "Get video information",
            "/video/download": "Download single video",
            "/video/batch": "Download multiple videos",
            "/downloads/{download_id}": "Get download status"
        }
    }

@app.post("/video/info", response_model=VideoInfo)
async def get_video_info(request: VideoInfoRequest):
    """Get detailed information about a video without downloading"""
    try:
        info = await downloader_service.get_video_info(str(request.url))
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/video/download", response_model=DownloadResponse)
async def download_video(request: VideoDownloadRequest, background_tasks: BackgroundTasks):
    """Download a single video"""
    try:
        # Get video info first
        info = await downloader_service.get_video_info(str(request.url))
        
        # Download the video
        result = await downloader_service.download_video(
            str(request.url),
            request.format,
            request.quality,
            request.audio_only,
            request.extract_audio
        )
        
        # Store download task info
        download_tasks[result['download_id']] = {
            'status': 'completed',
            'info': info.dict(),
            'file_path': result['file_path'],
            'filename': result['filename'],
            'file_size': result['file_size'],
            'created_at': datetime.now().isoformat()
        }
        
        return DownloadResponse(
            status="success",
            message="Video downloaded successfully",
            download_id=result['download_id'],
            info=info,
            download_url=f"/downloads/{result['download_id']}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/video/batch")
async def batch_download(request: BatchDownloadRequest):
    """Download multiple videos"""
    results = []
    errors = []
    
    for i, url in enumerate(request.urls):
        try:
            # Get video info
            info = await downloader_service.get_video_info(str(url))
            
            # Download video
            result = await downloader_service.download_video(
                str(url),
                request.format,
                request.quality,
                request.audio_only
            )
            
            # Store task info
            download_tasks[result['download_id']] = {
                'status': 'completed',
                'info': info.dict(),
                'file_path': result['file_path'],
                'filename': result['filename'],
                'file_size': result['file_size'],
                'created_at': datetime.now().isoformat()
            }
            
            results.append({
                'url': str(url),
                'status': 'success',
                'download_id': result['download_id'],
                'title': info.title,
                'platform': info.platform
            })
            
        except Exception as e:
            errors.append({
                'url': str(url),
                'error': str(e)
            })
    
    return {
        'status': 'completed',
        'total_requested': len(request.urls),
        'successful_downloads': len(results),
        'failed_downloads': len(errors),
        'results': results,
        'errors': errors
    }

@app.get("/downloads/{download_id}")
async def get_download_info(download_id: str):
    """Get information about a specific download"""
    if download_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Download not found")
    
    task_info = download_tasks[download_id]
    return {
        'download_id': download_id,
        'status': task_info['status'],
        'info': task_info['info'],
        'filename': task_info['filename'],
        'file_size': task_info['file_size'],
        'created_at': task_info['created_at']
    }

@app.get("/downloads")
async def list_downloads():
    """List all downloads"""
    return {
        'total_downloads': len(download_tasks),
        'downloads': [
            {
                'download_id': download_id,
                'title': task['info']['title'],
                'platform': task['info']['platform'],
                'status': task['status'],
                'created_at': task['created_at'],
                'filename': task['filename'],
                'file_size': task['file_size']
            }
            for download_id, task in download_tasks.items()
        ]
    }

@app.get("/platforms")
async def supported_platforms():
    """Get list of supported platforms"""
    return {
        'major_platforms': [
            'YouTube', 'TikTok', 'Instagram', 'Facebook',
            'Twitter/X', 'Reddit', 'Vimeo', 'Dailymotion',
            'Twitch', 'SoundCloud', 'Bandcamp'
        ],
        'total_supported': "1500+",
        'note': "This API supports downloading from over 1500 websites using yt-dlp library"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)