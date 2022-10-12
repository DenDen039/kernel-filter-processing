import cv2 as cv
from cv2 import boxFilter
import numpy as np
from os.path import exists


FILTERS_DIR = "./filters/"
FILTERS_LIST_NAME = "filters"


def GetFilterList() -> list[str]:
    filters_path = FILTERS_DIR+FILTERS_LIST_NAME+".bin"

    if not exists(filters_path):
        return []

    with open(filters_path, 'rb') as file:
        filter_binary = file.read()

    filters = filter_binary.decode("utf-8").split("\n")

    return filters[:len(filters)-1]


def CreateFilter(kernel: np.array, filter_name: str, post_proccesing: int = 0):
    if "." in filter_name or filter_name in GetFilterList():
        raise Exception("bad filter name")

    np.savetxt(FILTERS_DIR+filter_name+".txt", kernel)

    with open(FILTERS_DIR+filter_name+"_post_processing.txt", "w") as file:
        file.write(str(post_proccesing))

    filters_path = FILTERS_DIR+FILTERS_LIST_NAME+".bin"

    with open(filters_path, 'ab') as file:
        file.write((filter_name+"\n").encode('ascii'))

    return filter_name


def LoadFilter(name: str):
    if not name in GetFilterList():
        return Exception("No such filter")

    with open(FILTERS_DIR+name+"_post_processing.txt", "r") as file:
        post_processing = int(file.read())

    return np.genfromtxt(FILTERS_DIR+name+".txt", delimiter=' '), post_processing


def AddFilter(path: str):
    with open(path, "r") as file:
        text = file.read()
        parts = text.split("#")
        kernel = np.fromstring(parts[0], dtype=float, sep=' ')
        kernel = kernel.reshape(
            int(kernel.shape[0]**(1/2)), int(kernel.shape[0]**(1/2)))
        post_processing = int(parts[1])
    return kernel, post_processing


def ApplyFilter(img: np.array, filter_name: str) -> np.array:
    kernel, post_processing = LoadFilter(filter_name)

    norm_img = np.zeros(img.shape)
    res_img = cv.filter2D(img, -1, kernel)+post_processing

    return cv.normalize(res_img, norm_img, 0, 255, cv.NORM_MINMAX)


if __name__ == "__main__":
    boxFilter = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])/9
    gaussFilter = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])/16
    edgeFilter = np.array([[-1, 0, 1], [-1, 0, 1], [1, 0, -1]])
    precisionFilter = np.array([[-1, -2, -1], [-2, 22, -2], [-1, -2, -1]])/10
    embossingFilter =  np.array([[0, 1, 0], [1,0, -1], [0, -1, 0]])
    
    CreateFilter(boxFilter, "Box")
    CreateFilter(gaussFilter, "Gauss")
    CreateFilter(edgeFilter, "Edge")
    CreateFilter(precisionFilter, "Precision")
    CreateFilter(embossingFilter, "Embossing",128)
