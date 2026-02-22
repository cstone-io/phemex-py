import json
from importlib.resources import files


def get_products() -> dict:
    """
    Simple helper function to retrieve product data from our locally stored processed JSON file.
    This is a robust-enough solution for now until we have full automation with the API.
    """
    data = files("phemex_py").joinpath("products.json").read_text(encoding="utf-8")
    return json.loads(data)
