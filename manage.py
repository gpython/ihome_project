from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager, Server
from apps import create_app, db

#创建flask的应用对象
app = create_app('develop')

Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(use_debugger=True))

if __name__ == '__main__':
  manager.run()

