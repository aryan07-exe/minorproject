from flask import Flask, render_template, request, jsonify
from serpapi import GoogleSearch

app = Flask(__name__)

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# API route to fetch news articles
@app.route('/search', methods=['GET'])
def search_news():
    keyword = request.args.get('q')
    api_key = 'YOUR_API_KEY'  # Replace with your SerpAPI key

    params = {
        "q": keyword,
        "tbm": "nws",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    articles = []
    if 'news_results' in results:
        for item in results['news_results'][:5]:
            articles.append({
                'title': item.get('title'),
                'link': item.get('link')
            })

    return jsonify(articles)

if __name__ == '__main__':
    app.run(debug=True)
