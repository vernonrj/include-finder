"""
Get include structure from C/C++ source files
"""
import os

class Include(object):
    """
    include information for a file.
    """
    def __init__(self, filename, path=None):
        """populate file information on path"""
        if not path:
            self._file = os.path.basename(filename)
            self._path = os.path.dirname(filename)
        else:
            self._file = filename
            self._path = path
        self._incs = self._find_includes()
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
    def _find_includes(self):
        """
        find all includes in file
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
        try:
            with open(self.abspath) as fptr:
                lines = fptr.readlines()
        except IOError:
            return []
        # find all include lines
        lines = [x for x in lines if '#include' in x]
        includes = set()
        # strip off everything except file names
        for inc_raw in lines:
            try:
                inc = take_inside(inc_raw, '<', '>')
            except KeyError:
                inc = take_inside(inc_raw, '"')
            includes.add(inc.strip())
        return includes


