from cProfile import label
import stellargraph as sg
from stellargraph import StellarGraph
from stellargraph.data import UnsupervisedSampler
from stellargraph.mapper import Attri2VecLinkGenerator, GraphSAGELinkGenerator
from stellargraph.layer import Attri2Vec, GraphSAGE, link_classification

from tensorflow import keras

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import networkx as nx


def generate_random_subgraph(node_type, nodes, link_type, links, size):
    random_selection = np.random.choice(nodes.index,
                                        size=np.minimum(size,len(nodes.index)),
                                        replace=False)
    random_nodes = nodes.loc[random_selection]
    random_nodes_links = links[(links["source"].isin(random_nodes.index)) &
                               (links["target"].isin(random_nodes.index))]

    random_sub_graph = StellarGraph({node_type: random_nodes},
                                    {link_type: random_nodes_links[["source","target"]]})
    return random_sub_graph, random_nodes

""" Attri2vec """
def attri2vec_model(G,
                    number_of_walks=3, walk_length=3,
                    batch_size=50, layer_sizes=[32], epochs=2):
    nodes = list(G.nodes())
    print("Generate samples ...")
    unsupervised_samples = UnsupervisedSampler(G, nodes=nodes, length=walk_length, number_of_walks=number_of_walks)
    generator = Attri2VecLinkGenerator(G, batch_size)
    train_gen = generator.flow(unsupervised_samples)
    print("Attri2vec model ...")
    attri2vec = Attri2Vec(layer_sizes=layer_sizes, generator=generator, bias=False, normalize=None)
    x_inp, x_out = attri2vec.in_out_tensors()
    prediction = link_classification(output_dim=1, output_act="sigmoid", edge_embedding_method="ip")(x_out)
    print("Keras model ...")
    model = keras.Model(inputs=x_inp, outputs=prediction)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss=keras.losses.binary_crossentropy,
        metrics=[keras.metrics.binary_accuracy])
    print("Train the model ...")
    history = model.fit(train_gen,epochs=epochs,verbose=1,use_multiprocessing=False,workers=2,shuffle=True)
    return x_inp, x_out, history, model


""" GraphSAGE """
def graphsage_model(G,
                    number_of_walks=3, length=3,
                    batch_size=50, epochs=2, num_samples=[5,3],
                    layer_sizes=[64,32]):
    nodes = list(G.nodes())
    print("Generate samples ...")
    unsupervised_samples = UnsupervisedSampler(G, nodes=nodes, length=length, number_of_walks=number_of_walks)
    generator = GraphSAGELinkGenerator(G, batch_size, num_samples)
    train_gen = generator.flow(unsupervised_samples)
    print("GraphSAGE model ...")
    graphsage = GraphSAGE(layer_sizes=layer_sizes, generator=generator, bias=True, dropout=0.0, normalize="l2")
    x_inp, x_out = graphsage.in_out_tensors()
    prediction = link_classification(output_dim=1, output_act="sigmoid", edge_embedding_method="ip")(x_out)
    print("Keras model ...")
    model = keras.Model(inputs=x_inp, outputs=prediction)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss=keras.losses.binary_crossentropy,
        metrics=[keras.metrics.binary_accuracy])
    print("Train ...")
    history = model.fit(train_gen,epochs=epochs,verbose=1,use_multiprocessing=False,workers=4,shuffle=True)
    return x_inp, x_out, history, model


""" Generate embeddings with trained model """
def generate_embeddings(features, generator, x_inp_src, x_out_src):
    embedding_model = keras.Model(inputs=x_inp_src, outputs=x_out_src)
    node_gen = generator.flow(features.index)
    node_embeddings = embedding_model.predict(node_gen, workers=1, verbose=1)
    return node_embeddings

""" Plot embeddings using decomposed embeddings """
def plot_embeddings(embeddings, labels, transformation):
    embeddings_2d = transformation.fit_transform(embeddings)
    Colour_map = {0: 'red', 1: 'orange', 2: 'purple', 3: 'blue'}
    GroupNames = {0: 'Book', 1: 'DVD', 2: 'Music', 3: 'Video'}
    Colours = [Colour_map[label] for label in labels]
    Labels = [GroupNames[label] for label in labels]

    df = pd.DataFrame({"x":embeddings_2d[:, 0],
                       "y": embeddings_2d[:, 1],
                       "color": Colours,
                       "label": Labels})

    plt.figure(figsize=(7, 7))
    ax = df[df.label=="Book"].plot.scatter(x="x",y="y",c="color",label="Book")
    df[df.label=="DVD"].plot.scatter(ax=ax,x="x",y="y",c="color",label="DVD")
    df[df.label=="Music"].plot.scatter(ax=ax,x="x",y="y",c="color",label="Music")
    df[df.label=="Video"].plot.scatter(ax=ax,x="x",y="y",c="color",label="Video")
    plt.legend()
    plt.title("Visualization of node embeddings")
    plt.show()


def recommender(sample_nodes,no_recommendations, embeddings_df, nodes_df, metric='minkowski'):
    NN = NearestNeighbors(metric=metric)
    NN.fit(embeddings_df)
    samples_df = embeddings_df.loc[sample_nodes]
    recommendations = NN.kneighbors(samples_df,
                                    n_neighbors=no_recommendations,
                                    return_distance=False)
    for i in range(len(sample_nodes)):
        product = sample_nodes[i]
        recoms = recommendations[i]
        print(f"For product {nodes_df.loc[product,'Group']} '{nodes_df.loc[product,'Title']}' we recommend: ")
        for j,rec in enumerate(recoms):
            print(f"{j+1}. {nodes_df.loc[rec,'Group']} '{nodes_df.loc[rec,'Title']}")

    return recommendations

""" Prints similar products by similarities """
def print_sim_products(nodes_df, similarity_df, max_similars=10):
    for col in similarity_df.columns:
        prod = int(col.split('_')[0])
        group = str(nodes_df.loc[prod,"Group"])
        title = str(nodes_df.loc[prod,"Title"])
        df = similarity_df[similarity_df[col]>0]
        df = df.sort_values(col,ascending=False)
        similars = df.index
        values = list(df[col].values)
        if len(similars)==0: continue
        print(f"Product {group} '{title}':")
        print(f"Metric {col.split('_')[1]}: ")
        for i,similar in enumerate(similars):
            if i >= max_similars: break
            group = str(nodes_df.loc[similar,"Group"])
            title = str(nodes_df.loc[similar,"Title"])
            print(f"{i+1}. {group} '{title}': {values[i]}")