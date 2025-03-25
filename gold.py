import time
from playwright.sync_api import sync_playwright
import pyfiglet
from colorama import init, Fore, Style

# تهيئة colorama للألوان
init()

def load_tokens():
    """Load tokens from data.txt (one token per line)."""
    try:
        with open("data.txt", "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
        print(f"Tokens from data.txt: {Fore.RED}{len(tokens)}{Style.RESET_ALL}")
        return tokens
    except FileNotFoundError:
        print("data.txt not found!")
        return []

def check_energy(page, token):
    """Retrieve the current energy level from the page."""
    try:
        energy_element = page.query_selector("div._label_15n79_25")
        if energy_element:
            energy_text = energy_element.inner_text().strip()
            energy = int(energy_text.split("/")[0])
            return energy
    except Exception as e:
        print(f"Account {token['index']}: Error retrieving energy: {e}")
    return 0

def get_coin_count(page):
    """Retrieve the current coin balance from the page."""
    try:
        coin_element = page.query_selector("div._container_1wzqv_72 span._amount_1wzqv_81")
        if coin_element:
            return int(coin_element.inner_text().strip().replace(",", ""))
    except:
        pass
    return 0

def perform_task(token_data, page):
    """Perform the tapping cycle for one token."""
    token = token_data["token"]
    index = token_data["index"]
    print(f"Account {index}: {Fore.MAGENTA}Navigating...{Style.RESET_ALL}")
    page.goto("https://telegram.geagle.online/")
    time.sleep(3)

    print(f"Account {index}: {Fore.BLUE}Setting...{Style.RESET_ALL}")
    page.evaluate(f"window.localStorage.setItem('session_token', '{token}')")
    page.reload()
    time.sleep(3)

    energy = check_energy(page, token_data)
    print(f"Account {index} Energy Level: {energy}")
    if energy < 100:
        print(f"Account {index}: Energy too low ({energy}), skipping.")
        return 0

    print(f"Account {index}: Starting auto-tapping (50 taps/sec)...")
    page.evaluate("""
        (function(){
            var start = Date.now();
            var tapInterval = setInterval(function(){
                var tapBtn = document.querySelector("div._tapArea_njdmz_15");
                if(tapBtn){ tapBtn.click(); }
                var energyElement = document.querySelector("div._label_15n79_25");
                var energy = energyElement ? parseInt(energyElement.innerText().split("/")[0]) : 0;
                if (energy < 100 || Date.now() - start > 300000) { 
                    clearInterval(tapInterval); 
                } 
            }, 20);
        })();
    """)
    time.sleep(40)
    coins = get_coin_count(page)
    print(f"Account {index}: Tapping cycle complete. Coins: {coins}")
    return coins

def main():
    """Process tokens in an infinite loop with minimal delay."""
    # عرض Mohamed 306 كبيرًا في البداية
    print(pyfiglet.figlet_format("Mohamed 306"))

    tokens = load_tokens()
    if not tokens:
        print("No tokens found in data.txt! Exiting...")
        return

    # إضافة رقم لكل رمز
    tokens_with_index = [{"token": token, "index": i + 1} for i, token in enumerate(tokens)]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        total_coins = 0
        cycle_count = 0

        while True:
            cycle_count += 1
            print(f"{Fore.YELLOW}{pyfiglet.figlet_format(f'Starting Gold Eagle {cycle_count}')}{Style.RESET_ALL}")
            
            for token_data in tokens_with_index:
                total_coins += perform_task(token_data, page)
            
            # تعديل نهاية الدورة لعرض الرقم كبيرًا
            print("\nTotal Coins After Cycle:")
            print(pyfiglet.figlet_format(f"{total_coins:,}"))
            print("\n")
            time.sleep(1)

        browser.close()  # لن يصل إلى هنا بسبب الحلقة

if __name__ == "__main__":
    main()