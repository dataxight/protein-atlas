import logging
import traceback

import daft
import taipy
from taipy.gui import Gui

import plotly.express as px

cancer_data = None
gene_list = []
selected_gene_name = ""
gene_figure = None


def load_data():

    filename = "data/cancer_data.tsv"

    df = daft.read_csv(filename,
                       delimiter="\t")

    return df


def populate_gene_list(cancer_data):

    logger.debug("in populate_gene_list")

    gene_list = cancer_data.select("Gene name").distinct().to_pydict()["Gene name"]
    gene_list.sort()

    return gene_list


# this will be bound to the selector
def on_gene_selected(state, var, value):
    logger.debug("gene selection changed to " + value)
    state.selected_gene_name = value

    if value == "":
        logger.debug("no gene selected")
        return

    gene_data = compute_chart_data(state)
    render_chart(state, gene_data)

    return



def compute_chart_data(state):
    logger.debug("in compute_chart_data")

    gene_name = state.selected_gene_name
    cancer_data = state.cancer_data

    gene_data = cancer_data.where(daft.col("Gene name")==gene_name)
    return gene_data

    

def render_chart(state, gene_data):

    logger.debug("in render_chart")


    figure = px.bar(gene_data.to_arrow(),
                    x="Cancer", y=["Not detected", "Low", "Medium", "High"],
                    title="Count of expression levels",
                    labels={'value':'Count'}
                    )
    
    state.gene_figure = figure
    state.refresh("gene_figure")

    logger.debug("done render_chart")
    return


if __name__ == "__main__":
    
    logger = logging.getLogger("toy-data-web-app")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("starting")

    cancer_data = load_data()
    gene_list = populate_gene_list(cancer_data)
    

    Gui(page="src/page.md",
        path_mapping={'/':'./'}).run(
            debug=True,
            use_reloader=True,
            title="Cancer data (IHC)",
            port=8080)



