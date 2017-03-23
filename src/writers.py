from clang.cindex import CompilationDatabase, CursorKind, Diagnostic, TranslationUnit, TypeKind, AccessSpecifier
from conversions import *

def write_namespace(out, entry):
    out.write("namespace " + entry.name + " {\n")
    process_entry(out, entry)
    out.write("}\n")

def write_class(out, entry):
    out.write("class " + snake_to_pascal_case(entry.cursor.spelling) + " : ")
    if len(entry.bases) > 0:
        if entry.bases[0].displayname[0] != "_":
            out.write("public " + snake_to_pascal_case(entry.bases[0].displayname) + ", ")

    out.write("public " + entry.name)

    out.write(" {\n")

    out.write("public:\n\tusing " + entry.name + "::" + entry.name + ";\n")
    process_entry(out, entry)
    out.write("}\n")

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
    out.write("template<TODO>\n")
    write_class(out, entry)

def write_class_template_spe(out, entry):
    out.write("template<>\n")
    write_class(out, entry)

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