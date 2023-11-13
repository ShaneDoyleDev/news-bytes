import os
import pyfiglet
from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.table import Table
from user_account import UserAccount
from currency import Currency
from news_vendor import NewsVendor

# Load environment variables from '.env' file.
load_dotenv()
api_key = os.environ.get('API_KEY')

exchange_rate_api_key = os.environ.get('EXCHANGE_RATE_API_KEY')
news_api_key = os.environ.get('NEWS_API_KEY')

console = Console()

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main function."""
    clear_screen()

    LOGO = pyfiglet.figlet_format("NewsBytes", justify="center", font="slant")
    print(LOGO)

    # get username
    while True:
        username = input("👤 Enter your username: \n").strip()
        if not username:
            print("❌ Username cannot be empty. Please try again!")
        elif not all(name.isalpha() for name in username.split()):
            print("❌ Username should only contain letters. Please try again!")
        else:
            break

    # get user's currency
    while True:
        valid_currencies = ("USD", "EUR", "GBP", "CAD", "AUD", "CNY")
        currency = input("💰 Select your currency (EUR, USD, GBP, CAD, AUD, CNY): \n").strip().upper()
        if not currency in valid_currencies or not currency:
            print("❌ Please enter a valid currency!")
        else:
            break

    # instantiate user class
    user = UserAccount(username)

    # instantiate currency class
    currency = Currency(exchange_rate_api_key, currency)

    # instantiate news vendor class
    news_vendor = NewsVendor(news_api_key)

    while True:
        clear_screen()
        console.print("============== NewsBytes ==============", justify="center", style="bold cyan")
        console.print(f"🌐 Welcome to NewsBytes, {user.username}! 🌐", justify="center")
        print("")

        # Create a table instance
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, show_lines=True, title="Main Menu", title_style="bold cyan")

        # Add columns to the table
        table.add_column("Option", style="cyan", justify="center", no_wrap=True)
        table.add_column("Description", justify="left", style="white")

        # Add rows to the table with the menu options
        table.add_row("(1)", f"Add Funds ({currency.symbol}{user.funds:.2f})")
        table.add_row("(2)", "Purchase Credits ({} credits)".format(user.credits))
        table.add_row("(3)", "Purchase News Article")
        table.add_row("(4)", f"View Your Articles ({len(user.purchased_articles)} articles)")
        table.add_row("(5)", "Exit")

        # Print the table to the console
        console.print(table, justify="center")
        print("")

        # Get user's choice
        choice = input("Select your choice (1 - 5): ")

        # Add funds to user's account
        if choice == "1":
            clear_screen()
            print("============ Add Funds ============")
            print(f"💰 Account Funds: ({currency.symbol}{user.funds:.2f})")
            print("")

            while True:
                amount = input(f"Enter amount to add in {currency.currency_code}: ").strip()
                # Check for empty input
                if not amount:
                    print("❌ Amount cannot be empty. Please try again!")
                    continue
                try:
                    # Convert input to float and check its value
                    amount_float = float(amount)
                    if amount_float <= 0:
                        print("❌ Amount must be greater than 0. Please try again!")
                        continue
                    else:
                        # Add funds to user's account
                        user.add_funds(amount_float)
                        break
                except ValueError:
                    print("❌ Amount must be a number. Please try again!")

        # Purchase credits for users account
        if choice == "2":
            clear_screen()
            print("========= Purchase Credits =========")
            print(f"💳 Account Credits: ({user.credits})")
            for idx, option in enumerate(news_vendor.credit_options, 1):
                print(f"({idx}) {option} credits: {currency.symbol}{option * currency.conversion_rate:.2f}")
            print("")

            while True:
                credits_choice = input(f"Select credit amount (1 - {len(news_vendor.credit_options)}): ").strip()

                if not credits_choice:
                    print("❌ Amount cannot be empty. Please try again!")
                    continue

                if not credits_choice in map(str, range(1, len(news_vendor.credit_options)+1)):
                    print("❌ Please enter a valid option!")
                    continue

                selected_credits = news_vendor.credit_options[int(credits_choice) - 1]

                if user.funds < selected_credits * currency.conversion_rate:
                    clear_screen()
                    print("❌ Insufficient funds. Please add more funds to your account!")
                    print("↩️ Returning to main menu...")
                    sleep(3)
                    break
                else:
                    user.credits += selected_credits
                    user.funds -= selected_credits * currency.conversion_rate
                    break

        # Purchase news articles
        if choice == "3":
            clear_screen()
            print("====== Purchase News Article ======")
            print(f"💳 Account Credits: ({user.credits})")
            print("")

            promo_category = news_vendor.get_promo_category()

            # show categories
            for idx, category in enumerate(news_vendor.categories, 1):
                # add promo message to category if it is the promo category
                if category == promo_category:
                    print(f"({idx}) {category.title()} - {news_vendor.get_promo_message(category)} (Cost: 1 credit)")
                else:
                    print(f"({idx}) {category.title()} - (Cost: 2 credits)")

            while True:
                # get category choice
                print("")
                category_choice = input(f"Select category (1 - {len(news_vendor.categories)}): ").strip()

                if not category_choice:
                    print("❌ Category cannot be empty. Please try again!")
                    continue

                if not category_choice in map(str, range(1, len(news_vendor.categories) + 1)):
                    print("❌ Please enter a valid option!")
                    continue

                # get selected category
                selected_category = int(category_choice) - 1
                break

            #choose a news article from category
            clear_screen()
            print(f"🌍 Todays top international stories in {news_vendor.categories[selected_category]}: ")
            print("")

            # get and display articles from news vendor
            news_vendor.get_articles(selected_category)
            for idx, article in enumerate(news_vendor.selected_articles, 1):
                print(f"({idx}) {article['title']}")
            print("")
            print(f"💳 Account Credits: ({user.credits})")

            while True:
                # get article choice
                article_choice = input(f"Select article (1 - {len(news_vendor.selected_articles)}): ").strip()

                if not article_choice in map(str, range(1, len(news_vendor.selected_articles) + 1)) or not article_choice:
                    print("❌ Please enter a valid option!")
                    continue

                # get selected article and price
                selected_article = news_vendor.selected_articles[int(article_choice) - 1]

                # check if article discount applies
                if selected_article == promo_category:
                    article_price = 1
                else:
                    article_price = 2

                # check if user has enough credits
                if user.credits < article_price:
                    clear_screen()
                    print(f"❌ You don't have enough credits. These articles cost {article_price} credits each. Please top up your account!")
                    print("↩️ Returning to main menu...")
                    sleep(3)
                    break

                # purchase article and deduct account credits
                user.credits -= article_price
                user.purchased_articles.append(selected_article)
                print(f"🎉 Article purchased for {article_price} credits!")
                break

        # View purchased articles
        if choice == "4":
            clear_screen()
            print("======== Your Articles =========")
            print(f"📰 Account Articles: ({len(user.purchased_articles)})")
            print("")

            if not user.purchased_articles:
                print("You have not purchased any articles yet!")
            else:
                for idx, article in enumerate(user.purchased_articles, 1):
                    print(f"({idx}) {article['title']} by {article['author']}")
                    print(f"🗓️ published at: {article['publishedAt']}")
                    print("================================")
                    print(f"{article['description']}")
                    print(f"Access link ➡️ {article['url']}")
                    print("")

            print("")
            input("Press enter to return to main menu...")

        # Exit program
        if choice == "5":
            clear_screen()
            print("👋 Thank you for using NewsBytes!")
            print("Have a great day!")
            sleep(3)
            exit()


if __name__ == "__main__":
    main()