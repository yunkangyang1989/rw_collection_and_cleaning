"""
v1 version of clustering helper tools for political bias paper
"""
import pandas as pd
import requests
import datetime
from bs4 import BeautifulSoup
import os
# import newspaper
import tqdm
import operator
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.cluster import KMeans
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


def tf_idf(data_frame, description):
    """
    method to add convert articles into tf_idf vectors
    :param data_frame: input data frame
    :param description:
    :return: output data frame
    """
    text = list(data_frame['article'])
    vectorizer = TfidfVectorizer(stop_words='english')  # create the transform
    vectorizer.fit(text)  # tokenize and build vocab
    # save tf_idf vectorizer as pickle
    with open('resources/tf-idf_encoder_' + description + '.pkl', 'wb') as f:
        pickle.dump(vectorizer.vocabulary_, f)
    f.close()
    data_frame['tf-idf'] = data_frame['article'].apply(lambda x: vectorizer.transform([x]))
    return data_frame


def bow(data_frame, description):
    """
    method to add convert articles into bag of wordds vectors
    :param data_frame: input data frame
    :param description:
    :return: output data frame
    """
    text = list(data_frame['article'])
    vectorizer = CountVectorizer(stop_words='english')  # create the transform
    vectorizer.fit(text)      # tokenize and build vocab
    # save bow vectorizer as pickle
    with open('resources/bow_encoder_' + description + '.pkl', 'wb') as f:
        pickle.dump(vectorizer.vocabulary_, f)
    f.close()
    data_frame['bow'] = data_frame['article'].apply(lambda x: vectorizer.transform([x]))
    return data_frame


def sparse_matrix_to_array(data_frame, sparse_column):
    """
    transform tf-idf or bow from sparse matrix to array and store in np array
    :param data_frame:
    :param sparse_column: the name of the tf-idf or bow column
    :return:
    """
    array = data_frame[[sparse_column]]
    array[sparse_column] = array[sparse_column].apply(lambda x: x.toarray())
    array[sparse_column] = array[sparse_column].apply(lambda x: x[0])
    array = np.stack(array[sparse_column].values, axis=0)  # over write array df as an np array
    return array


def k_means_clustering(data, cluster_array, data_frame, v_type, description):
    """

    :param data:
    :param cluster_array:
    :param data_frame:
    :param v_type:
    :param description:
    :return:
    """
    for c in cluster_array:
        k_means = KMeans(n_clusters=c, random_state=0).fit(data)
        type_name = v_type + '_kmeans_cluster_' + str(c)
        data_frame[type_name] = k_means.labels_
        name = 'resources/' + description + '_' + v_type + "_cluster_centers_" + str(c) + ".pkl"
        df = pd.DataFrame(columns=['cluster', 'center_mean'])
        for idx, val in enumerate(k_means.cluster_centers_):
            print('Working on K:', str(val))
            df.loc[idx] = [idx, val]
        df.to_pickle(name)
    return data_frame


def return_top_tfidf_words(tfidf_dict, encoder):
    """
    top 30 on entire corpus
    :param tfidf_dict:
    :return:
    """
    load = open('resources/' + encoder, 'rb')
    encoder = pickle.load(load)
    load.close()
    encoder = dict([[v, k] for k,v in encoder.items()])
    top_30_idx = np.argsort(tfidf_dict)[-30:]
    result = {}
    for idx in top_30_idx:
        result[encoder[idx]] = tfidf_dict[idx]
    return result


def return_top_tfidf_words_array(array, encoder):
    """
    top 30 on entire corpus
    :param array:
    :return:
    """
    load = open('resources/' + encoder, 'rb')
    encoder = pickle.load(load)
    load.close()
    tfidf_dict = {}
    encoder = dict([[v, k] for k,v in encoder.items()])
    for idx, a in enumerate(array):
        tfidf_dict[encoder[idx]] = a
    sorted_dict = sorted(tfidf_dict.items(), key=operator.itemgetter(1))
    return sorted_dict[-30:]


def top_words(data_frame, column, encoder):
    """

    :param data_frame:
    :param column:
    :param encoder:
    :return:
    """
    result_list = []
    for i in range(len(data_frame)):
        result_list.append(return_top_tfidf_words(data_frame[column][i], encoder))
    data_frame['results_for_tfidf'] = result_list
    return data_frame


def combine_on_source(data_frame):
    temp = dict(data_frame['media_site'].value_counts())
    df = pd.DataFrame(columns=['media_site', 'article', 'number_or_articles', 'list_of_urls', 'num_grams'])
    for k, v in temp.items():
        if v>2:
            tf = data_frame[data_frame['media_site'] == k]
            art = ''
            for a in list(tf['article']):
                art += a + ' '
            list_urls = list(tf['url'])
            num = len(art.split(" "))
            df.loc[len(df)] = (k, art, v, list_urls, num)
    return df


