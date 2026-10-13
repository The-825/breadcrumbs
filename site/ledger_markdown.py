"""Parse quoted source links and table cells used by the public research ledgers."""
import re


def cells(line):
    output, cell = [], []
    escaped = False
    for char in line.strip()[1:-1]:
        if char == '|' and not escaped:
            output.append(''.join(cell).strip())
            cell = []
        else:
            cell.append(char)
        escaped = char == '\\' and not escaped
    output.append(''.join(cell).strip())
    return output


def source_link(value):
    match = re.search(r'\["((?:\\.|[^"\\])+)"\]\(', value)
    if not match:
        return value, ''
    start, position, depth = match.end(), match.end(), 1
    while position < len(value):
        char = value[position]
        if char == '\\' and position + 1 < len(value):
            position += 2
            continue
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                url = value[start:position]
                if not re.match(r'https?://\S+$', url):
                    return value, ''
                unescape = lambda text: re.sub(r'\\([|()"\\])', r'\1', text)
                return unescape(match[1]), unescape(url)
        position += 1
    return value, ''
