from app.configuration.routes.routes import Routes
from app.iternal.routes import user

__routes__ = Routes(routers=(user.router, )) 