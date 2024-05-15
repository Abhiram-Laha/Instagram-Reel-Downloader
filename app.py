from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def get_reel_url(instagram_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(instagram_url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to load page")

    print("Instagram HTML content:", response.text)

    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', text=lambda t: t and 'video_url' in t)
    if not script_tag:
        raise Exception("Reel video URL not found")

    match = re.search(r'"video_url":"([^"]+)"', script_tag.string)
    if match:
        return match.group(1).replace("\\u0026", "&")
    else:
        raise Exception("Reel video URL not found")

def download_video(video_url, output_path):
    response = requests.get(video_url, stream=True)
    if response.status_code != 200:
        raise Exception("Failed to download video")

    video_filename = os.path.join(output_path, "reel.mp4")
    with open(video_filename, 'wb') as video_file:
        for chunk in response.iter_content(chunk_size=8192):
            video_file.write(chunk)
    return video_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        instagram_url = request.form['url']
        try:
            print("Instagram URL:", instagram_url)
            reel_url = get_reel_url(instagram_url)
            print("Reel video URL:", reel_url)
            video_path = download_video(reel_url, 'downloads')
            print("Video downloaded successfully:", video_path)
            return send_file(video_path, as_attachment=True)
        except Exception as e:
            return str(e)
    return render_template('index.html')

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
