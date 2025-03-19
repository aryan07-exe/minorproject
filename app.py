from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer  # Alternative Summarizer
import nltk

nltk.download('punkt')

app = Flask(__name__)

def fetch_news(headline):
    """Fetches news article links from Google News."""
    query = headline.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    news_list = []
    for item in soup.select('div.BNeawe.vvjwJb.AP7Wnd'):
        title = item.get_text()
        link_tag = item.find_parent('a')
        if link_tag:
            link = link_tag['href']
            if link.startswith('/url?q='):
                link = link.split('/url?q=')[1].split('&')[0]  # Extract actual URL
            news_list.append({"title": title, "link": link})

    return news_list[:3]  # Limit to 3 articles for faster processing

def get_article_summary(url):
    """Fetches article content and summarizes it."""
    try:
        article = Article(url)
        article.download()
        article.parse()

        if not article.text:
            print(f"Article text empty for: {url}")
            return "No article content available."

        # Summarize using Sumy
        parser = PlaintextParser.from_string(article.text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, 3)  # Top 3 sentences

        if summary:
            print(f"Summary for {url}:\n", " ".join(str(sentence) for sentence in summary))
            return " ".join(str(sentence) for sentence in summary)
        else:
            print(f"Summarization failed for: {url}")
            return "Summary unavailable."
    
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return "Error summarizing article."

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        headline = request.form['headline']
        news = fetch_news(headline)

        # Extract summaries for each article
        summaries = [get_article_summary(item["link"]) for item in news]

        # Combine all summaries into one paragraph
        final_summary = " ".join(summaries) if summaries else "No summary available."

        return render_template('result.html', headline=headline, news=news, summary=final_summary)
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
