# Overview

This is a multi-platform video downloader API built with FastAPI that supports downloading videos from YouTube, TikTok, Instagram, Facebook, and over 1500+ other platforms. The application leverages yt-dlp (a powerful Python library) to handle video extraction and downloading from various social media and video hosting platforms. The API provides endpoints for single video downloads, batch downloads, and video information extraction with configurable quality and format options.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## API Framework
- **FastAPI**: Modern, fast web framework for building REST APIs with automatic OpenAPI documentation
- **CORS Middleware**: Configured to allow cross-origin requests from any domain for maximum accessibility
- **Pydantic Models**: Type-safe request/response validation and serialization

## Video Processing Engine
- **yt-dlp Integration**: Core video extraction library supporting 1500+ platforms
- **Asynchronous Processing**: Uses async/await patterns with aiofiles for non-blocking file operations
- **Concurrent Downloads**: Implements threading and concurrent.futures for handling multiple downloads simultaneously
- **Background Tasks**: FastAPI background tasks for handling long-running download operations

## Download Management
- **UUID-based File Naming**: Generates unique identifiers to prevent file conflicts
- **Quality Selection**: Supports configurable video quality (720p default) and format selection
- **Audio Extraction**: Optional audio-only downloads and audio extraction from video files
- **Batch Processing**: Handles multiple URL downloads in a single request

## File System Architecture
- **Local File Storage**: Downloads are stored locally with organized file structure
- **File Response Handling**: Direct file serving through FastAPI's FileResponse
- **Temporary File Management**: Handles cleanup of downloaded files after serving

## Request/Response Design
- **Structured Input Validation**: HttpUrl validation for video URLs with optional parameters
- **Flexible Format Options**: Support for various video formats and quality settings
- **Comprehensive Video Metadata**: Extraction of video information including titles and metadata

# External Dependencies

## Core Libraries
- **yt-dlp**: Primary video extraction and download library supporting 1500+ platforms
- **FastAPI**: Web framework for API development
- **Pydantic**: Data validation and serialization
- **aiofiles**: Asynchronous file operations

## Platform Support
- **YouTube**: Full video and audio download support
- **TikTok**: Short-form video downloads
- **Instagram**: Stories, posts, and reels
- **Facebook**: Video content extraction
- **1500+ Additional Platforms**: Comprehensive platform support through yt-dlp

## System Dependencies
- **Python Threading**: Concurrent processing capabilities
- **UUID Library**: Unique identifier generation
- **OS Module**: File system operations and path management
- **JSON Processing**: Metadata handling and configuration management