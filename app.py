from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from crawler.crawler import crawl, visited

app = Flask(__name__)
CORS(app)

@app.route("/api/detect", methods=["POST"])
def run_detection():
    data = request.get_json()
    start_url = data.get("url")

    if not start_url:
        return jsonify({"error": "URL이 제공되지 않았습니다."}), 400

    visited.clear()
    results = []

    # 팀원분의 크롤러를 호출하면서 결과를 담을 리스트 전달
    try:
        crawl(start_url, results)
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")

    return jsonify({
        "url": start_url,
        "total_violations": len(results),
        "violations": results
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)