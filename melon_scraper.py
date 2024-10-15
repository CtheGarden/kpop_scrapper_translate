#  1번째 수행

# melon_scraper.py

import requests
from lxml import html
import json
import time

# 개별 곡 상세 페이지에서 가사 스크래핑하는 함수 (한 줄씩 처리)
def scrape_song_lyrics(song_id):
    base_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    # 곡 상세 페이지 요청
    response = requests.get(base_url, headers=headers)
    tree = html.fromstring(response.content)

    # 가사 추출 (가사 부분을 한 줄씩 추출)
    lyrics = tree.xpath('//div[@id="d_video_summary"]/text() | //div[@id="d_video_summary"]/br/following-sibling::text()')
    lyrics = [line.strip() for line in lyrics if line.strip()] if lyrics else ['가사 없음']

    return lyrics

# 검색 결과 페이지에서 곡 정보(곡명, 아티스트, 가사)를 스크래핑하는 함수
def scrape_song_data_from_page(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    
    # 페이지 요청
    response = requests.get(page_url, headers=headers)
    tree = html.fromstring(response.content)

    # 곡 정보 추출
    song_data = []
    
    # 모든 곡의 정보를 가져오기
    for row in tree.xpath('//tr'):
        try:
            # 곡명 추출 (title 속성에서 곡명을 가져옴)
            song_title = row.xpath('.//a[@class="fc_gray"]/@title')
            song_title = song_title[0].strip() if song_title else 'Unknown'

            # 아티스트 추출
            artist_name = row.xpath('.//div[@id="artistName"]//a/text()')
            artist_name = artist_name[0].strip() if artist_name else 'Unknown'

            # 곡 ID 추출
            song_id = row.xpath('.//input[@name="input_check"]/@value')
            song_id = song_id[0].strip() if song_id else None

            # 곡 ID가 있으면 가사 추출
            if song_id:
                lyrics = scrape_song_lyrics(song_id)
            else:
                lyrics = ['가사 없음']

            song_data.append({
                '곡명': song_title,
                '아티스트': artist_name,
                '가사': lyrics
            })

            # 서버 부하 방지를 위한 딜레이
            time.sleep(1)

        except Exception as e:
            print(f"Error processing song entry: {e}")
            continue

    return song_data

# JSON 파일로 저장하는 함수
def save_to_json(data, filename='melon_songs.json'):
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 실행 부분
if __name__ == '__main__':
    page_url = 'https://www.melon.com/search/song/index.htm?q=%EB%B8%94%EB%9E%99%ED%95%91%ED%81%AC&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType=#params%5Bq%5D=%25EB%25B8%2594%25EB%259E%2599%25ED%2595%2591%25ED%2581%25AC&params%5Bsort%5D=hit&params%5Bsection%5D=all&params%5BsectionId%5D=&params%5BgenreDir%5D=&po=pageObj&startIndex=101'
    
    # 곡 정보 스크래핑
    all_songs = scrape_song_data_from_page(page_url)
    
    # 모든 곡 정보를 JSON 파일로 저장
    save_to_json(all_songs)

    print(f"곡 정보가 'melon_songs.json' 파일로 저장되었습니다.")
