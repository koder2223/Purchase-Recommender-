from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from pydantic import BaseModel
import csv

#Product Model
class ProductModel(BaseModel):
    id: int
    asin:str
    title:str
    group:str
    salesRank:int
    no_sim:int
    similar:list
    categories:int
    reviews:dict
    revDict:list


#Creating ProductModel Instance for each
def create_unique_nodes(file_path):
    unique_nodes = set()

    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)

        for row in csvreader:
            source_id = int(row['source'])
            target_id = int(row['target'])
            unique_nodes.add(source_id)
            unique_nodes.add(target_id)

    return [ProductModel(ProductId=node_id) for node_id in unique_nodes]

def save_vertices(g, vertices):
    for vertex in vertices:
        g.addV('Product').property('ProductId', vertex.ProductId).next()

def create_edges(file_path):
    edges = []

    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)

        for row in csvreader:
            source_id = int(row['source'])
            target_id = int(row['target'])
            edges.append((source_id, target_id))

    return edges


def connect_products(g,source_product_id, target_product_id):
    property_name = "ProductId"
    g.V().has(property_name, source_product_id).as_('source') \
                    .V().has(property_name, target_product_id).as_('target') \
                    .addE('CONNECTED').from_('source').to('target')
    print("Products connected successfully.")




def save_edges(g, edges):
    for edge in edges:
        source_id, target_id = edge
        connect_products(g,source_id,target_id)