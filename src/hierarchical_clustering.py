from math import sqrt
from numpy import corrcoef, mean
from PIL import Image, ImageDraw
from random import random
from itertools import combinations


def readfile(filename):
    lines = [line for line in open(filename, 'r')]
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:

        p = line.strip().split('\t')
        if p[0] in '0123456789':
            continue
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])

    return rownames, colnames, data


def pearson(v1, v2):
    return 1 - corrcoef(v1, v2)[0, 1]


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.id) + ' ' + str(self.distance)


def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1
    clust = [bicluster(row, id=i) for i, row in enumerate(rows)]
    while len(clust) > 1:
        lowestpair = clust[0], clust[1]

        closest = distance(clust[0].vec, clust[1].vec)

        for clusti, clustj in combinations(clust, 2):
            if (clusti.id, clustj.id) not in distances:
                distances[(clusti.id, clustj.id)] = distance(clusti.vec, clustj.vec)

            d = distances[(clusti.id, clustj.id)]
            if d < closest:
                closest = d
                lowestpair = clusti, clustj

        mergevec = [(v1 + v2) / 2 for v1, v2 in zip(lowestpair[0].vec, lowestpair[1].vec)]

        # create the new cluster
        newcluster = bicluster(mergevec,
                               left=lowestpair[0],
                               right=lowestpair[1],
                               distance=closest,
                               id=currentclustid)

        # cluster ids that weren't in the original set are negative
        currentclustid -= 1
        i = clust.index(lowestpair[0])
        j = clust.index(lowestpair[1])
        del clust[max(i, j)]
        del clust[min(i, j)]
        clust.append(newcluster)

    return clust[0]


def printclust(clust, labels=None, n=0):
    # indent to make a hierarchy layout
    for _ in range(n):
        print(' ', end='')
    if clust.id < 0:
        # negative id means that this is branch
        print('-', end='\n')
    else:
        # positive id means that this is an endpoint
        if labels is None:
            print(clust.id)
        else:
            print(labels[clust.id])

    # now print the right and left branches
    if clust.left is not None:
        printclust(clust.left, labels=labels, n=n + 1)
    if clust.right is not None:
        printclust(clust.right, labels=labels, n=n + 1)


class DrawClusters:
    @staticmethod
    def getheight(clust):
        if (clust.left) is None and (clust.right is None):
            return 1

        return DrawClusters.getheight(clust.left) + DrawClusters.getheight(clust.right)

    @staticmethod
    def getdepth(clust):
        if (clust.left is None) and (clust.right is None):
            return 0
        depth = max(DrawClusters.getdepth(clust.left), DrawClusters.getdepth(clust.right)) + clust.distance
        return depth

    @staticmethod
    def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
        # height and width
        h = DrawClusters.getheight(clust) * 20
        w = 1200
        depth = DrawClusters.getdepth(clust)

        # width is fixed, so scale distances accordingly
        scaling = float(w - 150) / depth

        # Create a new image with a white background
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        print(img.__class__.__name__)
        print(draw.__class__.__name__)
        draw.line((0, h / 2, 10, h / 2), fill=(0, 255, 0))

        # Draw the first node
        DrawClusters.drawnode(draw, clust, 10, (h / 2), scaling, labels)
        img.save(jpeg, 'JPEG')

    @staticmethod
    def drawnode(draw, clust, x, y, scaling, labels):
        if clust.id < 0:
            h1 = DrawClusters.getheight(clust.left) * 20
            h2 = DrawClusters.getheight(clust.right) * 20
            top = y - (h1 + h2) / 2
            bottom = y + (h1 + h2) / 2
            # Line length
            ll = clust.distance * scaling

            # Vertical line from this cluster to children
            draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(0, 255, 0))

            # Horizontal line to left item
            draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(0, 255, 0))

            # Horizontal line to right item
            draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(0, 255, 0))
            # draw.text((x+5,y-7),labels[clust.id],(0,0,0))

            # Call the function to draw the left and right nodes
            DrawClusters.drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
            DrawClusters.drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
        else:
            # If this is an endpoint, draw the item label
            draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 255))


def rotatematrix(data):
    newdata = list(zip(*data))
    return newdata


def kcluster(rows, distance=pearson, k=4, N=100):
    # Determine the minimum and maximum values for each point
    ranges = [(min(col), max(col)) for col in rotatematrix(rows)]

    # Create k randomly placed centroids
    clusters = [[random() * (_range[1] - _range[0]) + _range[0]
                 for _range in ranges] for j in range(k)]
    lastmatches = None
    for t in range(N):
        print('Iteration %d' % t)
        bestmatches = [[] for i in range(k)]
        # Find which centroid is the closest for each row
        for j, row in enumerate(rows):
            bestmatch = 0
            for i, cluster in enumerate(clusters):
                d = distance(cluster, row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)

            # If the results are the same as last time, this is complete
        if bestmatches == lastmatches:
            break
        else:
            lastmatches = bestmatches

        # Move the centroids to the average of their members
        clusters = []
        for bestmatch in bestmatches:
            if len(bestmatch) == 0:
                continue

            bestmatch_rows = [rows[j] for j in bestmatch]
            avgs = [mean(d) for d in zip(*bestmatch_rows)]
            clusters.append(avgs)

    return bestmatches


if __name__ == '__main__':
    file = '..//data//blogdata.txt'
    rownames, colnames, data = readfile(file)
    kclust = kcluster(data, k=10)
    for k, cluster in enumerate(kclust):
        print(k)
        for item in cluster:
            print('  ', rownames[item])

    clust = hcluster(data)
    DrawClusters.drawdendrogram(clust, rownames, jpeg='..//images//blog_clusters.jpg')
    #wordclust = hcluster(rotatematrix(data))
    #DrawClusters.drawdendrogram(wordclust, colnames, jpeg='..//images//word_clusters.jpg')
