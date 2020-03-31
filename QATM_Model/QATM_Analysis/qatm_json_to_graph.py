import json
import statistics
import numpy as np
import argparse
import os, sys
import cv2
import matplotlib.pyplot as plt
from scipy import stats
import warnings
from skimage.transform import resize
from scipy.stats import wasserstein_distance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from skimage.measure import compare_ssim
import argparse
import imutils
from PIL import Image
import qatm_clustering
warnings.filterwarnings('ignore')

##########################################################################################################################################


def min_max_normalize(arr):
    return (arr - np.min(arr)) / np.ptp(arr)

def plot_graph(qatm_score, index, prediction, save_basename , n_clusters):
    plt.figure()
    my_colors = {0:'red',2:'green',1:'blue', 3:'orange'}
    cluster_median = [0,0,0,0]
    cluster_average = [0,0,0,0,0]
    list_for_median_average = [[],[],[],[],[]]
    jump = len(index)//2000
    for i in index:
        list_for_median_average[prediction[i]].append(i)
        #to keep the graph readable, we draw only ~ 2000 dots on the graph
        if not i%jump== 0:
            continue
        plt.scatter(i , qatm_score[i] , color = my_colors.get(prediction[i], 'black'), s=4)

    for cluster in range(n_clusters):
        if len(list_for_median_average[cluster]) == 0:
            continue
        curr_list = np.asarray(list_for_median_average[cluster], dtype=np.float32)
        cluster_average[cluster] = statistics.mean(curr_list)
        cluster_median[cluster] = statistics.median(curr_list)

    for cluster in range(n_clusters):
        if len(list_for_median_average[cluster]) == 0:
            continue
        plt.scatter(cluster_median[cluster], 1.08, marker = "^", color = my_colors.get(cluster, 'black'), s=20)
        plt.scatter(cluster_average[cluster], 0.98, color = my_colors.get(cluster, 'black'), s=20)

    plt.xlabel("Index of matched windows")
    plt.ylabel("QATM rating")
    plt.show()
    plt.savefig("/home/yonif/SimulAI/QATM/" + save_basename + ".png")


def main_run():
    json_file = open("/home/yonif/SimulAI/QATM/all_results.json", "r")
    data = json.load(json_file)
    dir_json= '/home/yonif/SimulAI/QATM/QATM_GOOD_JSON'
    dir_templates = '/home/yonif/SimulAI/QATM/Corrected_Templates'
    path_templates = []
    path_templates.extend([os.path.join(dir_templates, (i[:-5]+".png")) for i in os.listdir(dir_json)])
    for (comparison, real_path) in zip(data["data"], path_templates):
        if len(comparison)<60000:  #for uniformity we look at the template that have 60,000 results and not less
            continue

        dataset = []
        qatm_score = np.zeros(60000)
        real_template = cv2.imread(real_path, 0)

        for i in range(0,  60000):
            path = comparison[i]["path"]
            img = cv2.imread(path,0)
            window = comparison[i]["window"]
            crop_img = img[window[1]:window[3], window[0]:window[2]]
            qatm_score[i] = (comparison[i]["distance"])
            dataset.append(crop_img)

        clustering_object = qatm_clustering.Clustering(dataset, real_path)
        prediction = clustering_object.clustering()
        min_max_qatm_score = min_max_normalize(qatm_score)
        max_in_arr = max(min_max_qatm_score)
        increase_min_max_qatm_score = [max_in_arr-x for x in min_max_qatm_score]

        qatm_score = min_max_normalize(qatm_score)
        index = range(0, len(qatm_score))
        plot_graph(qatm_score, index, prediction , os.path.basename(real_path)[:-4], 4)
        print("done - ", real_path)
        
main_run()