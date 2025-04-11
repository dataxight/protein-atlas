import os
import daft

import ceramist.data as datalib
import ceramist.graph as graphlib
import ceramist.io as iolib


def read_file(file_path):
    extension = os.path.splitext(file_path)[1]

    if extension == ".csv":
        return daft.read_csv(file_path)
    elif extension == ".tsv":
        return daft.read_csv(file_path, delimiter="\t")
    elif extension == ".parquet":
        return daft.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def get_cancer_data_graph_by_cancer(selected_cancer_name: str) -> graphlib.igraph.Graph:
    selected_cancer_name = selected_cancer_name

    if selected_cancer_name == "":
        return None

    filename = "data/" + selected_cancer_name + ".json"
    reader = iolib.ManifestReader()
    graph = reader.load_from_file(filename)
    reader.load_data_for_graph(graph)

    return graph


def get_dataframe_from_graph_node(graph, node_name: str) -> daft.DataFrame:
    if graph is None:
        raise RuntimeError("Selected cancer data graph is empty")

    node = graphlib.get_node(graph, node_name)
    df = datalib.get_node_data(node)

    return df
