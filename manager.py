from flask_script import Manager, Server, Shell

from main import bootstrap_app
from broker_rabbit.manager import broker_rabbit_manager

app = bootstrap_app()

manager = Manager(app)


manager.add_command("runserver", Server())
manager.add_command("shell", Shell())
manager.add_command("broker", broker_rabbit_manager)

if __name__ == "__main__":
    manager.run()
