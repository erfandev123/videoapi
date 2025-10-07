# Video Downloader Android App

A beautiful and modern Android app for downloading videos from 1500+ platforms using the Video Downloader API.

## Features

- 🎥 **Multi-Platform Support**: Download from YouTube, TikTok, Instagram, Facebook, Twitter/X, Reddit, Vimeo, and 1500+ other platforms
- 🎨 **Modern UI**: Clean, smooth, and beautiful design with Material Design principles
- ⚡ **Real-time Progress**: Live progress tracking with percentage and file size display
- 🎵 **Audio Only Option**: Download audio-only files (MP3)
- 📱 **Quality Selection**: Choose from 360p, 480p, 720p, and 1080p
- 🔄 **Real-time Status**: Live download status updates
- 📊 **Video Information**: Get detailed video info before downloading
- 🎯 **Error Handling**: Comprehensive error handling with retry options

## Screenshots

The app features:
- Clean card-based layout
- Modern color scheme with orange primary color
- Smooth animations and transitions
- Real-time progress bars
- Beautiful typography and spacing

## How to Use with AIDE

1. **Download the ZIP file**: `VideoDownloaderApp.zip`
2. **Extract the project**: Extract the ZIP file to your device
3. **Open in AIDE**: 
   - Open AIDE app
   - Select "Open Project"
   - Navigate to the extracted `VideoDownloaderApp` folder
   - Select the project
4. **Build the APK**:
   - Wait for AIDE to sync the project
   - Click "Build" → "Build APK"
   - Wait for the build to complete
5. **Install the APK**:
   - Click "Install" to install the APK on your device
   - Or find the APK in the project's `app/build/outputs/apk/` folder

## API Integration

The app connects to your hosted API at: `https://videoapi-fp4h.onrender.com`

### API Endpoints Used:
- `POST /video/info` - Get video information
- `POST /video/download` - Start video download
- `GET /downloads/{id}` - Check download status

## App Structure

```
VideoDownloaderApp/
├── app/
│   ├── src/main/
│   │   ├── java/com/videodownloader/app/
│   │   │   ├── MainActivity.java          # Main activity with UI logic
│   │   │   ├── ApiService.java           # API communication service
│   │   │   ├── VideoInfo.java            # Video info model
│   │   │   ├── DownloadResponse.java     # Download response model
│   │   │   └── DownloadStatus.java       # Download status model
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml     # Main UI layout
│   │   │   ├── values/
│   │   │   │   ├── strings.xml           # String resources
│   │   │   │   ├── colors.xml            # Color definitions
│   │   │   │   ├── themes.xml            # App themes
│   │   │   │   └── styles.xml            # Custom styles
│   │   │   └── drawable/                 # Button and background drawables
│   │   └── AndroidManifest.xml           # App manifest
│   └── build.gradle                      # App-level build configuration
├── build.gradle                          # Project-level build configuration
├── settings.gradle                       # Project settings
└── gradle.properties                     # Gradle properties
```

## Key Features Explained

### 1. Modern UI Design
- **Card-based Layout**: Clean, organized interface using CardView
- **Material Design**: Follows Google's Material Design guidelines
- **Color Scheme**: Orange primary color with blue secondary
- **Typography**: Clear, readable text with proper hierarchy

### 2. Real-time Functionality
- **Progress Tracking**: Live progress updates every 2 seconds
- **Status Updates**: Real-time download status (pending, downloading, completed, failed)
- **File Size Display**: Shows file size as it's calculated
- **Error Handling**: Comprehensive error messages with retry options

### 3. API Integration
- **Async Operations**: All API calls are performed asynchronously
- **Error Handling**: Proper error handling for network issues
- **JSON Parsing**: Custom JSON parsing for API responses
- **Progress Monitoring**: Continuous status checking during downloads

### 4. User Experience
- **Input Validation**: URL validation before API calls
- **Loading Indicators**: Progress dialogs during operations
- **Toast Messages**: User-friendly feedback messages
- **Retry Functionality**: Easy retry for failed downloads

## Customization

### Colors
Edit `app/src/main/res/values/colors.xml` to change the app's color scheme.

### Strings
Edit `app/src/main/res/values/strings.xml` to modify text content.

### API URL
Change the API URL in `ApiService.java`:
```java
private static final String BASE_URL = "https://videoapi-fp4h.onrender.com";
```

## Requirements

- **Android Version**: API 21+ (Android 5.0+)
- **Internet Permission**: Required for API calls
- **Storage Permission**: Required for downloading files
- **AIDE App**: For building the APK

## Troubleshooting

### Build Issues
1. **Gradle Sync Failed**: Make sure you have internet connection
2. **Build Error**: Check if all files are properly extracted
3. **Permission Denied**: Grant storage permissions when prompted

### Runtime Issues
1. **Network Error**: Check internet connection
2. **API Error**: Verify the API is running and accessible
3. **Download Failed**: Check if the video URL is valid and supported

## Support

This app is designed to work seamlessly with your hosted Video Downloader API. Make sure your API is running and accessible before using the app.

## License

This project is for educational purposes. Please respect the terms of service of video platforms and copyright laws.