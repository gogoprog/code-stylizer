import argparse
import os
import sys
import time
import traceback
import collections
import subprocess
import re
from os.path import realpath
import clang.cindex
from clang.cindex import CursorKind, Diagnostic, TranslationUnit

from entry import Entry
import writers

class Tagger():
    def __init__(self):
        self.tags = {}
        self.current_file_name = None
        self.current_file_lines = None

    def tag(self, cursor, tagname):
        if self.current_file_name != realpath(cursor.location.file.name):
            self.current_file_name = realpath(cursor.location.file.name)
            debug("  opening " + self.current_file_name)
            with open(self.current_file_name) as f:
                self.current_file_lines = f.readlines()

        if self.current_file_name not in self.tags:
            self.tags[self.current_file_name] = set()

        return self.tags[self.current_file_name].add((
            self.current_file_lines[cursor.location.line - 1].rstrip(),
            tagname,
            cursor.location.line,
            cursor.location.offset))

def main(argv):
    global args
    global initialCwd

    args = parse_args(argv)
    initialCwd = os.getcwd()

    for header in args.headers:
        process_header(header)

def process_header(header):
    name = os.path.basename(header)
    debug("  processing <" + name + "> header")
    tagger = Tagger()
    root_entry = Entry("$root")
    file_name = "/tmp/stl-stylizer." + name + ".cpp"

    os.chdir(initialCwd)
    out = open(file_name, "wb")
    out.write("#include \"" + header + "\"\nint main(int argc, char *argv[]) { return EXIT_SUCCESS; }")
    out.close()

    do_tags([file_name], tagger, root_entry)

    if not os.path.exists("out"):
        os.makedirs("out")

    out = open("out/" + name + ".h", "wb")
    out.write("/* Generated with code-stylizer - https://github.com/gogoprog/code-stylizer */\n")
    writers.process_entry(out, root_entry)
    out.close()

    print("  generated out/" + name + ".h")

    os.chdir(initialCwd)

def clang_default_include():
    sub = subprocess.Popen(['clang', '-v', '-x', 'c++', '-'],
                           stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _, out = sub.communicate('')
    reg = re.compile('lib/clang.*/include$')
    return next(line.strip() for line in out.split('\n') if reg.search(line))

def do_tags(compiler_command_line, tagger, root_entry):
    index = clang.cindex.Index.create()

    compiler_command_line = ['-I', clang_default_include()] + compiler_command_line

    try:
        start = time.time()
        tu = index.parse(None, compiler_command_line, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        debug("  clang parse took %.2fs" % (time.time() - start))
    except Exception:
        debug(traceback.format_exc())
        error("Clang failed to parse '%s'" % " ".join(compiler_command_line))

    errors = [d for d in tu.diagnostics
              if d.severity in (Diagnostic.Error, Diagnostic.Fatal)]
    if len(errors) > 0:
        debug("\n".join([d.spelling for d in errors]))
        error("File '%s' failed clang's parsing and type-checking" %
              tu.spelling)

    start = time.time()
    for c in tu.cursor.walk_preorder():
        do_cursor(c, tagger, root_entry)
    debug("  tag generation took %.2fs" % (time.time() - start))

def do_cursor(cursor, tagger, root_entry):
    global lastEntry

    if is_definition(cursor):
        parents = semantic_parents(cursor)
        direct_parent = root_entry

        for p in parents:
            if not direct_parent.has_child(p.displayname):
                direct_parent = direct_parent.add_child(Entry(p.displayname, p))
            else:
                direct_parent = direct_parent.children_map[p.displayname]

        name = cursor.displayname

        if not direct_parent.has_child(name):
            lastEntry = Entry(name, cursor)
            direct_parent.add_child(lastEntry)
        else:
            lastEntry = direct_parent.children_map[name]
            lastEntry.cursor = cursor

        tagger.tag(cursor, name)

    if cursor.kind == CursorKind.CXX_BASE_SPECIFIER:
        lastEntry.bases.append(cursor)

def is_definition(cursor):
    return (
        (cursor.is_definition() and not cursor.kind in [
            CursorKind.CXX_ACCESS_SPEC_DECL,
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.UNEXPOSED_DECL,
            ]) or
        # work around bug (?) whereby using PARSE_SKIP_FUNCTION_BODIES earlier
        # causes libclang to report cursor.is_definition() as false for
        # function definitions.
        cursor.kind in [
            CursorKind.FUNCTION_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.FUNCTION_TEMPLATE,
            ])

def semantic_parents(cursor):
    p = collections.deque()
    c = cursor.semantic_parent
    while c and is_named_scope(c):
        p.appendleft(c)
        c = c.semantic_parent
    return list(p)

def should_tag_children(cursor):
    return is_named_scope(cursor) or cursor.kind in [
        # 'extern "C" { ... }' should be LINKAGE_SPEC but is UNEXPOSED_DECL
        CursorKind.UNEXPOSED_DECL,
        ]

def is_named_scope(cursor):
    return cursor.kind in [
        CursorKind.NAMESPACE,
        CursorKind.STRUCT_DECL,
        CursorKind.UNION_DECL,
        CursorKind.ENUM_DECL,
        CursorKind.CLASS_DECL,
        CursorKind.CLASS_TEMPLATE,
        CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
        ]

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate C++ wrapper for any header in different coding style.",
        usage="\ncode-stylizer [options] <header files>")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable debugging output")
    parser.add_argument("--version", action="version",
                        version="stl-stylizer 0.1")
    parser.add_argument("headers", nargs="+", help="Headers to wrap")

    a = parser.parse_args(argv[1:])

    return a

def debug(s):
    if args.verbose:
        sys.stderr.write(s + "\n")

def warn(s):
    sys.stderr.write("%s: Warning: %s\n" % (os.path.basename(sys.argv[0]), s))

def error(s):
    sys.stderr.write("%s: Error: %s\n" % (os.path.basename(sys.argv[0]), s))
    sys.exit(1)
