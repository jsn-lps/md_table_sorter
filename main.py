import os
import sys

table_delim = "|"
file_dest = None

# arg 1: file input
try:
    sys.argv[1]
    file_input = sys.argv[1]
    if not os.path.isfile(file_input):
        raise SystemExit(
            "File Error: File not found"
        )

    if "/" in file_input:
        file_name = file_input.split("/")[-1]
        print(file_name)
    else:
        file_name = file_input

except Exception as e:
    if str(e) == "list index out of range":
        raise SystemExit(
            "Usage: mdtabsort <filename> <column> [dest](defaults to .)"
        )

# arg 2: column input
try:
    sys.argv[2]
    field_to_sort = sys.argv[2].strip()
except Exception as e:
    if str(e) == "list index out of range":
        raise SystemExit(
            "Error: No column entered"
        )

# arg 3 destination input (optional)
try:
    sys.argv[3]
    if sys.argv[3]:
        file_dest = sys.argv[3]
    # Todo: specify OS path
except Exception:
    UserWarning(
        "No destination specified. Saving to current working directory"
    )
    pass


def open_markdown(file_name: str) -> list:
    with open(file_name, "r") as file:
        content = file.readlines()
        return content


def get_col_head(content: list) -> object:
    col = []
    at_table = False
    col_line = 0  # line based on 0 index

    for line in content:
        if at_table is True and line.startswith(table_delim):
            col_line += 1
            continue
        elif at_table is True and not line.startswith(table_delim):
            at_table = False

        if line.startswith(table_delim) and at_table is False:
            head = line.lstrip(table_delim).rstrip("\n").rstrip(table_delim)
            col.append({col_line: head.split(table_delim)})
            at_table = True
        col_line += 1

    return col


def map_table(col, col_line, content) -> list | int:
    lines = []
    head = col_line
    height = 2  # skips the |-----| line

    ptr = content[head + height]
    while ptr.startswith(table_delim):
        row = ptr.lstrip(table_delim).rstrip("\n").rstrip(table_delim)
        row = row.split(table_delim)

        for col_num, col_value in enumerate(col):
            if col_num == 0:
                entry = height - 1
                entry = {}

            column = col_value
            value = row[col_num].strip()
            entry[column] = value

        lines.append(entry)
        height += 1
        ptr = content[head + height]

    table_height = height - 2  # skipping |-----|
    return lines, table_height


def sort_table(table, column) -> list:
    return sorted(table, key=lambda d: d[column])


def merge_tables(sorted_table) -> list:
    first_val = sorted_table[0][col_to_sort]
    top_list = []
    bottom_list = []
    for item in sorted_table:
        if item[col_to_sort] == first_val:
            top_list.append(item)
        else:
            bottom_list.append(item)

    top_list = sort_table(top_list, col[0])
    bottom_list = sort_table(bottom_list, col[0])
    top_list.extend(bottom_list)

    return top_list


def build_lines(top_list) -> list:
    list_of_lines = []
    for item in top_list:

        line = table_delim
        for k, v in item.items():
            line += v
            line += f" {table_delim} "
        line += "\n"
        list_of_lines.append(line)

    return list_of_lines


def write_file(file_name,
               content,
               lines_to_write,
               col_lines,
               table_heights,
               file_dest):

    writing_new_content = False
    items_written = 0
    cur_table = 0
    wrote_split_line = False

    if not file_dest:
        file_dest = f"sorted-{file_name}"

    # creates new file to avoid overwriting old one
    with open(file_dest, "w") as new_file:
        for line_index, cur_line in enumerate(content):

            # write last line after all tables sorted
            if cur_table == len(lines_to_write):
                new_file.write(cur_line)
                continue

            if writing_new_content is True:

                if items_written == 0 and wrote_split_line is False:
                    new_file.write(cur_line)
                    wrote_split_line = True
                    continue

                if items_written == table_heights[cur_table]:  # go next table
                    new_file.write(cur_line)
                    items_written = 0
                    cur_table += 1
                    writing_new_content = False
                    wrote_split_line = False
                    continue

                new_file.write(lines_to_write[cur_table][items_written])
                items_written += 1
                continue

            if line_index == col_lines[cur_table]:
                new_file.write(cur_line)
                writing_new_content = True
                continue

            if writing_new_content is False:
                new_file.write(cur_line)
                continue


if __name__ == "__main__":

    content = open_markdown(file_input)

    col = get_col_head(content)

    # field_to_sort = "Required"

    valid_tables = []
    for obj in col:
        for col_line, col_head in obj.items():
            for field in col_head:
                if field_to_sort.lower() == field.strip().lower():
                    valid_tables.append(obj)
                    break

    if len(valid_tables) == 0:
        raise SystemExit(f"Exiting: No columns by the name '{field_to_sort}'")

    lines_to_write = []
    table_heights = []
    col_lines = []
    for cur_table in valid_tables:
        col_line = list(cur_table.keys())[0]
        col = list(cur_table.values())[0]

        table, table_height = map_table(col, col_line, content)

        # TODO: dynamically find the column marked with keyword
        for item in col:
            if item.strip().lower() == field_to_sort.lower():
                col_to_sort = item

        sorted_table = sort_table(table, col_to_sort)
        # alphabetical, so "no" comes before yes
        sorted_table.reverse()

        top_list = merge_tables(sorted_table)

        list_of_lines = build_lines(top_list)
        lines_to_write.append(list_of_lines)
        table_heights.append(table_height)
        col_lines.append(col_line)

    write_file(
        file_name,
        content,
        lines_to_write,
        col_lines,
        table_heights,
        file_dest
    )

    raise SystemExit(f"Successfully sorted and wrote to 'sorted-{file_name}'")
