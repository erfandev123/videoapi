package com.videodownloader.app;

import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    
    // UI Components
    private EditText etVideoUrl;
    private Button btnGetInfo, btnDownload, btnRetry;
    private RadioButton rb360p, rb480p, rb720p, rb1080p;
    private CheckBox cbAudioOnly;
    private CardView cardVideoInfo, cardDownloadProgress, cardDownloadResult;
    private TextView tvVideoTitle, tvPlatform, tvDuration, tvUploader, tvViews;
    private TextView tvDownloadStatus, tvProgressText, tvFileSize, tvDownloadResult, tvDownloadError;
    private ProgressBar progressBar;
    
    // Variables
    private VideoInfo currentVideoInfo;
    private String currentDownloadId;
    private Timer progressTimer;
    private Handler mainHandler;
    private ProgressDialog progressDialog;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initializeViews();
        setupClickListeners();
        mainHandler = new Handler();
    }

    private void initializeViews() {
        etVideoUrl = findViewById(R.id.etVideoUrl);
        btnGetInfo = findViewById(R.id.btnGetInfo);
        btnDownload = findViewById(R.id.btnDownload);
        btnRetry = findViewById(R.id.btnRetry);
        
        rb360p = findViewById(R.id.rb360p);
        rb480p = findViewById(R.id.rb480p);
        rb720p = findViewById(R.id.rb720p);
        rb1080p = findViewById(R.id.rb1080p);
        cbAudioOnly = findViewById(R.id.cbAudioOnly);
        
        cardVideoInfo = findViewById(R.id.cardVideoInfo);
        cardDownloadProgress = findViewById(R.id.cardDownloadProgress);
        cardDownloadResult = findViewById(R.id.cardDownloadResult);
        
        tvVideoTitle = findViewById(R.id.tvVideoTitle);
        tvPlatform = findViewById(R.id.tvPlatform);
        tvDuration = findViewById(R.id.tvDuration);
        tvUploader = findViewById(R.id.tvUploader);
        tvViews = findViewById(R.id.tvViews);
        
        tvDownloadStatus = findViewById(R.id.tvDownloadStatus);
        tvProgressText = findViewById(R.id.tvProgressText);
        tvFileSize = findViewById(R.id.tvFileSize);
        tvDownloadResult = findViewById(R.id.tvDownloadResult);
        tvDownloadError = findViewById(R.id.tvDownloadError);
        
        progressBar = findViewById(R.id.progressBar);
    }

    private void setupClickListeners() {
        btnGetInfo.setOnClickListener(v -> getVideoInfo());
        btnDownload.setOnClickListener(v -> downloadVideo());
        btnRetry.setOnClickListener(v -> retryDownload());
        
        cbAudioOnly.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                // Disable quality selection when audio only is selected
                rb360p.setEnabled(false);
                rb480p.setEnabled(false);
                rb720p.setEnabled(false);
                rb1080p.setEnabled(false);
            } else {
                // Enable quality selection when audio only is unchecked
                rb360p.setEnabled(true);
                rb480p.setEnabled(true);
                rb720p.setEnabled(true);
                rb1080p.setEnabled(true);
            }
        });
    }

    private void getVideoInfo() {
        String url = etVideoUrl.getText().toString().trim();
        if (TextUtils.isEmpty(url)) {
            showToast("Please enter a video URL");
            return;
        }

        if (!isValidUrl(url)) {
            showToast("Please enter a valid video URL");
            return;
        }

        showProgressDialog("Getting video information...");
        
        ApiService.getVideoInfo(url, new ApiService.ApiCallback<VideoInfo>() {
            @Override
            public void onSuccess(VideoInfo result) {
                mainHandler.post(() -> {
                    hideProgressDialog();
                    currentVideoInfo = result;
                    displayVideoInfo(result);
                });
            }

            @Override
            public void onError(String error) {
                mainHandler.post(() -> {
                    hideProgressDialog();
                    showToast("Error: " + error);
                });
            }
        });
    }

    private void downloadVideo() {
        String url = etVideoUrl.getText().toString().trim();
        if (TextUtils.isEmpty(url)) {
            showToast("Please enter a video URL");
            return;
        }

        if (!isValidUrl(url)) {
            showToast("Please enter a valid video URL");
            return;
        }

        String quality = getSelectedQuality();
        boolean audioOnly = cbAudioOnly.isChecked();

        showProgressDialog("Starting download...");
        
        ApiService.downloadVideo(url, quality, audioOnly, new ApiService.ApiCallback<DownloadResponse>() {
            @Override
            public void onSuccess(DownloadResponse result) {
                mainHandler.post(() -> {
                    hideProgressDialog();
                    currentDownloadId = result.getDownloadId();
                    showDownloadProgress();
                    startProgressTracking();
                });
            }

            @Override
            public void onError(String error) {
                mainHandler.post(() -> {
                    hideProgressDialog();
                    showToast("Error: " + error);
                });
            }
        });
    }

    private void retryDownload() {
        cardDownloadResult.setVisibility(View.GONE);
        cardDownloadProgress.setVisibility(View.GONE);
        downloadVideo();
    }

    private void displayVideoInfo(VideoInfo videoInfo) {
        cardVideoInfo.setVisibility(View.VISIBLE);
        
        tvVideoTitle.setText("Title: " + videoInfo.getTitle());
        tvPlatform.setText("Platform: " + videoInfo.getPlatform());
        tvDuration.setText("Duration: " + formatDuration(videoInfo.getDuration()));
        tvUploader.setText("Uploader: " + videoInfo.getUploader());
        tvViews.setText("Views: " + formatNumber(videoInfo.getViewCount()));
    }

    private void showDownloadProgress() {
        cardDownloadProgress.setVisibility(View.VISIBLE);
        cardDownloadResult.setVisibility(View.GONE);
        
        tvDownloadStatus.setText("Starting download...");
        progressBar.setProgress(0);
        tvProgressText.setText("0%");
        tvFileSize.setText("File Size: Calculating...");
    }

    private void startProgressTracking() {
        if (progressTimer != null) {
            progressTimer.cancel();
        }
        
        progressTimer = new Timer();
        progressTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                if (currentDownloadId != null) {
                    checkDownloadStatus();
                }
            }
        }, 1000, 2000); // Check every 2 seconds
    }

    private void checkDownloadStatus() {
        ApiService.getDownloadStatus(currentDownloadId, new ApiService.ApiCallback<DownloadStatus>() {
            @Override
            public void onSuccess(DownloadStatus status) {
                mainHandler.post(() -> updateDownloadProgress(status));
            }

            @Override
            public void onError(String error) {
                mainHandler.post(() -> {
                    Log.e(TAG, "Error checking download status: " + error);
                });
            }
        });
    }

    private void updateDownloadProgress(DownloadStatus status) {
        String statusText = status.getStatus();
        double progress = status.getProgress();
        
        tvDownloadStatus.setText("Status: " + statusText);
        progressBar.setProgress((int) progress);
        tvProgressText.setText(String.format("%.1f%%", progress));
        
        if (status.getFileSize() > 0) {
            tvFileSize.setText("File Size: " + formatFileSize(status.getFileSize()));
        }
        
        if ("completed".equals(statusText)) {
            progressTimer.cancel();
            showDownloadCompleted();
        } else if ("failed".equals(statusText)) {
            progressTimer.cancel();
            showDownloadFailed(status.getError());
        }
    }

    private void showDownloadCompleted() {
        cardDownloadProgress.setVisibility(View.GONE);
        cardDownloadResult.setVisibility(View.VISIBLE);
        
        tvDownloadResult.setText("Download Completed!");
        tvDownloadResult.setTextColor(getResources().getColor(R.color.success));
        tvDownloadError.setVisibility(View.GONE);
        btnRetry.setVisibility(View.GONE);
        
        showToast("Download completed successfully!");
    }

    private void showDownloadFailed(String error) {
        cardDownloadProgress.setVisibility(View.GONE);
        cardDownloadResult.setVisibility(View.VISIBLE);
        
        tvDownloadResult.setText("Download Failed");
        tvDownloadResult.setTextColor(getResources().getColor(R.color.error));
        tvDownloadError.setText(error != null ? error : "Unknown error occurred");
        tvDownloadError.setVisibility(View.VISIBLE);
        btnRetry.setVisibility(View.VISIBLE);
        
        showToast("Download failed: " + (error != null ? error : "Unknown error"));
    }

    private String getSelectedQuality() {
        if (rb360p.isChecked()) return "360p";
        if (rb480p.isChecked()) return "480p";
        if (rb720p.isChecked()) return "720p";
        if (rb1080p.isChecked()) return "1080p";
        return "720p";
    }

    private boolean isValidUrl(String url) {
        return url.startsWith("http://") || url.startsWith("https://");
    }

    private String formatDuration(int seconds) {
        if (seconds <= 0) return "Unknown";
        
        int hours = seconds / 3600;
        int minutes = (seconds % 3600) / 60;
        int secs = seconds % 60;
        
        if (hours > 0) {
            return String.format("%d:%02d:%02d", hours, minutes, secs);
        } else {
            return String.format("%d:%02d", minutes, secs);
        }
    }

    private String formatNumber(long number) {
        if (number < 1000) return String.valueOf(number);
        if (number < 1000000) return String.format("%.1fK", number / 1000.0);
        if (number < 1000000000) return String.format("%.1fM", number / 1000000.0);
        return String.format("%.1fB", number / 1000000000.0);
    }

    private String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024.0));
        return String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0));
    }

    private void showProgressDialog(String message) {
        if (progressDialog == null) {
            progressDialog = new ProgressDialog(this);
            progressDialog.setCancelable(false);
        }
        progressDialog.setMessage(message);
        progressDialog.show();
    }

    private void hideProgressDialog() {
        if (progressDialog != null && progressDialog.isShowing()) {
            progressDialog.dismiss();
        }
    }

    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (progressTimer != null) {
            progressTimer.cancel();
        }
        if (progressDialog != null && progressDialog.isShowing()) {
            progressDialog.dismiss();
        }
    }
}