# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "click>=8.2.1",
#   "dotenv>=0.9.9",
#   "playwright>=1.58.0",
#   "requests>=2.32.5",
# ]
# ///

import os
import sys
from time import sleep

import click
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SIGNAL_API_PHONE = os.getenv("SIGNAL_API_PHONE")
SIGNAL_API_KEY = os.getenv("SIGNAL_API_KEY")
TICKET_TYPE = os.getenv("TICKET_TYPE")

LOGIN_URL = "https://anmeldung.fc-union-berlin.de/auth/realms/union/protocol/openid-connect/auth?client_id=union-tickets&scope=openid+lms_id&redirect_uri=https%3a%2f%2ftickets.union-zeughaus.de%2funveu%2fSynwayLoginSso%2fLoginCallback%2fAnmeldung&response_type=code"
LANDING_PAGE_URL = "https://tickets.union-zeughaus.de/unveu/data"
BASE_URL = "https://tickets.union-zeughaus.de/unveu/"

logos = {
    "1.FC Heidenheim 1846": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/1.FC%20Heidenheim%201846.png",
    "1.FC Köln": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/1.FC%20K%C3%B6ln.png",
    "1.FC Union Berlin": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/1.FC%20Union%20Berlin.png",
    "1.FSV Mainz 05": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/1.FSV%20Mainz%2005.png",
    "Bayer 04 Leverkusen": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Bayer%2004%20Leverkusen.png",
    "Bayern Munich": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Bayern%20Munich.png",
    "Borussia Dortmund": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Borussia%20Dortmund.png",
    "Borussia Mönchengladbach": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Borussia%20M%C3%B6nchengladbach.png",
    "Eintracht Frankfurt": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Eintracht%20Frankfurt.png",
    "FC Augsburg": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/FC%20Augsburg.png",
    "FC St. Pauli": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/FC%20St.%20Pauli.png",
    "Hamburger SV": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/Hamburger%20SV.png",
    "RB Leipzig": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/RB%20Leipzig.png",
    "SC Freiburg": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/SC%20Freiburg.png",
    "SV Werder Bremen": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/SV%20Werder%20Bremen.png",
    "TSG 1899 Hoffenheim": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/TSG%201899%20Hoffenheim.png",
    "VfB Stuttgart": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/VfB%20Stuttgart.png",
    "VfL Wolfsburg": "https://raw.githubusercontent.com/luukhopman/football-logos/refs/heads/master/logos/Germany%20-%20Bundesliga/VfL%20Wolfsburg.png",
}


def build_signal_api_url(phone, api_key):
    return (
        f"https://signal.callmebot.com/signal/send.php?phone={phone}&apikey={api_key}"
        if phone and api_key
        else None
    )


def send_signal_message(api_url, text):
    if not api_url:
        print("No Signal URL configured. Skipping notification.")
        return

    try:
        payload = {"text": text}
        response = requests.get(api_url, params=payload)
        if response.status_code == 200:
            print("Signal notification sent.")
        else:
            print(f"Failed to send Signal: {response.text}")
        sleep(5)
    except Exception as e:
        print(f"Error sending notification: {e}")


def send_signal_image(api_url, image_url=None):
    if not api_url:
        print("No Signal URL configured. Skipping notification.")
        return
    if not image_url:
        print("No image URL provided. Skipping notification.")
        return

    try:
        payload = {"image": image_url}
        response = requests.get(api_url, params=payload)
        if response.status_code == 200:
            print("Signal notification sent.")
        else:
            print(f"Failed to send Signal: {response.text}")
        sleep(5)
    except Exception as e:
        print(f"Error sending notification: {e}")


def build_image_url(team):
    if "Heidenheim" in team:
        return logos["1.FC Heidenheim 1846"]
    if "Köln" in team:
        return logos["1.FC Köln"]
    if "Union" in team:
        return logos["1.FC Union Berlin"]
    if "Mainz" in team:
        return logos["1.FSV Mainz 05"]
    if "Leverkusen" in team:
        return logos["Bayer 04 Leverkusen"]
    if "München" in team:
        return logos["Bayern Munich"]
    if "Dortmund" in team:
        return logos["Borussia Dortmund"]
    if "Mönchengladbach" in team:
        return logos["Borussia Mönchengladbach"]
    if "Frankfurt" in team:
        return logos["Eintracht Frankfurt"]
    if "Augsburg" in team:
        return logos["FC Augsburg"]
    if "Pauli" in team:
        return logos["FC St. Pauli"]
    if "Hamburg" in team:
        return logos["Hamburger SV"]
    if "Leipzig" in team:
        return logos["RB Leipzig"]
    if "Freiburg" in team:
        return logos["SC Freiburg"]
    if "Bremen" in team:
        return logos["SV Werder Bremen"]
    if "Hoffenheim" in team:
        return logos["TSG 1899 Hoffenheim"]
    if "Stuttgart" in team:
        return logos["VfB Stuttgart"]
    if "Wolfsburg" in team:
        return logos["VfL Wolfsburg"]


@click.command()
@click.option("--debug", "-d", default=False, is_flag=True, help="Enable debug mode.")
def draw_lots(debug):
    """
    Draws lots for upcoming home games of 1.FC Union Berlin and sends a notification via Signal with the game details and the team logo.
    :param debug: if true, runs the browser in non-headless mode for debugging purposes
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not debug)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="de-DE"
        )

        page = context.new_page()

        #
        # Login
        #

        try:
            page.goto(LOGIN_URL)
            page.fill("input[name='username']", USERNAME)
            page.fill("input[name='password']", PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            print("Login submitted.")
        except Exception as e:
            print(f"Login failed: {e}")
            sys.exit(1)

        #
        # Check home games
        #

        # Select option in cookie banner
        page.get_by_text("Ablehnen").click()

        page.goto(LANDING_PAGE_URL)

        url_home_games = [
            element
            for element in page.get_by_text(" Heimspiele ").all()
            if element.get_attribute("href") is not None
        ][0].get_attribute("href")
        page.goto(url_home_games)

        for info_button in page.get_by_text(" Infos ").all():
            url_info = BASE_URL + info_button.get_attribute("href")
            page.goto(url_info)

            team = page.locator("h2").first.inner_text().split(" - ")[1].strip().title()
            date = page.locator(".date.pr-3").inner_text().strip()
            time = page.locator(".time.pr-3").inner_text().strip()

            #
            # Draw lot
            #

            page.get_by_text(" Los sichern ").click()

            if TICKET_TYPE == "sitting":
                page.get_by_text(" Sitzplatz ").click()
            else:
                page.get_by_text(" Stehplatz ").click()

            page.get_by_text(" Buchen ").click()
            page.get_by_alt_text("Einkaufswagen").click()

            if page.locator(".alert-danger").count() > 0:
                print(f"Already drew for the game against {team} on {date}. Skipping.")
                continue

            page.get_by_role("button", name="Zur Kasse").click()

            for checkbox in page.get_by_role("checkbox").all():
                checkbox.check()

            page.get_by_text("Kaufen").click()

            #
            # Send signal message
            #

            signal_api_url = build_signal_api_url(SIGNAL_API_PHONE, SIGNAL_API_KEY)
            send_signal_message(
                signal_api_url,
                f"❤️🤍 Los gezogen für Spiel gegen {team} am {date} um {time}",
            )
            send_signal_image(signal_api_url, build_image_url(team))

        browser.close()


if __name__ == "__main__":
    draw_lots(sys.argv[1:])
