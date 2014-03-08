"""
Get include structure from C/C++ source files
"""
import os
import unittest


class Include(object):
    """
    include information for a file.
    """
    def __init__(self, iterable, filename, path=None):
        """populate file information on path"""
        if not path:
            self._file = os.path.basename(filename)
            self._path = os.path.dirname(filename)
        else:
            self._file = filename
            self._path = path
        self._incs = _find_includes(iterable)
    @classmethod
    def from_file(cls, filename, path=None):
        """populate file information from a filepath"""
        try:
            with open(filename) as fileobj:
                return cls(fileobj, filename, path)
        except IOError:
            return cls([], filename, path)
    @property
    def file(self):
        """return the file name"""
        return self._file
    @property
    def path(self):
        """return the path"""
        return self._path
    @property
    def abspath(self):
        """return path/file"""
        return os.path.join(self.path, self.file)
    @property
    def includes(self):
        """return all files included by this file"""
        return list(self._incs)
    def __repr__(self):
        return self.file
    def __hash__(self):
        return hash(self.file)


def _find_includes(iterable):
    """
    find all includes in an iterable collection
    """
    def take_inside(text, open_char, close_char=None):
        """
        take text inside open and close chars.
        if close_char isn't specified, it is set to open_char
        """
        if not close_char:
            close_char = open_char
        if open_char not in text:
            raise KeyError('"%s" not in text' % open_char)
        text = text[text.find(open_char)+1:]
        if close_char not in text:
            raise KeyError('"%s" not in text' % close_char)
        return text[:text.find(close_char)]
    # find all include lines

    lines = [x for x in strip_comments(iterable) if '#include' in x]
    includes = set()
    # strip off everything except file names
    for inc_raw in lines:
        try:
            inc = take_inside(inc_raw, '<', '>')
        except KeyError:
            inc = take_inside(inc_raw, '"')
        includes.add(inc.strip())
    return includes


def strip_comments(iterable):
    """
    return an iterable that has block comments stripped out
    """
    in_comment = False
    for line in iterable:
        final_line = line
        if '*/' in final_line:
            in_comment = False
            final_line = final_line[final_line.find('*/'):]
        if '//' in final_line:
            final_line = final_line[:final_line.find('//')]
        if '/*' in final_line:
            in_comment = True
            final_line = final_line[:final_line.find('/*')]
        if not in_comment and final_line:
            yield final_line
    raise StopIteration


# disable the 'too many class methods' from unittest.TestCase
# pylint: disable=R0904

class IncludeTests(unittest.TestCase):
    """test the including mechanism"""
    def test_locate(self):
        """test valid #includes"""
        incs = ["good", "goodagain"]
        incs_it = iter(incs)
        inc_list = ['// #include<failcomment>',
                    '#include"%s"' % incs_it.next(),
                    '#include<%s> // blah' % incs_it.next()]
        include = Include(inc_list, 'file')
        self.failUnless(len(include.includes) == len(incs))
    def test_comments(self):
        """test to ensure includes handle comments correctly"""
        incs = ["good", "again"]
        incs_it = iter(incs)
        inc_list = ['// #include<failcomment>',
                    '#include"%s"' % incs_it.next(),
                    '/*#include<verybad>*/',
                    '/*',
                    '#include<insanelybad>',
                    '*/',
                    '#include<%s> // blah' % incs_it.next()]
        include = Include(inc_list, 'file')
        self.failUnless(len(include.includes) == len(incs))
    def test_sys_incs(self):
        """test #include<thing>"""
        incs = set(["good", "again"])
        incs_it = iter(incs)
        inc_list = ['#include<%s>' % incs_it.next(),
                    '#include <%s>' % incs_it.next()]
        include = Include(inc_list, 'file')
        self.failUnless(set(include.includes) == incs)


if __name__ == '__main__':
    unittest.main()


# EOF
