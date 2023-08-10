from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify

# 로그인에 필요한 라이브러리를 가져옵니다.
import jwt
import datetime


# 시크릿 키 - JWT 토큰을 생성하거나 검증할 때 사용됩니다.
SECRET_KEY = "team8key"

app = Flask(__name__)
client = MongoClient(
    'mongodb+srv://sparta:test@cluster0.orw6l7l.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# /register url에 POST 요청이 들어오면 아래 함수를 작동


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

# 회원가입시 데이터 베이스에 저장


@app.route('/register', methods=['POST'])
def register_user():
    # fetch를 통해 register.html에서 날라온 데이터를 user info에 저장 후  각각의 변수에 담아 검사합니다.
    user_info = request.json
    print(user_info)
    username = user_info['username']
    password = user_info['password']
    email = user_info['email']

    if db.users.find_one({'username': username}):
        return jsonify({'msg': '이미 있는 닉네임 입니다.'}), 400

    user_info = {
        'username': username,
        'password': password,
        'email': email
    }

    db.users.insert_one(user_info)
    return jsonify({'msg': '회원가입을 축하드려요!'})


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_user():
    user_info = request.json
    username = user_info['username']
    password = user_info['password']

    user = db.users.find_one({'username': username})
#   if 문으로 유저가 없는 경우를 먼저 에러 처리해줬으면 좋지 않았을까
    if user and user['password'] == password:
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)

        }, SECRET_KEY)

        return jsonify({'msg': '로그인 성공', 'token': token})
    else:
        return jsonify({'msg': '로그인 실패'})


@app.route('/')
def home():
    return render_template('index.html')

# @app.route("/movie", methods=["POST"])
# def movie_post():

#     sample_url = request.form['sample_url']
#     sample_comment = request.form['sample_comment']
#     sample_star = request.form['sample_star']

#     URL = sample_url
#     headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
#     data = requests.get(URL,headers=headers)
#     soup = BeautifulSoup(data.text, 'html.parser')
#     ogtitle = soup.select_one('meta[property="og:title"]')['content']
#     ogimage = soup.select_one('meta[property="og:image"]')['content']
#     ogdesc = soup.select_one('meta[property="og:description"]')['content']

#     moive = {
#         'title' : ogtitle,
#         'image' : ogimage,
#         'description' : ogdesc,
#         'comment' : sample_comment,
#         'star' : sample_star
#     }
#     db.movies2.insert_one(moive)


#     return jsonify({'msg':'저장 완료!'})

# @app.route("/movie", methods=["GET"])
# def movie_get():
#     all_moives = list(db.movies2.find({},{'_id':False}))
#     return jsonify({'result': all_moives })

@app.route("/api/reviews", methods=["GET"])
def reviews_get():
    all_reviews = list(db.review.find({}, {'_id': False}))
    print(all_reviews)
    return jsonify({'reviews': all_reviews})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
