import sys

import os
from clang.cindex import CompilationDatabase, CursorKind, Diagnostic, TranslationUnit, TypeKind, AccessSpecifier
from conversions import *
import main

current_location = None
current_out = None

def write_namespace(cursor, depth):
    write_out(depth, "namespace " + snake_to_pascal_case(cursor.spelling) + " ")
    write_out(depth, "{\n")
    process_children(cursor, depth)
    write_out(depth, "}\n")

def write_class(cursor, depth, has_template=False):
    if not has_template and cursor.displayname.find('<') > 0: # skip specialization
        return

    write_out(depth, "class " + snake_to_pascal_case(cursor.spelling) + "\n")
    write_out(depth, " : public " + get_full_name(cursor) + "\n")

    write_out(depth, " // from " + os.path.realpath(cursor.location.file.name) + ":" + str(cursor.location.line) + "\n")

    no_template_name = get_without_template(cursor.displayname)
    full_name = get_full_name(cursor)
    write_out(depth, "{\n")
    write_out(depth, "public:\n")
    write_out(depth + 1, "using " + full_name + "::" + no_template_name + ";\n")
    process_children(cursor, depth)
    write_out(depth, "};\n")

def write_method(cursor, depth):
    if cursor.access_specifier == AccessSpecifier.PUBLIC:
        if cursor.displayname[:8] != "operator":
            name = get_method_name(cursor.displayname)
            converted_name = snake_to_camel_case(name)
            named_args = get_method_named_args_def(cursor.displayname)
            call_str = get_full_name(cursor.semantic_parent) + "::" + get_method_call(cursor.displayname)
            has_result = (cursor.result_type.kind != TypeKind.VOID)

            if converted_name != name:
                write_out(depth, ("auto " if has_result else "void ") + converted_name + named_args + " {\n")
                write_out(depth + 1, ("return " if has_result else "")  + call_str + ";\n")
                write_out(depth, "}\n");



def write_class_template(cursor, depth):
    write_out(depth, get_template_decl(cursor) + "\n")
    write_class(cursor, depth, True)

def write_typedef(cursor, depth):
    converted_name = snake_to_pascal_case(cursor.displayname)
    write_out(depth, "typedef typename " + get_full_name(cursor.semantic_parent) + "::" + cursor.displayname + " " + converted_name + ";\n")

writers = {
    CursorKind.NAMESPACE.value: write_namespace,
    CursorKind.CLASS_DECL.value: write_class,
    #CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION.value: write_class_template_spe,
    CursorKind.CLASS_TEMPLATE.value: write_class_template,
    CursorKind.CXX_METHOD.value: write_method,
    CursorKind.TYPEDEF_DECL.value: write_typedef
}

def process_cursor(cursor, depth):
    global current_location
    if not current_location or str(current_location.file) != str(cursor.location.file):
        current_location = cursor.location

        main.debug("  processing " + os.path.realpath(current_location.file.name))

        if not main.args.output:
            if current_out:
                current_out.close()
            open_file(current_location.file.name)
    if cursor.location.file:
        if is_definition(cursor):
            if cursor.displayname:
                if cursor.displayname[0] != '_' and cursor.kind.value in writers:
                    writers[cursor.kind.value](cursor, depth)


def process_children(cursor, depth):
    for c in cursor.get_children():
        process_cursor(c, depth + 1)

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

def open_file(file_name, full_path=True):
    global current_out
    real_path = os.path.realpath(file_name) if full_path else file_name
    out_path = "out/" + real_path
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))

    current_out = open(out_path, "wb")
    current_out.write("/* Generated with code-stylizer - https://github.com/gogoprog/code-stylizer */\n")

def write_out(depth, what):
    for d in range(0, depth):
        current_out.write('    ')
    current_out.write(what)

def get_full_name(cursor):
    current = cursor
    result = ""
    while current and current.kind != CursorKind.TRANSLATION_UNIT:
        if has_template(current) and has_template(current.semantic_parent):
            result = "::template " + current.displayname + result
        else:
            result = "::" + current.displayname + result
        current = current.semantic_parent
    return result

def has_template(cursor):
    return cursor.displayname.find('<') > 0

def get_template_decl(cursor):
    result = "template<"
    first = True
    for child in cursor.get_children():
        if child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
            if not first:
                result += ", "
            result += "typename " + child.displayname
            first = False

    result += ">"
    return result
