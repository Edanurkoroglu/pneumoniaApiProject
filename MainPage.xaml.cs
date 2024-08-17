using Microsoft.Maui.Controls;
using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Maui.Storage;
using Microsoft.Maui.Media;
using System.Threading;

namespace MauiApp1
{
    public partial class MainPage : ContentPage
    {
        private string _photoPath;
        private string _videoPath;

        public MainPage()
        {
            InitializeComponent();
        }

        private async void OnUploadPhotoClicked(object sender, EventArgs e)
        {
            _videoPath = null; // Videoyu sıfırla
            var result = await FilePicker.PickAsync(new PickOptions
            {
                FileTypes = FilePickerFileType.Images,
                PickerTitle = "Select an image"

            });

            if (result != null)
            {
                _photoPath = result.FullPath;
                UploadedPhoto.Source = ImageSource.FromFile(_photoPath);
                UploadedPhoto.IsVisible = true;
            }
        }

        private async void OnUploadVideoClicked(object sender, EventArgs e)
        {
            _photoPath = null; // Fotoğrafı sıfırla
            var result = await FilePicker.PickAsync(new PickOptions
            {
                FileTypes = FilePickerFileType.Videos,
                PickerTitle = "Select a video"
            });

            if (result != null)
            {
                _videoPath = result.FullPath;

                // Display the video file name
                VideoFileNameLabel.Text = $"Video uploaded: {Path.GetFileName(_videoPath)}";
                VideoFileNameLabel.IsVisible = true;
            }
        }

        private async void OnOpenCameraClicked(object sender, EventArgs e)
        {
            _videoPath = null; // Videoyu sıfırla
            var photoResult = await MediaPicker.CapturePhotoAsync();

            if (photoResult != null)
            {
                _photoPath = Path.Combine(FileSystem.CacheDirectory, photoResult.FileName);
                using (var stream = await photoResult.OpenReadAsync())
                using (var fileStream = File.OpenWrite(_photoPath))
                    await stream.CopyToAsync(fileStream);

                UploadedPhoto.Source = ImageSource.FromFile(_photoPath);
                UploadedPhoto.IsVisible = true;
            }
        }

        private async void OnSendClicked(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(_photoPath) && string.IsNullOrEmpty(_videoPath))
            {
                await DisplayAlert("Error", "Please upload a photo or video first.", "OK");
                return;
            }

            string filePath = !string.IsNullOrEmpty(_photoPath) ? _photoPath : _videoPath;
            var result = await SendFileToApi(filePath);
            ResultTextBox.Text = result;

            // İstek gönderildikten sonra dosya yollarını sıfırla
            _photoPath = null;
            _videoPath = null;
        }

        private async Task<string> SendFileToApi(string filePath)
        {
            try
            {
                using (var client = new HttpClient())
                {
                    var apiUrl = "http://localhost:8000/predict"; // Replace with your API URL
                    using (var form = new MultipartFormDataContent())
                    {
                        var stream = File.OpenRead(filePath);
                        form.Add(new StreamContent(stream), "file", System.IO.Path.GetFileName(filePath));

                        var response = await client.PostAsync(apiUrl, form);
                        response.EnsureSuccessStatusCode();

                        var responseContent = await response.Content.ReadAsStringAsync();
                        return responseContent; // Adjust according to your API's response
                    }
                }
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
        }
    }
}
