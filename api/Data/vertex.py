from pydantic import BaseModel
import json
#import nest_asyncio
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from Helpers import collect_objects,filter_by_group
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

#nest_asyncio.apply()

# Define the Pydantic data model
class ProductModel(BaseModel):
    id: int
    asin: str
    title: str
    group: str
    salesRank: int
    no_sim: int
    similar: list
    categories: int
    reviews: list
    revDicts: list
  # to support gremlin event loop in Jupyter Lab

# set the graph traversal from the local machine:
connection = DriverRemoteConnection("ws://localhost:8182/gremlin", "g")  # Connect it to your local server
g = traversal().withRemote(connection)


def create_vertex_from_product(g, product_data):
    # Serialize the reviews dictionary to a JSON string
    if "reviews" in product_data:
        product_data["reviews"] = json.dumps(product_data["reviews"])
    #Serializing the Dict's inside the RevDicts key value pair
    if "revdicts" in product_data:
        for i in range(len(product_data["revdicts"])):
            product_data["revdicts"][i]=json.dumps(product_data["revdicts"][i])
    #List of String to String
    product_data["revdicts"]=json.dumps(product_data["revdicts"])
    #List of strings to string
    product_data["similar"]=json.dumps(product_data["similar"])
    del product_data["catlists"]

    #Creation of the Vertex
    vertex = g.addV('Product').property('Id', product_data['Id']).next()

    for key, value in product_data.items():
        if key!="Id":
          g.V(vertex).property(key, value).next()


products=collect_objects("../Dataset/amazon-meta.txt")
products_list=filter_by_group(products)


#Actual Processing of the Vertex
for product_data in products_list:
    print("Starting Vertex Creation")
    create_vertex_from_product(g, product_data)
    print("Vertex Created ")

connection.close()

