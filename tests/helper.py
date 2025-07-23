import requests

def print_response(response: requests.Response) -> None:
    print(response.status_code)
    print(response.content)
    print()
