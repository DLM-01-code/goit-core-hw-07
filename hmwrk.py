from datetime import datetime, timedelta
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit():
            raise ValueError("Phone must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone must contain exactly 10 digits")
        super().__init__(value)



class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in DD.MM.YYYY format")
        super().__init__(value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone not found")

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Phone not found")

        try:
            new_phone_obj = Phone(new_phone)
        except ValueError as e:
            raise ValueError(f"Invalid new phone: {e}")

        index = self.phones.index(phone_obj)
        self.phones[index] = new_phone_obj

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"[{self.name.value}]: [{phones_str}], birthday: [{birthday_str}]"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if not record.birthday:
                continue

            bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            congratulation_date = bday_date.replace(year=today.year)

            if congratulation_date < today:
                congratulation_date = congratulation_date.replace(year=today.year + 1)

            delta_days = (congratulation_date - today).days

            if 0 <= delta_days <= days:

                if congratulation_date.weekday() == 5: 
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            name = args[0] if args else "Unknown"
            return f"Contact [{name}] not found."
        except IndexError:
            if func.__name__ == "add_birthday":
                return "Invalid input. Usage: add-birthday [name] [DD.MM.YYYY]"
            elif func.__name__ == "add":
                return "Invalid input. Usage: add [name] [phone]"
            elif func.__name__ == "change":
                return "Invalid input. Usage: change [name] [old_phone] [new_phone]"
            elif func.__name__ == "show_birthday":
                return "Invalid input. Usage: show-birthday [name]"
            elif func.__name__ == "phone":
                return "Invalid input. Usage: phone [name]"
            else:
                return "Not enough arguments. Please try again."
    return inner



@input_error
def add(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError
    name, phone = args
    record = book.find(name)

    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)

    return f"Contact [{name}] added successfully."


@input_error
def change(args, book: AddressBook):
    if len(args) != 3:
        raise IndexError
    name, old_phone, new_phone = args
    record = book.find(name)

    if not record:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return f"Phone for [{name}] updated successfully."


@input_error
def phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    if not record or not record.phones:
        return f"No phones found for [{name}]"

    phones_str = ", ".join(p.value for p in record.phones)
    return f"[{record.name.value}]: {phones_str}"


@input_error
def all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts available."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError
    name, birthday = args
    record = book.find(name)
    
    if not record:
        record = Record(name)
        book.add_record(record)

    record.add_birthday(birthday)
    return f"Birthday for [{name}] added successfully."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)

    if not record:
        raise KeyError

    if not record.birthday:
        return f"Birthday for [{name}] not found"

    return record.birthday.value


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays"

    result = ""
    for item in upcoming:
        result += f"{item['name']} congratulate in {item['birthday']}\n"

    return result.strip()


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    if len(parts) >1:
        two_word_command = f"{parts[0].lower()} {parts[1].lower()}"
        if two_word_command in ["add-birthday", "new-birthday", "add-b-day", "show-birthday", "birthday", "show-b-day", "birthdays", "upcoming birthdays", "upcoming b-days"]:
            return two_word_command, parts[2:]
    return command, parts[1:]


def main():
    book = AddressBook()
    print("Type 'hello' or 'hi' to display the commands.")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit","bye"]:
            print("Good bye!")
            break
        elif command in ["hello", "hi"]:
            print(":3"*5 + " " "Hi! I'm AddressBook and b-day bot" " " + ":3"*5)
            print("This your helps commands: ")
            print("1: add: add [name] [phone]\n2: change, edit: change [name] [old_phone] [new_phone]\n3: phone, show: phone [name]\n4: all, show-all: show all contacts\n5: add-birthday, new-birthday, add-b-day: add-birthday [name] [birthday]\n6: show-birthday, birthday, show-b-day: show birthday [name]\n7: birthdays, upcoming birthdays, upcoming b-days: show upcoming birthdays\n8: close, exit, bye: close the bot\n9: hello, hi: show help\n")
            print("How can I help you?")
        elif command in ["add", "new"]:
            print(add(args, book))
        elif command in ["change", "edit"]:
            print(change(args, book))
        elif command in ["phone", "show"]:
            print(phone(args, book))
        elif command in ["all", "show-all"]:
            print(all_contacts(book))
        elif command in ["add-birthday", "new-birthday", "add-b-day"]:
            print(add_birthday(args, book))
        elif command in ["show-birthday", "birthday", "show-b-day"]:
            print(show_birthday(args, book))
        elif command in ["birthdays", "upcoming birthdays", "upcoming b-days"]:
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()