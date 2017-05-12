import type_parser
from conversions import Case

def main():
    print("type_parser tests:")
    input_string = "my_namespace::std::hash_map<int, std::string<wide_char>>"
    my_type = type_parser.parse(input_string)
    print("input:  " + input_string)
    print("pascal: " + my_type.get_parented_string(Case.PASCAL))
    print("camel:  " + my_type.get_parented_string(Case.CAMEL))

main()
