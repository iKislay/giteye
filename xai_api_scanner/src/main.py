"""
Author: Kislay
GitHub: https://github.com/iKislay
LinkedIn: https://www.linkedin.com/in/kislayy/

Scan GitHub for available XAI API Keys
"""

import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
import re as _re

import rich
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from .configs import KEYWORDS, LANGUAGES, PATHS, REGEX_LIST
from core.managers import ProgressManager, CookieManager, DatabaseManager
from core.key_checker import check_key
from openai import OpenAI, APIStatusError, AuthenticationError, RateLimitError

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%X]")
log = logging.getLogger("XAI-API-Leakage")
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

class APIKeyLeakageScanner:
    """
    Scan GitHub for available XAI API Keys
    """
    def __init__(self, db_file: str, keywords: list, languages: list, headless: bool = False):
        self.db_file = db_file
        self.driver: webdriver.Chrome | None = None
        self.cookies: CookieManager | None = None
        self.headless = headless
        rich.print(f"📂 Opening database file xai_api_db.db")
        self.dbmgr = DatabaseManager('xai_api')
        self.keywords = keywords
        self.languages = languages
        self.candidate_urls = []
        for regex, too_many_results, _ in REGEX_LIST:
            for path in PATHS:
                self.candidate_urls.append(f"https://github.com/search?q=(/{regex.pattern}/)+AND+({path})&type=code&ref=advsearch")
            for language in self.languages:
                if too_many_results:
                    self.candidate_urls.append(f"https://github.com/search?q=(/{regex.pattern}/)+language:{language}&type=code&ref=advsearch")
                else:
                    self.candidate_urls.append(f"https://github.com/search?q=(/{regex.pattern}/)&type=code&ref=advsearch")

    def login_to_github(self):
        rich.print("🌍 Opening Chrome ...")
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        if getattr(self, 'headless', False):
            options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(3)
        self.cookies = CookieManager(self.driver)
        cookie_exists = os.path.exists("cookies.pkl")
        self.driver.get("https://github.com/login")
        if not cookie_exists:
            rich.print("🤗 No cookies found, please login to GitHub first")
            # input("Press Enter after you logged in: ")
            self.cookies.save()
        else:
            rich.print("🍪 Cookies found, loading cookies")
            self.cookies.load()
        if self.driver is not None:
            self.cookies.verify_user_login()

    def _expand_all_code(self):
        if self.driver is None:
            return
        elements = self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'more match')]")
        for element in elements:
            element.click()

    def _find_urls_and_apis(self) -> tuple[list[str], list[str]]:
        if self.driver is None:
            return [], []
        apis_found = []
        urls_need_expand = []
        codes = self.driver.find_elements(by=By.CLASS_NAME, value="code-list")
        for element in codes:
            apis = []
            for regex, _, too_long in REGEX_LIST[2:]:
                if not too_long:
                    apis.extend(regex.findall(element.text))
            if len(apis) == 0:
                a_tag = element.find_element(by=By.XPATH, value=".//a")
                urls_need_expand.append(a_tag.get_attribute("href"))
            apis_found.extend(apis)
        return apis_found, urls_need_expand

    def _process_url(self, url: str):
        if self.driver is None:
            raise ValueError("Driver is not initialized")
        self.driver.get(url)
        match = _re.search(r'q=\(/([^/]+)/\)', url)
        search_key = match.group(1) if match else url
        
        # Convert regex pattern to friendly service name
        if 'xai-' in search_key:
            friendly_name = "XAI API Key"
        else:
            friendly_name = search_key
            
        while True:
            if self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'You have exceeded a secondary rate limit')]"):
                for _ in tqdm(range(30), desc="⏳ Rate limit reached, waiting ..."):
                    time.sleep(1)
                self.driver.refresh()
                continue
            self._expand_all_code()
            apis_found, urls_need_expand = self._find_urls_and_apis()
            rich.print(f"    🌕 There are {len(urls_need_expand)} urls waiting to be expanded for [bold yellow]{friendly_name}[/bold yellow]")
            try:
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                rich.print(f"🔍 Clicking next page for [bold yellow]{friendly_name}[/bold yellow]")
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next Page']")))
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                next_buttons[0].click()
            except Exception:
                rich.print(f"⚪️ No more pages for [bold yellow]{friendly_name}[/bold yellow]")
                break
        for u in tqdm(urls_need_expand, desc="🔍 Expanding URLs ..."):
            if self.driver is None:
                raise ValueError("Driver is not initialized")
            with self.dbmgr as mgr:
                if mgr.get_url(u):
                    rich.print(f"    🔑 skipping url '{u[:10]}...{u[-10:]}'")
                    continue
            self.driver.get(u)
            time.sleep(3)
            retry = 0
            while retry <= 3:
                matches = []
                for regex, _, _ in REGEX_LIST:
                    matches.extend(regex.findall(self.driver.page_source))
                matches = list(set(matches))
                if len(matches) == 0:
                    rich.print(f"    ⚪️ No matches found in the expanded page, retrying [{retry}/3]...")
                    retry += 1
                    time.sleep(3)
                    continue
                with self.dbmgr as mgr:
                    new_apis = [api for api in matches if not mgr.key_exists(api)]
                    new_apis = list(set(new_apis))
                apis_found.extend(new_apis)
                rich.print(f"    🔬 Found {len(matches)} matches in the expanded page, adding them to the list")
                for match in matches:
                    rich.print(f"        '{match[:10]}...{match[-10:]}'")
                with self.dbmgr as mgr:
                    mgr.insert_url(url)
                break
        self.check_api_keys_and_save(apis_found)

    def check_api_keys_and_save(self, keys: list[str]):
        with self.dbmgr as mgr:
            unique_keys = list(set(keys))
            unique_keys = [api for api in unique_keys if not mgr.key_exists(api)]
        from functools import partial
        check_key_xai = partial(check_key, service='xai_api')
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(check_key_xai, unique_keys))
            with self.dbmgr as mgr:
                for idx, (status, status_code) in enumerate(results):
                    mgr.insert(unique_keys[idx], str((status, status_code)))
                # Export to CSV after each batch
                csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api_keys_export.csv'))
                mgr.export_to_csv(csv_path, service='xai_api')

    def search(self, from_iter: int | None = None):
        progress = ProgressManager()
        total = len(self.candidate_urls)
        pbar = tqdm(
            enumerate(self.candidate_urls),
            total=total,
            desc="🔍 Searching ...",
        )
        if from_iter is None:
            from_iter = progress.load(total=total)
        for idx, url in enumerate(self.candidate_urls):
            if idx < from_iter:
                pbar.update()
                time.sleep(0.05)
                log.debug("⚪️ Skip %s", url)
                continue
            self._process_url(url)
            progress.save(idx, total)
            log.debug("🔍 Finished %s", url)
            pbar.update()
        pbar.close()

    def deduplication(self):
        with self.dbmgr as mgr:
            mgr.deduplicate()

    def update_existed_keys(self):
        with self.dbmgr as mgr:
            rich.print("🔄 Updating existed keys")
            keys = mgr.all_keys()
            from functools import partial
            check_key_xai = partial(check_key, service='xai_api')
            for key in tqdm(keys, desc="🔄 Updating existed keys ..."):
                result = check_key_xai(key[0])
                mgr.delete(key[0])
                mgr.insert(key[0], str(result))

    def update_iq_keys(self):
        with self.dbmgr as mgr:
            rich.print("🔄 Updating insuffcient quota keys")
            keys = mgr.all_iq_keys()
            from functools import partial
            check_key_xai = partial(check_key, service='xai_api')
            for key in tqdm(keys, desc="🔄 Updating insuffcient quota keys ..."):
                result = check_key_xai(key[0])
                mgr.delete(key[0])
                mgr.insert(key[0], str(result))

    def all_available_keys(self) -> list:
        with self.dbmgr as mgr:
            return mgr.all_keys()

    def __del__(self):
        if hasattr(self, "driver") and self.driver is not None:
            self.driver.quit()

def main(from_iter: int | None = None, check_existed_keys_only: bool = False, keywords: list | None = None, languages: list | None = None, check_insuffcient_quota: bool = False, headless: bool = False):
    import os
    keywords = KEYWORDS.copy() if keywords is None else keywords
    languages = LANGUAGES.copy() if languages is None else languages
    leakage = APIKeyLeakageScanner("xai_api_db.db", keywords, languages, headless)
    leakage.headless = headless
    try:
        if not check_existed_keys_only:
            leakage.login_to_github()
            leakage.search(from_iter=from_iter)
        if check_insuffcient_quota:
            leakage.update_iq_keys()
        leakage.update_existed_keys()
        leakage.deduplication()
        keys = leakage.all_available_keys()
    except KeyboardInterrupt:
        rich.print("[bold red]Interrupted by user. Saving results so far...[/bold red]")
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api_keys_export.csv'))
        with leakage.dbmgr as mgr:
            mgr.export_to_csv(csv_path, service='xai_api')
        rich.print(f"[bold green]Partial results exported to {csv_path}[/bold green]")
        return
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api_keys_export.csv'))
    with leakage.dbmgr as mgr:
        mgr.export_to_csv(csv_path, service='xai_api')
    rich.print(f"[bold green]All API keys exported to {csv_path}[/bold green]")
    rich.print(f"🔑 [bold green]Available keys ({len(keys)}):[/bold green]")
    for key in keys:
        rich.print(f"[bold green]{key[0]}[/bold green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-iter", type=int, default=None, help="Start from the specific iteration")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug mode, otherwise INFO mode. Default is False (INFO mode)")
    parser.add_argument("-ceko", "--check-existed-keys-only", action="store_true", default=False, help="Only check existed keys")
    parser.add_argument("-ciq", "--check-insuffcient-quota", action="store_true", default=False, help="Check and update status of the insuffcient quota keys")
    parser.add_argument("-k", "--keywords", nargs="+", default=KEYWORDS, help="Keywords to search")
    parser.add_argument("-l", "--languages", nargs="+", default=LANGUAGES, help="Languages to search")
    parser.add_argument("-h", "--headless", action="store_true", default=False, help="Run in headless mode")
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    main(
        from_iter=args.from_iter,
        check_existed_keys_only=args.check_existed_keys_only,
        keywords=args.keywords,
        languages=args.languages,
        check_insuffcient_quota=args.check_insuffcient_quota,
        headless=args.headless,
    ) 