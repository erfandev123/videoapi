package com.videodownloader.app;

import android.os.AsyncTask;
import android.util.Log;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class ApiService {
    private static final String BASE_URL = "https://videoapi-fp4h.onrender.com";
    private static final String TAG = "ApiService";

    public interface ApiCallback<T> {
        void onSuccess(T result);
        void onError(String error);
    }

    public static void getVideoInfo(String videoUrl, ApiCallback<VideoInfo> callback) {
        final String finalVideoUrl = videoUrl;
        new AsyncTask<String, Void, VideoInfo>() {
            @Override
            protected VideoInfo doInBackground(String... urls) {
                try {
                    URL url = new URL(BASE_URL + "/video/info");
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("POST");
                    connection.setRequestProperty("Content-Type", "application/json");
                    connection.setDoOutput(true);

                    JSONObject jsonInput = new JSONObject();
                    jsonInput.put("url", finalVideoUrl);

                    OutputStream os = connection.getOutputStream();
                    os.write(jsonInput.toString().getBytes(StandardCharsets.UTF_8));
                    os.close();

                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();

                        return parseVideoInfo(response.toString());
                    } else {
                        Log.e(TAG, "Error response code: " + responseCode);
                        return null;
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error getting video info", e);
                    return null;
                }
            }

            @Override
            protected void onPostExecute(VideoInfo result) {
                if (result != null) {
                    callback.onSuccess(result);
                } else {
                    callback.onError("Failed to get video information");
                }
            }
        }.execute(videoUrl);
    }

    public static void downloadVideo(String videoUrl, String quality, boolean audioOnly, ApiCallback<DownloadResponse> callback) {
        final String finalVideoUrl = videoUrl;
        final String finalQuality = quality;
        final boolean finalAudioOnly = audioOnly;
        new AsyncTask<String, Void, DownloadResponse>() {
            @Override
            protected DownloadResponse doInBackground(String... params) {
                try {
                    URL url = new URL(BASE_URL + "/video/download");
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("POST");
                    connection.setRequestProperty("Content-Type", "application/json");
                    connection.setDoOutput(true);

                    JSONObject jsonInput = new JSONObject();
                    jsonInput.put("url", finalVideoUrl);
                    jsonInput.put("quality", finalQuality);
                    jsonInput.put("audio_only", finalAudioOnly);

                    OutputStream os = connection.getOutputStream();
                    os.write(jsonInput.toString().getBytes(StandardCharsets.UTF_8));
                    os.close();

                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();

                        return parseDownloadResponse(response.toString());
                    } else {
                        Log.e(TAG, "Error response code: " + responseCode);
                        return null;
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error downloading video", e);
                    return null;
                }
            }

            @Override
            protected void onPostExecute(DownloadResponse result) {
                if (result != null) {
                    callback.onSuccess(result);
                } else {
                    callback.onError("Failed to start download");
                }
            }
        }.execute(videoUrl, quality, String.valueOf(audioOnly));
    }

    public static void getDownloadStatus(String downloadId, ApiCallback<DownloadStatus> callback) {
        final String finalDownloadId = downloadId;
        new AsyncTask<String, Void, DownloadStatus>() {
            @Override
            protected DownloadStatus doInBackground(String... params) {
                try {
                    URL url = new URL(BASE_URL + "/downloads/" + finalDownloadId);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");

                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();

                        return parseDownloadStatus(response.toString());
                    } else {
                        Log.e(TAG, "Error response code: " + responseCode);
                        return null;
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error getting download status", e);
                    return null;
                }
            }

            @Override
            protected void onPostExecute(DownloadStatus result) {
                if (result != null) {
                    callback.onSuccess(result);
                } else {
                    callback.onError("Failed to get download status");
                }
            }
        }.execute(downloadId);
    }

    private static VideoInfo parseVideoInfo(String json) {
        try {
            JSONObject jsonObject = new JSONObject(json);
            VideoInfo videoInfo = new VideoInfo();
            videoInfo.setTitle(jsonObject.optString("title", "Unknown"));
            videoInfo.setDuration(jsonObject.optInt("duration", 0));
            videoInfo.setUploader(jsonObject.optString("uploader", "Unknown"));
            videoInfo.setViewCount(jsonObject.optLong("view_count", 0));
            videoInfo.setUploadDate(jsonObject.optString("upload_date", ""));
            videoInfo.setThumbnail(jsonObject.optString("thumbnail", ""));
            videoInfo.setDescription(jsonObject.optString("description", ""));
            videoInfo.setPlatform(jsonObject.optString("platform", "Unknown"));
            return videoInfo;
        } catch (JSONException e) {
            Log.e(TAG, "Error parsing video info", e);
            return null;
        }
    }

    private static DownloadResponse parseDownloadResponse(String json) {
        try {
            JSONObject jsonObject = new JSONObject(json);
            DownloadResponse response = new DownloadResponse();
            response.setStatus(jsonObject.optString("status", ""));
            response.setMessage(jsonObject.optString("message", ""));
            response.setDownloadId(jsonObject.optString("download_id", ""));
            response.setDownloadUrl(jsonObject.optString("download_url", ""));
            response.setFileUrl(jsonObject.optString("file_url", ""));

            if (jsonObject.has("info")) {
                JSONObject infoJson = jsonObject.getJSONObject("info");
                VideoInfo info = new VideoInfo();
                info.setTitle(infoJson.optString("title", "Unknown"));
                info.setPlatform(infoJson.optString("platform", "Unknown"));
                response.setInfo(info);
            }

            return response;
        } catch (JSONException e) {
            Log.e(TAG, "Error parsing download response", e);
            return null;
        }
    }

    private static DownloadStatus parseDownloadStatus(String json) {
        try {
            JSONObject jsonObject = new JSONObject(json);
            DownloadStatus status = new DownloadStatus();
            status.setDownloadId(jsonObject.optString("download_id", ""));
            status.setStatus(jsonObject.optString("status", ""));
            status.setProgress((float) jsonObject.optDouble("progress", 0.0));
            status.setFilename(jsonObject.optString("filename", ""));
            status.setFileSize(jsonObject.optLong("file_size", 0));
            status.setError(jsonObject.optString("error", ""));
            status.setCreatedAt(jsonObject.optString("created_at", ""));
            status.setCompletedAt(jsonObject.optString("completed_at", ""));

            if (jsonObject.has("info")) {
                JSONObject infoJson = jsonObject.getJSONObject("info");
                VideoInfo info = new VideoInfo();
                info.setTitle(infoJson.optString("title", "Unknown"));
                info.setPlatform(infoJson.optString("platform", "Unknown"));
                status.setInfo(info);
            }

            return status;
        } catch (JSONException e) {
            Log.e(TAG, "Error parsing download status", e);
            return null;
        }
    }
}