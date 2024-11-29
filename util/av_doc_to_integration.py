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

    main_content = soup.find("article")

    split = [
        line
        for line in main_content.text.splitlines()
        if (
            "❚ Required" in line
            and "❚ Required: function" not in line
            and "❚ Required: apikey" not in line
        )
        or "❚ Optional" in line
        or " function=" in line
    ]

    # Initialize variables
    grouped_dict = {}  # This will be the final dictionary
    current_group = {"required": [], "optional": []}
    current_function = None

    # Iterate through the list
    for item in split:
        if "function=" in item:
            # When a new function is found, save the current group under the previous function name
            if current_function and (
                current_group["required"] or current_group["optional"]
            ):
                grouped_dict[current_function] = current_group
                current_group = {"required": [], "optional": []}
            # Extract the new function name
            current_function = item.split("function=")[-1].strip()
        elif item.startswith("❚"):
            if "Required:" in item:
                param = item.replace(" ", "").replace("❚Required:", "").strip()
                if param not in current_group["required"]:
                    current_group["required"].append(param)
            elif "Optional:" in item:
                param = item.replace(" ", "").replace("❚Optional:", "").strip()
                if param != "datatype" and param not in current_group["optional"]:
                    current_group["optional"].append(param)

    # After the loop, save the last group under its function name
    if current_function and (current_group["required"] or current_group["optional"]):
        grouped_dict[current_function] = current_group

    brace_L = "{"
    brace_R = "}"
    iteration = 0

    av_integration_py = "from typing import Optional, Literal\n"
    with open(Path("util").joinpath("_av_integration_base.py"), "r") as file:
        av_integration_py = file.read()

    for k, v in grouped_dict.items():
        iteration += 1
        args_required = ""
        req_args_required = ""
        for i, arg in enumerate(v["required"]):
            args_required += f"    {arg},"
            req_args_required += f'            f"{arg}={brace_L}{arg}{brace_R}",'

            if i < len(v["required"]) - 1:
                args_required += "\n"
                req_args_required += "\n"

        args_optional = ""
        req_args_optional = ""
        for j, arg in enumerate(v["optional"]):
            args_optional += f"    {arg}=None,"
            f_string = f'f"{arg}={brace_L}{arg}{brace_R}"'
            req_args_optional += (
                f"            + ([{f_string}] if {arg} is None else [])"
            )
            if j < len(v["optional"]) - 1:
                args_optional += "\n"
                req_args_optional += "\n"

        args_required = f"""
    def get_{k.lower()}(
        self,
    {args_required}
    {args_optional}
        datatype: Literal["json", "csv"] = "json",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function=\"{k}\",
            request_args=[
    {req_args_required}
    {req_args_optional}
            ],
            **kwargs
        )
    """
        av_integration_py += args_required

    with open(Path("util").joinpath("av_integration_generated.py"), "w") as file:
        file.write(av_integration_py)


if __name__ == "__main__":
    main()
