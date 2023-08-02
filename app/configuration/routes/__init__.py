from app.configuration.routes.routes import Routes
from app.iternal.routes import file, auth

__routes__ = Routes(routers=(file.router, auth.router, )) 