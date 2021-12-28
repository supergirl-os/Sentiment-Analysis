from snownlp import SnowNLP
from snownlp import seg
from snownlp import sentiment
import numpy as np
import csv
import bottleneck as bn
import pandas as pd

path = "../utils/jd.csv"
# path = "../data/test_set.csv"


def test():

    s = SnowNLP(u'屏幕大小很喜欢，清晰度和色彩三星的屏太棒了，一直都用三星手机系统也很上手，从note8换成s21u有种飞的感觉，不愧为一代机皇，谢谢！')
    print(s.sentiments)
    # 文章关键字提取
    text = u'''
    我是一只猪，没有人比我厉害，我是一只猫，最漂亮的猫，我爱吃水果，我爱吃土豆，我喜欢睡大床
    '''
    s = SnowNLP(text)
    s.keywords(4)#提取关键词
    print(s.keywords(4))
    print(s.summary())


def train_snownlp():
    # train
    sentiment.train('../data/neg.csv',
                    '../data/pos.csv')  # 注意路径斜线别写错
    sentiment.save('sentiment1.marshal')
    # test
    q = SnowNLP(u'宝贝真的很不错，，这是我第二次买了，我的朋友都好喜欢，穿上特别漂亮！好性感！质量好好！大爱！')
    print(q.sentiments)


def predict_data(path):
    pre_dic = []
    neg_sample = {}
    neg_score = {}
    pos_sample = {}
    pos_score = {}
    with open(path, 'rt', encoding='GBK') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:

                q = SnowNLP(str(row))
                pre = q.sentiments
                pre_dic.append(pre)
                # print(pre,str(row))
    # with open(path,'r') as f:
    #     red = csv.DictReader(f)     # 通过csv自带的DictReader方法将数据转换成字典表
    #     for row in red:
    #         q = SnowNLP(str(row))
    #         pre = q.sentiments
    #         pre_dic.append(pre)
    #         print(str(row),pre)
    res = np.array(pre_dic)
    mean = np.mean(res)
    N = 3
    pos = -bn.partition(-res, N)[:N]
    # print(pos)
    # print(pos.shape)
    pos_index = bn.argpartition(-res,N)[:N]
    # print(pos_index)
    neg = bn.partition(res,N)[:N]
    # print(neg,neg.shape)
    neg_index = bn.argpartition(res, N)[:N]
    # print(neg_index)
    comment_info = pd.read_csv(path,encoding='GBK')

    pos_sample[0] = comment_info.loc[pos_index[0]-2]['content']  # 最大值
    pos_sample[1] = comment_info.loc[pos_index[1]-2]['content']
    pos_sample[2] = comment_info.loc[pos_index[2]-2]['content']
    neg_sample[0] = comment_info.loc[neg_index[0]-2]['content']  # 最小值
    neg_sample[1] = comment_info.loc[neg_index[1]-2]['content']
    neg_sample[2] = comment_info.loc[neg_index[2]-2]['content']
    print(pos_sample)
    print(neg_sample)
    return pos,pos_sample,neg,neg_sample,mean

# #
# predict_data(path)
# # test()