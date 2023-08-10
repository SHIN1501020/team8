# import requests
from flask import Flask, render_template, request, jsonify
from bson.objectid import ObjectId
import jwt
from pymongo import MongoClient


# SECRET_KEY = user_key
app = Flask(__name__)
client = MongoClient('sparta:test@cluster0.yxb3ggu.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# 시크릿 키 - JWT 토큰을 생성하거나 검증할 때 사용됩니다.
SECRET_KEY = "team8key"

app = Flask(__name__)
client = MongoClient(
    'mongodb+srv://sparta:test@cluster0.yxb3ggu.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta



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



#*메인화면
@app.route('/')
def home():
    return render_template('index.html')


#* 전체 리뷰 조회
@app.route("/api/reviews", methods=["GET"])
def reviews_get():
    all_reviews = list(db.review.find({}))
    for a in all_reviews:
            a['_id'] = str(a['_id'])#ObjectId Class을 str로 변경
    return jsonify({'reviews': all_reviews })


#* 리뷰 삭제
@app.route("/api/reviews/delete", methods=["POST"])
def reviews_delete():
    #현재 로그인 사용자 토근값
    review_token = request.form['review_token']#현재 사용자 토근값 전달
    token_user = jwt.decode(review_token, SECRET_KEY, algorithms=['HS256'])#토큰 디코드
    user = token_user['user']#현재 사용자의 username

    #review table '_id' 값
    review_id = request.form['review_id']

    #'_id' 값과  'wirte_usr'(현재 사용자 username)이 같다면 delete
    result = db.review.delete_one({
            '_id':ObjectId(review_id),
            'write_user':user})
    
    if(result.deleted_count == 1) :
        return jsonify({'reviews': "삭제 완료!" })
    else :
        return jsonify({'reviews': "삭제 권한이 없습니다." })


#* 리뷰 id별로 수정 페이지 이동(flask 동적 라우팅)
@app.route("/api/reviews/<id>", methods=["GET"])
def reviews_update_page(id):
    return render_template('review_form.html', id=id)


#* 리뷰 id별로 데이터 조회
@app.route("/api/reviews/<id>/update_form", methods=["GET"])
def reviews_update_form(id):
    #ObjectId Class type -> string으로 변환
    review = db.review.find_one({'_id':ObjectId(id)})
    review['_id'] = str(review['_id'])
    return jsonify({'review': review })


#* 리뷰 데이터 수정(update)
@app.route("/api/reviews/<id>/update", methods=["POST"])
def reviews_update(id):
    #현재 로그인 사용자 토큰값
    review_token = request.form['review_token']
    token_user = jwt.decode(review_token, SECRET_KEY, algorithms=['HS256'])
    user = token_user['user']
    
    review_title = request.form['review_title']
    review_author = request.form['review_author']
    review_description = request.form['review_description']
    review_star = request.form['review_star']
    review_comment = request.form['review_comment']

    #'_id' 값과  'wirte_usr'(현재 사용자 username)이 같다면 update
    result = db.review.update_one({'_id':ObjectId(id), 'write_user':user}, {'$set' : {'title' : review_title,
        'author' : review_author,
        'description' : review_description,
        'star' : review_star,
        'comment' : review_comment}                                           
    })
    
    if(result.matched_count == 1):
         return jsonify({'review': "수정 완료!" })
    else :
        return jsonify({'review': "수정 권한이 없습니다!" })

   


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)