import os
import penman
from tqdm import tqdm
from typing import List, Callable

ERROR_LOG_FILEPATH = 'precommit_errors.log'

def allDataFiles() -> List[str]:
    """
    For maintainability it might be useful to just have this crawl over all .txt files that aren't requirements
    :return:
    """
    files = []
    path = ""
    ldcPath = path + "../Data/english-umr"
    ldcSubfolders = [name for name in os.listdir(ldcPath) if os.path.isdir(os.path.join(ldcPath, name))]
    for directory in ldcSubfolders:
        for file in os.listdir(ldcPath + directory):
            if file.endswith(".txt"):
                files.append(ldcPath + directory + "/" + file)

    # files.append(path + "Minecraft-all-final.txt")
    # files.append(path + "Little_Prince.txt")
    return files


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
        return "ERROR parsing AMR ID"

    return ""


def write_error(raw_graph_text: List[str] = [],
                source_lines: List[str] = [],
                exception: Exception = None,
                filename: str = "<Unknown>",
                extra_message: str = "",
                start_line_in_file: int = -1):
    """
    Helper to dump out error info to a file.
    :param raw_graph_text:
    :param source_lines:
    :param exception:
    :param filename:
    :param extra_message:
    :param start_line_in_file:
    :return:
    """

    with open(ERROR_LOG_FILEPATH, 'a+', encoding='utf-8') as outfile:

        if extra_message:
            outfile.write(extra_message + "\n")

        if exception is not None:
            outfile.write(str(exception))
            outfile.write("\n\n\n")

        amr_id = extractAMRId(source_lines)
        if not amr_id:
            amr_id = "<Unknown>"

        outfile.write(f'ID: {amr_id}\n')
        outfile.write(f'Filename: {filename}\n')
        if start_line_in_file>0:
            outfile.write(f'\tnear line # {start_line_in_file}\n')

        outfile.write("\n")

        if len(raw_graph_text) > 0:
            all_text = "\n".join(raw_graph_text)
            outfile.write(all_text)

        outfile.write("\n\n\n")
        outfile.write('------------------------------------------\n')


def sanity_check_graph(graph: penman.Graph, source_lines: List[str]) -> penman.Graph:
    """
    TODO: More robust checks. NE type verification, etc.
    :param graph:
    :param source_lines:
    :return:
    """
    return graph


def test_one_graph(current_graph: List[str],
                   graph_function: Callable[[penman.Graph, List[str]], penman.Graph],
                   source_lines: List[str],
                   filename: str = "",
                   start_line_in_file: int = -1) -> bool:

    if len(current_graph) < 1:
        message = f"Tried to process an empty graph from file {filename}."
        write_error(extra_message=message,
                    source_lines=source_lines,
                    filename=filename,
                    start_line_in_file=start_line_in_file)
        return False

    penmanString = "".join(current_graph)

    graph = None
    try:
        graph = penman.decode(penmanString)

    except Exception as e:
        message = f"Error decoding graph from file {filename}"
        write_error(extra_message=message,
                    exception=e,
                    raw_graph_text=current_graph,
                    filename=filename,
                    source_lines=source_lines,
                    start_line_in_file=start_line_in_file)
        return False

    updated = graph_function(graph, source_lines)

    return True


def apply_test_function_to_graphs(infile_name: str) -> int:
    """
    :param infile_name: string for the file to read graphs from
    :return:
    """

    lines = []
    with open(infile_name, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    currentGraph = []
    currentSource = []
    failed = 0
    current_start_line = -1

    for idx, line in enumerate(lines):
        if line.startswith('#'):
            # header lines
            if len(currentGraph) > 0:
                # apply function and write to outfile, then reset
                passed = test_one_graph(filename=infile_name,
                                        current_graph=currentGraph,
                                        source_lines=currentSource,
                                        graph_function=sanity_check_graph,
                                        start_line_in_file=current_start_line)

                if not passed:
                    failed += 1

                currentGraph = []
                currentSource = []

            currentSource.append(line)
            continue

        elif line.strip():
            # if it's not a header and not empty, it has to be part of a graph
            if len(currentGraph) == 0:
                current_start_line = idx

            currentGraph.append(line)

    # end of file -- process last graph
    if len(currentGraph) > 0:
        passed = test_one_graph(filename=infile_name,
                                current_graph=currentGraph,
                                source_lines=currentSource,
                                graph_function=sanity_check_graph,
                                start_line_in_file=current_start_line)

        if not passed:
            failed += 1

    return failed


def check_well_formed():
    pass


def setup_for_tests() -> None:
    print('Running tests...\n')
    if os.path.exists(ERROR_LOG_FILEPATH):
        print(f'Erasing previous test results at {ERROR_LOG_FILEPATH}...')
        os.remove(ERROR_LOG_FILEPATH)
        print('done.\n')

    return


def tests_passed() -> bool:
    failed = 0
    for file in tqdm(allDataFiles()):
        failed += apply_test_function_to_graphs(file)

    if failed > 0:
        print(f"{failed} graphs failed. See {ERROR_LOG_FILEPATH} for details.")
        return False
    else:
        print('All tests passed!')
        return True


def main():
    setup_for_tests()
    if tests_passed():
        exit(0)

    exit(1)


if __name__ == '__main__':
    main()
