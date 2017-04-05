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
    file_name = "/tmp/stl-stylizer." + name + ".cpp"

    os.chdir(initialCwd)
    out = open(file_name, "wb")
    out.write("#include \"" + header + "\"\nint main(int argc, char *argv[]) { return EXIT_SUCCESS; }")
    out.close()

    if args.output:
        writers.open_file(args.output[0], False)

    start_process([file_name])

def clang_default_include():
    sub = subprocess.Popen(['clang', '-v', '-x', 'c++', '-'],
                           stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _, out = sub.communicate('')
    reg = re.compile('lib/clang.*/include$')
    return next(line.strip() for line in out.split('\n') if reg.search(line))

def start_process(compiler_command_line):
    index = clang.cindex.Index.create()

    compiler_command_line = ['-I', clang_default_include()] + compiler_command_line

    try:
        start = time.time()
        tu = index.parse(None, compiler_command_line, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        debug("  clang parse took %.2fs" % (time.time() - start))
    except Exception:
        debug(traceback.format_exc())
        error("Clang failed to parse '%s'" % " ".join(compiler_command_line))

    errors = [d for d in tu.diagnostics if d.severity in (Diagnostic.Error, Diagnostic.Fatal)]

    if len(errors) > 0:
        debug("\n".join([d.spelling for d in errors]))
        error("File '%s' failed clang's parsing and type-checking" % tu.spelling)

    start = time.time()
    for c in tu.cursor.get_children():
        writers.process_cursor(c, 0)
    debug("  generation took %.2fs" % (time.time() - start))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate C++ wrapper for any header in different coding style.",
        usage="\ncode-stylizer [options] <header files>")

    parser.add_argument("-v", "--verbose", action="store_true", help="enable debugging output")
    parser.add_argument("-o", "--output", nargs=1, help="pack in one output file")
    parser.add_argument("--version", action="version", version="stl-stylizer 0.1")
    parser.add_argument("headers", nargs="+", help="Headers to wrap")

    return parser.parse_args(argv[1:])

def debug(s):
    if args.verbose:
        sys.stderr.write(s + "\n")

def warn(s):
    sys.stderr.write("%s: Warning: %s\n" % (os.path.basename(sys.argv[0]), s))

def error(s):
    sys.stderr.write("%s: Error: %s\n" % (os.path.basename(sys.argv[0]), s))
    sys.exit(1)
