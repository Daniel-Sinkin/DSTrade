import io
import sys

import bs4
import requests

LBRACE = "{"
RBRACE = "}"

url = "https://www.alphavantage.co/documentation/"

response = requests.get(url)
if response.status_code != 200:
    raise RuntimeError("Failed to get HTML documentation from AlphaVantage!")

soup = bs4.BeautifulSoup(response.text, "html.parser")


def process_section(
    section: bs4.element.Tag,
) -> tuple[str, dict[str, dict[str, str | list[str]]]]:
    """
    Processes the section, returning a tuple consisting of the section name and a dict with
    keys

    * "description"
    * "id"
    * "examples"
    * "args_required"
    * "args_optional"

    for each API function in that section
    """
    section_title = section.find("h2").text

    function_map = {}
    contents = [
        c for c in section.contents if c != "\n" and not str(c).startswith("<br/")
    ]
    line_count = 0
    for _ in range(1000):
        try:
            while not str(contents[line_count]).startswith("<h4"):
                line_count += 1
        except IndexError:
            break
        func_name = contents[line_count].text
        id_ = contents[line_count].get("id")
        if func_name.startswith("Quote Endpoint"):
            func_name = "GLOBAL_QUOTE"

        line_count += 1
        descr = []
        while str(contents[line_count]).startswith("<p"):
            if contents[line_count].text != "":
                descr.append(contents[line_count].text.strip())
            line_count += 1
        description = "\n".join(descr)

        assert str(contents[line_count]) == "<h6><b>API Parameters</b></h6>"
        line_count += 1
        reqs = []
        opts = []
        for _ in range(100):
            if (
                str(contents[line_count])
                == "<p><b>❚ Required: <code>apikey</code></b></p>"
            ):
                line_count += 2
                break
            argument = str(contents[line_count].find("code").text)
            if argument == "function":
                code = contents[line_count + 1].find("code")
                if code is not None:
                    func_name = code.text.split("=")[1]
                line_count += 2
                continue

            lines = []
            is_req = str(contents[line_count]).startswith("<p><b>❚ Required: ")
            line_count += 1
            while "❚" not in str(contents[line_count]):
                lines.append(contents[line_count].text.strip())
                line_count += 1

            annotated_content = [argument, "\n".join(lines)]
            if is_req:
                reqs.append(annotated_content)
            else:
                opts.append(annotated_content)
        else:
            raise RuntimeError("Infinite Inner Section Loop Detected")

        assert contents[line_count].text.startswith("Example")
        line_count += 1

        examples = []
        for _ in range(100):
            if contents[line_count].text != "Language-specific guides":
                examples.append(contents[line_count].text)
                line_count += 1
            else:
                break
        else:
            raise RuntimeError("Infinite Inner section 2 loop detected.")
        if len(examples) > 0:
            examples = examples[:-1]

        assert contents[line_count].text == "Language-specific guides"
        line_count += 1
        assert str(contents[line_count]).startswith("<div>\n<button class=")

        assert func_name is not None
        function_map[func_name] = {
            "description": description,
            "id": id_,
            "examples": examples,
            "args_required": reqs,
            "args_optional": opts,
        }
        func_name = None
    else:
        raise RuntimeError("Infinite Outer Section Loop Detected")
    return section_title, function_map


def format_opt_request_arg(arg: str) -> str:
    return f'([f"{arg}={LBRACE}{arg}{RBRACE}"] if {arg} is not None else [])'


def format_opt_arg(arg: str) -> str:
    return f"{arg}:Optional[any]=None"


def print_function(k: str, v: dict[str, any]) -> None:
    args_req = [a[0] for a in v["args_required"]]
    args_req_str = ", ".join(args_req)
    args_req_request = [f'"{arg}={arg}"' for arg in args_req]

    args_opt = [a[0] for a in v["args_optional"]]
    args_opt_adj = [format_opt_arg(arg) for arg in args_opt]
    args_opt_str = ", ".join(args_opt_adj)
    args_opt_request = [format_opt_request_arg(arg) for arg in args_opt]

    args = ["self"]
    if args_req_str != "":
        args.append(args_req_str)
    if args_opt_str != "":
        args.append(args_opt_str)
    print(
        "    ",
        f"def get_{k.lower()}({','.join(args)},**kwargs) -> dict[str, any]:",
        sep="",
    )
    print('        """')
    print(f"https://www.alphavantage.co/documentation/#{v['id']}")
    for line_count in v["description"].splitlines():
        print("", line_count, sep="")
    for arg, desc in v["args_required"]:
        print(f"### {arg} (required)")
        print(f"{desc}")
    for arg, desc in v["args_optional"]:
        print(f"### {arg} (optional)")
        print(f"{desc}")
    print('        """')
    request_args_optional = (
        f" + {' + '.join(args_opt_request)}" if len(args_opt_request) > 0 else ""
    )
    print(f"""
        return self._send_request(
            function="{k}",
            request_args=[{','.join(args_req_request)}]{request_args_optional},
            **kwargs
        )
    """)


def print_section(section: str, section_dict: dict[str, dict[str, any]]) -> None:
    print("    ", "#" * (len(section) + 4), sep="")
    print("    ", "# ", section, " #", sep="")
    print("    ", "#" * (len(section) + 4), sep="")
    print()
    for func_name, func_dict in section_dict.items():
        print_function(func_name, func_dict)


def main() -> None:
    sections = soup.find_all("section")
    section_dict = {}
    for section in sections:
        section_title, collection = process_section(section)
        # Handle Duplicates
        if section_title == "Digital & Crypto Currencies":
            del collection["CURRENCY_EXCHANGE_RATE"]
        section_dict[section_title] = collection

    output_stream = io.StringIO()

    original_stdout = sys.stdout
    sys.stdout = output_stream

    try:
        for section, dict_ in section_dict.items():
            print_section(section, dict_)
    finally:
        sys.stdout = original_stdout

    python_code = output_stream.getvalue()

    with open("util/_av_integration_api_base.py", "r") as file:
        code_base = file.read()
    with open("testing.py", "w") as file:
        file.write(code_base + "\n" + python_code)


if __name__ == "__main__":
    main()
