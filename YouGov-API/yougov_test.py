
import os
import json
from urllib import response
from matplotlib.pylab import rint
import requests
from dotenv import load_dotenv

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

load_dotenv()

BASE_URL = "https://api.brandindex.com/v1"

EMAIL = os.getenv("YOUGOV_EMAIL")
PASSWORD = os.getenv("YOUGOV_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Missing YouGov credentials in .env file")

# Create a persistent session to retain authentication cookies
session = requests.Session()

session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json"
})


# --------------------------------------------------
# 2. Authenticate
# --------------------------------------------------

def authenticate():

    url = f"{BASE_URL}/auth/login"

    payload = {
        "meta": {"version": "v1"},
        "data": {
            "email": EMAIL,
            "password": PASSWORD
        }
    }

    print("\nAuthenticating with YouGov...")

    response = session.post(
        url,
        json=payload,
        timeout=30
    )

    print("Login status:", response.status_code)

    if response.status_code != 200:
        print("Authentication failed:")
        print(response.text)
        return False

    print("Authentication successful!")

    # Show cookie names, but never expose their values
    print("Session cookies:", list(session.cookies.keys()))


    print("\nSession diagnostics:")
    print("Cookies:", session.cookies.get_dict())
    print("Request headers:", {
        k: v for k, v in session.headers.items()
        if k.lower() != "authorization"
    })

    return True




# --------------------------------------------------
# 3. Submit BrandIndex query
# --------------------------------------------------

def run_analysis():

    url = f"{BASE_URL}/analyses/execute"

    payload = {
        "meta": {"version": "v1"},
        "data": {
            "queries": [
                {
                    "id": "first-query",

                    "entity": {
                        "region": "us",
                        "sector_id": 1,
                        "brand_id": 1007
                    },

                    "period": {
                        "start_date": {
                            "date": "2024-01-01"
                        },
                        "end_date": {
                            "date": "2024-01-31"
                        }
                    },

                    "metrics_score_types": {
                        "buzz": "net_score"
                    },

                    "filters": []
                }
            ]
        }
    }

    print("\nSubmitting BrandIndex query...")

    response = session.post(
        url,
        json=payload,
        timeout=60
    )

    print("Cookies sent:", response.request.headers.get("Cookie"))
    print("Request URL:", response.request.url)

    print("Analysis status:", response.status_code)

    if response.status_code != 200:
        print("Analysis request failed:")
        print(response.text)
        return

    print("\nAnalysis successful!")

    results = response.json()

    print("\nAPI Response:")
    print(json.dumps(results, indent=4))

    # Save response for inspection
    with open("yougov_response.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nResponse saved to yougov_response.json")




def test_authentication():

    url = f"{BASE_URL}/taxonomies/regions"

    print("\nTesting authenticated GET request...")

    # Prepare request to inspect the actual outgoing headers
    request = requests.Request("GET", url)
    prepared = session.prepare_request(request)

    print("\nOutgoing request diagnostics:")
    print("URL:", prepared.url)
    print("Cookie attached:", "Cookie" in prepared.headers)

    # Display cookie names only, never values
    cookie_header = prepared.headers.get("Cookie", "")
    cookie_names = [
        item.split("=")[0]
        for item in cookie_header.split(";")
        if "=" in item
    ]

    print("Cookie names:", cookie_names)

    # Inspect cookie metadata
    for cookie in session.cookies:
        print({
            "name": cookie.name,
            "domain": cookie.domain,
            "path": cookie.path,
            "secure": cookie.secure
        })

    # Execute the request
    response = session.send(prepared, timeout=30)

    print("\nGET status:", response.status_code)

    if response.status_code == 200:
        print("SUCCESS: Session authentication is working!")
        print(json.dumps(response.json(), indent=4))
    else:
        print("Authentication test failed:")
        print(response.text)

    return response.status_code == 200


def test_basic_auth():

    url = f"{BASE_URL}/taxonomies/regions"

    print("\nTesting HTTP Basic Authentication...")

    response = requests.get(
        url,
        auth=(EMAIL, PASSWORD),
        headers={"Accept": "application/json"},
        timeout=30
    )

    print("Basic Auth status:", response.status_code)

    if response.status_code == 200:
        print("SUCCESS: Basic authentication works!")
        print(json.dumps(response.json(), indent=4))

    else:
        print("Basic authentication failed:")
        print(response.text)
        print("Request ID:", response.headers.get("X-Request-ID"))





# --------------------------------------------------
# 4. Main execution
# --------------------------------------------------

if __name__ == "__main__":
     test_basic_auth()
    # if authenticate():
    #     test_authentication()
