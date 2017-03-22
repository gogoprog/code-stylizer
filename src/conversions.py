
def get_method_name(displayname):
    return displayname[:displayname.index('(')]

def get_method_named_args_def(displayname):
    args = displayname[displayname.index('('):]

    if len(args) == 2:
        return args

    arg_index = 0
    index = 1
    previous_index = 1
    result = '('
    while index != -1:
        index = args.find(',', index)

        template_index = args.find('<', previous_index, index)

        if template_index != -1:
            index = args.find('>', template_index)
            index = args.find(',', index)

        if index == -1:
            break

        result += args[previous_index:index]
        result += " " + chr(ord('a') + arg_index) + ","
        index += 1
        previous_index = index
        arg_index += 1

    index = args.find(')', index)
    result += args[previous_index:index]
    result += " " + chr(ord('a') + arg_index) + ')'

    return result

def get_method_call(displayname):
    args = displayname[displayname.index('('):]

    if len(args) == 2:
        return displayname

    count = args.count(',') + 1

    result = get_method_name(displayname) + '('
    for i in range(0, count):
        result += chr(ord('a') + i)
        if i != count - 1:
            result += ', '
    result += ')'

    return result

def snake_to_camel_case(input):
    words = input.split('_')
    result = ""
    first = True
    for w in words:
        result += w[:1] if first else w[:1].upper()
        result += w[1:]
        first = False
    return result

def snake_to_pascal_case(input):
    words = input.split('_')
    result = ""
    for w in words:
        result += w[:1].upper()
        result += w[1:]
    return result
