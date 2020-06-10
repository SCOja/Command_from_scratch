from mongodb import MongoDb
import time


class Repository:
    """
    Receiver mongodb functions: get, update, restore.
    Need to change 2 in two ways? get and update
    """

    def __init__(self, first_mongodb: MongoDb, second_mongodb: MongoDb,
                 data: dict) -> None:
        self._mongodb_first = first_mongodb
        self._mongodb_second = second_mongodb
        self._data = data

    def get_data(self) -> tuple:
        result1 = self._mongodb_first.data_to_get()
        result2 = self._mongodb_second.data_to_get()
        return result1, result2

    def restore_data(self, data) -> tuple:  # change/del dat
        result1 = self._mongodb_first.correct_data(data)
        result2 = self._mongodb_second.correct_data(data)
        return result1, result2

    def update_data_f(self) -> None:  # combine _f and _s
        self._mongodb_first.update_data(self._data)

    def update_data_s(self) -> None:  # same
        self._mongodb_second.update_data(self._data)

    def snapshot(self) -> dict:
        result = self._mongodb_first.data_to_get()
        return result

    def cancel_data(self, data) -> None:
        self._mongodb_first.update_data(data)


class GetData:

    def __init__(self, receiver):
        self._receiver = receiver

    def execute(self) -> dict:
        return self._receiver.get_data()


class UpdateDataFirst:  # combine F and S?

    def __init__(self, receiver):
        self._receiver = receiver
        self._snapshot = self._receiver.snapshot()

    def execute(self) -> None:
        self._receiver.update_data_f()

    def cancel(self) -> None:
        snap = self._snapshot
        self._receiver.cancel_data(snap)


class UpdateDataSecond:  # same

    def __init__(self, receiver):
        self._receiver = receiver
        self._snapshot = self._receiver.snapshot()

    def execute(self) -> None:
        self._receiver.update_data_s()

    def cancel(self) -> None:
        snap = self._snapshot
        self._receiver.cancel_data(snap)


class CancelData:  # only for testing?

    def __init__(self, receiver, data):
        self._receiver = receiver
        self._data = data

    def execute(self) -> None:
        self._receiver.restore_data(self._data)


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

    def undo(self):
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
    mongo1 = MongoDb('mongodb://localhost:27015/')
    mongo2 = MongoDb('mongodb://localhost:27016/')
    receiver_tst = Repository(mongo1, mongo2, data_to_update)

    # create commands:
    get_data = GetData(receiver_tst)
    upd_data1 = UpdateDataFirst(receiver_tst)
    upd_data2 = UpdateDataSecond(receiver_tst)
    cnl_data = CancelData(receiver_tst, data_initial)

    # register commands:
    invoker.register('GET', get_data)
    invoker.register('UPD1', upd_data1)
    invoker.register('UPD2', upd_data2)
    invoker.register('UNDO', cnl_data)

    # execute catch non_exist_name in mongodb's
    try:
        # print(invoker.execute('GET'))
        invoker.execute('UPD1')
        invoker.execute('UPD2')
    except ValueError:
        print('Wrong search params')
        invoker.undo()
        # invoker.execute('UNDO')

    print(invoker.history)
