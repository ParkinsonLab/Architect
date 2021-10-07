
def highligh_enzymes_in_KEGG(pathway_id, enzymes, ax=None, color="#FF1414"):
    """ Highlight enzymes in KEGG map

    Args:
        pathway_id (str): KEGG KO Pathway id (example: 'ko00740')
        enzymes (list): list of EC numbers to be highlighted
        ax (AxesSubplot): display on given AxesSuplot (optional)

    Returns:

    """

    from io import StringIO
    import requests
    import xml.etree.ElementTree as xml
    import PIL.ImageDraw
    import re
    import pandas as pd
    import matplotlib.pyplot as plt

    KEGG_API_URL = 'http://rest.kegg.jp'

    # Download KEGG pathway
    uri = KEGG_API_URL + "/get/{}/kgml".format(pathway_id)
    kgml_d = requests.get(uri)
    kgml_d = xml.parse(StringIO(kgml_d.content)).getroot()

    # Download KEGG pathway image
    image_d = requests.get(kgml_d.get("image"))
    pathway_image = PIL.Image.open(StringIO(image_d.content))
    pathway_image = pathway_image.convert(mode="RGBA")

    # Find locations of orthologs on the map
    orthologs_elements = []
    for entry_node in kgml_d.findall("entry"):
        entity_ids = set(re.sub("(KO:|EC:)", "", id) for id in entry_node.get("name").upper().split())
        entity_type = entry_node.get("type")

        if entity_type != "ortholog":
            continue

        graphic_element_node = entry_node.find("graphics")
        graphic_element_type = graphic_element_node.get("type")

        # extract the shape and coordinates of the graphic element
        if graphic_element_type in ("rectangle", "circle"):
            w = int(graphic_element_node.get("width"))
            h = int(graphic_element_node.get("height"))
            x0 = int(graphic_element_node.get("x")) - w / 2
            y0 = int(graphic_element_node.get("y")) - h / 2
            x1, y1 = x0 + w, y0 + h

            orthologs_elements.append({'orthologs': set(entity_ids),
                                       'gtype': graphic_element_type,
                                       "x0": x0, "y0": y0, "x1": x1, "y1": y1})

    # Create mapping between orthologs and enzymes
    orthologs = [ko for oe in orthologs_elements for ko in oe['orthologs']]
    orthologs = [re.sub("^KO:", "", o) for o in orthologs]
    ec_table = requests.get(KEGG_API_URL + "/link/enzyme/{}".format("+".join(orthologs)))
    ec_table = pd.read_table(StringIO(re.sub("(ko:|ec:)", "", ec_table.content)), names=["ortholog", "ec"])

    # highlight provided ENZYMES on the KEGG map
    pathway_image_copy = pathway_image.copy()
    highlighted_orthologs = set(ko for ec in enzymes for ko in ec_table.ortholog[ec_table.ec == ec].values)
    for el in orthologs_elements:
        if len(el['orthologs'].intersection(highlighted_orthologs)) > 0:
            overlay_image = PIL.Image.new('RGBA', pathway_image.size)
            draw = PIL.ImageDraw.Draw(overlay_image)
            draw.rectangle([el["x0"], el["y0"] - 1, el["x1"], el["y1"] - 1], outline=color)
            pathway_image_copy.paste(overlay_image, mask=overlay_image)

    if not ax:
       _, ax = plt.subplots(1,1)

    return ax.imshow(pathway_image_copy, interpolation='nearest')
