import logging
import os

import daft
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from taipy.gui import Gui, State, invoke_long_callback, navigate, notify

from helpers import get_data_graph, get_dataframe_from_graph_node, read_file

file_path = ""
# For level 1
data_graph = None
table_list = None
hpa_data = None
# For level 2
selected_table = ""
genes_list = None
brain_region_list = None
selected_gene = ""
selected_brain_region = ""
heatmap_region_figure = None
heatmap_gene_figure = None
# For level 3
progress = 0
status = 0
logs = "Not running"

def reset_attributes_by_level(state, level):
    """
    Level of states:
    - Cancer: 1
    - First clinical attribute: 2
    - Second clinical attribute: 3
    """
    state_attributes = {
        1: [
            # For level 1
            "data_graph",
            "table_list",
            "hpa_data",
            # For level 2
            "selected_table",
            "genes_list",
            "brain_region_list",
            "selected_gene",
            "selected_brain_region",
            "heatmap_region_figure",
            "heatmap_gene_figure",
            # For level 3
            "progress",
            "status",
            "logs",
        ],
        2: [
            # For level 2
            "selected_table",
            "genes_list",
            "brain_region_list",
            "selected_gene",
            "selected_brain_region",
            "heatmap_region_figure",
            "heatmap_gene_figure",
            # For level 3
            "progress",
            "status",
            "logs",
        ],
        3: [
            "progress",
            "logs",
            "status",
            # "selected_gene",
            # "selected_brain_region",
        ]
    }

    reset_attributes = state_attributes.get(level, [])
    for attr in reset_attributes:
        setattr(state, attr, globals().get(attr))


def on_file_input(state) -> daft.DataFrame:
    logger.debug("File input changed to " + state.file_path)
    reset_attributes_by_level(state, 1)

    extension = os.path.splitext(state.file_path)[1]
    if extension == ".json":
        state.data_graph = get_data_graph(state.file_path)
        state.table_list = list(state.data_graph["description"]["tables"].keys())
    elif extension in [".csv", ".tsv", ".parquet"]:
        state.hpa_data = read_file(state.file_path)
        get_list_of_genes_and_brain_regions(state)


def on_table_selected(state, var, value):
    logger.debug("Graph node selection changed to " + value)
    reset_attributes_by_level(state, 2)
    state.hpa_data = get_dataframe_from_graph_node(state.data_graph, value)
    get_list_of_genes_and_brain_regions(state)


def get_list_of_genes_and_brain_regions(state):
    state.genes_list = sorted(filter(None, state.hpa_data.select("Gene name").distinct().to_pydict()["Gene name"]))
    state.brain_region_list = sorted(filter(None, state.hpa_data.select("Brain region").distinct().to_pydict()["Brain region"]))


def on_gene_selected(state, var, value):
    logger.debug("Gene selection changed to " + value)
    state.selected_gene = value

    if value == "":
        logger.debug("no gene selected")
        return


def on_region_selected(state, var, value):
    logger.debug("Brain region selection changed to " + value)
    state.selected_brain_region = value

    if value == "":
        logger.debug("no brain region selected")
        return


def long_callback_status(state: State, status, result):
    state.logs = f"Processing... {status}s"
    if isinstance(status, bool):
        if status:
            state.logs = "✅ Heatmap generated!"
            state.heatmap_gene_figure, state.heatmap_region_figure = result
            state.progress = 100
            state.refresh("heatmap_region_figure")
            state.refresh("heatmap_gene_figure")
            notify(state, "success", "Chart ready")
        else:
            notify(state, "error", "Something went wrong")
    else:
        state.status += 1
        state.progress += 1


def render_chart(hpa_data=None, selected_gene="", selected_brain_region=""):
    gene_figure = None
    region_figure = None
    df_filtered = None
    x_label = ["TPM", "pTPM", "nTPM"]

    # Cast all numeric columns at once
    hpa_data = hpa_data.with_columns(
        {col: daft.col(col).cast(daft.DataType.float64())
         for col in x_label
         if hpa_data.schema()[col].dtype != daft.DataType.float64()}
    )

    if selected_gene != "":
        logger.debug(f"Rendering chart for {selected_gene}")
        df_filtered = hpa_data.filter(daft.col("Gene name") == selected_gene)
        data = df_filtered.exclude("Gene", "Gene name", "Brain region").to_arrow()
        y_label = df_filtered.select("Brain region").to_pydict()["Brain region"]
        fig = px.imshow(
            data,
            labels=dict(x="Expression Values", y="Brain Regions", color="Values"),
            x=x_label,
            y=y_label,
            title=f"Expression of {selected_gene} gene across brain regions",
            text_auto=True, aspect="auto"
        )
        gene_figure = fig

    if selected_brain_region != "":
        logger.debug(f"Rendering chart for {selected_brain_region}")
        df_filtered = hpa_data.filter(daft.col("Brain region") == selected_brain_region)
        data = df_filtered.exclude("Gene", "Gene name", "Brain region").to_arrow()
        z_log = np.log1p(data)
        y_label = df_filtered.select("Gene name").to_pydict()["Gene name"]
        fig = go.Figure(data=go.Heatmap(
            x = x_label,
            y = y_label,
            z = z_log,
            colorbar=dict(title="log(value + 1)"),
            text=data,
        ))
        fig.update_layout(
            title=f"Expression of {selected_brain_region} region across Genes",
            xaxis_title="Expression Values",
            yaxis_title="Genes",
            coloraxis_colorbar=dict(title="Values"),
        )
        region_figure = fig

    logger.debug("Chart rendering complete")
    return gene_figure, region_figure


def on_generate_heatmap(state: State):
    logger.debug("Generating heatmap")
    reset_attributes_by_level(state, 3)
    invoke_long_callback(
        state,
        render_chart,
        [state.hpa_data, state.selected_gene, state.selected_brain_region],
        long_callback_status,
        [],
        1000,
    )


def on_menu_option_selected(state, action, info):

    page_name = info["args"][0]
    logging.debug("navigating to %s", page_name)
    navigate(state, to=page_name)
    return


if __name__ == "__main__":
    logger = logging.getLogger("champions-oncology")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("starting")

    # theme = get_theme()
    # theme_mode = theme["mode"]

    pages = {
        "/": "src/root.md",
        "human_protein_atlas": "src/page1.md",
        "proteomics": "src/page2.md",
    }

    Gui(pages=pages, path_mapping={"/": "./"}).run(
        debug=True, use_reloader=True, title="Human Protein Atlas", port=8080)
    # uncommenting this is suppoed to apply styles.css to the logo
    # however, we need it to set the proper size for the logo,
    # and that seems to not work
    #Gui(pages=pages, path_mapping={"/": "./"}, css_file="styles.css").run(
    #    debug=True, use_reloader=True, title="Human Protein ", port=8080)


    # uncommenting out this will use the ui_mode described in themes
    # however, we need to figure out which font size / heights to reduce
    # so that the menu looks like it does when we do not load the themes
    #
    # ui_modes = ui_theme.get_modes()
    #Gui(pages=pages, path_mapping={"/": "./"}, css_file="styles.css").run(
    #    debug=True, use_reloader=True, title="Human Protein ", port=8080,
    #    light_theme=ui_modes['light'], dark_theme=ui_modes['dark']
    #)
