from flask import Flask, jsonify, request
from textblob import TextBlob
app = Flask(__name__)

@app.get('/health')
def health(): return jsonify({'status':'ok','service':'sentiment-service'})

@app.post('/analyze')
def analyze():
    text = (request.json or {}).get('text','')
    polarity = TextBlob(text).sentiment.polarity
    sentiment = 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'
    return jsonify({'sentiment': sentiment, 'score': round(polarity, 3), 'text': text})

if __name__ == '__main__': app.run(host='0.0.0.0', port=5002)
