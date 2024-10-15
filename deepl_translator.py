# 2번째 수행

import requests
import json
import time
import os

# DeepL API 키 설정
DEEPL_API_KEY = 'DEEPL_API_KEY를 여기에 넣으세요'

# DeepL API를 사용한 번역 함수
def translate_text(text, target_language):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        'auth_key': DEEPL_API_KEY,
        'text': text,
        'target_lang': target_language
    }
    
    response = requests.post(url, data=params)

    if response.status_code != 200:
        print(f"Error: Failed to get a valid response. Status code: {response.status_code}")
        return f"Error: Unable to translate. Status code {response.status_code}"

    try:
        result = response.json()
        return result['translations'][0]['text']
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return "Error: Failed to decode JSON"

# JSON 파일에서 곡 데이터 로드
def load_songs_from_json(filename='melon_songs.json'):
    with open(filename, mode='r', encoding='utf-8') as file:
        return json.load(file)

# 번역된 가사를 JSON 파일에 저장하는 함수
def save_translated_songs_to_json(data, filename='translated_songs.json'):
    # 파일이 존재하지 않으면 생성하고 빈 리스트를 저장
    if not os.path.exists(filename):
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    # 기존 파일에 데이터 추가
    with open(filename, mode='r+', encoding='utf-8') as file:
        try:
            existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = []

        existing_data.append(data)

        # 파일의 처음으로 돌아가서 다시 덮어쓰기
        file.seek(0)
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# 곡 2개 번역 처리
def translate_two_songs(songs):
    batch = []
    
    for i, song in enumerate(songs[:5]):  # 곡 5개만 번역 처리
        original_lyrics = song['가사']
        
        # DeepL API를 이용해 영어 및 스페인어로 번역
        translated_english_lyrics = [translate_text(line, 'EN') for line in original_lyrics]
        translated_spanish_lyrics = [translate_text(line, 'ES') for line in original_lyrics]
        
        # 번역된 가사를 song 데이터에 추가
        song['번역된 가사'] = {
            '영어': translated_english_lyrics,
            '스페인어': translated_spanish_lyrics
        }
        
        # 배치에 추가
        batch.append(song)
        
        # 번역이 완료될 때마다 콘솔에 메시지 출력
        print(f"{song['곡명']} complete")

        time.sleep(1)  # DeepL API 요청 간의 딜레이

    # 번역된 곡 2개를 JSON 파일에 저장
    for s in batch:
        save_translated_songs_to_json(s)
    print("songs processed and saved.")

# 실행 부분
if __name__ == '__main__':
    # JSON 파일을 미리 생성 (파일이 없을 경우)
    if not os.path.exists('translated_songs.json'):
        with open('translated_songs.json', mode='w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        print("translated_songs.json 파일이 생성되었습니다.")

    # JSON 파일에서 곡 데이터 로드
    songs = load_songs_from_json()
    
    # 곡 2개 번역 처리
    translate_two_songs(songs)