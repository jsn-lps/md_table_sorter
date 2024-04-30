table_delim = "|"


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


def write_file(file_name, content, lines_to_write, col_lines, table_heights):
    writing_new_content = False
    items_written = 0
    cur_table = 0
    wrote_split_line = False

    # creates new file to avoid overwriting old one
    with open(f"sorted-{file_name}", "w") as new_file:
        for line_index, cur_line in enumerate(content):

            if cur_table == len(lines_to_write):
                new_file.write(cur_line)
                continue

            if writing_new_content is True:

                if items_written == 0 and wrote_split_line is False:
                    # building the |---| table split
                    split_line = ""
                    for char in cur_line:
                        if char == table_delim:
                            split_line += char
                            continue
                        split_line += "-"
                    if split_line.endswith("-"):  # sometimes extra space
                        split_line = split_line[:-1]

                    split_line += "\n"
                    new_file.write(split_line)
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
    file_name = "alb-ec2-readme.md"
    content = open_markdown(file_name)

    col = get_col_head(content)

    field_to_sort = "Required"

    valid_tables = []
    for obj in col:
        for col_line, col_head in obj.items():
            for field in col_head:
                if field_to_sort == field.strip():
                    valid_tables.append(obj)
                    break

    lines_to_write = []
    table_heights = []
    col_lines = []
    for cur_table in valid_tables:
        col_line = list(cur_table.keys())[0]
        col = list(cur_table.values())[0]

        table, table_height = map_table(col, col_line, content)

        # TODO: dynamically find the column marked with keyword
        for item in col:
            if item.strip() == field_to_sort:
                col_to_sort = item

        sorted_table = sort_table(table, col_to_sort)
        # alphabetical, so "no" comes before yes
        sorted_table.reverse()

        top_list = merge_tables(sorted_table)

        list_of_lines = build_lines(top_list)
        lines_to_write.append(list_of_lines)
        table_heights.append(table_height)
        col_lines.append(col_line)

    write_file(file_name, content, lines_to_write, col_lines, table_heights)
