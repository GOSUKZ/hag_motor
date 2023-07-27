import redis
from fastapi import Request, Response
from app.iternal.config import settings
import secrets
import bcrypt


SECRET_KEY = "secrets_key"
REDIS_PASS = settings.REDIS_PASS
REDIS_PORT = settings.REDIS_PORT
REDIS_HOST = settings.REDIS_HOST


class RSessions:
    def __init__(self, expiry: int = 86400) -> None:
        self.expiry = expiry

        self.db = redis.StrictRedis(host=REDIS_HOST,
                                    port=REDIS_PORT,
                                    password=REDIS_PASS,
                                    encoding="utf-8",
                                    decode_responses=True)

    def __del__(self):
        self.db.close()

    def create_session(self, response: Response, session_data: dict) -> str:
        session_id = secrets.token_urlsafe(32)
        self.db.hmset(session_id, session_data)
        self.db.expire(session_id, self.expiry)

        response.set_cookie(key="session_id",
                            value=session_id,
                            httponly=True,
                            secure=True)
        return session_id

    def get_session(self, request: Request) -> dict:
        session_id = request.cookies.get("session_id")
        try:
            session_db = self.db.hgetall(session_id)
            return session_db
        except:
            pass
        return {}

    def end_session(self, request: Request, response: Response) -> None:
        session_id = request.cookies.get("session_id")
        try:
            self.db.delete(session_id)
            response.delete_cookie(key="session_id")
        except:
            pass

    def protected_session(self, request: Request, response: Response) -> bool:
        session_db = self.get_session(request)
        if len(session_db) > 0:
            if session_db.get('logged_in') != '1':
                self.end_session(request, response)
                return False
            return True
        else:
            self.end_session(request, response)
        return False

    def __generate_hashed_key(value: str) -> bytes:
        # Hash the "value" using bcrypt with the salt
        hashed_key = bcrypt.hashpw(value.encode(), SECRET_KEY)
        return hashed_key

    def __verify_key(value: str, hashed_key: bytes) -> bool:
        # Verify the "value" by checking if it matches the hashed_key
        return bcrypt.checkpw(value.encode(), hashed_key)
