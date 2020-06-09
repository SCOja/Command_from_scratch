from abc import ABC, abstractmethod
from mongodb import MongoDb
import time


class Command(ABC):
    """source"""
    @abstractmethod
    def execute(self) -> None:
        pass


class Undo(ABC):
    """source"""
    @abstractmethod
    def history(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class Receiver:
    """
    Receiver mongodb functions: get, update, restore.
    Need to change 2 in two ways? get and update
    """

    def __init__(self, first_mongodb: MongoDb, second_mongodb: MongoDb,
                 data: dict, cancel_data: dict) -> None:
        self._mongodb_first = first_mongodb
        self._mongodb_second = second_mongodb
        self._data = data
        self._data2 = cancel_data

    def get_data(self) -> tuple:
        result1 = self._mongodb_first.data_to_get()
        result2 = self._mongodb_second.data_to_get()
        return result1, result2

    def restore_data(self) -> tuple:  # change/del dat
        result1 = self._mongodb_first.correct_data(self._data2)
        result2 = self._mongodb_second.correct_data(self._data2)
        return result1, result2

    def update_data_f(self) -> None:  # combine _f and _s
        self._mongodb_first.update_data(self._data)

    def update_data_s(self) -> None:  # same
        self._mongodb_second.update_data(self._data)


class GetData(Command):

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> dict:
        return self._receiver.get_data()


class UpdateDataFirst(Command):  # combine F and S?

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> None:
        self._receiver.update_data_f()


class UpdateDataSecond(Command):  # same

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> None:
        self._receiver.update_data_s()


class CancelData(Command):  # only for testing?

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> None:
        self._receiver.restore_data()


class Invoker(Undo):

    def __init__(self):
        self._commands = {}
        self._history = [(time.time(), 'Start')]
        self._history_position = 0  # The position that is used for UNDO

    @property
    def history(self):
        return self._history

    def register(self, command_name, command):
        self._commands[command_name] = command

    def undo(self):
        if self._history_position > 0:
            self._history_position -= 1
            self._commands[
                self._history[self._history_position][1]
            ].execute()
        else:
            print("nothing to undo")

    def execute(self, command_name) -> None:
        if command_name in self._commands.keys():
            self._history_position += 1
            result = self._commands[command_name].execute()
            if len(self._history) == self._history_position:
                self._history.append((time.time(), command_name))
                return result
            else:
                """ put something right here """
                self._history = self._history[:self._history_position + 1]
                self._history[self._history_position] = {
                    time.time(): [command_name]
                }
        else:
            print(f'Command [{command_name}] not recognised')


if __name__ == '__main__':

    data_initial = {'surname': 'Doe'}
    data_to_update = {'surname': 'Doe changed'}
    invoker = Invoker()
    mongo1 = MongoDb('mongodb://localhost:27015/')
    mongo2 = MongoDb('mongodb://localhost:27016/')
    receiver_tst = Receiver(mongo1, mongo2, data_to_update, data_initial)

    # create commands:
    GET_DATA = GetData(receiver_tst)
    UPD_DATA1 = UpdateDataFirst(receiver_tst)
    UPD_DATA2 = UpdateDataSecond(receiver_tst)
    CNL_DATA = CancelData(receiver_tst)

    # register commands:
    invoker.register('GET', GET_DATA)
    invoker.register('UPD1', UPD_DATA1)
    invoker.register('UPD2', UPD_DATA2)
    invoker.register('UNDO', CNL_DATA)

    # execute catch non_exist_name in mongodb's
    try:
        print(invoker.execute('GET'))
        invoker.execute('UPD1')
        invoker.execute('UPD2')
    except ValueError:
        print('Wrong search params')
        invoker.undo()
        # invoker.execute('UNDO')

    print(invoker.history)
