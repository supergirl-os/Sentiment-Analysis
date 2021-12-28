
g = open('reviews.txt','r',encoding='UTF-8') # What we know!
reviews = list(map(lambda x:x[:-1],g.readlines()))
g.close()

g = open('labels.txt','r',encoding='UTF-8') # What we WANT to know!
labels = list(map(lambda x:x[:-1].upper(),g.readlines()))
g.close()

from collections import Counter
import numpy as np
import time
import sys
import numpy as np


class SentimentNetwork:
    def __init__(self, reviews,labels,min_count = 10,polarity_cutoff = 0.1,hidden_nodes = 10, learning_rate = 0.1):
        np.random.seed(1)
                    ################神经网络的数据预处理#################
        self.pre_process_data(reviews, labels, polarity_cutoff, min_count)
                    ##########神经网络的数据初始化###########
        self.init_network(len(self.review_vocab),hidden_nodes, 1, learning_rate)

                ###################################################
                 #############神经网络的数据预处理函数实现#############
                 ###################################################

    def pre_process_data(self, reviews, labels, polarity_cutoff, min_count):

    ###建立三个计数器分别对正面，负面，所有，进行计数
        positive_counts = Counter()
        negative_counts = Counter()
        total_counts = Counter()

        #对正面评论的单词进行计数
        for i in range(len(reviews)):
            if(labels[i] == 'POSITIVE'):
                for word in reviews[i].split(" "):
                    positive_counts[word] += 1
                    total_counts[word] += 1
        #对负面评价的单词进行计数
            else:
                for word in reviews[i].split(" "):
                    negative_counts[word] += 1
                    total_counts[word] += 1

        ###建立一个比率计数器
        pos_neg_ratios = Counter()

        ###对正面与反面的评论单词的比率进行计数
        ###正面比率大则为正数，反面比率大则为负数
        for term,cnt in list(total_counts.most_common()):
            if(cnt >= 50):
                pos_neg_ratio = positive_counts[term] / float(negative_counts[term]+1)
                pos_neg_ratios[term] = pos_neg_ratio

        for word,ratio in pos_neg_ratios.most_common():
            if(ratio > 1):
                pos_neg_ratios[word] = np.log(ratio)
            else:
                pos_neg_ratios[word] = -np.log((1 / (ratio + 0.01)))

        ###只对出现总次数大于min_count以及比率介于±polarity_cutoff之间的单词进行统计
        review_vocab = set()
        for review in reviews:
            for word in review.split(" "):
                if(total_counts[word] > min_count):
                    if(word in pos_neg_ratios.keys()):
                        if((pos_neg_ratios[word] >= polarity_cutoff) or (pos_neg_ratios[word] <= -polarity_cutoff)):
                            review_vocab.add(word)
                    else:
                        review_vocab.add(word)

        #将词汇表转换为一个列表，这样我们就可以通过索引访问单词。
        self.review_vocab = list(review_vocab)

        # 对单词所对应的标签进行填充
        label_vocab = set()
        for label in labels:
            label_vocab.add(label)

        # 将标签词汇表转换为一个列表，这样我们就可以通过索引访问标签。
        self.label_vocab = list(label_vocab)

        #存储影评和标签词汇数组的大小。
        self.review_vocab_size = len(self.review_vocab)
        self.label_vocab_size = len(self.label_vocab)

        #对索引的影评与标签重新编写字典
        self.word2index = {}
        for i, word in enumerate(self.review_vocab):
            self.word2index[word] = i

        self.label2index = {}
        for i, label in enumerate(self.label_vocab):
            self.label2index[label] = i

            ###################################################
            ##########神经网络的数据初始化的函数实现###############
            ###################################################

    def init_network(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        #输入层、隐藏层、输出层的节点数量
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes

        #学习速率
        self.learning_rate = learning_rate

        #权重初始化
        self.weights_0_1 = np.zeros((self.input_nodes,self.hidden_nodes))
        self.weights_1_2 = np.random.normal(0.0, self.output_nodes**-0.5,
                                                (self.hidden_nodes, self.output_nodes))

        #初始化隐藏层数据
        self.layer_1 = np.zeros((1,hidden_nodes))


    #############标签数字化##############
    def get_target_for_label(self,label):
        if(label == 'POSITIVE'):
            return 1
        else:
            return 0

    ###############激活函数：sigmoid函数################
    def sigmoid(self,x):
        return 1 / (1 + np.exp(-x))

     ###############sigmoid函数的倒数################
    def sigmoid_output_2_derivative(self,output):
        return output * (1 - output)


    ###########################################################
    ###################训练函数代码实现########################
    ###########################################################

    def train(self, training_reviews_raw, training_labels):

    #标记条影评中每个出现的单词，对应在字典中记录下来作为输入层
        training_reviews = list()
        for review in training_reviews_raw:
            indices = set()
            for word in review.split(" "):
                if(word in self.word2index.keys()):
                    indices.add(self.word2index[word])
            training_reviews.append(list(indices))

        # 确保每个影评都有且仅有一个标签与其对应
        assert(len(training_reviews) == len(training_labels))

       #记录预测正确的数量
        correct_so_far = 0

        # 记录时间
        start = time.time()

        #对每条影评学习的循环
        for i in range(len(training_reviews)):

            review = training_reviews[i]
            label = training_labels[i]

            #### 实现前向传播 ####

            # 隐藏层的计算
            self.layer_1 *= 0
            for index in review:
                self.layer_1 += self.weights_0_1[index]

            # 输出层的计算
            layer_2 = self.sigmoid(self.layer_1.dot(self.weights_1_2))

            ### 反向传播的实现 ###

            # 输出误差计算
            layer_2_error = layer_2 - self.get_target_for_label(label)
            layer_2_delta = layer_2_error * self.sigmoid_output_2_derivative(layer_2)

            # 反向传播误差计算
            layer_1_error = layer_2_delta.dot(self.weights_1_2.T)
            layer_1_delta = layer_1_error

            # 更新权重
            self.weights_1_2 -= self.layer_1.T.dot(layer_2_delta) * self.learning_rate

            for index in review:
                self.weights_0_1[index] -= layer_1_delta[0] * self.learning_rate # update input-to-hidden weights with gradient descent step

            # 对预测情况进行判断
            if(layer_2 >= 0.5 and label == 'POSITIVE'):
                correct_so_far += 1
            elif(layer_2 < 0.5 and label == 'NEGATIVE'):
                correct_so_far += 1

            # 对预测以及学习情况进行即时输出
            elapsed_time = float(time.time() - start)
            reviews_per_second = i / elapsed_time if elapsed_time > 0 else 0

            sys.stdout.write("\rProgress:" + str(100 * i/float(len(training_reviews)))[:4] \
                             + "% Speed(reviews/sec):" + str(reviews_per_second)[0:5] \
                             + " #Correct:" + str(correct_so_far) + " #Trained:" + str(i+1) \
                             + " Training Accuracy:" + str(correct_so_far * 100 / float(i+1))[:4] + "%")
            if(i % 2500 == 0):
                print("")
    ###################################################
    ###################测试函数的实现##################
    ###################################################
    def test(self, testing_reviews, testing_labels):

    #用于直接测试的函数，没有train函数的权重更新
        correct = 0
        start = time.time()
        for i in range(len(testing_reviews)):
            pred = self.run(testing_reviews[i])
            if(pred == testing_labels[i]):
                correct += 1

            elapsed_time = float(time.time() - start)
            reviews_per_second = i / elapsed_time if elapsed_time > 0 else 0

            sys.stdout.write("\rProgress:" + str(100 * i/float(len(testing_reviews)))[:4] \
                             + "% Speed(reviews/sec):" + str(reviews_per_second)[0:5] \
                             + " #Correct:" + str(correct) + " #Tested:" + str(i+1) \
                             + " Testing Accuracy:" + str(correct * 100 / float(i+1))[:4] + "%")
    #################################################
    ####################run函数的实现################
    #################################################
    def run(self, review):

    #该函数通过数据的前向传播直接输出预测结果

        self.layer_1 *= 0
        unique_indices = set()
        for word in review.lower().split(" "):
            if word in self.word2index.keys():
                unique_indices.add(self.word2index[word])
        for index in unique_indices:
            self.layer_1 += self.weights_0_1[index]
        layer_2 = self.sigmoid(self.layer_1.dot(self.weights_1_2))
        if(layer_2[0] >= 0.5):
            return "POSITIVE"
        else:
            return "NEGATIVE"


mlp = SentimentNetwork(reviews[:-1000],labels[:-1000],min_count=20,polarity_cutoff=0.8,learning_rate=0.01)
mlp.train(reviews[:-1000],labels[:-1000])

mlp.test(reviews[-1000:],labels[-1000:])