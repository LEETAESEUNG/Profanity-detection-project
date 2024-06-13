import sqlite3
import re
from konlpy.tag import Okt

# SQLite3 데이터베이스 연결
def connect_db(db_file):
    print("데이터베이스에 연결 중...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    print("데이터베이스에 연결되었습니다.")
    return conn, cursor

# 형태소 분석 함수
def analyze_text(text):
    print("텍스트 분석 중...")
    okt = Okt()
    morphs = okt.pos(text)
    print("텍스트 분석이 완료되었습니다.")
    print(f"분석된 형태소: {morphs}")
    return morphs

# 새로운 욕설로 추정되는 형태소를 저장하는 함수
def store_new_swearing_morphs_in_db(new_swearing_morphs, cursor):
    print("욕설로 추정되는 형태소 저장 중...")
    if new_swearing_morphs:
        print(f"감지된 새로운 욕설 단어: {new_swearing_morphs}")
    else:
        print("새로운 욕설 단어가 감지되지 않았습니다.")
    for word in new_swearing_morphs:
        print(f"처리 중인 단어: {word}")
        # 단어가 이미 존재하는지 확인
        cursor.execute("SELECT COUNT(*) FROM words WHERE word = ?", (word,))
        count = cursor.fetchone()[0]
        if count == 0:
            print(f"단어 삽입: {word}")
            cursor.execute("INSERT INTO words (word, source) VALUES (?, ?)", (word, 'new_swearing'))
        else:
            print(f"단어 이미 존재: {word}")
    print("욕설로 추정되는 형태소 저장이 완료되었습니다.")

# 변형된 욕설 단어를 감지하는 함수
def detect_variants_of_swearing_words(text, swearing_words, filter_words):
    variants = []
    special_chars = r"!@#$%^&*()_+=-{}[]|:;'<>,.?/~`"
    
    for word in swearing_words:
        # 단어 길이 확인
        if len(word) < 3:
            continue
        
        # 단어 이스케이프 처리
        escaped_word = re.escape(word)
        
        # 정규식을 이용해 변형된 욕설 단어 탐지
        patterns = [
            rf'\b{escaped_word}\b',  # 단어 자체
            rf'\b{escaped_word[0]}[{special_chars}]{escaped_word[1:]}\b',  # 문자 하나로 대체된 형태
            rf'\b{escaped_word[0]}.{escaped_word[1:]}\b',  # 문자 하나와 뒤에 다른 문자가 붙은 형태
            rf'\b{escaped_word[0]}\W{escaped_word[1:]}\b',  # 단어 사이에 특수문자가 포함된 형태
            rf'\b{escaped_word[0]}[\W_]{{0,2}}{escaped_word[1:]}[\W_]{{0,2}}\b',  # 단어 내에 임의의 특수문자가 포함된 형태
            rf'\b{escaped_word[:2]}.{escaped_word[2:]}\b',  # 부분적인 대체
            rf'\b{escaped_word[0]}\W{escaped_word[1]}.{escaped_word[2:]}\b',  # 부분적인 대체
            rf'\b({escaped_word[0]}+|{escaped_word[:2]}+)\b',  # 단어의 반복적인 철자
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # 필터링된 단어 목록에 있는 단어는 제외
                if match.lower() not in filter_words and match.lower() not in swearing_words:
                    # 공백을 포함한 단어는 공백으로 분리해서 개별적으로 처리
                    if ' ' in match:
                        sub_words = match.split()
                        for sub_word in sub_words:
                            if 3 <= len(sub_word) <= 15 and sub_word.lower() not in filter_words and sub_word.lower() not in swearing_words:
                                variants.append(sub_word.lower())
                    else:
                        # 단어의 길이가 3 이상이고 15 이하인 경우에만 추가
                        if 3 <= len(match) <= 15:
                            variants.append(match.lower())
    return variants

if __name__ == "__main__":
    # 데이터베이스 파일 경로 정의
    db_file = "C:/Users/LEETAESEUNG/바탕 화면/자연어처리 기말 프로젝트/data/corpus.db"

    # 데이터베이스 연결
    conn, cursor = connect_db(db_file)

    # 욕설 단어 사전 불러오기
    word_dict_file_path = "C:/Users/LEETAESEUNG/바탕 화면/자연어처리 기말 프로젝트/data/word_dict.txt"
    with open(word_dict_file_path, 'r', encoding='utf-8') as file:
        swearing_words = [line.strip() for line in file if line.strip()]
        print(f"욕설 단어 사전 로드 완료: {len(swearing_words)}개 단어")
        print(f"욕설 단어 목록: {swearing_words}")

    # 필터링할 단어 목록 불러오기
    filter_word_dict_file_path = "C:/Users/LEETAESEUNG/바탕 화면/자연어처리 기말 프로젝트/data/filter_words.txt"
    with open(filter_word_dict_file_path, 'r', encoding='utf-8') as file:
        filter_words = [line.strip() for line in file if line.strip()]
        print(f"필터링할 단어 사전 로드 완료: {len(filter_words)}개 단어")
        print(f"필터링 단어 목록: {filter_words}")

    # posts 테이블에서 content 컬럼의 값을 가져와서 분석
    cursor.execute("SELECT content FROM posts LIMIT 5000 OFFSET 50000")
    contents = cursor.fetchall()
    print(f"{len(contents)}개의 텍스트를 가져왔습니다.")
    for idx, content in enumerate(contents, start=1):
        print(f"텍스트 {idx} 분석 중...")
        text = content[0]
        morphs = analyze_text(text)

        # 새로운 욕설 감지
        new_swearing_morphs = detect_variants_of_swearing_words(text, swearing_words, filter_words)
        store_new_swearing_morphs_in_db(new_swearing_morphs, cursor)

    try:
        # 커밋이 제대로 완료되었는지 확인
        conn.commit()
        print("데이터베이스에 새로운 욕설로 추정되는 형태소를 저장했습니다.")
    except Exception as e:
        print(f"데이터베이스 커밋 중 오류 발생: {e}")
        raise
    finally:
        # 연결 닫기
        conn.close()
