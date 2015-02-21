#!/usr/bin/env python
"""
Note: this was taken from the gfam library on github, and modified to
accommodate my needs. I removed the dependencies on the gfam utilities and
error handling by making them more generic. In addition, I updated the
source to abide by PEP8 standards. Hail PEP8.

Source: https://github.com/ntamas/gfam/blob/master/gfam/go/obo.py

A very simple and not 100% compliant parser for the OBO file format.

This parser is supplied "as is"; it is not an official parser, it
might puke on perfectly valid OBO files, it might parse perfectly
invalid OBO files, it might steal your kitten or set your garden shed
on fire. Apart from that, it should be working, or at least
it should be in a suitable condition to parse the Gene Ontology,
which is my only test case anyway.

Usage example::

    import gfam.go.obo
    parser = gfam.go.obo.Parser(open("gene_ontology.1_2.obo"))
    gene_ontology = {}
    for stanza in parser:
        gene_ontology[stanza.tags["id"][0]] = stanza.tags
"""

__author__ = "Tamas Nepusz"
__email__ = "tamas@cs.rhul.ac.uk"
__copyright__ = "Copyright (c) 2009, Tamas Nepusz"
__license__ = "MIT"
__version__ = "0.1"


__all__ = ["Stanza", "Parser", "Value"]


from cStringIO import StringIO
import re
import tokenize


class Value(object):
    """Class representing a value and its modifiers in the OBO file

    This class has two member variables. `value` is the value itself,
    `modifiers` are the corresponding modifiers in a tuple. Currently
    the modifiers are not parsed in any way, but this might change in
    the future.
    """

    __slots__ = ["value", "modifiers"]

    def __init__(self, value, modifiers=()):
        self.value = str(value)
        if modifiers:
            self.modifiers = tuple(modifiers)
        else:
            self.modifiers = None

    def __str__(self):
        """Returns the value itself (without modifiers)"""
        return str(self.value)

    def __repr__(self):
        """Returns a Python representation of this object"""
        return "%s(%r, %r)" % (self.__class__.__name__,
                               self.value, self.modifiers)


class Stanza(object):
    """Class representing an OBO stanza.

    An OBO stanza looks like this::

      [name]
      tag: value
      tag: value
      tag: value

    Values may optionally have modifiers, see the OBO specification
    for more details. This class stores the stanza name in the
    `name` member variable and the tags and values in a Python
    dict called `tags`. Given a valid stanza, you can do stuff like
    this:

      >>> stanza.name
      "Term"
      >>> print stanza.tags["id"]
      ['GO:0015036']
      >>> print stanza.tags["name"]
      ['disulfide oxidoreductase activity']

    Note that the `tags` dict contains lists associated to each
    tag name. This is because theoretically there could be more than
    a single value associated to a tag in the OBO file format.
    """

    __slots__ = ["name", "tags"]

    def __init__(self, name, tags=None):
        self.name = name
        if tags:
            self.tags = dict(tags)
        else:
            self.tags = dict()

    def __repr__(self):
        """Returns a Python representation of this object"""
        return "%s(%r, %r)" % (self.__class__.__name__, self.name, self.tags)


class Parser(object):
    """The main attraction, the OBO parser."""

    def __init__(self, file_handle):
        """Creates an OBO parser that reads the given file-like object.
        If you want to create a parser that reads an OBO file, do this:

          >>> import gfam.go.obo
          >>> parser = gfam.go.obo.Parser(open("gene_ontology.1_2.obo"))

        Only the headers are read when creating the parser. You can
        access these right after construction as follows:

          >>> parser.headers["format-version"]
          ['1.2']

        To read the stanzas in the file, you must iterate over the
        parser as if it were a list. The iterator yields `Stanza`
        objects.
        """
        self.file_handle = open(file_handle)
        self.line_re = re.compile(r"\s*(?P<tag>[^:]+):\s*(?P<value>.*)")
        self.lineno = 0
        self.headers = {}
        self._extra_line = None
        self._read_headers()

    def _lines(self):
        """Iterates over the lines of the file, removing
        comments and trailing newlines and merging multi-line
        tag-value pairs into a single line"""
        while True:
            self.lineno += 1
            line = self.file_handle.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                yield line
                continue

            if line[0] == '!':
                continue
            if line[-1] == '\\':
                # This line is continued in the next line
                print line
                lines = [line[:-1]]
                finished = False
                while not finished:
                    self.lineno += 1
                    line = self.file_handle.readline()
                    if line[0] == '!':
                        continue
                    line = line.strip()
                    if line[-1] == '\\':
                        lines.append(line[:-1])
                    else:
                        lines.append(line)
                        finished = True
                line = " ".join(lines)
            else:
                try:
                    # Search for a trailing comment
                    comment_char = line.rindex("!")
                    line = line[0:comment_char].strip()
                except ValueError:
                    # No comment, fine
                    pass
            yield line

    def _parse_line(self, line):
        """Parses a single line consisting of a tag-value pair
        and optional modifiers. Returns the tag name and the
        value as a `Value` object."""
        match = self.line_re.match(line)
        if not match:
            return False
        tag, value_and_mod = match.group("tag"), match.group("value")

        # If the value starts with a quotation mark, we parse it as a
        # Python string -- luckily this is the same as an OBO string
        if value_and_mod and value_and_mod[0] == '"':
            gen = tokenize.generate_tokens(StringIO(value_and_mod).readline)
            for toknum, tokval, _, (_, ecol), _ in gen:
                if toknum == tokenize.STRING:
                    value = eval(tokval)
                    mod = (value_and_mod[ecol:].strip(), )
                    break
                raise RuntimeError("cannot parse string literal", self.lineno)
        else:
            value = value_and_mod
            mod = None

        value = Value(value, mod)
        return tag, value

    def _read_headers(self):
        """Reads the headers from the OBO file"""
        for line in self._lines():
            if not line or line[0] == '[':
                # We have reached the end of headers
                self._extra_line = line
                return
            key, value = self._parse_line(line)
            try:
                self.headers[key].append(value.value)
            except KeyError:
                self.headers[key] = [value.value]

    def stanzas(self):
        """Iterates over the stanzas in this OBO file,
        yielding a `Stanza` object for each stanza.
        Note: this was modified to ensure final term yielded - @jawrainey """
        stanza = None
        for line in self._lines():
            if not line:
                continue
            if 'Term' in line:
                stanza = Stanza(line[1:-1])
                if stanza:
                    yield stanza
                continue
            tag, value = self._parse_line(line)
            try:
                stanza.tags[tag].append(value)
            except KeyError:
                stanza.tags[tag] = [value]

    def __iter__(self):
        return self.stanzas()
