import streamlit as st
from document_store import NewsAnalyzer
import os
from dotenv import load_dotenv
import base64
import datetime
import re

# 환경 변수 로드
load_dotenv()

def get_base64_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode('utf-8')
    return encoded

# 날짜 형식을 "YYYY년 M월 D일"로 변환하는 함수
def format_date(user_date):
    return datetime.datetime.strptime(user_date, '%Y%m%d').strftime('%Y년 %m월 %d일')

def display_content(analyzer, user_date):
    # 날짜를 포맷된 형식으로 변환
    birthday = format_date(user_date)

    with st.spinner("운세 생성 중..."):
        articles_df = analyzer.get_articles_by_date(user_date)
        if articles_df.empty:
            st.error("해당 날짜의 기사가 없습니다.")
            return
        top_articles = analyzer.get_top_articles(articles_df)
        titles = top_articles['title'].tolist()
        sajupalja = analyzer.generate_sajupalja(titles)

    # 신문 이미지 표시
    image_path = os.path.join('images', f"{user_date}.jpg")
    if os.path.exists(image_path):
        encoded_image = get_base64_file(image_path)
    else:
        default_image_path = os.path.join('images', 'default.png')
        if os.path.exists(default_image_path):
            encoded_image = get_base64_file(default_image_path)
        else:
            st.error("기본 이미지를 찾을 수 없습니다.")
            encoded_image = None

    if encoded_image:
        st.markdown(f"""
        <div style='text-align: center;'>
            <div class="image-container" style='display: inline-block; width: 300px; height: 400px; background-image: url("data:image/png;base64,{encoded_image}"); background-size: cover; animation: breakingNews 0.7s forwards; opacity: 0; overflow: hidden;'>
            </div>
        </div>
        <style>
        @keyframes breakingNews {{
            0% {{
                transform: rotate(0deg) scale(0);
                opacity: 0;
            }}
            50% {{
                opacity: 1;
            }}
            100% {{
                transform: rotate(360deg) scale(1);
                opacity: 1;
            }}
        }}
        .image-container:hover {{
            transform: scale(1.5);
            transition: transform 0.5s ease;
        }}
        </style>
        """, unsafe_allow_html=True)

    # 신문 이미지 애니메이션 시간
    newspaper_animation_duration = 0.7  # seconds

    # 주요 키워드 제목 출력 (신문 이미지 애니메이션이 끝난 후)
    st.markdown(f"""
        <h2 style='text-align: center; font-family: "PyeongChang"; font-size: 3em; animation: fadeInTitle 0.5s forwards; animation-delay: {newspaper_animation_duration}s; opacity: 0;'>
            <span style='color: #ffdd00;'>🔮</span> 
            <span style='background: linear-gradient(to right, #ff77aa, #ffdd00); -webkit-background-clip: text; color: transparent;'>주요 키워드</span>
        </h2>
        <style>
        @keyframes fadeInTitle {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

    # 키워드 애니메이션
    keywords = extract_keywords(sajupalja)

    # 애니메이션 딜레이 계산
    total_delay = newspaper_animation_duration + 0.5  # 신문 이미지와 제목 애니메이션 시간 합계

    animation_delays_css = ""
    for i in range(len(keywords)):
        animation_delay = total_delay + i * 1  # 각 키워드의 애니메이션 딜레이 설정
        animation_delays_css += f".keyword-{i} {{ animation-delay: {animation_delay}s; }}\n"

    # 키워드 HTML 생성
    keywords_html = "<div class='keywords-container'>"
    for i, keyword in enumerate(keywords):
        keywords_html += f"<div class='keyword keyword-{i}'>{keyword}</div>"
    keywords_html += "</div>"

    st.markdown(keywords_html, unsafe_allow_html=True)

    # 키워드 스타일 정의
    st.markdown(f"""
    <style>
    .keywords-container {{
        display: flex;
        justify-content: space-around;
        align-items: center;
        width: 100%;
        margin-bottom: 20px;
    }}
    .keyword {{
        font-size: 2vw;
        font-family: 'Shilla_Culture(B)';
        color: white;
        text-shadow: -2px -2px 0 black, 2px -2px 0 black, -2px 2px 0 black, 2px 2px 0 black;
        opacity: 0;
        animation: keywordAnimation 2s forwards;
    }}
    {animation_delays_css}
    @keyframes keywordAnimation {{
        0% {{
            opacity: 0;
            transform: translateY(50px) scale(5) rotate(0deg);
        }}
        100% {{
            opacity: 1;
            transform: translateY(0) scale(1) rotate(360deg);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # 운세 출력 (키워드 애니메이션이 끝난 후)
    last_keyword_animation_end = total_delay + (len(keywords) - 1) * 1 + 2  # 마지막 키워드 애니메이션 종료 시간
    fortune_delay = last_keyword_animation_end

    st.markdown(f"""
    <div style='background-color: rgba(46, 46, 46, 0.8); padding: 20px; border-radius: 10px; font-size: 1.5em; text-align: center; color: #ffcc00; font-family: "GmarketSans"; animation: fadeInFortune 2s forwards; animation-delay: {fortune_delay}s; opacity: 0;'>
        ✨ {sajupalja} ✨
    </div>
    <style>
    @keyframes fadeInFortune {{
        0% {{ opacity: 0; transform: scale(0.8); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # 주요 기사 표시 (운세 애니메이션이 끝난 후)
    fortune_animation_duration = 2  # 운세 애니메이션 시간
    articles_delay = fortune_delay + fortune_animation_duration

    articles_html = f"""
        <div style='animation: fadeInArticles 1s forwards; animation-delay: {articles_delay}s; opacity: 0;'>
            <hr>
            <h2 style='text-align: center; font-family: "PyeongChang"; font-size: 3em;'>
                <span style='color: #ffdd00;'>📃</span> 
                <span style='background: linear-gradient(to right, #ff77aa, #ffdd00); -webkit-background-clip: text; color: transparent;'>주요 기사</span>
            </h2>
            <ul style='list-style-type: none; padding-left: 0;'>
    """

    for _, row in top_articles.iterrows():
        articles_html += f"<li style='font-family: \"GmarketSans\"; font-size: 1.2em; margin-bottom: 10px;'><a href='{row['url']}' target='_blank' style='color: white; text-decoration: none;'>{row['title']}</a></li>"

    articles_html += """
            </ul>
        </div>
        <style>
        @keyframes fadeInArticles {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        </style>
    """

    st.markdown(articles_html, unsafe_allow_html=True)

def extract_keywords(sajupalja):
    match = re.search(r"주요 키워드:\s*(.*)", sajupalja)
    if match:
        keywords_str = match.group(1)
        keywords = [k.strip() for k in keywords_str.split(',')]
        return keywords[:3]  # 최대 3개의 키워드 반환
    else:
        return ["행운", "기회", "성공"]  # 기본 키워드

def main():
    st.set_page_config(
        page_title="운세 챗봇",
        page_icon="🔮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # 배경 비디오 설정
    video_url = "https://yourdomain.com/path/to/background.mp4"  # 여기에 실제 비디오 URL을 입력하세요.
    st.markdown(f"""
    <style>
    #bg-video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        object-fit: cover;
    }}
    </style>
    <video autoplay muted loop id="bg-video">
        <source src="{video_url}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

    # 폰트 적용
    font_path_pyeongchang = os.path.join('font', 'PyeongChangPeace-Bold.ttf')
    if os.path.exists(font_path_pyeongchang):
        font_base64_pyeongchang = get_base64_file(font_path_pyeongchang)
        font_css_pyeongchang = f"""
        @font-face {{
            font-family: 'PyeongChang';
            src: url("data:font/ttf;base64,{font_base64_pyeongchang}") format('truetype');
        }}
        """
    else:
        font_css_pyeongchang = ""

    font_path_gmarket = os.path.join('font', 'GmarketSansTTFBold.ttf')
    if os.path.exists(font_path_gmarket):
        font_base64_gmarket = get_base64_file(font_path_gmarket)
        font_css_gmarket = f"""
        @font-face {{
            font-family: 'GmarketSans';
            src: url("data:font/ttf;base64,{font_base64_gmarket}") format('truetype');
        }}
        """
    else:
        font_css_gmarket = ""

    font_path_shilla = os.path.join('font', 'Shilla_Culture(B).ttf')
    if os.path.exists(font_path_shilla):
        font_base64_shilla = get_base64_file(font_path_shilla)
        font_css_shilla = f"""
        <style>
        @font-face {{
            font-family: 'Shilla_Culture(B)';
            src: url("data:font/ttf;base64,{font_base64_shilla}") format('truetype');
        }}
        </style>
        """
        st.markdown(font_css_shilla, unsafe_allow_html=True)
    else:
        st.error("Shilla_Culture(B).ttf 폰트 파일을 찾을 수 없습니다.")

    st.markdown(f"""
    <style>
    {font_css_pyeongchang}
    {font_css_gmarket}
    </style>
    """, unsafe_allow_html=True)

    # 운세 확인 여부를 저장하기 위한 상태 변수 설정
    if 'fortune_checked' not in st.session_state:
        st.session_state['fortune_checked'] = False

    if not st.session_state['fortune_checked']:
        # 타이틀 설정
        st.markdown("""
            <h1 style='text-align: center; font-family: "PyeongChang"; font-size: 3em; background: linear-gradient(to right, #ffdd00, #ff77aa); -webkit-background-clip: text; color: transparent;'>
                당신이 태어난 날은?
            </h1>
        """, unsafe_allow_html=True)

        # 캐릭터 이미지와 파티클 효과
        character_path = os.path.join('static', 'character.png')
        if os.path.exists(character_path):
            st.markdown(f"""
            <div style='text-align: center; position: relative; z-index: 2;'>
                <img src='data:image/png;base64,{get_base64_file(character_path)}' style='width:150px; position: relative; z-index: 2;' />
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("character.png 이미지를 찾을 수 없습니다.")

        # 생년월일 입력 폼
        with st.form(key='birth_date_form', clear_on_submit=True):
            st.markdown("<div style='text-align: center; font-size:1.2em; font-family: \"GmarketSans\";'>생년월일을 입력하세요</div>", unsafe_allow_html=True)
            birth_date = st.date_input(
                "생년월일 입력",  # label 추가
                min_value=datetime.date(1995, 1, 1),
                max_value=datetime.date(2021, 12, 31),
                value=datetime.date(2000, 1, 1),
                label_visibility="hidden"  # label 숨기기
            )
            submit_button = st.form_submit_button(label="🔮 운세 확인하기")
            st.markdown("""
            <style>
            .stButton > button {
                width: 100%;
                text-align: center;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'GmarketSans';
            }
            </style>
            """, unsafe_allow_html=True)

        if submit_button:
            st.session_state['birth_date'] = birth_date.strftime('%Y%m%d')
            st.session_state['fortune_checked'] = True
            st.rerun()  # 변경: experimental_rerun() -> rerun()
    else:
        # 운세 출력
        display_content(NewsAnalyzer('data/articles.csv'), st.session_state['birth_date'])

if __name__ == "__main__":
    main()
