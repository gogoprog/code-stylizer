import type_parser

def main():
    print("type_parser tests:")
    my_type = type_parser.parse("std::map<int, std::string>")
    print(my_type.get_parented_string())


main()