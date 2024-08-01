from collections import UserDict
import re
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self.value = None
        self.set_phone(value)

    def set_phone(self, value):
        if re.fullmatch(r'\d{10}', value):
            self.value = value
        else:
            raise ValueError("Phone number must be exactly 10 digits.")

    def __str__(self):
        return self.value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.set_phone(new_phone)
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        birthday_str = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found.")

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today()
        for record in self.data.values():
            if record.birthday:
                days = record.days_to_birthday()
                if days is not None and days <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": record.birthday.value.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper

@input_error
def add_birthday(args, book):
    name, birthday = args[0], args[1]
    if name in book.data:
        book.data[name].add_birthday(birthday)
        print(f"Birthday {birthday} added for {name}.")
    else:
        print(f"No contact found with name {name}.")

@input_error
def show_birthday(args, book):
    name = args[0]
    if name in book.data and book.data[name].birthday:
        print(f"{name}'s birthday is on {book.data[name].birthday}.")
    else:
        print(f"No birthday found for {name}.")

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        for entry in upcoming:
            print(f"{entry['name']} has a birthday on {entry['birthday']}.")
    else:
        print("No upcoming birthdays in the next 7 days.")

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0], parts[1:]

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) < 2:
                print("Please provide both name and phone number.")
                continue
            name, phone = args[0], args[1]
            if name in book.data:
                book.data[name].add_phone(phone)
                print(f"Added phone {phone} to existing contact {name}.")
            else:
                record = Record(name)
                record.add_phone(phone)
                book.add_record(record)
                print(f"Created new contact {name} with phone {phone}.")

        elif command == "change":
            if len(args) < 3:
                print("Please provide name, old phone, and new phone.")
                continue
            name, old_phone, new_phone = args[0], args[1], args[2]
            if name in book.data:
                try:
                    book.data[name].edit_phone(old_phone, new_phone)
                    print(f"Changed phone {old_phone} to {new_phone} for contact {name}.")
                except ValueError:
                    print(f"Phone number {old_phone} not found for contact {name}.")
            else:
                print(f"No contact found with name {name}.")

        elif command == "phone":
            if len(args) < 1:
                print("Please provide a name.")
                continue
            name = args[0]
            if name in book.data:
                phones = ", ".join(str(phone) for phone in book.data[name].phones)
                print(f"{name}'s phone numbers: {phones}.")
            else:
                print(f"No contact found with name {name}.")

        elif command == "all":
            if not book.data:
                print("No contacts found.")
            else:
                print(book)

        elif command == "add-birthday":
            if len(args) < 2:
                print("Please provide both name and birthday.")
                continue
            add_birthday(args, book)

        elif command == "show-birthday":
            if len(args) < 1:
                print("Please provide a name.")
                continue
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(args, book)

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
