from fastapi import FastAPI
import pandas as pd
from recommenderFunction import productRecommendations

import json
import uvicorn
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/recommend/{productId}")
async def recommend_product(productId):
    productId=int(productId)
    result=productRecommendations(productId)
    result =result.to_json(orient = 'records')
    data = json.loads(result)
    return {"Result":f"""{data}""".strip()}



@app.get("/similar/{productId}")
async def similar_product(productId):
    productId=int(productId)
    return {"Result":"Result"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)