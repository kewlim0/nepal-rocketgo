from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import time
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from datetime import datetime
from collections import defaultdict
from terminal_utils import setup_automation_terminal, cleanup_terminal, print_status

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n[WARNING] Shutdown signal received. Cleaning up...")
    try:
        driver.quit()
        print("[INFO] Browser closed successfully")
    except:
        print("[WARNING] Browser was already closed or unavailable")
    sys.exit(0)




# Windows Firefox profile path (comment out if you want a fresh profile)
# profile_path = "C:\\Users\\BDC Computer ll\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\your-profile-name"
# firefox_profile = webdriver.FirefoxProfile(profile_path)

options = Options()
# options.set_preference("profile", profile_path)  # Commented out for fresh profile
# Optional: Use a specific Firefox profile for Windows
# To find your Firefox profiles, navigate to: %APPDATA%\Mozilla\Firefox\Profiles\
# Example Windows profile path:
# options.profile = "C:\\Users\\YourUsername\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\xxxxxxxx.selenium-profile"

# Headless mode if needed
# options.add_argument('--headless')

# ======== Website Configuration ========
website_configs = {
    "1": {
        "name": "NepalWin",
        "url": "https://bo.nepalwin.com/user/login",
        "username": "kewlim888",
        "password": "aaaa1111",
        "username_xpath": "//input[@placeholder='Username:']",
        "password_xpath": "//input[@placeholder='Password:']"
    },
    "2": {
        "name": "95np",
        "url": "https://bo.95np.com/user/login/",  # Update this with correct 95np URL
        "username": "tommy8888",     # Update this with correct 95np username
        "password": "tommy6666",     # Update this with correct 95np password
        "username_xpath": "//input[@placeholder='Username:']",  # Update if different
        "password_xpath": "//input[@placeholder='Password:']"   # Update if different
    }
}

def select_website():
    """Display menu and get user selection"""
    print("\n" + "="*50)
    print("           SELECT WEBSITE")
    print("="*50)
    
    for key, config in website_configs.items():
        print(f"{key}. {config['name']}")
    
    print("="*50)
    
    while True:
        try:
            choice = input("Enter your choice (1-2): ").strip()
            if choice in website_configs:
                selected_config = website_configs[choice]
                print(f"\n✅ Selected: {selected_config['name']}")
                print(f"🌐 URL: {selected_config['url']}")
                print(f"👤 Username: {selected_config['username']}")
                print("-"*50)
                return selected_config
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            exit(0)

# Setup terminal with custom settings
setup_automation_terminal("Deposit Crawler")

# Select website configuration BEFORE driver initialization
config = select_website()

# Setup the driver with error handling
try:
    print("🔧 Setting up Firefox driver...")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    print("✅ Firefox driver started successfully")
except Exception as e:
    print(f"❌ Firefox driver failed to start: {e}")
    print("\n🔧 Trying alternative Firefox setup...")
    try:
        # Try without GeckoDriverManager
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service()  # Use system geckodriver
        driver = webdriver.Firefox(service=service, options=options)
        driver.maximize_window()
        print("✅ Firefox driver started with alternative setup")
    except Exception as e2:
        print(f"❌ Alternative Firefox setup also failed: {e2}")
        print("\n🔧 Trying Chrome as fallback...")
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            driver.maximize_window()
            print("✅ Chrome driver started successfully as fallback")
        except Exception as e3:
            print(f"❌ Chrome fallback also failed: {e3}")
            print("\n💡 Troubleshooting suggestions:")
            print("1. Make sure Firefox or Chrome is installed and updated")
            print("2. Try restarting your computer")
            print("3. Check if any antivirus is blocking webdrivers")
            print("4. Run as administrator")
            print("5. Try running: pip install --upgrade selenium webdriver-manager")
            sys.exit(1)

# Login with selected configuration
print(f"\n🚀 Connecting to {config['name']}...")
driver.get(config['url'])

wait = WebDriverWait(driver, 40)
username_input = wait.until(EC.presence_of_element_located((By.XPATH, config['username_xpath'])))
username_input.send_keys(config['username'])

wait = WebDriverWait(driver, 40)
password_input = wait.until(EC.presence_of_element_located((By.XPATH, config['password_xpath'])))
password_input.send_keys(config['password'])
password_input.send_keys(Keys.ENTER)

print(f"✅ Login attempted for {config['name']}")



# ======== Entered Main Page ========

# ======== Entered Transaction =======

# Select date section
from date_selector import get_date_selection, DateSelector

# Use date selection modal
start_date, end_date = get_date_selection()

if start_date and end_date:
    print(f"\033[1;32m[APPROVED]\033[0m Date range selected: {start_date} to {end_date}")
    print(f"\033[1;33m[INFO]\033[0m Using optimized extraction with early stopping")
else:
    print("\033[1;31m[ERROR] No dates selected, exiting...\033[0m")
    driver.quit()
    exit(1)


# ======= Print Logic Here =======

def extract_transaction_data_with_date_filter(driver, start_date, end_date, wait_timeout=20):
    """
    Extracts transaction data with early-stopping date filtering.
    Returns (collected_records, should_stop_scraping)
    """
    print(f"[INFO] Filtering for dates: {start_date} to {end_date}")
    
    # Find the Bank Transaction Record table
    try:
        title_elem = driver.find_element(
            By.XPATH, "//div[@class='ant-pro-table-list-toolbar-title' and normalize-space()='Bank Transaction Record']"
        )
        table_elem = title_elem.find_element(
            By.XPATH, "./ancestor::div[contains(@class,'ant-pro-card')]//table"
        )
        rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"[SUCCESS] Found {len(rows)} rows in Bank Transaction Record table")
    except Exception as e:
        print(f"[ERROR] Could not find Bank Transaction Record table: {e}")
        return [], True  # Stop if we can't find the table
    
    if not rows:
        print("[WARNING] No rows found in table")
        return [], False
    
    collected_records = []
    should_stop_scraping = False
    
    print(f"[INFO] Processing {len(rows)} rows with date filtering...")
    time.sleep(1)  # Stability delay
    
    for idx, row in enumerate(rows):
        try:
            cols = row.find_elements(By.TAG_NAME, 'td')
            
            if len(cols) < 6:  # Need at least 6 columns
                print(f"[WARNING] Row {idx + 1} has only {len(cols)} columns. Skipping.")
                continue
            
            # Skip summary rows
            first_col_text = cols[0].text.strip()
            if "Page Summary" in first_col_text or "Total Summary" in first_col_text:
                print(f"[INFO] Skipping summary row: '{first_col_text}'")
                continue
            
            
            # Extract date from column 2 (format: '2025-08-14 16:35:02')
            full_date_str = cols[1].text.strip()
            if not full_date_str:
                print(f"[WARNING] No date in row {idx + 1}, skipping")
                continue
            
            try:
                # Extract only the date part (ignore time)
                date_str = full_date_str.split(" ")[0]  # '2025-08-14'
                row_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # print(f"[DEBUG] Row {idx + 1}: Date {row_date}, Range {start_date} to {end_date}")
                
                # Date filtering logic
                if row_date > end_date:
                    print(f"[DEBUG] Row {idx + 1} too new ({row_date}), skipping")
                    continue
                
                if row_date < start_date:
                    print(f"[INFO] Row {idx + 1} too old ({row_date}), stopping scraping")
                    should_stop_scraping = True
                    break
                
                # Row is within date range (start_date <= row_date <= end_date)
                # Filter transaction type first
                txn_type = cols[6].text.strip() if len(cols) > 6 else ""
                print(f"[DEBUG] Row {idx + 1}: Found transaction type '{txn_type}'")
                
                if txn_type.upper() not in ("DEPOSIT", "PENDING_DEPOSIT", "MANUAL_DEPOSIT", "WITHDRAWAL", "MANUAL_WITHDRAWAL", "ADJUSTMENTADD", "ADJUSTMENTDEDUCT", "CASH_IN", "CASH_OUT", "INTERBANK_TRANSFER_IN", "INTERBANK_TRANSFER_OUT"):
                    print(f"[DEBUG] Row {idx + 1}: Skipping '{txn_type}' - not in allowed list")
                    continue
                
                print(f"[INFO] Row {idx + 1}: Collecting '{txn_type}' transaction")
                

                
                # Parse amount - different column based on transaction type
                if txn_type.upper() in ("WITHDRAWAL", "MANUAL_WITHDRAWAL", "ADJUSTMENTDEDUCT", "CASH_OUT", "INTERBANK_TRANSFER_OUT"):
                    amount_text = cols[8].text.strip().replace("Rs", "").replace(",", "").strip()
                else:  # DEPOSIT, PENDING_DEPOSIT, MANUAL_DEPOSIT, ADJUSTMENTADD, CASH_IN, INTERBANK_TRANSFER_IN
                    amount_text = cols[7].text.strip().replace("Rs", "").replace(",", "").strip()
                try:
                    amount = float(amount_text) if amount_text else 0.0
                except ValueError:
                    print(f"[WARNING] Invalid amount '{amount_text}' in row {idx + 1}, setting to 0.0")
                    amount = 0.0

                # Create record
                record = {
                    "Gateway": cols[5].text.strip(),
                    "Order ID": cols[0].text.strip(),   
                    "Phone Number": cols[4].text.strip(),  
                    "Amount": amount,  
                    "Time": full_date_str,  # Keep full timestamp
                    "Transaction Type": txn_type,
                    "Bank Tax": cols[10].text.strip() if len(cols) > 10 else "",
                    "Balance": cols[9].text.strip(),
                    "Date": row_date  # Add parsed date for easier processing
                }
                collected_records.append(record)
                
            except ValueError as e:
                print(f"[WARNING] Invalid date format '{full_date_str}' in row {idx + 1}: {e}")
                continue
                
        except Exception as e:
            print(f"[ERROR] Failed to process row {idx + 1}: {e}")
            continue
    
    print(f"[INFO] Collected {len(collected_records)} records from this page")
    print(f"[INFO] Should stop scraping: {should_stop_scraping}")
    
    return collected_records, should_stop_scraping



def print_grouped_results(gateway_groups):
    print(f"[DEBUG] print_grouped_results called with {len(gateway_groups)} gateway groups")
    for gateway, records in gateway_groups.items():
        print(f"[DEBUG] Gateway '{gateway}' has {len(records)} records")

    grand_total = 0
    grand_tax_total = 0

    # Get script directory and build path to result folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: crawler -> nepalwin -> rocketgo auto
    working_dir = os.path.dirname(os.path.dirname(script_dir))
    result_dir = os.path.join(working_dir, "result")
    os.makedirs(result_dir, exist_ok=True)
    output_file = os.path.join(result_dir, "selenium-transaction_history.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        # Separate deposits and withdrawals
        deposit_groups = defaultdict(list)
        withdrawal_groups = defaultdict(list)
        
        for gateway, records in gateway_groups.items():
            for record in records:
                txn_type = record.get("Transaction Type", "").upper()
                print(f"[DEBUG] Record transaction type: '{txn_type}' from record: {record.get('Transaction Type', 'MISSING')}")
                if txn_type in ("DEPOSIT", "PENDING_DEPOSIT", "MANUAL_DEPOSIT", "ADJUSTMENTADD", "CASH_IN", "INTERBANK_TRANSFER_IN"):
                    deposit_groups[gateway].append(record)
                    print(f"[DEBUG] Added to deposits: {txn_type}")
                elif txn_type in ("WITHDRAWAL", "MANUAL_WITHDRAWAL", "ADJUSTMENTDEDUCT", "CASH_OUT", "INTERBANK_TRANSFER_OUT"):
                    withdrawal_groups[gateway].append(record)
                    print(f"[DEBUG] Added to withdrawals: {txn_type}")
                else:
                    print(f"[DEBUG] Transaction type '{txn_type}' not recognized for grouping")
        
        # Helper function to process a group of transactions
        def process_transaction_group(groups, section_title):
            nonlocal grand_total
            if not groups:
                return
                
            f.write("="*80 + "\n")
            f.write(f"                              {section_title}\n")
            f.write("="*80 + "\n")
            print(f"\033[92m{'='*80}\033[0m")
            print(f"\033[92m                              {section_title}\033[0m")
            print(f"\033[92m{'='*80}\033[0m")
            
            for gateway, records in groups.items():
                total_amount = sum(record["Amount"] if isinstance(record["Amount"], (int, float)) else float(record["Amount"].replace(",", "")) for record in records)
                grand_total += total_amount 

                header = f"\n==== {gateway} ({len(records)} record{'s' if len(records) != 1 else ''}) | Total Amount: Rs {total_amount:,.2f} ====\n"
                print(f"\033[92m{header}\033[0m")
                f.write(header)

                # Sort records by Order ID (higher ID = latest) with error handling
                def safe_parse_id(record):
                    """Parse Order ID for sorting (higher ID = more recent)"""
                    try:
                        order_id = record.get("Order ID", "0")
                        if order_id and str(order_id).strip():
                            return int(str(order_id).strip())
                        else:
                            return 0  # Put records with no ID at the end
                    except (ValueError, TypeError):
                        print(f"[WARNING] Invalid Order ID format: '{record.get('Order ID')}'")
                        return 0

                sorted_records = sorted(records, key=safe_parse_id, reverse=True)

                for i, record in enumerate(sorted_records, 1):
                    entry = (
                        f"\nRecord #{i}\n"
                        f"Order ID: {record['Order ID']}\n"
                        f"Transaction Type: {record.get('Transaction Type', 'Unknown')}\n"
                        f"Phone Number: {record['Phone Number']}\n"
                        f"Amount: {record['Amount']:,.2f}\n"
                        f"Bank Charges: {record.get('Bank Tax', 'N/A')}\n"
                        f"Balance: {record.get('Balance', 'N/A')}\n"
                        f"Time: {record['Time']}\n"
                    )
                    print(f"\033[94m{entry}\033[0m")
                    f.write(entry)

                footer = f"\n>> Total Amount for {gateway}: Rs {total_amount:,.2f}\n"
                print(f"\033[93m{footer}\033[0m")
                f.write(footer)
        
        # Process deposits and withdrawals separately
        print(f"[DEBUG] Final groups: Deposits={sum(len(r) for r in deposit_groups.values())}, Withdrawals={sum(len(r) for r in withdrawal_groups.values())}")
        process_transaction_group(deposit_groups, "DEPOSITS")
        process_transaction_group(withdrawal_groups, "WITHDRAWALS")

        total_records = sum(len(records) for records in gateway_groups.values())

        # Helper to parse Bank Tax value from string
        def parse_fee(fee_str):
            try:
                return float(str(fee_str).replace("Rs", "").replace(",", "").strip()) if fee_str and str(fee_str).strip() else 0.0
            except (ValueError, TypeError):
                return 0.0

        DEPOSIT_TYPES = ("DEPOSIT", "PENDING_DEPOSIT", "MANUAL_DEPOSIT", "ADJUSTMENTADD", "CASH_IN", "INTERBANK_TRANSFER_IN")
        WITHDRAWAL_TYPES = ("WITHDRAWAL", "MANUAL_WITHDRAWAL", "ADJUSTMENTDEDUCT", "CASH_OUT", "INTERBANK_TRANSFER_OUT")

        # Collect per-gateway stats
        deposit_stats = {}  # gateway -> (count, amount, fee)
        withdrawal_stats = {}

        for gateway, records in gateway_groups.items():
            dep_records = [r for r in records if r.get("Transaction Type", "").upper() in DEPOSIT_TYPES]
            wit_records = [r for r in records if r.get("Transaction Type", "").upper() in WITHDRAWAL_TYPES]

            if dep_records:
                deposit_stats[gateway] = (
                    len(dep_records),
                    sum(r["Amount"] for r in dep_records),
                    sum(parse_fee(r.get("Bank Tax", "")) for r in dep_records)
                )
            if wit_records:
                withdrawal_stats[gateway] = (
                    len(wit_records),
                    sum(r["Amount"] for r in wit_records),
                    sum(parse_fee(r.get("Bank Tax", "")) for r in wit_records)
                )

        # Helper to build a box-drawing table
        def build_table(title, stats):
            """Build a box-drawing table. stats = {gateway: (count, amount, fee)}"""
            if not stats:
                return ""

            # Calculate column widths
            col1_width = max(len(title), max(len(gw) for gw in stats), len("TOTAL"))
            col2_width = max(len("Records"), max(len(str(s[0])) for s in stats.values()))

            # Format amounts and fees
            amounts = {gw: f"Rs {s[1]:,.2f}" for gw, s in stats.items()}
            fees = {gw: f"Rs {s[2]:,.2f}" for gw, s in stats.items()}
            total_count = sum(s[0] for s in stats.values())
            total_amount = sum(s[1] for s in stats.values())
            total_fee = sum(s[2] for s in stats.values())
            total_amount_str = f"Rs {total_amount:,.2f}"
            total_fee_str = f"Rs {total_fee:,.2f}"

            col3_width = max(len("Amount"), max(len(a) for a in amounts.values()), len(total_amount_str))
            col4_width = max(len("Fee"), max(len(f) for f in fees.values()), len(total_fee_str))
            col2_width = max(col2_width, len(str(total_count)))

            # Build the table
            sep = f"+-{'-'*col1_width}-+-{'-'*col2_width}-+-{'-'*col3_width}-+-{'-'*col4_width}-+"
            header = f"| {title:<{col1_width}} | {'Records':>{col2_width}} | {'Amount':>{col3_width}} | {'Fee':>{col4_width}} |"

            lines = [sep, header, sep]
            for gw, (count, _, _) in stats.items():
                lines.append(f"| {gw:<{col1_width}} | {count:>{col2_width}} | {amounts[gw]:>{col3_width}} | {fees[gw]:>{col4_width}} |")
            lines.append(sep)
            lines.append(f"| {'TOTAL':<{col1_width}} | {total_count:>{col2_width}} | {total_amount_str:>{col3_width}} | {total_fee_str:>{col4_width}} |")
            lines.append(sep)

            return "\n".join(lines)

        # Build grand total output
        f.write("\n")
        grand_total_header = "=========================== GRAND TOTAL ==========================="
        print(f"\033[92m{grand_total_header}\033[0m")
        f.write(grand_total_header + "\n")

        # Deposits table
        dep_table = build_table("DEPOSITS", deposit_stats)
        if dep_table:
            print(f"\033[92m{dep_table}\033[0m")
            f.write(dep_table + "\n")

        # Blank line between tables
        print()
        f.write("\n")

        # Withdrawals table
        wit_table = build_table("WITHDRAWALS", withdrawal_stats)
        if wit_table:
            print(f"\033[92m{wit_table}\033[0m")
            f.write(wit_table + "\n")



def wait_for_table_loaded(driver, timeout=20):
    """Wait for the ant-spin-blur effect to disappear, indicating table data is ready."""
    try:
        # First, wait briefly for the blur to appear (it may take a moment after click)
        time.sleep(0.5)

        # Check if blur is present
        blur_elements = driver.find_elements(By.CSS_SELECTOR, ".ant-spin-container.ant-spin-blur")
        if blur_elements:
            print("[INFO] Table loading detected (blur effect). Waiting for data to load...")
            WebDriverWait(driver, timeout).until(
                EC.none_of(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-spin-container.ant-spin-blur")))
            )
            print("[INFO] Table loading complete (blur removed)")
        else:
            print("[DEBUG] No blur detected, table may already be loaded")

        # Small extra delay for DOM to stabilize
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"[WARNING] Timeout waiting for blur to clear: {e}. Proceeding anyway.")
        time.sleep(2)
        return True


def click_next_page(driver, wait_timeout=10):
    try:
        selectors_to_try = [
            "//li[@title='Next Page' and @aria-disabled='false']//button[@class='ant-pagination-item-link']",
            # Fallback: by class only (less strict)
            "//button[@class='ant-pagination-item-link']",
        ]

        next_button = None
        working_selector = None

        print("[DEBUG] Searching for Next button...")

        for selector in selectors_to_try:
            try:
                print(f"[DEBUG] Trying: {selector}")
                next_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                working_selector = selector
                print(f"[SUCCESS] Found next button using: {selector}")
                break
            except Exception as e:
                print(f"[DEBUG] Failed: {e}")
                continue

        if not next_button:
            print("[ERROR] Could not find Next button with any selector")
            return False

        # Try multiple click strategies
        print(f"[DEBUG] Found button, attempting to click using: {working_selector}")

        # Strategy 1: Regular click
        try:
            next_button.click()
            time.sleep(1)
            print(f"[INFO] Successfully clicked Next button with regular click")
            return True
        except Exception as e:
            print(f"[DEBUG] Regular click failed: {e}")

        # Strategy 2: JavaScript click
        try:
            print("[DEBUG] Trying JavaScript click...")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(1)
            print(f"[INFO] Successfully clicked Next button with JavaScript")
            return True
        except Exception as e:
            print(f"[DEBUG] JavaScript click failed: {e}")

        # Strategy 3: Action chains click
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            print("[DEBUG] Trying ActionChains click...")
            ActionChains(driver).move_to_element(next_button).click().perform()
            time.sleep(1)
            print(f"[INFO] Successfully clicked Next button with ActionChains")
            return True
        except Exception as e:
            print(f"[DEBUG] ActionChains click failed: {e}")

        # Strategy 4: Scroll into view then click
        try:
            print("[DEBUG] Trying scroll into view then click...")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(1)
            print(f"[INFO] Successfully clicked Next button after scrolling into view")
            return True
        except Exception as e:
            print(f"[DEBUG] Scroll + click failed: {e}")

        print("[ERROR] All click strategies failed")
        return False

    except Exception as e:
        print(f"[WARNING] Could not click Next button: {e}")
        return False




gateway_groups = defaultdict(list)  # Global collector
seen_order_ids = set()  # Track seen Order IDs to prevent duplicates


def run_optimized_transaction_extraction(driver, start_date, end_date):
    """
    Optimized extraction with early stopping based on date range.
    Stops scraping when encountering dates older than start_date.
    """
    page_counter = 1
    all_collected_records = []
    duplicate_count = 0
    stop_scraping = False
    
    print(f"\033[92m[INFO] Starting optimized extraction for date range: {start_date} to {end_date}\033[0m")
    
    while not stop_scraping:
        print(f"\033[92m[INFO] Scraping page {page_counter}...\033[0m")
        
        # Extract data from current page with date filtering
        page_records, should_stop = extract_transaction_data_with_date_filter(
            driver, start_date, end_date
        )
        
        # Check for duplicates and add to collection
        for record in page_records:
            order_id = record["Order ID"]
            if order_id not in seen_order_ids:
                all_collected_records.append(record)
                seen_order_ids.add(order_id)
            else:
                duplicate_count += 1
                print(f"\033[93m[WARNING] Duplicate Order ID '{order_id}' found on page {page_counter}. Skipping.\033[0m")
        
        print(f"[INFO] Page {page_counter}: Collected {len(page_records)} new records")
        
        # Check if we should stop scraping
        if should_stop:
            print(f"\033[93m[INFO] Reached date boundary. Stopping extraction at page {page_counter}.\033[0m")
            stop_scraping = True
            break
        
        # Try to go to next page
        print(f"[DEBUG] Attempting to navigate to next page...")
        has_next = click_next_page(driver)
        if not has_next:
            print("[INFO] No more pages found. Finishing extraction.")
            break

        # Wait for blur/loading effect to finish before scraping next page
        wait_for_table_loaded(driver)
        print(f"[SUCCESS] Successfully navigated to page {page_counter + 1}")

        page_counter += 1
    
    # Group records by gateway for output
    gateway_groups = defaultdict(list)
    for record in all_collected_records:
        gateway_groups[record["Gateway"]].append(record)
    
    # Print summary
    total_records = len(all_collected_records)
    print(f"\033[92m[SUMMARY] Extraction completed:\033[0m")
    print(f"  - Pages scraped: {page_counter}")
    print(f"  - Total records collected: {total_records}")
    print(f"  - Unique gateways: {len(gateway_groups)}")
    print(f"  - Duplicates skipped: {duplicate_count}")
    
    if total_records > 0:
        print_grouped_results(gateway_groups)
    else:
        print("\033[93m[WARNING] No records found in the specified date range.\033[0m")
    
def show_post_crawl_menu():
    """Show menu after crawling is complete"""
    import subprocess

    # Get script directory and project root (nepalwin folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Goes up from crawler to nepalwin

    # Define script paths relative to project structure
    scripts = {
        "1": os.path.join(script_dir, "phone_number.py"),  # In same crawler folder
        "2": os.path.join(project_root, "add_data", "add_deposit"),
        "3": os.path.join(project_root, "add_data", "add-player"),
    }

    print("\n" + "="*70)
    print("           CRAWLING COMPLETED - SELECT NEXT ACTION")
    print("="*70)
    print("1. Run Phone Number Crawler Script")
    print("2. Run Add Deposit Script (with start Order ID configuration)")
    print("3. Run Add Player Script")
    print("4. Exit")
    print("="*70)

    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice in ["1", "2", "3"]:
                script_path = scripts[choice]
                script_name = os.path.basename(script_path)

                if not os.path.exists(script_path):
                    print(f"❌ Script not found: {script_path}")
                    continue

                print(f"\n🚀 Starting {script_name}...")
                print("="*70)
                subprocess.run(["python", script_path], check=False)
                return
            elif choice == "4":
                print("\n✅ Exiting...")
                return
            else:
                print("❌ Invalid choice. Please enter 1-4.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            return

def main():
    run_optimized_transaction_extraction(driver, start_date, end_date)
    time.sleep(5)
    driver.quit()
    cleanup_terminal()

    # Show post-crawl menu
    show_post_crawl_menu()

if __name__ == "__main__":
    # Set up signal handlers for stopping
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill command
    print("🚦 Press Ctrl+C to stop the automation at any time")
    print("   (Note: On macOS terminal, use Ctrl+C, not Cmd+C)")
    main()