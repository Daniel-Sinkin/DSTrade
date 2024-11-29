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
    current_function = None
    for item in split:
        if current_function == "ANALYTICS_FIXED_WINDOW":
            current_function = "__SKIP"
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
            if current_function == "__SKIP":
                continue
            if "Required:" in item:
                param = item.replace(" ", "").replace("❚Required:", "").strip()
                if param not in current_group["required"]:
                    current_group["required"].append(param)
            elif "Optional:" in item:
                param = item.replace(" ", "").replace("❚Optional:", "").strip()
                if param == "time_fromandtime_to":
                    current_group["optional"].append("time_from")
                    current_group["optional"].append("time_to")
                elif param != "datatype" and param not in current_group["optional"]:
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

    print(f"Generating {len(grouped_dict)} api functions.")
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
                f"            + ([{f_string}] if {arg} is not None else [])"
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
            ]
{req_args_optional}
            + ([f"datatype={brace_L}datatype{brace_R}"] if datatype != \"json\" else []),
            **kwargs
        )
    """
        av_integration_py += args_required

    av_integration_py += "\n"
    av_integration_py += (
        "    def get_analytics_fixed_window(self, *args, **kwargs) -> None:\n"
    )
    av_integration_py += "        raise NotImplementedError('The multiple RANGE argument is currently not supported!')\n"
    av_integration_py += "\n"

    # Either no arguments at all (not automatically supported), or function not given in documentation
    av_integration_py += """
    def get_global_quote(
        self,
        symbol,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="GLOBAL_QUOTE",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
        )
    
    def get_market_status(
        self,
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="MARKET_STATUS",
            **kwargs
        ) 
    
    def get_top_gainers_losers(
        self,
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="TOP_GAINERS_LOSERS",
            **kwargs
        ) 

    def get_real_gdp_per_capita(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="REAL_GDP_PER_CAPITA",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    
    def get_inflation(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="INFLATION",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    
    def get_retail_sales(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="RETAIL_SALES",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    
            
    def get_durables(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="DURABLES",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    
                    
    def get_unemployment(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="UNEMPLOYMENT",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    
                            
    def get_nonfarm_payroll(
        self,
        datatype: Literal[\"json\", \"csv\"] = \"json\",
        **kwargs
    ) -> Optional[dict[str, any]]:
        return self.send_request(
            function="NONFARM_PAYROLL",
            request_args = []
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs
        ) 
    """

    print("Saving to file.")
    with open(Path("util").joinpath("av_integration.py"), "w") as file:
        file.write(av_integration_py)


if __name__ == "__main__":
    main()
