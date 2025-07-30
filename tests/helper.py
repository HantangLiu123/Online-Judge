import requests
import json

def print_response(response: requests.Response) -> None:
    print(response.status_code)
    formatted_content = json.dumps(response.json(), indent=4, ensure_ascii=False)
    print(formatted_content)
    print()
