import asyncio
import os
import datetime
from playwright.async_api import async_playwright
import asyncpg

# Database connection details
DATABASE_URL = os.environ.get("DATABASE_URL", "")

async def scrape_gmail_and_calendar():
    """
    Uses Playwright to scrape Gmail and Google Calendar.
    Saves screenshots and stores data in PostgreSQL.
    """
    # Set the DISPLAY environment variable for headful operation
    os.environ["DISPLAY"] = ":1"

    # Ensure screenshots directory exists
    os.makedirs("/home/ubuntu/projects/services/pulseboard/screenshots", exist_ok=True)

    async with async_playwright() as p:
        # Launch a headful Chromium browser
        browser = await p.chromium.launch(headless=False, args=["--disable-web-security"])
        page = await browser.new_page()

        # --- SCRAPE GMAIL ---
        try:
            print("Navigating to Gmail...")
            await page.goto("https://mail.google.com/")

            # Wait for login page or inbox to load
            await page.wait_for_load_state("networkidle")
            # Add logic here to handle potential login if not already logged in
            # This is a simplified version assuming the user is already logged in or will log in manually during headful execution

            # Take a screenshot of the inbox
            gmail_screenshot_path = "/home/ubuntu/projects/services/pulseboard/screenshots/gmail-inbox.png"
            await page.screenshot(path=gmail_screenshot_path, full_page=True)
            print(f"Gmail screenshot saved to {gmail_screenshot_path}")

            # Scrape email subjects and senders
            # This is a simplified example; actual selectors may vary based on Gmail's UI
            # Look for elements representing emails in the inbox view
            # Example: .zE class for starred emails, .afn for subject, .yW for sender name
            # These selectors are fragile and may break with UI updates.
            # A more robust solution would involve the Gmail API.
            # For this demo, we'll use common selectors for the inbox list items.
            email_elements = await page.query_selector_all("tr.zA") # Common selector for email rows in inbox
            emails_scraped = []
            for element in email_elements[:10]: # Limit to first 10 emails for demo
                try:
                    sender_element = await element.query_selector(".yP, .zF") # Try common sender selectors
                    subject_element = await element.query_selector(".y6, .aHS-b-n") # Try common subject selectors
                    sender = await sender_element.inner_text() if sender_element else "Unknown Sender"
                    subject = await subject_element.inner_text() if subject_element else "No Subject"
                    # Determine read/unread status - often indicated by font weight or other styles
                    is_read = await element.get_attribute("class") is not None and "zE" not in (await element.get_attribute("class")).split() # Simplified logic
                    emails_scraped.append({
                        "sender": sender.strip(),
                        "subject": subject.strip(),
                        "is_read": is_read
                    })
                except Exception as e:
                    print(f"Error scraping individual email item: {e}")
                    continue

            print(f"Scraped {len(emails_scraped)} emails from Gmail.")

        except Exception as e:
            print(f"Error scraping Gmail: {e}")
            # Take a screenshot even if an error occurs
            gmail_error_screenshot_path = "/home/ubuntu/projects/services/pulseboard/screenshots/gmail-error.png"
            await page.screenshot(path=gmail_error_screenshot_path, full_page=True)
            print(f"Gmail error screenshot saved to {gmail_error_screenshot_path}")


        # --- SCRAPE GOOGLE CALENDAR ---
        try:
            print("Navigating to Google Calendar...")
            # Navigate to Google Calendar in a new tab
            calendar_page = await browser.new_page()
            await calendar_page.goto("https://calendar.google.com/")
            await calendar_page.wait_for_load_state("networkidle")

            # Take a screenshot of the calendar view
            calendar_screenshot_path = "/home/ubuntu/projects/services/pulseboard/screenshots/calendar-today.png"
            await calendar_page.screenshot(path=calendar_screenshot_path, full_page=True)
            print(f"Calendar screenshot saved to {calendar_screenshot_path}")

            # Scrape today's events
            # This is also fragile and depends on the UI structure.
            # Look for events on the current day/month view.
            # Example: .mv, .Om, .J-K-U-Jo-ax, .J-K-U-Jo-Jw
            # A more robust solution would use the Google Calendar API.
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            # Find elements representing events for the current day
            # This selector `.g3dbUd` is commonly associated with event containers in month view.
            # It might not capture all events depending on view type (day, week, month).
            event_elements = await calendar_page.query_selector_all(".g3dbUd") # Common selector for event items
            events_scraped = []
            for element in event_elements:
                try:
                    # Attempt to extract event title/time
                    # Title is often within a child element with specific classes
                    title_element = await element.query_selector("div, span") # Generic search within event container
                    title = await title_element.inner_text() if title_element else "Untitled Event"
                    # Time extraction is tricky without knowing the exact DOM structure reliably
                    # For simplicity, we'll just get the title and assume it's for today
                    events_scraped.append({
                        "name": title.strip(),
                        "date": today_date # Assuming scraped events are for today
                    })
                except Exception as e:
                    print(f"Error scraping individual calendar event: {e}")
                    continue

            print(f"Scraped {len(events_scraped)} events from Google Calendar.")

            await calendar_page.close()

        except Exception as e:
            print(f"Error scraping Google Calendar: {e}")
            # Take a screenshot even if an error occurs
            calendar_error_screenshot_path = "/home/ubuntu/projects/services/pulseboard/screenshots/calendar-error.png"
            await page.screenshot(path=calendar_error_screenshot_path, full_page=True)
            print(f"Calendar error screenshot saved to {calendar_error_screenshot_path}")

        finally:
            await browser.close()

    # --- STORE DATA IN POSTGRESQL ---
    try:
        print("Connecting to database to store scraped data...")
        pool = await asyncpg.create_pool(DATABASE_URL)

        async with pool.acquire() as conn:
            # Insert scraped emails into pulseboard_emails table
            for email in emails_scraped:
                await conn.execute(
                    "INSERT INTO pulseboard_emails (timestamp, sender, subject, is_read, data) VALUES ($1, $2, $3, $4, $5)",
                    datetime.datetime.now(datetime.timezone.utc),
                    email["sender"],
                    email["subject"],
                    email["is_read"],
                    {"source": "browser_automation_gmail"}
                )

            # Insert scraped events into pulseboard_events table
            for event in events_scraped:
                await conn.execute(
                    "INSERT INTO pulseboard_events (timestamp, name, source, data) VALUES ($1, $2, $3, $4)",
                    datetime.datetime.now(datetime.timezone.utc),
                    event["name"],
                    "browser_automation_calendar",
                    {"scraped_date": event["date"], "source": "browser_automation_calendar"}
                )

        print(f"Stored {len(emails_scraped)} emails and {len(events_scraped)} events in the database.")
        await pool.close()

    except Exception as e:
        print(f"Error storing data in database: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_gmail_and_calendar())
