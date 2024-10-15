# 3번째 수행

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
import time
from datetime import datetime, timedelta

# OAuth 인증을 위한 Blogger API 설정
SCOPES = ['https://www.googleapis.com/auth/blogger']

# 인증을 위한 함수
def authenticate_blogger():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# 특정 시간대에 예약 게시물을 작성하는 함수
def schedule_post(service, blog_id, title, content, publish_time):
    post_body = {
        'kind': 'blogger#post',
        'title': title,
        'content': content,
        'published': publish_time  # 예약 시간 설정
    }

    post = service.posts().insert(blogId=blog_id, body=post_body).execute()
    print(f"Post scheduled: {post['url']} at {publish_time}")

# JSON 파일에서 번역된 가사와 곡 정보를 로드하여 Blogger에 업로드
def upload_posts_from_json(blog_id, json_filename='translated_songs.json'):
    with open(json_filename, mode='r', encoding='utf-8') as file:
        songs = json.load(file)

    # OAuth 인증
    creds = authenticate_blogger()
    service = build('blogger', 'v3', credentials=creds)

    # 대한민국 시간 기준으로 예약 시간 설정 (1시, 2시 3시, 4시, 5시)
    now = datetime.now()
    publish_times = [
        (now + timedelta(hours=1)).isoformat() + 'Z',  # 대한민국 시간 기준 오전 3시
        (now + timedelta(hours=2)).isoformat() + 'Z',  # 대한민국 시간 기준 오전 3시
        (now + timedelta(hours=3)).isoformat() + 'Z',  # 대한민국 시간 기준 오전 3시
        (now + timedelta(hours=4)).isoformat() + 'Z',  # 오전 4시
        (now + timedelta(hours=5)).isoformat() + 'Z'   # 오전 5시
    ]

    for idx, song in enumerate(songs[:5]):  # 5개의 게시물만 예약 처리
        title = f"{song['아티스트']} - {song['곡명']} (Korean - English, Spanish Translation)"
        content = '<div style="text-align: center;">'

        # 가사: 원본, 영어, 스페인어 한 줄씩 추가
        for original, english, spanish in zip(song['가사'], song['번역된 가사']['영어'], song['번역된 가사']['스페인어']):
            content += f"<p>{original}<br>{english}<br>{spanish}</p><br>"

        content += '</div>'  # 가운데 정렬 끝

        # 예약된 시간에 게시물 작성
        publish_time = publish_times[idx]
        schedule_post(service, blog_id, title, content, publish_time)
        time.sleep(2)  # API 제한을 방지하기 위한 딜레이 설정

if __name__ == '__main__':
    blog_id = 'Blogger 블로그 ID를 여기에 넣으세요'  # Blogger 블로그 ID
    upload_posts_from_json(blog_id)