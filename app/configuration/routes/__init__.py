from app.configuration.routes.routes import Routes
from app.iternal.routes import file, auth, user, god, company, manager

__routes__ = Routes(routers=(file.router,
                             auth.router,
                             user.router,
                             god.router,
                             company.router,
                             manager.router))
