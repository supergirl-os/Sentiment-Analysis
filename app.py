from flask import Flask, render_template, request, redirect, url_for, session
from wtforms import Form, TextAreaField, validators
from svm.train_svm import svm_predict
from wsgiref.simple_server import make_server
from utils.Crawl_jd import spider_jd
from train.train_model import predict_data
from train.generate_advice import Generator
from gevent import pywsgi

# from lstm.lstm_test import lstm_predict_single

app = Flask(__name__)
app.config["SECRET_KEY"] = 'TPmi4aLWRbyVq8zu9v82dWYW1'


@app.route('/')
@app.route('/index', methods=['POST', 'get'])
def index():
    form = ReviewForm(request.form)
    return render_template('index.html', form=form)


@app.route('/welcome', methods=['POST', 'get'])
def welcome():
    # 首页，进行商品链接的搜索
    if request.json:
        # 对传回的数据进行处理，存入数据库
        data = request.json
        catcher = spider_jd(data)
        catcher.start_request()
        image = catcher.get_image()
        name = catcher.get_name()
        session['image'] = image
        session['name'] = name
        print(image)
        print(data)
        return redirect(url_for('result'))
    return render_template('welcome.html')


@app.route('/result')
def result():
    path ="utils/jd.csv"
    image = session.get('image')
    name = session.get('name')
    # if not image:
    #     image = "../static/images/good.png"
    pos, pos_sample, neg, neg_sample, mean = predict_data(path)
    good = Generator(mean + 0.2,path)
    summary = good.generate()
    return render_template('result.html', image=image, name=name, summary=summary, pos_0=pos[0], pos_1=pos[1],
                           pos_2=pos[2], neg_0=neg[0], neg_1=neg[1], neg_2=neg[2], pos_sample_0=pos_sample[0],
                           pos_sample_1=pos_sample[1], pos_sample_2=pos_sample[2], neg_sample_0=neg_sample[0],
                           neg_sample_1=neg_sample[1], neg_sample_2=neg_sample[2],mean=mean)


@app.route("/main", methods=['POST', 'get'])
def main():
    form = ReviewForm(request.form)
    if request.method == "POST" and form.validate():
        # 获取表单提交的评论
        review_text = request.form["review"]
        res = svm_predict(review_text)

        # 将分类结果返回给界面进行显示
        return render_template("reviewform.html", review=review_text, label=res)
    return render_template("index.html", form=form)


class ReviewForm(Form):
    review = TextAreaField("", [validators.DataRequired()])


if __name__ == '__main__':
    server = make_server('127.0.0.1', 5000, app)
    server.serve_forever()
    app.run(debug=True)
