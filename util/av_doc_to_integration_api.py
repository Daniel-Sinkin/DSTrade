import io
import sys

import bs4
import requests

LBRACE = "{"
RBRACE = "}"

url = "https://www.alphavantage.co/documentation/"


def process_section(
    section: bs4.element.Tag,
) -> tuple[str, dict[str, dict[str, str | list[str]]]]:
    section_title = section.find("h2").text
    # print("Section Title:", section_title)

    collection = {}
    contents = [
        c for c in section.contents if c != "\n" and not str(c).startswith("<br/")
    ]
    i = 0
    while True:
        try:
            while not str(contents[i]).startswith("<h4"):
                i += 1
        except IndexError:
            break
        func_name = contents[i].text
        id_ = contents[i].get("id")
        if func_name.startswith("Quote Endpoint"):
            func_name = "GLOBAL_QUOTE"

        i += 1
        descr = []
        while str(contents[i]).startswith("<p"):
            if contents[i].text != "":
                descr.append(contents[i].text.strip())
            i += 1
        description = "\n".join(descr)

        assert str(contents[i]) == "<h6><b>API Parameters</b></h6>"
        i += 1
        reqs = []
        opts = []
        while True:
            if str(contents[i]) == "<p><b>❚ Required: <code>apikey</code></b></p>":
                i += 2
                break
            argument = str(contents[i].find("code").text)
            if argument == "function":
                code = contents[i + 1].find("code")
                if code is not None:
                    func_name = code.text.split("=")[1]
                i += 2
                continue

            lines = []
            is_req = str(contents[i]).startswith("<p><b>❚ Required: ")
            i += 1
            while "❚" not in str(contents[i]):
                lines.append(contents[i].text)
                i += 1

            annotated_content = [argument, "\n".join(lines)]
            if is_req:
                reqs.append(annotated_content)
            else:
                opts.append(annotated_content)

        assert func_name is not None
        collection[func_name] = {
            "description": description,
            "id": id_,
            "args_required": reqs,
            "args_optional": opts,
        }
        func_name = None
    return section_title, collection


def format_opt_request_arg(arg: str) -> str:
    return f'([f"{arg}={LBRACE}{arg}{RBRACE}"] if {arg} is not None else [])'


def format_opt_arg(arg: str) -> str:
    return f"{arg}:Optional[any]=None"


def write_processed_dict_to_script(section_dict) -> None:
    output_stream = io.StringIO()

    original_stdout = sys.stdout
    sys.stdout = output_stream

    try:
        for section, dict_ in section_dict.items():
            print("    ", "#" * (len(section) + 4), sep="")
            print("    ", "# ", section, " #", sep="")
            print("    ", "#" * (len(section) + 4), sep="")

            print()
            for k, v in dict_.items():
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
                for line in v["description"].splitlines():
                    print("", line, sep="")
                for arg, desc in v["args_required"]:
                    print(f"### {arg} (required)")
                    print(f"{desc}")
                for arg, desc in v["args_optional"]:
                    print(f"### {arg} (optional)")
                    print(f"{desc}")
                print('        """')
                request_args_optional = (
                    f" + {' + '.join(args_opt_request)}"
                    if len(args_opt_request) > 0
                    else ""
                )
                print(f"""
            return self._send_request(
                function="{k}",
                request_args=[{','.join(args_req_request)}]{request_args_optional},
                **kwargs
            )
                """)
    finally:
        sys.stdout = original_stdout

    python_code = output_stream.getvalue()

    with open("util/_av_integration_api_base.py", "r") as file:
        code_base = file.read()
    with open("test_output.py", "w") as file:
        file.write(code_base + "\n" + python_code)


def main() -> None:
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError("Failed to get HTML documentation from AlphaVantage!")

    soup = bs4.BeautifulSoup(response.text, "html.parser")

    sections = soup.find_all("section")
    section_dict = {}
    for section in sections:
        section_title, collection = process_section(section)
        if section_title == "Digital & Crypto Currencies":
            del collection[
                "CURRENCY_EXCHANGE_RATE"
            ]  # This is duplicated, also appears in FX
        section_dict[section_title] = collection


if __name__ == "__main__":
    main()
