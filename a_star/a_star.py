import argparse
import pickle
import xml.etree.ElementTree as ET
import sys
from heapq import heappush, heappop
import math
import webbrowser
import gmplot


def construct_nodes_dictionary(map_file):
    """ Construct a dictionary containing information about the vertices of
    the graph.

    Args:
        map_file (str): name of the .osm file.
    """

    tree = None
    try:
        tree = ET.parse(args.map_file + ".osm")

    except Exception:
        print("Error parsing file.", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()
    nodes = {}

    for node in root.findall("./node"):
        ref = int(node.attrib["id"])

        nodes[ref] = {
            "ref": ref,
            "lat": float(node.attrib["lat"]),
            "lon": float(node.attrib["lon"]),
            "adj": set(),
            "parent": None,
            "g": 0,
            "h": 0
        }

    for way in root.findall("./way"):
        valid_road = False

        for tag in way.findall("./tag"):
            if tag.attrib["k"] == "highway":
                valid_road = True
                break

        if not valid_road:
            continue

        way_nodes = [int(item.attrib["ref"]) for item in way.findall("./nd")]

        for i in range(len(way_nodes)):
            if i == 0:
                nodes[way_nodes[i]]["adj"].add(way_nodes[i+1])
            elif i == len(way_nodes) - 1:
                nodes[way_nodes[i]]["adj"].add(way_nodes[i-1])
            else:
                nodes[way_nodes[i]]["adj"].add(way_nodes[i-1])
                nodes[way_nodes[i]]["adj"].add(way_nodes[i+1])

    return nodes


def haversine_distance(a, b):
    """ Calculate distance between two nodes.

    Distance calculation is done using the Haversine formula, which
    calculates the distance between two points on a sphere, using their
    latitude, and longitude.
    """

    R = 6371 * 10**3

    d_phi = math.radians(b["lat"] - a["lat"])
    d_lambda = math.radians(b["lon"] - a["lon"])
    phi_1 = math.radians(a["lat"])
    phi_2 = math.radians(b["lat"])

    a = (math.sin(d_phi/2))**2 + math.cos(phi_1)*math.cos(phi_2) * \
        (math.sin(d_lambda/2))**2

    y = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * y

    return d


def AStar(source_id, dest_id, nodes):
    """ Run the A* algorithm and return the shortest path between the source_id
    and the destination.

    Args:
        source_id (int): unique ref number of the source node found in the .osm
            file.
        dest_id (int): unique ref number of the destination node found in the
            .osm file.
        nodes (dict): dictionary containing information about the nodes such
            as the latitudes, longitudes, adjacency list.
    """

    dest_node = nodes[dest_id]

    p_queue = []
    opened = {}
    closed = {}

    heappush(p_queue, (0, source_id))
    opened[source_id] = True

    found_path = True
    while p_queue:

        _, curr_id = heappop(p_queue)

        if curr_id == dest_id:
            found_path = True
            break

        curr_node = nodes[curr_id]
        for neighbour_id in curr_node["adj"]:
            neighbour_node = nodes[neighbour_id]

            temp_g = haversine_distance(neighbour_node, curr_node) \
                + curr_node["g"]

            if not opened.get(neighbour_id) and not closed.get(neighbour_id):
                neighbour_node["g"] = temp_g
                neighbour_node["h"] = haversine_distance(
                        neighbour_node, dest_node)
                neighbour_node["parent"] = curr_id

                f = neighbour_node["g"] + neighbour_node["h"]
                heappush(p_queue, (f, neighbour_id))
                opened[neighbour_id] = True

            elif opened.get(neighbour_id):
                if neighbour_node["g"] > temp_g:
                    neighbour_node["g"] = temp_g
                    neighbour_node["parent"] = curr_id

            elif closed.get(neighbour_id):
                if neighbour_node["g"] > temp_g:
                    del closed[neighbour_id]
                    neighbour_node["g"] = temp_g
                    neighbour_node["parent"] = curr_id

                    f = neighbour_node["g"] + neighbour_node["h"]
                    heappush(p_queue, (f, neighbour_id))
                    opened[neighbour_id] = True

        opened[curr_id] = False
        closed[curr_id] = True

    path = []
    if found_path:
        curr_id = dest_id

        while curr_id is not None:
            curr_node = nodes[curr_id]
            path.append(curr_node["ref"])
            curr_id = curr_node["parent"]

    path.reverse()
    return path


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("map_file", type=str, help=".osm map file of the area")

    args = parser.parse_args()

    nodes = None
    try:
        # Check if pickle cache file exists for given map. If it does load
        # it, to get the nodes dictionary.
        with open(args.map_file + ".pickle", "rb") as pickle_file:
            nodes = pickle.load(pickle_file)
    except Exception:
        # Pickle cache file doesn't exist, construct nodes dictionary from
        # osm file, and cache it using pickle for future uses.
        nodes = construct_nodes_dictionary(args.map_file)
        with open(args.map_file + ".pickle", "wb") as pickle_file:
            pickle.dump(nodes, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    # Source        - Main Gate, BITS Pilani - Hyderabad Campus
    # Destination   - Water Tank, Bolarum

    source_id = 2684790802
    dest_id = 662739299
    path = AStar(source_id, dest_id, nodes)

    if not path:
        print("Path not found.")
        sys.exit(0)

    latitudes = [nodes[ref]["lat"] for ref in path]
    longitudes = [nodes[ref]["lon"] for ref in path]

    gmap = gmplot.GoogleMapPlotter(latitudes[0], longitudes[0], 15)
    gmap.plot(latitudes, longitudes, "green", edge_width=5)
    gmap.scatter(latitudes, longitudes, "red", marker=True)
    gmap.draw(args.map_file + ".html")
    webbrowser.open(args.map_file + ".html")
