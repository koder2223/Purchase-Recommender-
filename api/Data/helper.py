import re

def filter_by_group(data_list):
    allowed_groups = ["Book", "Music", "DVD", "Video"]
    filtered_list = [item for item in data_list if item.get('group') in allowed_groups]
    return filtered_list

def collect_objects(filename):
    collect = []
    obj = {"Id": "","ASIN": "","title": "","group": "","salesrank": "","no_sim": "",
        "similar": [],"categories": "","catlists": [],"reviews": "","revdicts": []}
    keys = ["Id","ASIN","title","group","salesrank","similar","categories","reviews"]
    i = 0
    with open(filename, encoding="utf8") as f:
        for line in f:
            i += 1
            line = line.strip() #.replace("'","").replace('"','').replace("\\","")
            if line == "":
                collect.append(obj)
                obj = {"Id": "","ASIN": "","title": "","group": "","salesrank": "","no_sim": "",
                    "similar": [],"categories": "","catlists": [],"reviews": "","revdicts": []}
            key = line.split(":")[0]
            if key in keys:
                obj[key] = line[(len(key)+2):].strip()
                if key in ["Id","salesrank","categories"]:
                    value = obj[key]
                    obj[key] = int(value)
                if key == "similar":
                    value = obj[key].split()
                    obj[key] = value[1:]
                    obj["no_sim"] = int(value[0])
                if key == "reviews":
                    value = obj[key].split("  ")
                    obj[key] = {}
                    for v in value:
                        obj[key][v.split(":")[0].strip()] = float(v.split(":")[1].strip())
            if (len(line)>0) and (key not in keys):
                if line[0] == "|":
                    obj["catlists"].append(line[1:].split("|"))
                if re.match(r"(\d{4}-)", line) != None:
                    splits = line.split()
                    if len(splits) == 9:
                        revdict = {
                            "date":splits[0],
                            "customer":splits[2],
                            "rating":float(splits[4]),
                            "votes":float(splits[6]),
                            "helpful":float(splits[8])
                        }
                        obj["revdicts"].append(revdict)
    return collect



def convert_list_to_string(value_list):
    return ','.join(str(item) for item in value_list)

def populate_vertices_with_metadata(g, metadata_list):
    # Define the property name for your productId in the graph
    property_name = "ProductId"

    # Define the keys you want to insert into the vertex properties
    keys_to_insert = ['Id', 'ASIN', 'title', 'group', 'salesrank', 'no_sim', 'categories']

    for metadata in metadata_list:
        product_id = metadata.get('Id')

        # Find the vertices with the matching ProductId
        vertices = g.V().has(property_name, product_id).toList()

        # Check if any vertex is found with the given ProductId
        if not vertices:
            continue  # Skip to the next metadata item if vertex not found

        # Since there can be multiple vertices with the same ProductId, loop through each one
        for vertex in vertices:
            # Update the vertex properties with the selected metadata
            for key, value in metadata.items():
                if key in keys_to_insert:
                    g.V(vertex).property(key, value).next()