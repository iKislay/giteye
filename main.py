"""
GitEye - GitHub Leaked API Key Scanner
======================================

Author: Kislay
GitHub: https://github.com/iKislay
LinkedIn: https://www.linkedin.com/in/kislayy/

A comprehensive tool for scanning GitHub repositories for leaked API keys
from multiple AI services including Anthropic, OpenAI, and XAI.
"""

import threading
import sys
import rich

# Import the main functions from each scanner
from anthropic_api_scanner_main.src.main import main as anthropic_main
from chatgpt_api_leakage.src.main import main as openai_main
from xai_api_scanner.src.main import main as xai_api_main

def main():
    """
    Main entry point for GitEye - GitHub API Key Scanner
    """
    # Display GitEye logo
    rich.print("""
[bold cyan]
 ██████╗ ██╗████████╗███████╗██╗  ██╗███████╗██╗   ██╗███████╗
██╔════╝ ██║╚══██╔══╝██╔════╝╚██╗██╔╝██╔════╝╚██╗ ██╔╝██╔════╝
██║  ███╗██║   ██║   █████╗  ╚███╔╝ █████╗   ╚████╔╝ █████╗  
██║   ██║██║   ██║   ██╔══╝  ██╔██╗ ██╔══╝    ╚██╔╝  ██╔══╝  
╚██████╔╝██║   ██║   ███████╗██╔╝ ██╗███████╗   ██║   ███████╗
 ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝
[/bold cyan]
[bold yellow]GitHub API Key Scanner - Find leaked API keys across multiple services[/bold yellow]

[bold green]Author:[/bold green] Kislay
[bold blue]GitHub:[/bold blue] https://github.com/iKislay
[bold blue]LinkedIn:[/bold blue] https://www.linkedin.com/in/kislayy/
""")

    rich.print("\n[bold green]Welcome to GitEye![/bold green]")
    rich.print("Select which API keys to scan for:\n")
    print("1. Anthropic\n2. OpenAI\n3. XAI API\n4. All")
    choice = input("Select which keys to search (1/2/3/4): ").strip()

    headless = False
    if choice == "4":
        headless_input = input("Do you want to use headless Chrome? (y/n): ").strip().lower()
        headless = headless_input == "y"

    if choice == "1":
        anthropic_main()
    elif choice == "2":
        openai_main()
    elif choice == "3":
        xai_api_main()
    elif choice == "4":
        t1 = threading.Thread(target=anthropic_main, kwargs={"headless": headless})
        t2 = threading.Thread(target=openai_main, kwargs={"headless": headless})
        t3 = threading.Thread(target=xai_api_main, kwargs={"headless": headless})
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == "__main__":
    main()
