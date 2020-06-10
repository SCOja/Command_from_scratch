from mongodb import MongoDB
import time


class Repository:
    """
    Receiver mongodb functions: get, snap, update, restore.
    """

    def __init__(self, mongodb: MongoDB, data: dict) -> None:
        self._mongodb = mongodb
        self._data = data

    def get_data(self) -> dict:
        result = self._mongodb.data_to_get()
        return result

    def update_data(self) -> None:
        self._mongodb.update_data(self._data)

    def snapshot(self) -> dict:
        result = self._mongodb.data_to_get()
        return result

    def cancel_data(self, data) -> None:
        self._mongodb.update_data(data)


class GetData:

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> dict:
        return self._receiver.get_data()


class UpdateData:

    def __init__(self, receiver):
        self._receiver = receiver
        self._snapshot = self._receiver.snapshot()

    def execute(self) -> None:
        self._receiver.update_data()

    def cancel(self) -> None:
        snap = self._snapshot
        self._receiver.cancel_data(snap)


class Invoker:

    def __init__(self):
        self._commands = {}
        self._history = [(time.time(), 'Start')]
        self._history_position = 0  # The position that is used for UNDO

    @property
    def history(self):
        return self._history

    def register(self, command_name, command):
        self._commands[command_name] = command

    def undo(self) -> None:
        if self._history_position > 1:
            self._history_position -= 1
            self._commands[
                self._history[self._history_position][1]
            ].cancel()
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
        else:
            print(f'Command [{command_name}] is not recognised')


if __name__ == '__main__':

    data_initial = {'surname': 'Doe'}
    data_to_update = {'surname': 'Doe changed'}
    invoker = Invoker()
    mongo1 = MongoDB('mongodb://localhost:27015/')
    mongo2 = MongoDB('mongodb://localhost:27016/')
    receiver_one = Repository(mongo1, data_to_update)
    receiver_two = Repository(mongo2, data_to_update)

    # create commands:
    get_data1 = GetData(receiver_one)
    get_data2 = GetData(receiver_one)
    upd_data1 = UpdateData(receiver_one)
    upd_data2 = UpdateData(receiver_two)

    # register commands:
    invoker.register('GET1', get_data1)
    invoker.register('GET2', get_data2)
    invoker.register('UPD1', upd_data1)
    invoker.register('UPD2', upd_data2)

    # execute catch non_exist_name in mongodb's
    try:
        # print(invoker.execute('GET'))
        invoker.execute('UPD1')
        invoker.execute('UPD2')
    except ValueError:
        print('Wrong search params')
        invoker.undo()

    print(invoker.history)
