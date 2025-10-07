package com.videodownloader.app;

public class DownloadResponse {
    private String status;
    private String message;
    private String downloadId;
    private VideoInfo info;
    private String downloadUrl;
    private String fileUrl;

    // Constructor
    public DownloadResponse() {}

    // Getters and Setters
    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getDownloadId() {
        return downloadId;
    }

    public void setDownloadId(String downloadId) {
        this.downloadId = downloadId;
    }

    public VideoInfo getInfo() {
        return info;
    }

    public void setInfo(VideoInfo info) {
        this.info = info;
    }

    public String getDownloadUrl() {
        return downloadUrl;
    }

    public void setDownloadUrl(String downloadUrl) {
        this.downloadUrl = downloadUrl;
    }

    public String getFileUrl() {
        return fileUrl;
    }

    public void setFileUrl(String fileUrl) {
        this.fileUrl = fileUrl;
    }
}