import requests as requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://kyungrin:1234@cluster0.ylo6hsh.mongodb.net/?retryWrites=true&w=majority')
db = client.project

@app.route('/')
def home():
    return render_template('index.html')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.sharedit.co.kr/seminars', headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')

seminars = soup.select('#index_list > section > div > div > div > ul > li')

for seminar in seminars:
    title = seminar.select_one('header > strong > a').text
    time = seminar.select_one('dl > dd:nth-child(2)').text
    image = seminar.find('figure').attrs['style']
    im = image.split('//')[1]
    if im.find('opacity') == -1:
        ima = im[0:-3]
    else:
        ima = im[0:-15]
    url = seminar.select_one('header > strong > a')['href']
    link = url.split('/')[2]
    place = seminar.select_one('dl > dd:nth-child(4)')
    if place is not None:
        a = place.text
        if a.find('댓') == -1:
            doc = {
                'title': title,
                'time': time,
                'place': a,
                'link': link,
                'image': ima
            }
        else:
            doc = {
                'title': title,
                'time': time,
                'place': '웹 세미나',
                'link': link,
                'image': ima
            }
    if place is None:
        doc = {
            'title': title,
            'time': time,
            'place': '웹 세미나',
            'link': link,
            'image': ima
        }

    db.seminar.delete_one(doc)
    db.seminar.insert_one(doc)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/seminar", methods=["GET"])
def seminar_get():
    seminar_list = list(db.seminar.find({}, {'_id': False}))
    return jsonify({'smn_list':seminar_list})

# 세미나에 저장되어있는 데이터에서 link값을 가져와서 url 뒤에 붙여줌
@app.route('/detail/<link>')
def view(link):
    return render_template('detail.html')

# 댓글이 등록되면 DB로 등록해줌
@app.route("/detail", methods=["POST"])
def comment_post():

    link_receive = request.form['link_give']
    name_receive = request.form['name_give']
    grade_receive = request.form['grade_give']
    comment_receive = request.form['comment_give']

    doc = {
        'link':link_receive,
        'name':name_receive,
        'grade':grade_receive,
        'comment':comment_receive
    }
    db.comments.insert_one(doc)

    return jsonify({'msg': '댓글 등록 완료'})


@app.route("/detail", methods=["GET"])
def com_get():
    comment_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': comment_list})

@app.route("/info", methods=["GET"])
def comment_get():
    seminar_info = list(db.seminar.find({}, {'_id': False}))
    return jsonify({'seminar': seminar_info})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
