import aspose.words as aw
import requests

doc_url = "https://www.mevzuat.gov.tr/MevzuatMetin/1.5.5252.doc"
file = requests.get(doc_url).content
doc = aw.Document(file)

runs = []

def test_recurse_all_nodes():

    doc = aw.Document(file)

    # Invoke the recursive function that will walk the tree.
    traverse_all_nodes(doc)


# <summary>
# A simple function that will walk through all children of a specified node recursively
# and print the type of each node to the screen.
# </summary>
def traverse_all_nodes(parentNode) :

    # This is the most efficient way to loop through immediate children of a node.
    for childNode in parentNode.child_nodes :

        print(aw.Node.node_type_to_string(childNode.node_type))
        if childNode.node_type == aw.NodeType.RUN :
          run = childNode.as_run()
          runs.append(run)
          print(run.text)

        print("-------------------------")

        # Recurse into the node if it is a composite node.
        if childNode.is_composite :
            traverse_all_nodes(childNode.as_composite_node())