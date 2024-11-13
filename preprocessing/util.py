import re
import constants
import os
from typing import List, IO
import penman


def allDataFiles():
    files = []
    path = constants.RETROFITTED_FOLDER
    ldcPath = path + "LDC/AMRs/"
    ldcSubfolders = [name for name in os.listdir(ldcPath) if os.path.isdir(os.path.join(ldcPath, name))]
    for directory in ldcSubfolders:
        for file in os.listdir(ldcPath + directory):
            if file.endswith(".txt"):
                files.append(ldcPath + directory + "/" + file)

    files.append(path + "Minecraft-all-final.txt")
    files.append(path + "Little_Prince.txt")
    return files


def ldcDataFiles():
    files = []
    path = constants.RETROFITTED_FOLDER
    ldcPath = path + "LDC/AMRs/"
    ldcSubfolders = [name for name in os.listdir(ldcPath) if os.path.isdir(os.path.join(ldcPath, name))]
    for directory in ldcSubfolders:
        for file in os.listdir(ldcPath + directory):
            if file.endswith(".txt"):
                files.append(ldcPath + directory + "/" + file)

    return files


def minecraftDataFile():
    return constants.RETROFITTED_FOLDER + "Minecraft-all-final.txt"


def littlePrinceDataFile():
    return constants.RETROFITTED_FOLDER + "Little_Prince.txt"


def errorDump(thrownException, amrId, currentGraph, errorLogFile="error_log.txt"):
    print(f"AMR {amrId} was not parsed successfully. See {errorLogFile} for more details.")

    with open(errorLogFile, "a+", encoding='utf-8') as out:
        out.write(str(type(thrownException)))
        out.write(str(thrownException))

        out.write(f"\nAMR: {amrId}\n\n")

        for line in currentGraph:
            out.write(line)

        out.write("-------------------------------\n\n\n")


def get_node_str_from_var_name(variable_name, graph_lines):
    graph_lines = [line.strip() for line in graph_lines]
    graphString = "".join(graph_lines)
    regex = f"\({variable_name} .*"

    results = re.search(regex, graphString)
    if results:
        return parenMatch(results.group(0))

    return ""


def extractSourceText(source_lines: List[str]) -> str:
    """
    Fetches the source sentence from the header for a graph
    :param source_lines: graph header lines
    :return: original sentence for the graph
    """
    for line in source_lines:
        if "::snt-type" in line:
            continue
        tokens = line.split("::snt")
        if len(tokens) > 1:
            try:
                return tokens[1]

            except:
                return ""

    return ""


# quick and dirty function to get a node from a graph via paren manipulation
def parenMatch(string):
    stack = []
    for idx, char in enumerate(string):
        if char == "(":
            stack.append(char)
        elif char == ")":
            stack.remove("(")
            if len(stack) < 1:
                return string[:idx + 1]

    return string  # default


def getNodeStringFromVar(variable_name: [str],
                         graph_lines: List[str],
                         use_ne_cutoff=False,
                         graph: penman.Graph = None) -> str:
    """
    Fetches a subgraph string for a given variable.
    Includes the node of interest and all descendants.
    :param variable_name:
    :param graph_lines:
    :param use_ne_cutoff:
    :param graph: optional instead of using the graph lines
    :return: flat string for the subgraph
    """

    if graph is not None:
        encoded = penman.encode(graph)
        graph_lines = encoded.split("\n")

    graph_lines = [line.strip() for line in graph_lines]
    graphString = "".join(graph_lines)
    regex = f"\({variable_name} .*"

    results = re.search(regex, graphString)
    if results:
        string_form = parenMatch(results.group(0))

        if use_ne_cutoff:
            if ":name" in string_form:
                match = re.search(r":name (.+?)\(", string_form)
                if match:
                    return string_form[:match.end()]
            elif ":wiki" in string_form:
                match = re.search(r":wiki (.+?)\(", string_form)
                if match:
                    return string_form[:match.end()]

        return string_form

    return ""


def nextNodeWithLetterName(node_letter: str,
                           graph: penman.Graph) -> str:
    """
    Finds the next available variable name in a graph for a given start letter
    :param node_letter: node letter prefix
    :param graph: graph where the node is to be added
    :return: next node name available which starts with the letter
    """

    conflicts = [(re.sub("[A-z]", "", var)) for var in graph.variables() if var.startswith(node_letter)]

    onlyEmptyString = (len(conflicts) > 0)

    for item in conflicts:
        if item != "":
            onlyEmptyString = False

    if onlyEmptyString:
        return node_letter + str(2)

    conflicts = [int(conf) for conf in conflicts if conf]

    if len(conflicts) == 0:
        return node_letter

    return node_letter + str(max(conflicts) + 1)


def getVariableInstance(variable, graph) -> str:
    """
    Fetches the instance for a given variable in a graph
    :param variable: variable to look up
    :param graph:
    :return: instance of the given variable, or "" if not in graph
    """
    for instance in graph.instances():
        if instance.source == variable and instance.role == ':instance':
            return instance.target

    return ""


def extractAMRId(source_lines: List[str]) -> str:
    """
    Fetches the AMR ID from the graph header
    :param source_lines: List of lines which precede the graph
    :return: AMR ID
    """
    try:
        for line in source_lines:
            tokens = line.split("::date")
            if len(tokens) > 1:

                return tokens[0].split("::id")[1].strip()

            else:
                if "::id" in line:
                    return line.split("::id")[1].strip()
    except:
        return ""

    return ""


def isPropBankConcept(string: str) -> bool:
    pattern = r'-\d*$'
    match = re.search(pattern, string.strip())
    if match:
        return True
    else:
        return False


def all_english_pronouns() -> List[str]:
    return ['he', 'she', 'they', 'i', 'you', 'you-all', 'we']


def is_english_pronoun(string: str) -> bool:
    return string in all_english_pronouns()


# Convenience functions for graph maniputations


def rename_instance_in_graph(old_node_name: str,
                             new_node_name: str,
                             graph: penman.Graph) -> penman.Graph:
    """
    Updates a single graph, replacing the instance with one name to another
    :param old_node_name: name of the node to be renamed
    :param new_node_name: new name for the node
    :param graph: graph to rename
    :return: new graph
    """

    top = graph.top

    instances, edges, attributes = apply_rename(old_node_name,
                                                new_node_name,
                                                graph.instances(),
                                                graph.edges(),
                                                graph.attributes())

    if top == old_node_name:
        top = new_node_name

    new_graph = penman.Graph(instances + edges + attributes, top=top)
    return new_graph


def apply_rename(old_node_name: str,
                 new_node_name: str,
                 graph_instances: List[penman.graph.Instance],
                 graph_edges: List[penman.graph.Edge],
                 graph_attributes: List[penman.graph.Attribute]):
    """

    Helper to apply name change to graph
    :param old_node_name:
    :param new_node_name:
    :param graph_instances:
    :param graph_edges:
    :param graph_attributes:
    :return:
    """

    old_type = ""
    for inst in graph_instances:
        if inst.source == old_node_name:
            old_type = inst.target
            break

    new_instances = [instance for instance in graph_instances if instance.source != old_node_name]
    replacement_inst = penman.graph.Instance(new_node_name, ':instance', old_type)
    new_instances.append(replacement_inst)

    new_edges = []
    for edge in graph_edges:

        if edge.target == old_node_name:
            new_edges.append(penman.graph.Edge(edge.source, edge.role, new_node_name))

        elif edge.source == old_node_name:
            new_edges.append(penman.graph.Edge(new_node_name, edge.role, edge.target))

        else:
            new_edges.append(edge)

    new_attributes = []
    for attr in graph_attributes:
        if attr.source == old_node_name:
            new_attributes.append(penman.graph.Attribute(new_node_name, attr.role, attr.target))

        elif attr.target == old_node_name:
            new_attributes.append(penman.graph.Attribute(attr.source, attr.role, new_node_name))

        else:
            new_attributes.append(attr)

    return new_instances, new_edges, new_attributes


def extract_subgraph(graph: penman.graph.Graph,
                     subgraph_root_node: str,
                     supress_error=False) -> penman.graph.Graph:

    """
    Creates a graph from the components of a subgraph rooted at a specific node
    :param graph: graph to extract the subgraph from
    :param subgraph_root_node: name of the subgraph root
    :param supress_error: whether to suppress exceptions of the subgraph is not found
    :return:
    """

    # TODO unclear how this should / could handle inversions like 'ARG-of' where the penman string may make something look like
    # part of a subgraph but its not technically
    # in those cases, using the paren-matching of the string-fetching function is usable

    node_stack = [subgraph_root_node]
    subgraph_nodes = []
    subgraph_edges = []
    subgraph_attributes = []

    while len(node_stack) > 0:

        current_node_name = node_stack.pop()
        # get the instance of the chosen node

        for instance in graph.instances():
            if instance.source == current_node_name:
                subgraph_nodes.append(instance)

        # get every edge where the chosen node is the source, modify stack for searching
        for edge in graph.edges():
            if edge.source == current_node_name:
                subgraph_edges.append(edge)
                node_stack.append(edge.target)

        # get every attribute where the chosen node is the source

        for attr in graph.attributes():
            if attr.source == current_node_name:
                subgraph_attributes.append(attr)

    if not supress_error and len(subgraph_nodes) == 0:
        raise Exception('subgraph with specified root node not found.')

    subgraph = penman.graph.Graph(subgraph_nodes + subgraph_attributes + subgraph_edges, top=subgraph_root_node)

    return subgraph


def write_graph(graph: penman.graph.Graph,
                outfile: IO[str] = None,
                add_spacing: bool = True) -> None:
    """
    Convenience function to write a graph out to a file
    :param graph: graph to write out
    :param outfile: optional. if not specified, prints to terminal instead
    :param add_spacing: whether to add a line break at the end of the graph. default: True
    :return:
    """

    encoded = penman.encode(graph)

    if outfile is not None:
        outfile.write(encoded)
    else:
        print(encoded, end='')

    if add_spacing:
        if outfile is not None:
            outfile.write('\n')
        else:
            print('\n')

    return
