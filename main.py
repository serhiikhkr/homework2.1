from collections import UserDict
from datetime import datetime
import re
import pickle
from pathlib import Path
from abc import ABC, abstractmethod


class Field(ABC):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @abstractmethod
    def validate(self, value):
        pass


class Address(Field):
    def __format__(self, format_spec):
        return '{:^25}'.format(self.value)

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Адресс должно быть текстом')


class Email(Field):
    def __format__(self, format_spec):
        return self.value

    def validate(self, value):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(regex, value):
            raise ValueError("Некорректный e-mail")


class Birthday(Field):
    def __format__(self, format_spec):
        return datetime.strftime(self.value, "%d.%m.%Y")

    def validate(self, value):
        pattern = "\d\d.\d\d.\d{4}"
        if value == re.search(pattern, value).group():
            now_t = datetime.now()
            old_d = datetime.strptime(value, '%d.%m.%Y')
            diff_date = now_t - old_d
            if diff_date.days >= 0:
                self._value = datetime.strptime(value, "%d.%m.%Y")
            else:
                raise Exception("Дата не может быть в будущем")
        else:
            raise Exception("Пожалуйста, введите дату в формате: 'dd.mm.YYYY'")


class Name(Field):
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Имя должно быть текстом')


class Phone(Field):
    def validate(self, value):
        if not value.isdigit():
            raise ValueError('Некорректный телефон')


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None, address: Address = None,
                 email: Email = None):
        self.name = name
        self.phones = []
        self.birthday = birthday
        self.address = address
        self.email = email

        if phone:
            self.phones.append(phone)

    def add_phone(self, phone):
        new_phone = Phone(phone)
        if new_phone.value not in [ph.value for ph in self.phones]:
            self.phones.append(new_phone)

    def delete_phone(self, phone):
        for ph in self.phones:
            if phone == ph.value:
                self.phones.remove(ph)

    def change_phone(self, old_phone, new_phone):
        for ph in self.phones:
            if old_phone == ph.value:
                self.delete_phone(old_phone)
                self.add_phone(new_phone)

    def edit_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)

    def edit_email(self, new_email):
        self.email = Email(new_email)

    def edit_address(self, new_address):
        self.address = Address(new_address)

    def days_to_birthday(self):
        today = datetime.now()
        birthday = self.birthday.value
        days_to_birthday = (birthday - today).days
        if days_to_birthday < 0:
            birthday = birthday.replace(year=today.year + 1)
            days_to_birthday = (birthday - today).days
            return days_to_birthday
        return days_to_birthday

    def __str__(self):
        return f"{self.name.value} {[ph.value for ph in self.phones]} {self.birthday.value.date()}"


class AddressBook(UserDict):
    file_name = 'my_addressBook.bin'
    path_file_name = Path(file_name)

    def save_address_book(self):
        with open(self.path_file_name, 'wb') as file:
            pickle.dump(self.data, file)

    def load_address_book(self):
        if not self.path_file_name.exists():
            return print("\nВаша адресная книга пуста")
        with open(self.path_file_name, 'rb') as file:
            self.data = pickle.load(file)
        return print('-----')

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def search(self, search_str: str):
        result_1 = '\n Результат поиска :\n'
        result_2 = ''
        result_3 = '{:^15}|  {:^25} | {:^25} | {:^10} | {:^10}\n'.format('"NAME"', '"PHONE"', '"ADDRESS"', '"BIRTHDAY"',
                                                                         '"EMAIL"')
        first_run = 1
        for record_id, records in self.data.items():
            list_phones = [i.value for i in records.phones]
            try:
                phone_join = ','.join(list_phones)
            except:
                phone_join = list_phones[0]
            try:
                len(records.address)
            except:
                records.address = '----'
            try:
                '{:^10}'.format(records.address)
            except TypeError:
                records.address = '----'
            try:
                '{:^10}'.format(records.birthday)
            except TypeError:
                records.birthday = '----'
            try:
                '{:^10}'.format(records.email)
            except:
                records.email = '----'
            if search_str in self.data[record_id].phones or search_str in record_id and first_run == 1:
                result_2 = result_2 + result_1 + result_3 + '{:^15}:  {:^25} | {:^25} | {:^10} | {:^10} \n'.format(
                    record_id, phone_join, records.address, records.birthday, records.email)
                first_run += 1
            elif search_str in self.data[record_id].phones or search_str in record_id and first_run != 1:
                result_2 = result_2 + '{:^15}:  {:^25} | {:^25} | {:^10} | {:^10} \n'.format(record_id, phone_join,
                                                                                             records.address,
                                                                                             records.birthday,
                                                                                             records.email)
        if len(result_2) < 1:
            return print('Совпадений не найдено')
        else:
            return print(result_2)


# Создаем запись
name = Name("John Doe")
phone = Phone("123456789")
birthday = Birthday("01.01.1990")
address = Address("123 Main St.")
email = Email("john.doe@example.com")
record = Record(name, phone, birthday, address, email)

# Создаем адресную книгу
address_book = AddressBook()

# Добавляем запись в адресную книгу
address_book.add_record(record)

# Сохраняем адресную книгу
address_book.save_address_book()

# Загружаем адресную книгу
address_book.load_address_book()

# Ищем запись
address_book.search("John")
