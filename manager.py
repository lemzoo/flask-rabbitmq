#! /usr/bin/env python3

from flask_script import Manager, Server, Shell

from main import create_app


app = create_app()

manager = Manager(app)


manager.add_command("runserver", Server())
manager.add_command("shell", Shell())


if __name__ == "__main__":
    manager.run()
