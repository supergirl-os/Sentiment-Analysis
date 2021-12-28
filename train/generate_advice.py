import csv
import pandas as pd
import numpy as np
from snownlp import SnowNLP
from snownlp import seg
from snownlp import sentiment

path = "../utils/jd.csv"
# path = "../data/test_set.csv"

class Generator:
    def __init__(self, mean,path):
        self.criterion = mean
        self.path = path

    def get_content(self):
        content = []
        with open(self.path, 'rt', encoding='GBK') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                q = SnowNLP(str(row))
                pre = q.sentiments
                if np.abs(pre-self.criterion) < 1e-2:
                    content.append(str(row))
                    if len(content)>5:
                        return content
        return content

    def generate(self):
        content = self.get_content()
        data = ' '.join(content)
        if self.criterion <0.7:
            summary = "商品可信度较低，不建议购买"
        else:
            summary = "商品可信度较高，建议购买"
        # print(data)
        # s = SnowNLP(data)
        # s.keywords(4)  # 提取关键词
        # # print(s.keywords(4))
        # print(s.summary(3))
        return summary


