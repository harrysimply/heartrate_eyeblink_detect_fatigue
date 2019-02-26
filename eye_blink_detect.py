#coding=utf-8

import numpy as np


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    """
    每一只眼睛总共有6个坐标，14为眼睛长度，26为眼睛左边高度，3,5为右边高度

    :param eye:
    :return:
    """


    A = euclidean_dist(eye[1], eye[5])
    B = euclidean_dist(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = euclidean_dist(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear
def euclidean_dist(list1,list2):
    # compute and return the euclidean distance between the two
    # points
    return np.linalg.norm(list1 - list2)