import os
from math import floor

import requests
import json


def buy_sell_item(item_id):
    url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MyRuneScapePriceChecker/1.0"
    }
    response = requests.get(url, headers=headers)  #
    # print(dump.dump_all(response).decode("utf-8"))
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    data = response.json()  # Parse the JSON response
    return data["data"][f"{item_id}"]["high"], data["data"][f"{item_id}"]["low"]


def item_mapping():
    url = f"https://prices.runescape.wiki/api/v1/osrs/mapping"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MyRuneScapePriceChecker/1.0"
    }
    response = requests.get(url, headers=headers)  #
    # print(dump.dump_all(response).decode("utf-8"))
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    data = response.json()  # Parse the JSON response
    filtered_items = {item["id"]: item["name"] for item in data}
    return filtered_items


def gather_item_details(items):
    buy_items = {}

    while True:
        item_id_input = input("BUY: Enter the item id/item name (or 'd' to move to sell): ")
        if item_id_input.lower() == 'd':
            break
        try:
            item_id = item_id_from_input(item_id_input, items)
            quantity = int(input("Enter the quantity: "))
            print(f"Item ID: {item_id}, name: {items[item_id]}, Quantity: {quantity}")
            buy_items[item_id] = {
                "quantity": quantity
            }
        except ValueError:
            print("Please enter valid numbers for item id and quantity.")
        except Exception as e:
            print(f"Error: {e}")

    return buy_items


def gather_sell_item(items):
    sell_item = {}
    while True:
        item_id_input = input("SELL: Enter the item id/item name (or 'd' to move to evaluation): ")
        if item_id_input.lower() == 'd':
            break
        try:
            item_id = item_id_from_input(item_id_input, items)

            ratio_input = input("Enter the manufacturing ratio (or 'd' for 1): ")
            ratio = 1.0
            if ratio_input.lower() != 'd':
                ratio = float(ratio_input.strip())

            print(f"Item ID: {item_id}, name: {items[item_id]}, ratio: {ratio}")
            sell_item = {
                "item_id": item_id,
                "ratio": ratio
            }
            break
        except ValueError as e:
            print(f"Please enter valid numbers for sell price and ratio. {e}")
        except Exception as e:
            print(f"Error: {e}")

    return sell_item


def item_id_from_input(item_id_input, items):
    if item_id_input.isdigit():
        item_id = int(item_id_input)
    else:
        item_id = next((iid for iid, name in items.items() if name.lower() == item_id_input.lower()), None)
        if item_id is None:
            raise ValueError("Item not found.")
    return item_id


def print_results(items, buy_items, sell_item):
    longest_name = max(max([len(items[int(item_id)]) for item_id in buy_items]), len("Item Name"))
    longest_price = max(max([(buy_items[item_id]["buy_price"] % 10) for item_id in buy_items]), len("Buy Price"))
    longest_quantity = max(max([(buy_items[item_id]["purchaseQuantity"] % 10) for item_id in buy_items]),
                           len("Quantity"))
    print(f"--{'-' * longest_name}---{'-' * longest_price}---{'-' * longest_quantity}--")
    print(
        f"| {'Item Name'.ljust(longest_name)} | {'Buy Price'.ljust(longest_price)} | {'Quantity'.ljust(longest_quantity)} |")
    print(f"--{'-' * longest_name}---{'-' * longest_price}---{'-' * longest_quantity}--")
    for item_id in buy_items:
        item_name = items[int(item_id)].ljust(longest_name)
        item_price = str(buy_items[item_id]["buy_price"]).ljust(longest_price)
        item_quantity = str(buy_items[item_id]["purchaseQuantity"]).ljust(longest_quantity)
        print(f"| {item_name} | {item_price} | {item_quantity} |")
    print(f"--{'-' * longest_name}---{'-' * longest_price}---{'-' * longest_quantity}--")
    print(f"Sell Item: {items[sell_item['item_id']]} for {sell_item['sell_item']}")


# noinspection PyTypeChecker
def perform_pricing():
    items = item_mapping()
    buy_items = {}
    sell_item = {}
    print("Welcome to the RuneScape Price Checker!")
    print("This tool will help you calculate the profit from buying and selling items in RuneScape.")
    load_format_input = input("Would you like to load from a file or build?: (l/b) ")
    if load_format_input.lower() == 'l':
        print(f"Available files: {', '.join([f for f in os.listdir() if f.endswith('.json')])}")
        file_name = input("Enter the name of the file to load (without .json): ")
        try:
            with open(f"{file_name.strip()}.json", "r") as f:
                data = json.load(f)
                buy_items = data.get("buy_items", {})
                sell_item = data.get("sell_item", {})
                print("Data loaded successfully.")
        except FileNotFoundError as e:
            print(f"File {file_name.strip()}.json not found. Starting fresh. {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from the file. {e}")
    else:
        buy_items = gather_item_details(items)
        sell_item = gather_sell_item(items)

        save_input = input("Would you like to save these inputs? (y/n) ")
        if save_input.lower() == 'y':
            name_input = input("Enter a name for the input (without .json): ")
            with open(f"{name_input.strip()}.json", "w") as f:
                json.dump({
                    "buy_items": buy_items,
                    "sell_item": sell_item
                }, f, indent=4)
        else:
            print("Inputs not saved.")

    while True:
        price(buy_items, items, sell_item)
        cont = input("Exit or restart? (y/n/r): ")
        if cont.lower() == 'r':
            perform_pricing()
        elif cont.lower() != 'y':
            print("Exiting the RuneScape Price Checker. Goodbye!")
            break


def price(buy_items, items, sell_item):
    for buy_item in buy_items:
        try:
            buy_price, _ = buy_sell_item(buy_item)
            buy_items[buy_item]["buy_price"] = buy_price
        except Exception as e:
            print(f"Error fetching buy price for item {buy_item}: {e}")
    try:
        _, sell_price = buy_sell_item(sell_item["item_id"])
        sell_item["sell_item"] = sell_price
    except Exception as e:
        print(f"Error fetching sell price for item {sell_item['item_id']}: {e}")
    total_price = 0
    for item_id in buy_items:
        total_price += buy_items[item_id]["quantity"] * buy_items[item_id]["buy_price"]

    print(f"Total price of items to buy: {total_price}")

    ratioed_sell_item = sell_item["sell_item"] * sell_item["ratio"]

    print(f"Profit per item: {ratioed_sell_item - total_price}")

    total_cash = 0
    while True:
        total_cash_input = input("Enter total cash (in k) (or 'd' to quit): ")
        if total_cash_input.lower() == 'd':
            break
        try:
            total_cash = int(total_cash_input) * 1000
            break
        except ValueError as e:
            print(f"Please enter valid numbers total cash. {e}")
        except Exception as e:
            print(f"Error: {e}")
    purchasable_items = floor(total_cash // total_price)
    for item_id in buy_items:
        buy_items[item_id]["purchaseQuantity"] = buy_items[item_id]["quantity"] * purchasable_items
    print_results(items, buy_items, sell_item)
    print(
        f"Total cash: {total_cash}, You can make {purchasable_items}. Final cash: {purchasable_items * ratioed_sell_item}")


if __name__ == '__main__':
    perform_pricing()
