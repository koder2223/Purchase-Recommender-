import pandas as pd
from sklearn.neighbors import NearestNeighbors
import networkx as nx
import joblib


X_GraphSAGE=pd.read_csv("./Model/X_graph.csv").set_index("Id")
nodes=pd.read_csv("./ModelData/nodesData.csv")
nodes = nodes.set_index("Id")

NN_MODEL=joblib.load("./Model/NNMODEL.pkl")



def productRecommendations(productId):
    productDF=X_GraphSAGE.loc[[productId]]
    recommendations=NN_MODEL.kneighbors(productDF,n_neighbors=5,return_distance=False)
    result=[]
    for recommended in recommendations:
        ans=nodes.loc[recommended]
        result.append(ans)
    return result[0]
