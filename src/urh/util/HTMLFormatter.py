INDENT_WIDTH_PX = 20


def monospace(string):
    return "<samp>" + string + "</samp>"


def indent_string(string, depth=1):
    width = depth * INDENT_WIDTH_PX
    return '<table style="margin-left: {0}px;" border=0><tr><td>{1}</td></tr></table>'.format(
        width, string
    )


def mark_differences(value: str, compare_against: str):
    result = []
    for i, char in enumerate(value):
        try:
            if char != compare_against[i]:
                result.append('<font color="red">{}</font>'.format(char))
            else:
                result.append(char)
        except IndexError:
            result.append(char)

    return "".join(result)


def align_expected_and_got_value(expected: str, got: str, align_depth=1):
    width = align_depth * INDENT_WIDTH_PX
    got_marked = mark_differences(got, expected)
    return (
        '<table style="margin-left: {0}px;" border=0>'
        "<tr><td>Expected: </td><td>{1}</td></tr><tr><td>Got: </td><td>{2}</td> </tr>"
        "</table>".format(width, monospace(expected), monospace(got_marked))
    )
