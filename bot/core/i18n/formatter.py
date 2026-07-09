from string import Formatter


def safe_format(template: str, replacements: dict[str, object]) -> str:
    formatter = Formatter()
    output = []
    for literal_text, field_name, _, _ in formatter.parse(template):
        output.append(literal_text)
        if field_name is None:
            continue
        value = replacements.get(field_name)
        if value is None:
            output.append("{" + field_name + "}")
            continue
        output.append(str(value))
    return "".join(output)
