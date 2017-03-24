from clang.cindex import CompilationDatabase, CursorKind, Diagnostic, TranslationUnit, TypeKind, AccessSpecifier
from conversions import *

def write_namespace(out, entry):
    out.write("namespace " + snake_to_pascal_case(entry.cursor.spelling) + " {\n")
    out.write("using namespace " + entry.cursor.spelling + ";\n")
    process_entry(out, entry)
    out.write("}\n")

def write_class(out, entry):
    out.write("class " + snake_to_pascal_case(entry.cursor.spelling) + " : ")
    if len(entry.bases) > 0:
        if entry.bases[0].displayname[0] != "_":
            write_base(out, entry.bases[0])
        else:
            out.write("public " + entry.name)
    else:
        out.write("public " + entry.name)

    out.write(" // from " + entry.cursor.location.file.name + ":" + str(entry.cursor.location.line));
    out.write("\n{\n")

    no_template_name = get_without_template(entry.name)
    out.write("public:\n\tusing " + no_template_name + "::" + no_template_name + ";\n")
    process_entry(out, entry)
    out.write("};\n")

def write_method(out, entry):
    if entry.cursor.access_specifier == AccessSpecifier.PUBLIC:
        if entry.name[:8] != "operator":
            name = get_method_name(entry.name)
            named_args = get_method_named_args_def(entry.name)
            call_str = get_method_call(entry.name)
            has_result = (entry.cursor.result_type.kind != TypeKind.VOID)

            out.write("\t" + ("auto " if has_result else "void ") + snake_to_camel_case(entry.name) + named_args
                    + " {\n\t\t" + ("return " if has_result else "")  + call_str + ";\n\t}\n")


def write_class_template(out, entry):
    out.write(entry.get_template_decl())
    out.write("\n")
    write_class(out, entry)

def write_class_template_spe(out, entry):
    pass

def write_base(out, cursor):
    result = cursor.displayname
    if result[:6] == "class ":
        result = result[6:]

    results = result.split("::")

    result = ""

    for r in results:
        result += "::" + snake_to_pascal_case(r)

    out.write("public " + result)

writers = {
    CursorKind.NAMESPACE.value: write_namespace,
    CursorKind.CLASS_DECL.value: write_class,
    CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION.value: write_class_template_spe,
    CursorKind.CLASS_TEMPLATE.value: write_class_template,
    CursorKind.CXX_METHOD.value: write_method
}

def process_entry(out, entry):
    for child_entry in entry.children:
        if child_entry.name and child_entry.name[0] != '_' and child_entry.cursor.kind.value in writers:
            writer = writers[child_entry.cursor.kind.value]
            writer(out, child_entry)