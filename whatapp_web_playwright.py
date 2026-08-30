import csv
import os
import re
import time
from datetime import datetime

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


# ============================================================
# CONFIGURATION
# ============================================================

PROFILE_DIR = "whatsapp_profile"

CONTACTS_FILE = "contacts.csv"

OUTPUT_FILE = "extracted_chats.csv"

# Delay between contacts
MESSAGE_DELAY = 5

# Wait timeout
TIMEOUT = 60000

# Number of messages to extract
MESSAGE_LIMIT = 20


# ============================================================
# LOG FUNCTION
# ============================================================

def log(message):

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(
        f"[{current_time}] {message}"
    )


# ============================================================
# CLEAN PHONE NUMBER
# ============================================================

def clean_phone(phone):

    """
    Convert:

    +91 98765 43210
    91-9876543210
    919876543210

    into:

    919876543210
    """

    phone = re.sub(
        r"\D",
        "",
        str(phone)
    )

    return phone


# ============================================================
# VALIDATE INDIAN PHONE
# ============================================================

def validate_phone(phone):

    phone = clean_phone(phone)

    # India number:
    # 91 + 10 digits
    if len(phone) != 12:
        return False

    if not phone.startswith("91"):
        return False

    mobile = phone[2:]

    if len(mobile) != 10:
        return False

    if mobile[0] not in "6789":
        return False

    return True


# ============================================================
# READ CONTACT CSV
# ============================================================

def read_contacts():

    if not os.path.exists(
        CONTACTS_FILE
    ):

        raise FileNotFoundError(
            f"{CONTACTS_FILE} not found."
        )

    contacts = []

    with open(
        CONTACTS_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "name",
            "phone",
            "message"
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        if not required_columns.issubset(
            actual_columns
        ):

            raise ValueError(
                "CSV must contain: "
                "name, phone, message"
            )

        for row in reader:

            name = row["name"].strip()

            phone = clean_phone(
                row["phone"]
            )

            message = row["message"].strip()

            if not name:

                log(
                    "Skipping row: name is empty"
                )

                continue

            if not validate_phone(phone):

                log(
                    f"INVALID PHONE: "
                    f"{name} -> {phone}"
                )

                continue

            if not message:

                log(
                    f"Skipping {name}: "
                    f"message is empty"
                )

                continue

            contacts.append({

                "name": name,

                "phone": phone,

                "message": message
            })

    return contacts


# ============================================================
# OPEN WHATSAPP
# ============================================================

def open_whatsapp(page):

    log(
        "Opening WhatsApp Web..."
    )

    page.goto(
        "https://web.whatsapp.com/",
        wait_until="domcontentloaded",
        timeout=TIMEOUT
    )

    time.sleep(5)

    log(
        "Waiting for WhatsApp login..."
    )

    try:

        # WhatsApp main application
        page.locator(
            "#pane-side"
        ).wait_for(
            state="visible",
            timeout=120000
        )

        log(
            "WhatsApp Web is ready."
        )

    except PlaywrightTimeoutError:

        log("")
        log(
            "======================================"
        )
        log(
            "QR CODE LOGIN REQUIRED"
        )
        log(
            "Scan the QR code using WhatsApp."
        )
        log(
            "======================================"
        )
        log("")

        raise RuntimeError(
            "WhatsApp login timeout."
        )


# ============================================================
# OPEN CHAT DIRECTLY
# ============================================================

def open_chat(page, phone):

    """
    Instead of:

        Search number
        ↓
        Find search result
        ↓
        Click result

    we directly open:

        https://web.whatsapp.com/send?phone=NUMBER
    """

    phone = clean_phone(phone)

    url = (
        "https://web.whatsapp.com/"
        f"send?phone={phone}"
    )

    log(
        f"Opening chat: {phone}"
    )

    try:

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=TIMEOUT
        )

        time.sleep(5)

        # ----------------------------------------------------
        # Check main WhatsApp window
        # ----------------------------------------------------

        try:

            page.locator(
                "#main"
            ).wait_for(
                state="visible",
                timeout=15000
            )

            log(
                f"Chat opened successfully: {phone}"
            )

            return True

        except PlaywrightTimeoutError:

            # ------------------------------------------------
            # Check for invalid number message
            # ------------------------------------------------

            body_text = page.locator(
                "body"
            ).inner_text(
                timeout=5000
            )

            if (
                "Phone number shared via url is invalid"
                in body_text
                or
                "invalid" in body_text.lower()
            ):

                log(
                    f"Invalid WhatsApp number: {phone}"
                )

            else:

                log(
                    f"Chat did not open: {phone}"
                )

            return False

    except Exception as error:

        log(
            f"Error opening chat "
            f"{phone}: {error}"
        )

        return False


# ============================================================
# FIND MESSAGE BOX
# ============================================================

def find_message_box(page):

    """
    WhatsApp DOM can change.

    Try multiple selectors.
    """

    selectors = [

        # Most common
        "#main footer div[contenteditable='true']",

        # Role textbox
        "#main footer div[role='textbox']",

        # Contenteditable textbox
        "#main div[contenteditable='true'][role='textbox']",

        # Generic contenteditable
        "#main div[contenteditable='true']",

        # Footer fallback
        "footer div[contenteditable='true']"
    ]

    for selector in selectors:

        try:

            locator = page.locator(
                selector
            ).last

            if locator.is_visible(
                timeout=6000
            ):

                log(
                    f"Message box found: "
                    f"{selector}"
                )

                return locator

        except Exception:
            continue

    return None


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(
    page,
    contact
):

    name = contact["name"]

    phone = contact["phone"]

    template = contact["message"]

    # --------------------------------------------------------
    # Personalize message
    # --------------------------------------------------------

    message = template.replace(
        "{name}",
        name
    )

    log("")
    log(
        f"Sending to: {name}"
    )

    log(
        f"Phone: {phone}"
    )

    # --------------------------------------------------------
    # Open chat
    # --------------------------------------------------------

    chat_opened = open_chat(
        page,
        phone
    )

    if not chat_opened:

        log(
            f"FAILED: Could not open "
            f"chat for {name}"
        )

        return False

    # --------------------------------------------------------
    # Find message box
    # --------------------------------------------------------

    time.sleep(2)

    message_box = find_message_box(
        page
    )

    if message_box is None:

        log(
            f"FAILED: Message box not found "
            f"for {name}"
        )

        return False

    # --------------------------------------------------------
    # Type message
    # --------------------------------------------------------

    try:

        message_box.click()

        time.sleep(0.5)

        message_box.fill(
            message
        )

        log(
            f"Message typed for {name}"
        )

    except Exception as error:

        log(
            f"FAILED typing message "
            f"for {name}: {error}"
        )

        return False

    # --------------------------------------------------------
    # Send
    # --------------------------------------------------------

    try:

        page.keyboard.press(
            "Enter"
        )

        time.sleep(
            MESSAGE_DELAY
        )

        log(
            f"SUCCESS: Message sent "
            f"to {name}"
        )

        return True

    except Exception as error:

        log(
            f"FAILED sending to "
            f"{name}: {error}"
        )

        return False


# ============================================================
# FIND CHAT MESSAGES
# ============================================================

def find_message_nodes(page):

    selectors = [

        "#main div[data-testid='msg-container']",

        "#main div.message-in",

        "#main div.message-out",

        "#main div[role='row']"
    ]

    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )

            count = locator.count()

            if count > 0:

                log(
                    f"Message selector found: "
                    f"{selector}"
                )

                return locator

        except Exception:
            continue

    return None


# ============================================================
# EXTRACT CHAT
# ============================================================

def extract_chat(
    page,
    contact
):

    name = contact["name"]

    phone = contact["phone"]

    log("")
    log(
        f"Extracting chat: {name}"
    )

    # --------------------------------------------------------
    # Open chat
    # --------------------------------------------------------

    if not open_chat(
        page,
        phone
    ):

        return []

    time.sleep(3)

    # --------------------------------------------------------
    # Find messages
    # --------------------------------------------------------

    message_nodes = find_message_nodes(
        page
    )

    if message_nodes is None:

        log(
            f"No messages found: {name}"
        )

        return []

    count = message_nodes.count()

    log(
        f"Messages found: {count}"
    )

    start_index = max(
        0,
        count - MESSAGE_LIMIT
    )

    extracted = []

    # --------------------------------------------------------
    # Read messages
    # --------------------------------------------------------

    for index in range(
        start_index,
        count
    ):

        try:

            node = message_nodes.nth(
                index
            )

            # --------------------------------------------
            # Extract message text
            # --------------------------------------------

            text_elements = node.locator(
                "span.selectable-text"
            )

            text_count = (
                text_elements.count()
            )

            message_text = ""

            for j in range(
                text_count
            ):

                text = (
                    text_elements
                    .nth(j)
                    .inner_text()
                    .strip()
                )

                if text:

                    message_text += (
                        text + " "
                    )

            message_text = (
                message_text.strip()
            )

            if not message_text:

                continue

            # --------------------------------------------
            # Identify sender
            # --------------------------------------------

            classes = (
                node.get_attribute(
                    "class"
                ) or ""
            )

            if (
                "message-out"
                in classes
            ):

                sender = "Me"

            else:

                sender = "Contact"

            # --------------------------------------------
            # Save
            # --------------------------------------------

            extracted.append({

                "extracted_at":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "contact":
                    name,

                "phone":
                    phone,

                "sender":
                    sender,

                "message":
                    message_text
            })

        except Exception as error:

            log(
                f"Message extraction error: "
                f"{error}"
            )

    return extracted


# ============================================================
# SAVE CHAT DATA
# ============================================================

def save_chat_data(data):

    if not data:

        log(
            "No chat data to save."
        )

        return

    file_exists = os.path.exists(
        OUTPUT_FILE
    )

    with open(
        OUTPUT_FILE,
        "a",
        encoding="utf-8",
        newline=""
    ) as file:

        fieldnames = [

            "extracted_at",

            "contact",

            "phone",

            "sender",

            "message"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:

            writer.writeheader()

        writer.writerows(
            data
        )

    log(
        f"Saved {len(data)} messages "
        f"to {OUTPUT_FILE}"
    )


# ============================================================
# SEND ALL MESSAGES
# ============================================================

def send_all_messages(
    page,
    contacts
):

    success = 0

    failed = 0

    log("")
    log(
        "======================================"
    )
    log(
        "STARTING MESSAGE SENDING"
    )
    log(
        "======================================"
    )

    for index, contact in enumerate(
        contacts,
        start=1
    ):

        log("")
        log(
            f"PROCESSING {index}/"
            f"{len(contacts)}"
        )

        try:

            result = send_message(
                page,
                contact
            )

            if result:

                success += 1

            else:

                failed += 1

        except Exception as error:

            failed += 1

            log(
                f"Unexpected error: {error}"
            )

    log("")
    log(
        "======================================"
    )
    log(
        "MESSAGE SENDING COMPLETE"
    )
    log(
        "======================================"
    )

    log(
        f"SUCCESS : {success}"
    )

    log(
        f"FAILED  : {failed}"
    )


# ============================================================
# EXTRACT ALL CHATS
# ============================================================

def extract_all_chats(
    page,
    contacts
):

    all_data = []

    log("")
    log(
        "======================================"
    )
    log(
        "STARTING CHAT EXTRACTION"
    )
    log(
        "======================================"
    )

    for index, contact in enumerate(
        contacts,
        start=1
    ):

        log(
            f"EXTRACTING {index}/"
            f"{len(contacts)}"
        )

        try:

            data = extract_chat(
                page,
                contact
            )

            all_data.extend(
                data
            )

        except Exception as error:

            log(
                f"Extraction error for "
                f"{contact['name']}: "
                f"{error}"
            )

    save_chat_data(
        all_data
    )


# ============================================================
# MAIN
# ============================================================

def main():

    log("")
    log(
        "======================================"
    )
    log(
        "WHATSAPP AUTOMATION BOT"
    )
    log(
        "======================================"
    )

    # --------------------------------------------------------
    # Read contacts
    # --------------------------------------------------------

    try:

        contacts = read_contacts()

    except Exception as error:

        log(
            f"CSV ERROR: {error}"
        )

        return

    if not contacts:

        log(
            "No valid contacts found."
        )

        return

    log(
        f"Valid contacts: {len(contacts)}"
    )

    # --------------------------------------------------------
    # Playwright
    # --------------------------------------------------------

    with sync_playwright() as p:

        log(
            "Starting Chromium..."
        )

        context = (
            p.chromium
            .launch_persistent_context(

                PROFILE_DIR,

                headless=False,

                viewport={
                    "width": 1400,
                    "height": 900
                },

                args=[
                    "--start-maximized"
                ]
            )
        )

        # ----------------------------------------------------
        # Get page
        # ----------------------------------------------------

        if context.pages:

            page = context.pages[0]

        else:

            page = context.new_page()

        try:

            # ------------------------------------------------
            # WhatsApp login
            # ------------------------------------------------

            open_whatsapp(
                page
            )

            # ------------------------------------------------
            # SEND
            # ------------------------------------------------

            send_all_messages(
                page,
                contacts
            )

            # ------------------------------------------------
            # EXTRACT
            # ------------------------------------------------

            extract_all_chats(
                page,
                contacts
            )

            # ------------------------------------------------
            # FINISH
            # ------------------------------------------------

            log("")
            log(
                "======================================"
            )
            log(
                "BOT FINISHED"
            )
            log(
                "======================================"
            )

            log(
                f"Output file: "
                f"{OUTPUT_FILE}"
            )

            time.sleep(5)

        except Exception as error:

            log("")
            log(
                f"MAIN ERROR: {error}"
            )

        finally:

            context.close()


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()