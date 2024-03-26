import networkx as nx
import matplotlib.pyplot as plt
import notion_helper
import os
import uuid

IMG_DIR = "images"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)


DEFAULT_COLOR = "lightgrey"
LOCUS_COLOR = "#BEA7E5"
COLOR_MAP = {
    "Not started": "lightgrey",
    "In progress": "lightgrey",
    "Done": "lightblue",
    "Blocked": "lightgrey",
    "Abandoned": "lightblue",
}
"""
DEFAULT_COLOR = "#D1C7D1"
COLOR_MAP = {
    "Not started": "#BEA7E5",
    "In progress": "#FFD6AF",
    "Done": "#BEE7E8",
    "Blocked": "#A0D2DB",
    "Abandoned": "#A0D2DB",
}
"""
TERMINAL_STATES = {
    "Done",
    "Abandoned",
}
node_info = {}


def crawl_pages(node, G=nx.DiGraph()):
    # if a page has a parent, that parent has the page as a child
    # if a page has a child, that child has the page as a parent
    # the graph can be cyclical, but we care about all the edges

    page = notion_helper.get_page(node)
    node_info[node] = page
    print(page["properties"])

    parents = get_relations(page["properties"]["Parent Tasks"])
    for parent in parents:
        visited = G.has_node(parent)
        G.add_edge(parent, node)
        if not visited:
            crawl_pages(parent, G)

    children = get_relations(page["properties"]["Child Tasks"])
    for child in children:
        visited = G.has_node(child)
        G.add_edge(node, child)
        if not visited:
            crawl_pages(child, G)

    return G


def get_multiline(s, length=20):
    if len(s) < length:
        return s
    elif s[:length].rfind(" ") < length:
        i = s[:length].rfind(" ")
        return s[:i] + "\n" + get_multiline(s[i + 1 :])
    elif s.find(" ") > 0:
        i = s.find(" ")
        return s[:i] + "\n" + get_multiline(s[i + 1 :])
    else:
        return s


def get_relations(d):
    return [relation["id"] for relation in d["relation"]]


def get_title(page):
    return notion_helper.unwrap_notion_prop(page["properties"]["Item"]["title"])


def get_status(page):
    return notion_helper.unwrap_notion_prop(page["properties"]["Status"]["status"])


def get_color(node):
    page = node_info[node]
    status = get_status(page)
    blocked = False
    for child in get_relations(page["properties"]["Child Tasks"]):
        if get_status(node_info[child]) not in TERMINAL_STATES:
            blocked = True

    return COLOR_MAP.get(status, DEFAULT_COLOR) if not blocked else DEFAULT_COLOR


def draw_graph(G, locus):
    nx.draw(
        G,
        node_size=1500,
        node_color=[get_color(n) if n != locus else LOCUS_COLOR for n in G.nodes],
        arrowsize=8,
        with_labels=True,
        labels={n: get_multiline(get_title(node_info[n])) for n in G.nodes},
        edge_color="#555555",
        font_color="#000000",
        font_size=10,
        pos=nx.drawing.nx_agraph.graphviz_layout(G, prog="dot", args="-Grankdir=TB -x"),
    )
    plt.margins(x=0.4)


def format(id):
    return str(uuid.UUID(hex=id))


def get_image(node):
    node_info.clear()
    id = format(node)
    G = crawl_pages(id, nx.DiGraph())
    draw_graph(G, id)
    img_path = f"{IMG_DIR}/{id}.png"
    plt.savefig(get_image_path(id))
    plt.clf()
    return img_path


def get_image_path(node):
    id = format(node)
    return f"{IMG_DIR}/{id}.png"


if __name__ == "__main__":
    import sys

    node = sys.argv[1]
    print(get_image(node))
