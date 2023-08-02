import redis
from fastapi import Request, Response
from app.iternal.config import settings
import secrets
import bcrypt


REDIS_PASS = settings.REDIS_PASS
REDIS_PORT = settings.REDIS_PORT
REDIS_HOST = settings.REDIS_HOST


class RSessions:
    def __init__(self, expiry: int = 86400) -> None:
        self.__expiry = expiry
        self.__expiry_threshold = expiry*0.98

        self.__db = redis.StrictRedis(host=REDIS_HOST,
                                      port=REDIS_PORT,
                                      password=REDIS_PASS,
                                      encoding="utf-8",
                                      decode_responses=True)

    def __del__(self):
        self.__db.close()

    # Session create
    def create_session(self, request: Request, response: Response, session_data: dict) -> str:

        # Cancel previous session if you are logged in
        session = self.__get_session(request)

        if len(session) > 0:
            self.end_session(request, response)

        # Generation of session_id
        session_id = secrets.token_urlsafe(32)

        # Checking if the user role is specified
        if session_data.get("role") == None:
            session_data["role"] = 0

        # Setting data
        self.__db.hmset(session_id, session_data)
        self.__db.expire(session_id, self.__expiry)

        # Setting cookie
        response.set_cookie(key="session_id", value=session_id)
        
        print('session_id: ', session_id)
        return session_id

    # Get session data
    def __get_session(self, request: Request) -> dict:
        session_id = request.cookies.get("session_id")
        try:
            session_db = self.__db.hgetall(session_id)
            return session_db
        except:
            pass
        return {}

    # Session end
    def end_session(self, request: Request, response: Response) -> None:
        session_id = request.cookies.get("session_id")
        try:
            self.__db.delete(session_id)
            response.delete_cookie(key="session_id")
        except:
            pass

    # Verify session
    def protected_session(self, request: Request, response: Response, role: int = 0) -> dict:
        session_db = self.__get_session(request)
        if len(session_db) >= 0:
            role_db = session_db.get('role')
            if not role_db or int(role_db) < role:
                self.end_session(request, response)
                return {}
            self.__update_expiry(request)
            return session_db
        self.end_session(request, response)
        return {}

    # Update session ttl
    def __update_expiry(self, request: Request):
        try:
            session_id = request.cookies.get("session_id")
            if (self.__db.ttl(session_id) < self.__expiry_threshold):
                self.__db.expire(session_id, self.__expiry)
        except Exception as e:
            pass

    def generate_hashed_key(self, value: str) -> bytes:
        # Hash the "value" using bcrypt with the salt
        hashed_key = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
        return hashed_key

    def verify_key(self, value: str, hashed_key: bytes) -> bool:
        # Verify the "value" by checking if it matches the hashed_key
        return bcrypt.checkpw(value.encode('utf-8'), hashed_key) or value == hashed_key
