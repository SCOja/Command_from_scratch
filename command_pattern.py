from mongodb import MongoDB


class Repository:
    """
    Receiver mongodb functions: get, snap, update, restore.
    """

    def __init__(self, mongodb: MongoDB, data: dict) -> None:
        self._mongodb = mongodb
        self._data = data

    def update_data(self) -> None:
        self._mongodb.update_data(self._data)

    def snapshot(self) -> dict:
        result = self._mongodb.data_to_get()
        return result

    def cancel_data(self, data) -> None:
        self._mongodb.update_data(data)


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
        self.history = ['Start']
        self.history_position = 0  # The position that is used for UNDO

    def history(self):
        return self.history

    def register(self, command_name, command):
        self._commands[command_name] = command

    def undo(self) -> None:
        if self.history_position > 1:
            self.history_position -= 1
            self._commands[
                self.history[self.history_position]
            ].cancel()
        else:
            print("nothing to undo")

    def execute(self, command_name) -> None:
        if command_name in self._commands.keys():
            self.history_position += 1
            self._commands[command_name].execute()
            if len(self.history) == self.history_position:
                self.history.append(command_name)
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
    upd_data1 = UpdateData(receiver_one)
    upd_data2 = UpdateData(receiver_two)

    # register commands:
    invoker.register('UPD1', upd_data1)
    invoker.register('UPD2', upd_data2)

    # execute catch non_exist_name in mongodb's
    try:
        invoker.execute('UPD1')
        invoker.execute('UPD2')
    except ValueError:
        print('Wrong search params')
        invoker.undo()

    print(invoker.history)
