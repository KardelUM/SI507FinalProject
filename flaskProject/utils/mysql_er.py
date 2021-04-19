import mysql.connector


class MySQLConnector:
    def __init__(self):
        self.conn = mysql.connector.connect(user="kardel", password='alksdj1029a', host="localhost", database="SI507")

    def close(self):
        self.conn.close()
    def get_game_by_id(self, id):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM Game WHERE id='{id}';"
        cursor.execute(query)
        print("query:", query)
        game_tuple = cursor.fetchone()
        print("game_tuple:", game_tuple)
        d = {
            "id": game_tuple[0],
            "name": game_tuple[1],
            "content": game_tuple[2],
            "platform": game_tuple[3],
            "releaseDate": game_tuple[4],
            "publisher": game_tuple[5],
            "userScore": game_tuple[6],
            "metaScore": game_tuple[7],
            "user_positive": game_tuple[8],
            "user_mixed": game_tuple[9],
            "user_negative": game_tuple[10],
            "meta_positive": game_tuple[11],
            "meta_mixed": game_tuple[12],
            "meta_negative": game_tuple[13],
        }

        return d
    def get_games(self, start_index, select_num):
        cursor = self.conn.cursor()
        query = "SELECT * FROM Game LIMIT %s OFFSET %s"
        cursor.execute(query, (select_num - 1, start_index))
        games_tuple = cursor.fetchall()
        l = []
        for game_tuple in games_tuple:
            d = {
                "id": game_tuple[0],
                "name": game_tuple[1],
                "content": game_tuple[2],
                "platform": game_tuple[3],
                "releaseDate": game_tuple[4],
                "publisher": game_tuple[5],
                "userScore": game_tuple[6],
                "metaScore": game_tuple[7],
                "user_positive": game_tuple[8],
                "user_mixed": game_tuple[9],
                "user_negative": game_tuple[10],
                "meta_positive": game_tuple[11],
                "meta_mixed": game_tuple[12],
                "meta_negative": game_tuple[13],
            }
            l.append(d)
        return l

    def get_reviews(self, game_id):
        cursor = self.conn.cursor()
        # print("game_id:",game_id)
        query = f"SELECT * FROM review WHERE game_id='{game_id}'"
        # print("query:", query)
        cursor.execute(query)
        games_tuple = cursor.fetchall()
        l = []
        for game_tuple in games_tuple:
            # print("game`_tuple", game_tuple)
            d = {
                "type": game_tuple[1],
                "score": game_tuple[2],
                "date": game_tuple[3],
                "content": game_tuple[4],
                "source": game_tuple[5],
                "game_id": game_tuple[6],
            }
            l.append(d)
        return l
