import pandas as pd
import os
from dotenv import load_dotenv
import openai

# 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class NewsAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = pd.read_csv(data_path)
        # write_date를 'YYYYMMDD' 형식의 문자열로 변환
        self.data['write_date'] = pd.to_datetime(self.data['write_date']).dt.strftime('%Y%m%d')
        # title 열의 결측값을 빈 문자열로 대체하여 길이를 계산할 수 있게 함
        self.data['title'] = self.data['title'].fillna("")
        self.data['title_length'] = self.data['title'].apply(len)

    def get_articles_by_date(self, date_str):
        """입력된 날짜의 기사들을 반환합니다."""
        articles = self.data[self.data['write_date'] == date_str]
        return articles[['title', 'url', 'title_length']]

    def get_top_articles(self, articles_df, top_k=3):
        """기사 DataFrame에서 상위 top_k개의 기사를 반환합니다."""
        # 제목 길이로 내림차순 정렬하여 상위 top_k개 선택
        top_articles = articles_df.sort_values(by='title_length', ascending=False).head(top_k)
        return top_articles

    def generate_sajupalja(self, titles):
        """기사 제목들을 바탕으로 운세를 생성합니다."""
        combined_titles = ' '.join(titles)
        prompt = f"""
당신은 무속인입니다. 다음의 기사 제목들을 참고하여 해당 날짜에 태어난 사람의 운세와 주요 키워드를 아래 템플릿에 맞춰 작성해주세요.

[템플릿]
주요 키워드: [3개의 키워드 나열]
운세: [키워드와 연관지은 운세]

기사 제목들: {combined_titles}

주요 키워드 및 운세:
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "당신은 전문 사주 해설가입니다. 항상 템플릿에 맞춰 간결하게 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # 응답 길이 제한
            temperature=0.7,
        )
        sajupalja = response['choices'][0]['message']['content'].strip()
        return sajupalja

# 사용 예시 (필요 시 제거 가능)
if __name__ == "__main__":
    analyzer = NewsAnalyzer('data/articles.csv')
    user_date = input("생년월일을 YYYYMMDD 형식으로 입력하세요: ")
    articles_df = analyzer.get_articles_by_date(user_date)
    if articles_df.empty:
        print("해당 날짜의 기사가 없습니다.")
    else:
        top_articles = analyzer.get_top_articles(articles_df, top_k=3)
        print(f"\n[{user_date}의 가장 중요한 기사 3개]")
        for idx, row in top_articles.iterrows():
            print(f"{idx+1}. {row['title']} - {row['url']}")
        titles = top_articles['title'].tolist()
        sajupalja = analyzer.generate_sajupalja(titles)
        print("\n[운세]")
        print(sajupalja)
