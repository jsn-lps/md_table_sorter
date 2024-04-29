table_delim = "|"


def open_markdown(file_name: str) -> list:
    with open(file_name, "r") as file:
        content = file.readlines()
        return content


def get_col_head(content: list) -> list | int:
    col = None
    col_line = 0
    for line in content:
        if line.startswith(table_delim) and col is None:
            head = line.lstrip(table_delim).rstrip("\n").rstrip(table_delim)
            col = head.split(table_delim)
            return col, col_line
        col_line += 1  # line based on 0 index


def map_table(col, col_line, content) -> list | int:
    lines = []
    head = col_line
    height = 2  # skips the |-----| line

    ptr = content[head + height]
    while ptr.startswith(table_delim):
        row = ptr.lstrip(table_delim).rstrip("\n").rstrip(table_delim).split(table_delim)

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

    table_height = height - 2
    return lines, table_height


def sort_table(table, column):
    return sorted(table, key=lambda d: d[column])


if __name__ == "__main__":
    content = open_markdown("alb-ec2-readme.md")

    col, col_line = get_col_head(content)
    table, table_height = map_table(col, col_line, content)

    # do an input here to find out which column to sort by
    col_to_sort = col[4]  # ' Required '

    sorted_table = sort_table(table, col_to_sort)
    # alphabetical, so "no" comes before yes
    sorted_table.reverse()

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

    list_of_lines = []
    for item in top_list:

        line = table_delim
        for k, v in item.items():
            line += v
            line += f" {table_delim} "
        line += "\n"
        list_of_lines.append(line)

    writing_new_content = False
    items_written = 0
    with open('alb-ec2-readme copy.md', "w") as new_file:
        for index, line in enumerate(content):

            if writing_new_content is True:

                if items_written == table_height:
                    writing_new_content = False
                    new_file.write(line)
                    items_written = 0
                    continue

                new_file.write(list_of_lines[items_written])
                items_written += 1
                continue

            if index == col_line:
                print("found column")

                # building table header split bar
                split_line = ""
                for char in line:
                    if char == table_delim:
                        split_line += char
                        continue
                    split_line += "-"
                if split_line.endswith("-"):
                    split_line = split_line[:-1]

                split_line += "\n"
                new_file.write(line)
                new_file.write(split_line)

                writing_new_content = True
                continue

            if writing_new_content is False:
                new_file.write(line)
                continue
