import penman
from typing import List, Callable, IO, Union, Tuple
from util import write_graph


class DocumentInformation:
    # class which represents document-level information when building search results.
    #
    def __init__(self, doc_name="", split_folder=""):
        self.document = doc_name
        self.split = split_folder

        return


class GraphInfo:
    def __init__(self,
                 header_lines: List[str] = [],
                 graph: penman.Graph = None,
                 doc_info: DocumentInformation = None):
        self.graph = graph
        self.header_lines = header_lines
        self.doc_info = doc_info
        return


# Applies a single function to a graph, then writes the modified graph to the outfile.
def process_one_graph(graph_lines_or_graph: Union[penman.Graph, List[str]],
                      outfile: IO[str],
                      graph_function: Callable[[penman.Graph, List[str]], penman.Graph],
                      source_lines: List[str],
                      suppress_outfile_write: bool = False) -> None:


    try:
        if isinstance(graph_lines_or_graph, list):

            if len(graph_lines_or_graph) < 1:
                return

            graph = try_decode_graph(graph_lines_or_graph)
        elif isinstance(graph_lines_or_graph, penman.Graph):
            graph = graph_lines_or_graph

        else:
            raise Exception("Must pass a graph or list of str.")

        updated = graph_function(graph, source_lines)

        if not suppress_outfile_write:
            write_graph(updated, outfile=outfile, add_spacing=True)

    except:

        print("Unable to process graph {}.")

    return



def try_decode_graph(graph_lines: List[str]) -> penman.Graph:


    try:
        graph = None
        penmanString = "".join(graph_lines)

        graph = penman.decode(penmanString)

    except:
        print("Unable to process graph.")

    return graph


def parse_amr_document(infile_name) -> List[GraphInfo]:
    """
    Parses the document into graph objects
    :param infile_name: file to read from
    :return: List of corresponding GraphInfo objects
    """
    doc_info = DocumentInformation(doc_name=infile_name)
    graphs = []

    lines = []
    with open(infile_name, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    currentGraph = []
    currentSource = []
    for line in lines:
        if line.startswith('#'):
            # header lines
            if len(currentGraph) > 0:
                penman_graph = try_decode_graph(currentGraph)
                graphs.append(GraphInfo(graph=penman_graph,
                                        header_lines=currentSource,
                                        doc_info=doc_info))

                currentGraph = []
                currentSource = []

            currentSource.append(line)

            continue

        elif line.strip():
            # if it's not a header and not empty, it has to be part of a graph
            currentGraph.append(line)

        else:
            # whitespace
            pass

    # end of file -- process last graph
    if len(currentGraph) > 0:
        penman_graph = try_decode_graph(currentGraph)
        graphs.append(GraphInfo(graph=penman_graph,
                                header_lines=currentSource,
                                doc_info=doc_info))

    return graphs



def applyDocumentContextFunctionToGraphs(infile_name: str,
                                         outfile_name: str,
                                         graph_function: Callable[[GraphInfo, List[GraphInfo], any], Tuple[penman.Graph, any]],
                                         suppress_outfile_write: bool = False):

    graph_infos = parse_amr_document(infile_name)
    cached_info = None

    for graph_info in graph_infos:
        new_penman_graph, cached_info = graph_function(graph_info, graph_infos, cached_info)
        graph_info.graph = new_penman_graph

    if suppress_outfile_write:
        return

    # write to outfile
    with open(outfile_name, encoding='utf-8') as outfile:
        for graph_info in graph_infos:
            # TODO: how much do we care about preserving whitespace?

            try:
                outfile.writelines(graph_info.header_lines)
                outfile.write("\n")
                write_graph(graph_info.graph, outfile, add_spacing=True)

            except:
                print("unable to process graph.")

    return


def applyFunctionToGraphs(infile_name: str,
                          outfile_name: str,
                          graph_function: Callable[[penman.Graph, List[str]], penman.Graph],
                          suppress_outfile_write: bool = False):

    """
    Main entry point for modifying a file full of penman-style graphs.
    crawls over a file. simply copies non-graph lines (source text, metadata, etc.) from infile to outfile.
    applies a function to each graph before
    decoding and writing to outfile.
    graph_function must take a penman-type graph
    :param infile_name: string for the file to read graphs from
    :param outfile_name: string for the file to write out to (can be the same as the infile)
    :param graph_function: arbitrary function to apply to each graph. see interface in typing suggestions above
    :param suppress_outfile_write: set if you want to force no write to the outfile
    :return:
    """

    lines = []
    with open(infile_name, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    currentGraph = []
    currentSource = []
    with open(outfile_name, 'w+', encoding='utf-8') as outfile:
        for line in lines:
            if line.startswith('#'):
                # header lines
                if len(currentGraph) > 0:
                    # apply function and write to outfile, then reset
                    process_one_graph(currentGraph, outfile, graph_function, currentSource, suppress_outfile_write)
                    currentGraph = []
                    currentSource = []

                currentSource.append(line)

                if not suppress_outfile_write:
                    outfile.write(line)
                continue

            elif line.strip():
                # if it's not a header and not empty, it has to be part of a graph
                currentGraph.append(line)

            else:
                # whitespace, just preserve it
                if not suppress_outfile_write:
                    outfile.write(line)

        # end of file -- process last graph
        if len(currentGraph) > 0:
            process_one_graph(currentGraph, outfile, graph_function, currentSource, suppress_outfile_write)
