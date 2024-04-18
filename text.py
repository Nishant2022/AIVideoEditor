
def center_concat(input_lines: list) -> str:
    """
    Takes a list of strings and concatinates and centers each line.

    Inputs:
        input_lines: list - contains strings to be concatinated

    Output: str - concatinated string

    """
    max_line_len = max(len(i) for i in input_lines)
    output = ""
    for line in input_lines:
        output += line.center(max_line_len) + "\n"
    return output


if __name__ == '__main__':
    print(center_concat(['temp', 'hello world']))
