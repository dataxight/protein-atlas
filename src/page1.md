<|container|

<|text-center|

# Gene Expression Heatmap Viewer

Transcript expression levels summarized per gene in 13 regions based on samples from the Human Brain Tissue Bank (HBTB; Semmelweis University, Budapest) analysed with RNA-seq on the MGI platform. The tab-separated file includes Ensembl gene identifier, analysed region, transcripts per million ("TPM"), protein-transcripts per million ("pTPM") and normalized expression ("nTPM"). The data is based on The Human Protein Atlas version 24.0 and Ensembl version 109.


<||layout|columns=1 1|gap=20px|
<|
**Choose your file**: <|{file_path}|file_selector|label={file_path.split("/")[-1] if file_path != "" else "Select manifest file or data file"}|on_action=on_file_input|extensions=.json, .tsv, .csv, .parquet|drop_message=Drop here to upload|>
|>

<|part|render={table_list is not None}|
<|
**Table**: <|{selected_table}|selector|label=Select a table|lov={table_list}|dropdown|on_change=on_table_selected|>
|>
|>
|>


<|part|render={hpa_data is not None}|
<|layout|columns=1 1|gap=20px|
<|
**Gene**: <|{selected_gene}|selector|label=Select a Gene|lov={genes_list}|dropdown|on_change=on_gene_selected|>
|>

<|
**Brain region**: <|{selected_brain_region}|selector|label=Select a Brain Region|lov={brain_region_list}|dropdown|on_change=on_region_selected|>
|>
|>
|>

<|layout|columns=1|
<|part|render={hpa_data is not None}|
<|Apply|button|on_action=on_generate_heatmap|>

<|part|render={progress != 0 and progress != 100}|
<|progress|value={progress}|linear|title=Processing...|title_anchor=top|show_value|>
|>
|>

<br/>
<|card|
**Logs**

<|{logs}|text|raw|>
|>

|>

<|layout|columns=1|
<|part|render={heatmap_gene_figure is not None}|
<|chart|figure={heatmap_gene_figure}|rebuild|>
|>
<|part|render={heatmap_region_figure is not None}|
<|chart|figure={heatmap_region_figure}|rebuild|>
|>
|>

|>
|>
