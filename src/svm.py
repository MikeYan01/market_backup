#coding=utf-8
from sklearn.externals import joblib
from sklearn.svm import SVC
# 卡方特征词选择算法
class ChiSquare:
    def __init__(self, train_data, train_labels):
        self.all_dict, self.pos_dict, self.neg_dict = {}, {}, {} # 单词 ==> 单词出现次数
        self.words_ChiSquare = {}

        for i, data in enumerate(train_data):
            for word in data:
                self.all_dict[word] = self.all_dict.get(word, 0) + 1
                if train_labels[i] == 1:
                    self.pos_dict[word] = self.pos_dict.get(word, 0) + 1

        total_pos_freq = sum(self.pos_dict.values())
        total_freq = sum(self.all_dict.values())
        for each_word, freq in self.all_dict.items():
            value = self.func(self.pos_dict.get(each_word, 0), freq, total_pos_freq, total_freq)
            self.words_ChiSquare[each_word] = value

    # 单词出现在正文档频率n11、某单词出现在负文档频率n10、某单词不出现在正文档频率n01、某单词不出现在负文档频率n00
    # 某单词在正文档中出现频率word_pos_freq，某单词总频率word_freq，正文档总频率total_pos_freq, 总频率total_freq
    # ChiSquare计算公式
    @staticmethod
    def func(word_pos_freq, word_freq, total_pos_freq, total_freq):
        n11 = word_pos_freq
        n10 = word_freq - word_pos_freq
        n01 = total_pos_freq - word_pos_freq
        n00 = total_freq - n11 - n01 - n10
        return total_freq * (float((n11*n00 - n01*n10)**2) / ((n11 + n01) * (n11 + n10) * (n01 + n00) * (n10 + n00)))

    # 将每个词按照chi square值从大到小排序，选取前k个值作为特征
    def get_features(self, k): 
        words = sorted(self.words_ChiSquare.items(), key=lambda d: d[1], reverse=True)
        return [word[0] for word in words[:k]]
        

class SVM:
    def __init__(self, features):
        self.features = features

    # 单词转向量
    def words2vec(self, all_data):
        index = {} # 特征词 ==> 特征词位置
        for i, word in enumerate(self.features):
            index[word] = i

        # 录入每一条数据后，向量的变化情况
        all_vecs = []
        for data in all_data:
            vec = [0 for each in range(len(self.features))]
            for word in data:
                i = index.get(word)
                if i is not None:
                    vec[i] += 1
            all_vecs.append(vec)
        return all_vecs

    # 训练函数
    def train(self, train_data, train_labels, C):
        self.svc = SVC(C=C)
        train_vec = self.words2vec(train_data)
        self.svc.fit(train_vec, train_labels)
        joblib.dump(self.svc, "../model/train_model.pkl")

    # 预测
    def predict(self, test_data):
        # self.svc = joblib.load("../model/train_model.pkl")
        vec = self.words2vec([test_data])
        result = self.svc.predict(vec)
        return result[0]