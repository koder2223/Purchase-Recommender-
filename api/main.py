from fastapi import FastAPI
import pandas as pd
import json
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from Functions.dataTransform import transformData
from Views import getAllProducts,getProductsGroup,getProductById,getSimilarProductsDetails

graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))
app = FastAPI()



"""Get All"""
@app.get("/")
async def root():
    products = await asyncio.to_thread(getAllProducts,g)
    res=[]
    for prod in products:
        res.append(transformData(prod))
    return {"Products":res[:50]}

"""Get by Group"""
@app.get("/products/{group}")
async def get_products(group: str):
    # Start the asynchronous task to fetch products by group
    products = await asyncio.to_thread(getProductsGroup,g,group)
    res=[]
    for prod in products:
        res.append(transformData(prod))
    return {group: res[:20]}

"""Get by Id"""
@app.get("/{productId}")
async def getProductDetails(productId:int):
    product = await asyncio.to_thread(getProductById, g,productId)
    return {"Product":product}


"""Get Similar Products"""
@app.get("/similar/{productId}")
async def getSimilarProducts(productId:int):
    product = await asyncio.to_thread(getSimilarProductsDetails,g, productId)
    return {"Similar Products":product}




