from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import sys
import os

# detector 폴더를 불러올 수 있도록 경로 추가
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from detector.detector import detect_ad

visited = set()

def crawl(url, results=None):
    if url in visited:
        return

    visited.add(url)
    print("방문:", url)

    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'  # 한글 깨짐 방지
    except Exception as e:
        print(f"크롤링 오류 발생 ({url}): {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    print("=== 불법 광고 탐지 결과 ===")

    # 1. 댓글(.comment) 영역 검사
    comments = soup.find_all(class_ = "comment")
    for comment in comments:
        text = comment.get_text(strip=True)
        result = detect_ad(text)

        print()
        print("내용:", text)
        print("판정:", result)

        if result != "정상" and results is not None:
            results.append({
                "location": f"댓글 ({url})",
                "text": text,
                "category": result
            })

    # 2. 게시글(.post) 영역 검사 (본문 추가!)
    posts = soup.find_all(class_ = "post")
    for post in posts:
        text = post.get_text(strip=True)
        result = detect_ad(text)

        print()
        print("내용:", text)
        print("판정:", result)

        if result != "정상" and results is not None:
            results.append({
                "location": f"게시글 ({url})",
                "text": text,
                "category": result
            })

    # 3. 페이지 안의 링크 찾기 및 재귀 탐색
    links = soup.find_all("a")
    for link in links:
        href = link.get("href")
        if not href:
            continue
        
        full_url = urljoin(url, href)
        print("발견", full_url)

        # 로컬 내부 링크만 재귀 호출
        if "127.0.0.1" in full_url or "localhost" in full_url:
            crawl(full_url, results)

if __name__ == "__main__":
    start_url = "http://127.0.0.1:5500/test_site/index.html"
    visited.clear()
    test_results = []
    crawl(start_url, test_results)