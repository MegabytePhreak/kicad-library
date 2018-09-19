__author__ = 'MegabytePhreak'

import re


class ParseError(Exception):
    pass


class FieldNotFoundException(Exception):
    pass


def tokenize(line):

    tokens = []
    start = 0
    quoted = False
    escaped = False
    in_tok = False
    for pos, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == ' ' and not quoted:
            if in_tok:
                tokens.append(line[start:pos])
                in_tok = False
            start = pos + 1
        elif char == '"':
            in_tok = True
            quoted = not quoted
        else:
            in_tok = True
    if in_tok:
        tokens.append(line[start:])

    return tokens


def quote(s, if_needed=False):
    if (not if_needed) or re.search(r'[\s"]', s):
        chars = ['"']
        for char in s:
            if char == '"' or char == '\\':
                chars.append('\\')
            chars.append(char)
        chars.append('"')
        return "".join(chars)

    return s


def unquote(s):

    if '"' in s:
        # TODO: simple approach for now. Need to handle escapes
        s = s.strip('"')

    if s.find('\\'):
        escaped = False
        s2 = []
        for char in s:
            if escaped:
                escaped = False
                s2.append(char)
            else:
                if char == '\\':
                    escaped = True
                else:
                    escaped = False
                    s2.append(char)
        s = ''.join(s2)

    return s


class Symbol:
    @staticmethod
    def load_from_string(text):
        return Symbol(text.split('\n'))

    def __init__(self, lines):
        self._lines = lines

    def _find_def(self):
        for lineno, line in enumerate(self._lines):
            if line.startswith('DEF '):
                return lineno
        raise ParseError("DEF not found in symbol '%s'", self)

    def _find_field_or_last(self, name):
        last = None
        for lineno, line in enumerate(self._lines):
            if line[0] == 'F':
                last = lineno
                if name == 'Reference':
                    if line.startswith('F0 '):
                        break
                elif name == 'Name':
                    if line.startswith('F1 '):
                        break
                elif name == 'Footprint':
                    if line.startswith('F2'):
                        break
                elif name == 'Datasheet':
                    if line.startswith('F3'):
                        break
                else:
                    tokens = tokenize(line)
                    if len(tokens) >= 10:
                        #print(quote(name), tokens[9])
                        if tokens[9] == quote(name):
                            break
        else:
            return (None, last)
        return (lineno, last)

    def _find_field_or_except(self, name):
        lineno, last = self._find_field_or_last(name)
        if lineno is None:
            raise FieldNotFoundException(
                "Unable to find field '%s' in symbol '%s'", name, self)

        return lineno

    def set_or_add_field(self, name, value):
        lineno, last = self._find_field_or_last(name)

        if lineno is not None:
            self.set_field(name, value)

        else:
            tokens = tokenize(self._lines[last])
            id = int(tokens[0][1:]) + 1
            tokens = [
                'F%d' % id,
                quote(value), '0', '0', '50', 'H', 'I', 'L', 'CNN',
                quote(name)
            ]
            #tokens[0] = 'F%d' % id
            #tokens[1] = quote(value)
            #tokens[6] = 'I'
            #tokens[9] = quote(name)

            self._lines.insert(last + 1, " ".join(tokens))

    def set_visible(self, name, visible):
        lineno = self._find_field_or_except(name)

        tokens = tokenize(self._lines[lineno])
        tokens[6] = 'V' if visible else 'I'
        self._lines[lineno] = " ".join(tokens)

    def has_field(self, name):
        lineno, last = self._find_field_or_last(name)
        if lineno is None:
            return False
        return True

    def set_field(self, name, value, force=False):
        if not force:
            if name == 'Name':
                return self.set_name(value)
            elif name == 'Reference':
                return self.set_reference(value)

        lineno = self._find_field_or_except(name)

        tokens = tokenize(self._lines[lineno])
        tokens[1] = quote(value)
        self._lines[lineno] = " ".join(tokens)

    def get_field(self, name):
        lineno = self._find_field_or_except(name)

        tokens = tokenize(self._lines[lineno])
        return unquote(tokens[1])

    def set_name(self, name):
        self.set_field('Name', name, force=True)
        lineno = self._find_def()
        tokens = tokenize(self._lines[lineno])

        tokens[1] = quote(name, if_needed=True)

        self._lines[lineno] = " ".join(tokens)

    def set_reference(self, name):
        self.set_field('Reference', name, force=True)
        lineno = self._find_def()
        tokens = tokenize(self._lines[lineno])

        tokens[2] = quote(name, if_needed=True)

        self._lines[lineno] = " ".join(tokens)

    def serialize(self):
        return "\n".join(self._lines)


def load_lib(f):

    symbols = []
    filename = f.filename if hasattr(f, 'filename') else '<unknown>'

    lines = f.readlines()
    start = None
    for lineno, line in enumerate(lines):
        if line.startswith('DEF '):
            if start is not None:
                raise ParseError('%s:%d: Nested DEF', filename, lineno + 1)
            else:
                start = lineno
        elif line.startswith('ENDDEF'):
            if start is not None:
                symbols.append(
                    Symbol([x.strip() for x in lines[start:lineno + 1]]))
                start = None
            else:
                raise ParseError('%s:%d: Unexpected ENDDEF', filename,
                                 lineno + 1)

    return symbols
