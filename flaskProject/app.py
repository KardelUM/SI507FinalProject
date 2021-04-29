import base64
import json
import os
import re
import urllib

from flask import Flask, render_template, request, jsonify
from flask_restful import reqparse
from wordcloud import WordCloud

from utils.mysql_er import MySQLConnector

app = Flask(__name__)


def parse_arg_from_requests(arg, **kwargs):
    parse = reqparse.RequestParser()
    parse.add_argument(arg, **kwargs)
    args = parse.parse_args()
    return args[arg]


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


@app.route('/', methods=['GET', "POST"])
def index():
    if request.method == 'GET':
        connector = MySQLConnector()
        games = connector.get_games(1, 13)
        connector.close()
        return render_template('index.html', games=games)
    elif request.method == 'POST':
        # AJAX PART
        print("post!")

        start_page = json.loads(request.get_data().decode("utf-8"))["start_index"]
        connector = MySQLConnector()
        games = connector.get_games(start_page, 13)

        connector.close()
        return jsonify(games)


@app.route('/index2', methods=['GET', "POST"])
def index2():
    if request.method == 'GET':

        return render_template('index2.html')
    elif request.method == 'POST':
        # AJAX PART
        print("post!")
        page_index = json.loads(request.get_data().decode("utf-8"))["page_index"]

        if not os.path.exists(os.path.join(os.getcwd(), "cache2")):
            print("created!")
            os.mkdir(os.path.join(os.getcwd(), "cache2"))

        if not os.path.exists(os.path.join(os.getcwd(), "cache2", str(page_index))):
            os.mkdir(os.path.join(os.getcwd(), "cache2", str(page_index)))

            with urllib.request.urlopen(
                    "http://localhost:9080/crawl.json?spider_name=game-spider-main-game&url=https://www.metacritic.com/browse/games/score/userscore/all/filtered?page=" + str(
                        page_index)) as res:
                s = res.read()
            games = json.loads(s)

            print(len(games))
            s = json.dumps(games)
            with open(os.path.join(os.getcwd(), "cache2", str(page_index), "games.json"), 'w+') as gamesJson:
                gamesJson.write(s)

            return jsonify(games)
        else:
            with open(os.path.join(os.getcwd(), "cache2", str(page_index), "games.json"), 'r') as gamesJson:
                s = gamesJson.read()
            games = json.loads(s)
            return jsonify(games)


def generateWCfromReviews(reviews, game):
    words_frequency = {}
    sw_list = get_stop_words()
    for review in reviews:
        content = review["content"]
        raw_words = re.findall(r'\w+', content)
        # print("raw_words:", raw_words)
        for raw_word in raw_words:
            word = raw_word.lower()
            if word in sw_list or word == "game" or word == "like" or word == "love" or word == "play" or word == "great" or word == "good" or word in re.findall(
                    r'\w+', game["name"].lower()) or len(word) == 1:
                # stopword, ignore
                pass
            else:
                if word in words_frequency:
                    words_frequency[word] += 1
                else:
                    words_frequency[word] = 1

    wordcloud = WordCloud(width=1000, height=500, background_color="rgba(255, 255, 255, 0)",
                          mode="RGBA").generate_from_frequencies(words_frequency)
    print("wordcloud")
    wordcloud.to_file("temp.png")
    with open("temp.png", 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode("ascii")
    return encoded_string, words_frequency


@app.route("/game_detail/<id>", methods=["GET"])
def game_detail(id):
    connector = MySQLConnector()
    game = connector.get_game_by_id(id)
    connector.close()
    print("game", game)
    connector = MySQLConnector()
    reviews = connector.get_reviews(id)
    # print("reviews:",reviews)
    connector.close()
    meta_reviews = []
    users_reviews = []
    for review in reviews:
        if review["type"] == "meta":
            meta_reviews.append(review)
        else:
            users_reviews.append(review)
    meta_encoded_string, meta_words_frequency = generateWCfromReviews(meta_reviews, game)
    users_encoded_string, users_words_frequency = generateWCfromReviews(users_reviews, game)
    # print(encoded_string)
    metaHotwords = sorted(meta_words_frequency, key=meta_words_frequency.get, reverse=True)[:5]
    usersHotwords = sorted(users_words_frequency, key=users_words_frequency.get, reverse=True)[:5]
    hotWordsInterestion = list(set(usersHotwords) & set(metaHotwords))
    print(meta_words_frequency)
    print(reviews)
    game["userScore"] = 10 * game["userScore"]
    return render_template("game_detail.html", game=game, meta_wordcloud=meta_encoded_string,
                           users_wordcloud=users_encoded_string, hotwords=hotWordsInterestion)


@app.route("/game_detail2/<url>", methods=["GET"])
def game_detail2(url):
    words_frequency = {}
    original_url = url.split("/")[-1]
    url = url.replace("|", "/")
    print("url:", url)
    print("url:", original_url)
    if not os.path.exists(os.path.join(os.getcwd(), "cache2", "reviews")):
        os.mkdir(os.path.join(os.getcwd(), "cache2", "reviews"))
    if not os.path.exists(os.path.join(os.getcwd(), "cache2", "reviews", original_url + ".json")):
        with urllib.request.urlopen(
                "http://localhost:9080/crawl.json?spider_name=game-detailed-spider&url=" + url) as res:
            s = res.read()
        jsobj = json.loads(s)
        reviews = []
        game = {}
        if jsobj["status"] == "ok":
            for item in jsobj["items"]:
                if "id" in item:
                    game["content"] = item["summary"]
                    game["name"] = item["name"]
                    game["platform"] = item["platform"]
                    game["releaseDate"] = item["releaseDate"]
                    game["publisher"] = item["publisher"]

                    print("hello", item["userScore"] * 10)
                    game["userScore"] = int(float(item["userScore"]) * 10)
                    game["metaScore"] = int(item["metaScore"])
                    game["user_positive"] = item["user_positive"]
                    game["user_mixed"] = item["user_mixed"]
                    game["user_negative"] = item["user_negative"]
                    game["meta_positive"] = item["meta_positive"]
                    game["meta_mixed"] = item["meta_mixed"]
                    game["meta_negative"] = item["meta_negative"]
                else:
                    reviews.append(item)

        meta_reviews = []
        users_reviews = []
        for review in reviews:
            if review["type"] == "meta":
                meta_reviews.append(review)
            else:
                users_reviews.append(review)
        meta_encoded_string, meta_words_frequency = generateWCfromReviews(meta_reviews, game)
        users_encoded_string, users_words_frequency = generateWCfromReviews(users_reviews, game)
        # print(encoded_string)
        metaHotwords = sorted(meta_words_frequency, key=meta_words_frequency.get, reverse=True)[:5]
        usersHotwords = sorted(users_words_frequency, key=users_words_frequency.get, reverse=True)[:5]
        hotWordsIntersection = list(set(usersHotwords) & set(metaHotwords))
        print(meta_words_frequency)
        print(reviews)
        # print(encoded_string)
        d = {'game': game,
             'meta_encoded_string': meta_encoded_string,
             'users_encoded_string': users_encoded_string,
             'hotWordsIntersection': hotWordsIntersection}
        s = json.dumps(d)
        with open(os.path.join(os.getcwd(), "cache2", "reviews", original_url + ".json"), 'w+') as f:
            f.write(s)
        return render_template("game_detail.html", game=game, meta_wordcloud=meta_encoded_string,
                               users_wordcloud=users_encoded_string, hotwords=hotWordsIntersection)


    else:
        with open(os.path.join(os.getcwd(), "cache2", "reviews", original_url + ".json"), 'r') as f:
            s = f.read()
        j = json.loads(s)
        print(j)
        game = j["game"]
        meta_encoded_string = j["meta_encoded_string"]
        users_encoded_string = j["users_encoded_string"]
        hotWordsIntersection = j["hotWordsIntersection"]
        return render_template("game_detail.html", game=game, meta_wordcloud=meta_encoded_string,
                               users_wordcloud=users_encoded_string, hotwords=hotWordsIntersection)


if __name__ == '__main__':
    app.run()
