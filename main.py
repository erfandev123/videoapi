from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
import concurrent.futures
import threading

app = FastAPI(
    title="Multi-Platform Video Downloader API",
    description="A powerful API for downloading videos from YouTube, TikTok, Instagram, Facebook and 1500+ other platforms",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
    file_url: Optional[str] = None

class JobStatus(BaseModel):
    download_id: str
    status: str  # pending, downloading, completed, failed
    progress: Optional[float] = None
    info: Optional[VideoInfo] = None
    file_path: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

# Global storage for download tasks and thread pool
download_tasks = {}
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

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
                if info and 'formats' in info and info['formats']:
                    for fmt in info['formats']:
                        formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'resolution': fmt.get('resolution', 'N/A'),
                            'filesize': fmt.get('filesize'),
                            'quality': fmt.get('quality')
                        })
                
                if info:
                    description = info.get('description', '')
                    if description and len(description) > 500:
                        description = description[:500] + "..."
                    
                    return VideoInfo(
                        title=info.get('title', 'Unknown'),
                        duration=info.get('duration'),
                        uploader=info.get('uploader'),
                        view_count=info.get('view_count'),
                        upload_date=info.get('upload_date'),
                        thumbnail=info.get('thumbnail'),
                        description=description,
                        formats=formats[:10],  # Limit to first 10 formats
                        platform=self.extract_platform(url)
                    )
                else:
                    raise HTTPException(status_code=400, detail="Failed to extract video info")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract video info: {str(e)}")
    
    def download_video_sync(self, url: str, download_id: str, format_selector="best", quality="720p", audio_only=False, extract_audio=False):
        """Synchronous video download function for thread execution"""
        try:
            # Update status to downloading
            if download_id in download_tasks:
                download_tasks[download_id]['status'] = 'downloading'
            
            ydl_opts = self.get_ydl_opts(format_selector, quality, audio_only, extract_audio)
            
            # Add progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        if download_id in download_tasks:
                            download_tasks[download_id]['progress'] = progress
                elif d['status'] == 'finished':
                    if download_id in download_tasks:
                        download_tasks[download_id]['progress'] = 100.0
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("Failed to extract video information")
                
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
                    if video_id in file:
                        downloaded_file = file
                        break
                
                if not downloaded_file:
                    # Try matching by title
                    for file in os.listdir(self.download_dir):
                        if any(word in file.lower() for word in safe_title.lower().split('_')[:3]):
                            downloaded_file = file
                            break
                
                if downloaded_file:
                    file_path = os.path.join(self.download_dir, downloaded_file)
                    file_size = os.path.getsize(file_path)
                    
                    # Update task with completion
                    if download_id in download_tasks:
                        download_tasks[download_id].update({
                            'status': 'completed',
                            'file_path': file_path,
                            'filename': downloaded_file,
                            'file_size': file_size,
                            'completed_at': datetime.now().isoformat(),
                            'progress': 100.0
                        })
                    
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
            # Update task with error
            if download_id in download_tasks:
                download_tasks[download_id].update({
                    'status': 'failed',
                    'error': str(e),
                    'completed_at': datetime.now().isoformat()
                })
            raise e
    
    async def start_download(self, url: str, format_selector="best", quality="720p", audio_only=False, extract_audio=False) -> str:
        """Start async video download and return download_id"""
        download_id = str(uuid.uuid4())
        
        # Create initial task entry
        download_tasks[download_id] = {
            'status': 'pending',
            'progress': 0.0,
            'created_at': datetime.now().isoformat(),
            'url': url
        }
        
        # Submit to thread pool
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            thread_pool,
            self.download_video_sync,
            url, download_id, format_selector, quality, audio_only, extract_audio
        )
        
        return download_id

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
            "/video/download": "Start video download",
            "/video/batch": "Start multiple video downloads",
            "/downloads/{download_id}": "Get download status and progress",
            "/files/{download_id}": "Download completed video file"
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
        
        # Start the download
        download_id = await downloader_service.start_download(
            str(request.url),
            request.format or "best",
            request.quality or "720p",
            request.audio_only or False,
            request.extract_audio or False
        )
        
        # Store video info in task
        if download_id in download_tasks:
            download_tasks[download_id]['info'] = info.dict()
        
        return DownloadResponse(
            status="accepted",
            message="Download started. Use download_id to check progress.",
            download_id=download_id,
            info=info,
            download_url=f"/downloads/{download_id}",
            file_url=f"/files/{download_id}"
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
            
            # Start download
            download_id = await downloader_service.start_download(
                str(url),
                request.format or "best",
                request.quality or "720p",
                request.audio_only or False,
                False  # extract_audio for batch downloads
            )
            
            # Store info in task
            if download_id in download_tasks:
                download_tasks[download_id]['info'] = info.dict()
            
            results.append({
                'url': str(url),
                'status': 'started',
                'download_id': download_id,
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
    response = {
        'download_id': download_id,
        'status': task_info['status'],
        'progress': task_info.get('progress', 0.0),
        'created_at': task_info['created_at']
    }
    
    # Add optional fields if available
    if 'info' in task_info:
        response['info'] = task_info['info']
    if 'filename' in task_info:
        response['filename'] = task_info['filename']
    if 'file_size' in task_info:
        response['file_size'] = task_info['file_size']
    if 'completed_at' in task_info:
        response['completed_at'] = task_info['completed_at']
    if 'error' in task_info:
        response['error'] = task_info['error']
    if task_info['status'] == 'completed':
        response['file_url'] = f"/files/{download_id}"
    
    return response

@app.get("/files/{download_id}")
async def download_file(download_id: str):
    """Download the actual video file"""
    if download_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Download not found")
    
    task_info = download_tasks[download_id]
    
    if task_info['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Download not completed. Status: {task_info['status']}")
    
    if 'file_path' not in task_info or not os.path.exists(task_info['file_path']):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = task_info['file_path']
    filename = task_info.get('filename', 'video.mp4')
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/downloads")
async def list_downloads():
    """List all downloads"""
    downloads = []
    for download_id, task in download_tasks.items():
        download_info = {
            'download_id': download_id,
            'status': task['status'],
            'created_at': task['created_at'],
            'progress': task.get('progress', 0.0)
        }
        
        # Add optional fields safely
        if 'info' in task:
            download_info['title'] = task['info'].get('title', 'Unknown')
            download_info['platform'] = task['info'].get('platform', 'Unknown')
        else:
            download_info['title'] = 'Unknown'
            download_info['platform'] = 'Unknown'
            
        if 'filename' in task:
            download_info['filename'] = task['filename']
        if 'file_size' in task:
            download_info['file_size'] = task['file_size']
        if 'completed_at' in task:
            download_info['completed_at'] = task['completed_at']
        if 'error' in task:
            download_info['error'] = task['error']
            
        downloads.append(download_info)
    
    return {
        'total_downloads': len(download_tasks),
        'downloads': downloads
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