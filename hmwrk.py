from datetime import datetime
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
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
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
        self.phones.remove(phone_obj)
        self.phones.append(Phone(new_phone))

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_birthday(self):
        self.birthday = None

    def examination_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"[{self.name.value}]: [{phones_str}], birthday: [{birthday_str}]"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name, None)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        for record in self.data.values():
            if not record.birthday:
                continue
            bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            congratulation_date =bday_date.replace(year=today.year)
            if congratulation_date < today:
                congratulation_date = congratulation_date.replace(year=today.year + 1)
            delta_days = (congratulation_date - today).days
            if 0 < delta_days <= days:
                yield record.name.value, congratulation_date.strftime("%d.%m.%Y")


    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
    return inner

@input_error
def add(args, book: AddressBook):
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
        return f"No phones found for {name}"
    return ", ".join(p.value for p in record.phones)

@input_error
def all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts available."
    return str(book)

@input_error
def all_birthdays(book: AddressBook):
    if not book.data:
        return "No contacts available."
    return str(book)


def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        record = Record(name, birthday)
        book.add_record(record)
    else:
        record.add_birthday(birthday)
    return f"Birthday for [{name}] added successfully."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return f"Birthday for [{name}] not found"
    return record.birthday.value if record.birthday else "No birthday"

@input_error
def birthdays(args, book: AddressBook):
    args 
    result = ""
    for name, days in book.get_upcoming_birthdays():
        result += f"[{name}]: {days}\n"
    return result if result else "No upcoming birthdays"


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]

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
            print("1: add - add [name] [phone]\n2: change, edit - change [name] [old_phone] [new_phone]\n3: phone, show - phone [name]\n4: all, show-all - show all contacts\n5: add-birthday, new-birthday, add-b-day - add-birthday [name] [birthday]\n6: show-birthday, birthday, show-b-day - show birthday [name]\n7: birthdays, upcoming birthdays, upcoming b-days - show upcoming birthdays\n8: close, exit, bye - close the bot\n9: hello, hi - show help\n")
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
