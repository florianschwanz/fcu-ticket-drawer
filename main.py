# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "click>=8.3.1",
#   "dotenv>=0.9.9",
#   "numpy>=2.4.2",
#   "opencv-python>=4.13.0.92",
#   "playwright>=1.58.0",
#   "pytesseract>=0.3.13",
#   "pytest>=9.0.2",
#   "requests>=2.32.5",
# ]
# ///

import os
import random
import sys
import time
from glob import glob
from time import sleep

import click
import cv2
import numpy as np
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SIGNAL_API_PHONE = os.getenv("SIGNAL_API_PHONE", None)
SIGNAL_API_KEY = os.getenv("SIGNAL_API_KEY", None)
DRAW_LOTTERY_TICKET_MEN = (
    os.getenv("DRAW_LOTTERY_TICKET_MEN", "False").lower() == "true"
)
DRAW_LOTTERY_TICKET_WOMEN = (
    os.getenv("DRAW_LOTTERY_TICKET_WOMEN", "False").lower() == "true"
)
DRAW_LOTTERY_TICKET_TYPE = os.getenv("DRAW_LOTTERY_TICKET_TYPE")

BUY_TICKET_MEN = os.getenv("BUY_TICKET_MEN", "False").lower() == "true"
BUY_TICKET_WOMEN = os.getenv("BUY_TICKET_WOMEN", "False").lower() == "true"
BUY_TICKET_FAVORITE_BLOCKS = [
    block.strip() for block in os.getenv("BUY_TICKET_FAVORITE_BLOCKS", "").split(",")
]
BUY_TICKET_TYPE = os.getenv("BUY_TICKET_TYPE", "member")
BUY_TICKET_VOUCHER_CODE = os.getenv("BUY_TICKET_VOUCHER_CODE", None)

LOGOS = {
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

LOGIN_URL = "https://anmeldung.fc-union-berlin.de/auth/realms/union/protocol/openid-connect/auth?client_id=union-tickets&scope=openid+lms_id&redirect_uri=https%3a%2f%2ftickets.union-zeughaus.de%2funveu%2fSynwayLoginSso%2fLoginCallback%2fAnmeldung&response_type=code"
LANDING_PAGE_URL = "https://tickets.union-zeughaus.de/unveu/data"
BASE_URL = "https://tickets.union-zeughaus.de/unveu/"
HOME_GAMES_MEN_URL = (
    f"{BASE_URL}/SynwayWarengruppen/data/shop/e25ac3cd-90f7-46bc-8a61-951f371a3a72"
)
HOME_GAMES_WOMEN_URL = (
    f"{BASE_URL}/SynwayWarengruppen/data/shop/e1d93006-319c-4a8a-93f6-2d1bbffc10f2"
)

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)


@click.command()
@click.option("--debug", "-d", default=False, is_flag=True, help="Enable debug mode.")
@click.option("--lots", "-l", default=False, is_flag=True, help="Enable drawing lots.")
@click.option(
    "--tickets", "-t", default=False, is_flag=True, help="Enable buying tickets."
)
def main(debug, lots, tickets):
    """
    Draws lottery tickets / buys tickets for upcoming home games of 1.FC Union Berlin and sends a notification via Signal with the game details and the team logo.
    :param debug: if true, runs the browser in non-headless mode for debugging purposes
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not debug,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="de-DE",
        )

        page = context.new_page()

        # Inject JavaScript to delete the 'webdriver' property
        page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

        #
        # Login
        #

        try:
            page.goto(LOGIN_URL)
            page.type("input[name='username']", USERNAME, delay=100) and human_sleep(
                0.5, 1.5
            )
            page.type("input[name='password']", PASSWORD, delay=100) and human_sleep(
                0.5, 1.5
            )
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
        try:
            page.get_by_text("Ablehnen").click()
        except:
            pass

        if lots:
            if DRAW_LOTTERY_TICKET_MEN:
                draw_lottery_tickets_for_team(
                    page,
                    url=HOME_GAMES_MEN_URL,
                    team_name="men's team",
                    signal_message_template="❤️🤍 Los gezogen für das Spiel der Profis Männer gegen {opponent_name} am {date} um {time}",
                    debug=debug,
                )

            if DRAW_LOTTERY_TICKET_WOMEN:
                draw_lottery_tickets_for_team(
                    page,
                    url=HOME_GAMES_WOMEN_URL,
                    team_name="women's team",
                    signal_message_template="❤️🤍 Los gezogen für das Spiel der Profis Frauen gegen {opponent_name} am {date} um {time}",
                    debug=debug,
                )

        if tickets:
            if BUY_TICKET_MEN:
                buy_tickets_for_team(
                    page,
                    url=HOME_GAMES_MEN_URL,
                    team_name="men's team",
                    signal_message_template="❤️🤍 Ticket gekauft für das Spiel der Profis Männer gegen {opponent_name} am {date} um {time}",
                    debug=debug,
                )

            if BUY_TICKET_WOMEN:
                buy_tickets_for_team(
                    page,
                    url=HOME_GAMES_WOMEN_URL,
                    team_name="women's team",
                    signal_message_template="❤️🤍 Ticket gekauft für das Spiel der Profis Frauen gegen {opponent_name} am {date} um {time}",
                    debug=debug,
                )

        browser.close()


def draw_lottery_tickets_for_team(
    page: Page, url, team_name, signal_message_template, debug
):
    """
    Draws lottery tickets for all available home games for the given team.
    :param page: page
    :param url: URL
    :param team_name: team name
    :param signal_message_template: template for signal message
    :return:
    """

    debug and print(f"Go to {url}")
    page.goto(url)

    if page.get_by_text("Infos").count() == 0:
        print(f"No upcoming {team_name} games found to draw a lot for. Skipping.")
        return

    for venue_button in page.get_by_text("Infos").all():
        venue_url = venue_button.get_attribute("href")

        if venue_url is None:
            print(f"No upcoming {team_name} games found to draw a lot for. Skipping.")
            continue

        venue_url = BASE_URL + venue_url
        debug and print(f"Go to {venue_url}")
        page.goto(venue_url)

        opponent_name = (
            page.locator("h2").first.inner_text().split("-")[1].strip().title()
        )
        date = page.locator(".date.pr-3").inner_text().strip()
        time = page.locator(".time.pr-3").inner_text().strip()

        #
        # Draw lottery ticket
        #

        if page.get_by_text("Los sichern").count() == 0:
            print(
                f"Drawing phase already over for the {team_name} game against {opponent_name} on {date}. Skipping."
            )
            continue

        page.get_by_text("Los sichern").click()

        if DRAW_LOTTERY_TICKET_TYPE == "sitting":
            page.get_by_text("Sitzplatz").click()
        else:
            page.get_by_text("Stehplatz").click()

        page.get_by_text("Buchen").click()
        sleep(5)
        page.get_by_alt_text("Einkaufswagen").click()

        # Check if a lottery ticket is already drawn for this game
        if page.locator(".alert-danger").count() > 0:
            print(
                f"Already drew a lottery ticket for the {team_name} game against {opponent_name} on {date}. Skipping."
            )
            continue

        page.get_by_role("button", name="Zur Kasse").click()

        # Check all checkboxes
        for checkbox in page.get_by_role("checkbox").all():
            checkbox.check()

        page.get_by_text("Kaufen").click()

        #
        # Send signal message
        #

        signal_api_url = build_signal_api_url(SIGNAL_API_PHONE, SIGNAL_API_KEY)
        send_signal_message(
            signal_api_url,
            signal_message_template.format(
                opponent_name=opponent_name, date=date, time=time
            ),
        )

        send_signal_image(signal_api_url, build_image_url(opponent_name))


def buy_tickets_for_team(
    page: Page, url, team_name, signal_message_template, debug=False
):
    """
    Buys tickets for all available home games for the given team.
    :param page: page
    :param url: URL
    :param team_name: team name
    :param signal_message_template: template for signal message
    :return:
    """

    debug and print(f"Go to {HOME_GAMES_WOMEN_URL}")
    page.goto(url)

    if page.get_by_text("Tickets").count() == 0:
        print(f"No upcoming {team_name} games found to buy a ticket for. Skipping.")
        return

    for venue_button in page.get_by_text("Tickets").all():
        if venue_button.get_attribute(
            "href"
        ) is None or "venue" not in venue_button.get_attribute("href"):
            continue

        venue_url = BASE_URL + venue_button.get_attribute("href")
        debug and print(f"Go to {venue_url}")
        page.goto(venue_url)

        opponent_name = page.locator("h2").first.inner_text().split("-")[1].strip()
        date = page.locator(".date.pr-3").inner_text().strip()
        time = page.locator(".time.pr-3").inner_text().strip()

        #
        # Select block and seat
        #

        # Wait for the canvas to load
        sleep(5)

        # Take screenshot of canvas
        os.makedirs(os.path.join(script_path, "tmp"), exist_ok=True)
        canvas = page.locator(".jsVenue")

        # Identify positions of blocks on screenshot of canvas
        blocks_map = get_clickable_items(
            canvas,
            os.path.join(script_path, "tmp", "canvas-stadium.png"),
            os.path.join(script_path, "templates", "blocks"),
        )

        # Iterate over favorite blocks
        for block in BUY_TICKET_FAVORITE_BLOCKS:
            # Check if desired block is not identified
            if block not in blocks_map or blocks_map[block][0] is None:
                continue

            # Click on block
            coords = blocks_map[block][0]
            canvas.click(position={"x": coords[0], "y": coords[1]})

            # Select seat
            if block in ["A1", "A2", "B1", "B2", "B3", "C1", "C2", "VIP"]:
                # Wait for the canvas to update
                sleep(5)

                seats_map = get_clickable_items(
                    page.locator(".jsVenue"),
                    os.path.join(script_path, "tmp", "canvas-seats.png"),
                    os.path.join(script_path, "templates", "seats"),
                )

                # Convert dict to list
                seat_list = [seat for sublist in seats_map.values() for seat in sublist]
                # Check if desired block is not identified
                if not seat_list:
                    print(f"No seat found in block {block}. Skipping.")
                    return

                for coords in seat_list:
                    # Click on seat
                    canvas.click(position={"x": coords[0], "y": coords[1]})

                    # Check if ticket is in the shopping cart
                    if (
                        int(
                            page.locator(
                                "#jsShoppingCartButtonCount"
                            ).first.inner_text()
                        )
                        > 0
                    ):
                        break

                    sleep(1)

            # Check if ticket is in the shopping cart
            if int(page.locator("#jsShoppingCartButtonCount").first.inner_text()) > 0:
                break

        # Check if ticket for the desired block was added to the shopping cart
        if int(page.locator("#jsShoppingCartButtonCount").first.inner_text()) == 0:
            print(
                f"Could not buy a ticket for the {team_name} against {opponent_name} on {date}."
            )
            break

        page.get_by_role("button", name="Zur Kasse").click()

        # Check if a ticket is already bought for this game
        if page.locator(".alert-danger").count() > 0:
            print(
                f"Already bought a ticket for the {team_name} game against {opponent_name} on {date}. Skipping."
            )
            continue

        # Select ticket type
        page.get_by_role("button", name="Vollzahler").click()

        if BUY_TICKET_TYPE == "full-payer":
            page.get_by_role("button", name="Vollzahler").click()
        if BUY_TICKET_TYPE == "member":
            page.get_by_role("button", name="Mitglied", exact=True).click()
        elif BUY_TICKET_TYPE == "child":
            page.get_by_role("button", name="Kind [6 - 12 Jahre]").click()
        elif BUY_TICKET_TYPE == "member-child":
            page.get_by_role("button", name="Mitglied | Kind [6 bis 12 Jahre]").click()
        else:
            print(
                f"Invalid ticket type specified: {BUY_TICKET_TYPE}. Please choose one of 'full-payer', 'member', 'child' or 'member-child'."
            )
            break

        # Enter voucher code
        page.type(
            "input[name='KTRANS_GutscheinEinloesen']",
            BUY_TICKET_VOUCHER_CODE,
            delay=100 if not debug else 0,
        ) and human_sleep(0.5, 1.5)
        page.locator('input[value="Hinzufügen"]').click()

        # Check if voucher code is invalid
        if page.locator("#AlertDialogTitle").count() > 0:
            print(f"Invalid voucher code. Skipping.")
            return

        # Check all checkboxes
        for checkbox in page.get_by_role("checkbox").all():
            checkbox.check()

        page.get_by_text("Kaufen").click()

        #
        # Send signal message
        #

        signal_api_url = build_signal_api_url(SIGNAL_API_PHONE, SIGNAL_API_KEY)
        send_signal_message(
            signal_api_url,
            signal_message_template.format(
                opponent_name=opponent_name, date=date, time=time
            ),
        )

        send_signal_image(signal_api_url, build_image_url(opponent_name))


def get_clickable_items(canvas, screenshot_path, templates_dir):
    # Take screenshot of canvas
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    canvas.screenshot(path=screenshot_path)

    # Load image
    image = cv2.imread(screenshot_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if image is None:
        print("Error: Map image not found.")
        return {}

    found_items = {}

    # Iterate through all template images
    for template_path in glob(os.path.join(templates_dir, "*.png")):
        # Get the label from filename
        label, _ = os.path.splitext(os.path.basename(template_path))

        # Load template in grayscale
        template = cv2.imread(template_path)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]

        # Perform Template Matching
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

        # Filter for High Confidence Matches
        threshold = 0.8
        loc = np.where(res >= threshold)

        # We might find multiple pixels for the same letter (clusters).
        # We need to group them into one single (x, y) point per item.
        mask = np.zeros(image.shape, dtype="uint8")

        for pt in zip(*loc[::-1]):
            # Draw a white rectangle on a mask to "fuse" close detections
            cv2.rectangle(mask, pt, (pt[0] + w, pt[1] + h), 255, -1)

        # Find contours on this mask to get distinct centers
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w_c, h_c = cv2.boundingRect(contour)
            center_x = x + w_c // 2
            center_y = y + h_c // 2
            coordinates = (center_x, center_y)

            if label not in found_items:
                found_items[label] = []
            if label in found_items and coordinates not in found_items[label]:
                found_items[label].append(coordinates)

    for key, value in sorted(found_items.items()):
        print(f"Found item {key} at {value}")

    return found_items


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
        return LOGOS["1.FC Heidenheim 1846"]
    if "Köln" in team:
        return LOGOS["1.FC Köln"]
    if "Union" in team:
        return LOGOS["1.FC Union Berlin"]
    if "Mainz" in team:
        return LOGOS["1.FSV Mainz 05"]
    if "Leverkusen" in team:
        return LOGOS["Bayer 04 Leverkusen"]
    if "München" in team:
        return LOGOS["Bayern Munich"]
    if "Dortmund" in team:
        return LOGOS["Borussia Dortmund"]
    if "Mönchengladbach" in team:
        return LOGOS["Borussia Mönchengladbach"]
    if "Frankfurt" in team:
        return LOGOS["Eintracht Frankfurt"]
    if "Augsburg" in team:
        return LOGOS["FC Augsburg"]
    if "Pauli" in team:
        return LOGOS["FC St. Pauli"]
    if "Hamburg" in team:
        return LOGOS["Hamburger SV"]
    if "Leipzig" in team:
        return LOGOS["RB Leipzig"]
    if "Freiburg" in team:
        return LOGOS["SC Freiburg"]
    if "Bremen" in team:
        return LOGOS["SV Werder Bremen"]
    if "Hoffenheim" in team:
        return LOGOS["TSG 1899 Hoffenheim"]
    if "Stuttgart" in team:
        return LOGOS["VfB Stuttgart"]
    if "Wolfsburg" in team:
        return LOGOS["VfL Wolfsburg"]


def human_sleep(min_seconds=1.0, max_seconds=3.0):
    time.sleep(random.uniform(min_seconds, max_seconds))


if __name__ == "__main__":
    main(sys.argv[1:])
