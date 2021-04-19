import base64
import json
import re
import urllib

import nltk
from wordcloud import WordCloud

nltk.download('stopwords')
from utils.mysql_er import MySQLConnector
from flask import Flask, render_template

app = Flask(__name__)


def get_stop_words():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    sw_url = "http://xpo6.com/wp-content/uploads/2015/01/stop-word-list.txt"
    req = urllib.request.Request(sw_url, headers=headers)
    response = urllib.request.urlopen(req)
    r = response.read()
    response.close()
    swlist_r = r.decode("UTF-8")
    sw_list = swlist_r.strip().split("\r\n")
    return sw_list

@app.route('/', methods=['GET'])
def index():
    connector = MySQLConnector()
    games = connector.get_games(1, 13)
    connector.close()
    return render_template('index.html', games=games)


@app.route("/game_detail/<id>", methods=["GET"])
def game_detail(id):
    connector = MySQLConnector()
    game = connector.get_game_by_id(id)
    connector.close()
    print("game",game)
    connector = MySQLConnector()
    reviews = connector.get_reviews(id)
    # print("reviews:",reviews)
    connector.close()
    words_frequency = {}
    sw_list = get_stop_words()
    for review in reviews:
        content = review["content"]
        raw_words = re.findall(r'\w+', content)
        # print("raw_words:", raw_words)
        for raw_word in raw_words:
            word = raw_word.lower()
            if word in sw_list or word == "game" or word in re.findall(r'\w+', game["name"].lower()):
                # stopword, ignore
                pass
            else:
                if word in words_frequency:
                    words_frequency[word] += 1
                else:
                    words_frequency[word] = 1

    wordcloud = WordCloud(width = 1000, height = 500, background_color="rgba(255, 255, 255, 0)", mode="RGBA").generate_from_frequencies(words_frequency)
    print("wordcloud")
    wordcloud.to_file("temp.png")
    with open("temp.png", 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode("ascii")
    print(encoded_string)
    return render_template("game_detail.html", game=game, wordcloud=encoded_string)



if __name__ == '__main__':
    app.run()
