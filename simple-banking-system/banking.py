# Write your code here
from string import digits
import random
import sqlite3


class Card:
    IIN = str(400000)
    list_of_digits = list(digits)
    user_choice = None

    def __init__(self):
        account_number = "".join(map(str, random.sample(Card.list_of_digits, 9)))
        checksum = Card.find_checksum(account_number)
        self.number = (Card.IIN + account_number + checksum)
        self.PIN = "".join(map(str, random.sample(Card.list_of_digits, 4)))

    @classmethod
    def find_checksum(cls, account_number):
        IIN_by_digits = [int(digit) for digit in Card.IIN]
        account_number_by_digits = [int(digit) for digit in account_number]
        # Luhn algorithm:
        # 1. Original number without last digit
        all_digits = IIN_by_digits + account_number_by_digits
        # 2. Multiply odd digits (i.e with even index) by 2
        all_digits = [digit[1] * 2 if digit[0] % 2 == 0 else digit[1] for digit in enumerate(all_digits)]
        # 3. Subtract 9 from numbers over 9
        all_digits = [(digit - 9) if digit > 9 else digit for digit in all_digits]
        # 4. Add all numbers
        all_digits = sum(all_digits)
        checksum = 10 - (all_digits % 10) if all_digits % 10 != 0 else 0
        return str(checksum)

    @staticmethod
    def main_menu():
        Card.create_db_and_table()
        while True:
            print("""
                1. Create an account
                2. Log into account
                0. Exit
            """)
            Card.user_choice = int(input())
            if Card.user_choice == 1:
                Card.create_card()
            elif Card.user_choice == 2:
                Card.log_in()

            if Card.user_choice == 0:
                print("\nBye!")
                break

    @staticmethod
    def create_db_and_table():
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS card(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0);
                    """)
        conn.commit()

    @staticmethod
    def create_card():
        card_instance = Card()
        card_instance.add_card_to_db()
        print("\nYour card has been created")
        print("Your card number:")
        print(card_instance.number)
        print("Your card PIN:")
        print(card_instance.PIN)

    def add_card_to_db(self):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO  card (number, pin)
                    VALUES (?, ?);
                    """, (self.number, self.PIN,))
        conn.commit()

    @staticmethod
    def log_in():
        card_number = input("Enter your card number:\n")
        PIN = input("\nEnter your PIN:\n")

        card = Card.check_credentials(card_number, PIN)
        if card:
            print("You have successfully logged in!")
            Card.account_menu(card)
        else:
            print("Wrong card number or PIN!")

    @staticmethod
    def check_credentials(card_number, PIN):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute("""
                    SELECT * FROM card WHERE number = ? AND pin = ?;
                    """, (card_number, PIN,))
        return cur.fetchone()

    @staticmethod
    def account_menu(card):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        while True:
            print("""
                1. Balance
                2. Add income
                3. Do transfer
                4. Close account
                5. Log out
                0. Exit
            """)
            Card.user_choice = int(input())
            if Card.user_choice == 1:
                balance = Card.get_balance(cur, card[1])
                print("\nBalance:", balance)
            elif Card.user_choice == 2:
                income = int(input("Enter income:\n"))
                Card.add_income(conn, cur, income, card[1])
                print("Income was added!")
            elif Card.user_choice == 3:
                number_to_transfer = input("Transfer\nEnter card number:\n")
                if card[1] == number_to_transfer:
                    print("You can't transfer money to the same account!")
                else:
                    # Check Luhn algorithm
                    checksum = Card.find_checksum(number_to_transfer[6:-1])
                    if checksum != number_to_transfer[-1]:
                        print("Probably you made a mistake in the card number. Please try again!")
                    else:
                        existence = Card.check_existence(cur, number_to_transfer)
                        if existence:
                            money_to_transfer = int(input("Enter how much money you want to transfer:\n"))
                            balance = Card.get_balance(cur, card[1])
                            if balance >= money_to_transfer:
                                Card.transfer_money(conn, cur, money_to_transfer, card[1])
                                Card.add_income(conn, cur, money_to_transfer, number_to_transfer)
                                print("Success!")
                            else:
                                print("Not enough money!")
                        else:
                            print("Such a card does not exist.")
            elif Card.user_choice == 4:
                Card.close_account(conn, cur, card[1])
            elif Card.user_choice == 5:
                print("\nYou have successfully logged out!")
                break
            elif Card.user_choice == 0:
                print("\nBye!")
                break

    @staticmethod
    def get_balance(cur, card_number):
        cur.execute("""
                   SELECT balance FROM card WHERE number = ?;
                    """, (card_number,))
        balance = cur.fetchone()[0]
        return balance

    @staticmethod
    def add_income(conn, cur, income, card_number):
        cur.execute("""
                    UPDATE card
                    SET balance = balance + ? WHERE number = ?;
                    """, (income, card_number, ))
        conn.commit()

    @staticmethod
    def check_existence(cur, number_to_transfer):
        cur.execute("""
                    SELECT * FROM card WHERE number = ?;
                    """, (number_to_transfer, ))
        return cur.fetchone()

    @staticmethod
    def transfer_money(conn, cur, money_to_transfer, card_number):
        cur.execute("""
                    UPDATE card 
                    SET balance = balance - ? WHERE number = ?;
                    """, (money_to_transfer, card_number, ))
        conn.commit()

    @staticmethod
    def close_account(conn, cur, card_number):
        cur.execute("""
                    DELETE FROM card WHERE number = ?;
                    """, (card_number, ))
        conn.commit()


Card.main_menu()
