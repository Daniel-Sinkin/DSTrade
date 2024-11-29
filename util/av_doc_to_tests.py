"""Takes the examples and makes rudimentary pytests out of them, mostly as a foundation to build more rigorous testing logic on top of."""

from pathlib import Path

import requests
from bs4 import BeautifulSoup

# URL of the Alpha Vantage documentation
url = "https://www.alphavantage.co/documentation/"


def main() -> None:
    # Fetch the page content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        raise RuntimeError

    request_base_url = "https://www.alphavantage.co/query?function="
    lines = [
        line for line in soup.text.splitlines() if line.startswith(request_base_url)
    ]

    examples: dict[str, list[dict[str, str]]] = {}
    for line in lines:
        split = line.removeprefix(request_base_url).split("&")[:-1]
        function = split[0]
        if function not in examples:
            examples[function] = []
        args = split[1:]
        examples[function].append(args)

    handler_name = "handler"
    filename = "test_av_integration.py"
    test_av_integration = f"from src.av_integration import AlphaVantageAPIHandler\n\n{handler_name}=AlphaVantageAPIHandler(api_key='demo')\n"
    for func, args in examples.items():
        test_av_integration += f"def test_{func.lower()}() -> None:\n"
        for arg in args:
            arg = [f'"{a}"' for a in arg]
            test_av_integration += f"    assert {handler_name}.get_{func.lower()}({', '.join(arg)}) is not None\n"
        test_av_integration += "\n"
    with open(Path("util").joinpath(filename), "w") as file:
        file.write(test_av_integration)


if __name__ == "__main__":
    main()
