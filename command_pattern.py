from mongodb import MongoDB


class Repository:
    """
    Receiver mongodb functions: snap, update, restore.
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
        self._commands = []
        self.history = []

    def history(self):
        return self.history

    def register(self, command):
        self._commands.append(command)

    def undo(self) -> None:
        if len(self.history) > 0:
            for command in self.history:
                command.cancel()
        else:
            print("nothing to undo")

    def execute(self, command) -> None:
        if command in self._commands:
            command.execute()
            self.history.append(command)
        else:
            print(f'Command [{command}] is not recognised')


if __name__ == '__main__':

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
    invoker.register(upd_data1)
    invoker.register(upd_data2)

    # execute catch non_exist_name in mongodb's
    try:
        invoker.execute(upd_data1)
        invoker.execute(upd_data2)
    except ValueError:
        print('Wrong search params')
        invoker.undo()

    print(invoker.history)
