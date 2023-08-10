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



#* 메인화면
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