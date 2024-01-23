import time

import requests
from dotenv import dotenv_values
from tqdm import tqdm

config = dotenv_values(".env")

# Set these two variables
domain = config["DOMAIN"]
base_url = f"https://{domain}"
session_token = config["SESSION_TOKEN"]


# Set up the session with the token
def get_session():
    session = requests.Session()
    session.cookies.set(
        "__Secure-next-auth.session-token", session_token, path="/", domain=domain
    )

    return session


def get_links(session):
    links = session.get(f"{base_url}/api/v1/links?sort=0").json()["response"]
    cursor = int(links[0]["id"]) - 19
    while True:
        if cursor <= 0:
            break
        response_links = session.get(f"{base_url}/api/v1/links?sort=0&cursor={cursor}")
        result = response_links.json()["response"]
        links.extend(result)
        cursor -= 20
    return links


def main():
    session = get_session()
    links = get_links(session)
    print(f"Found {len(links)} links")
    links = [link for link in links if link["pdf"] == "unavailable"]
    print(f"Found {len(links)} links to archive")

    for link in tqdm(links):
        response = session.put(f"{base_url}/api/v1/links/{link['id']}/archive")
        if response.status_code != 200:
            print(response.json())
            continue
        time.sleep(3)


if __name__ == "__main__":
    main()
