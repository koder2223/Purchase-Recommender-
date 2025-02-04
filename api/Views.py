from Functions.dataTransform import transformData
import json

def getAllProducts(g):
    query_result = g.V().hasLabel('Product').valueMap(True).toList()
    return query_result


def getProductsGroup(g,group):
    query_result = g.V().hasLabel('Product').has('group', group).valueMap(True).toList()
    return query_result

def getProductById(g,item_id):
    # Execute the Gremlin query to fetch products by ID number
    query_result = g.V().hasLabel('Product').has('Id', item_id).valueMap(True).toList()
    return transformData(query_result[0])


def getProductByAsin(g,asin):
    query_result = g.V().hasLabel('Product').has('ASIN', asin).valueMap(True).toList()
    return query_result

def getSimilarProductsId(g,productId):
    # Execute the Gremlin query to fetch products by ID number
    query_result = g.V().hasLabel('Product').has('Id', productId).valueMap(True).toList()
    ans= query_result[0]["similar"]
    if len(ans)>0:
        data=json.loads(ans[0])
        return data
    return []

def getSimilarProductsDetails(g,productId):
    products=getSimilarProductsId(g,productId)
    res=[]
    for product in products:
        productData=getProductByAsin(g,product)
        if productData:
          res.append(product)
    return res

