import re
from typing import Final

from pwdlib import PasswordHash


PASSWORD_MIN_LENGTH: Final[int] = 8
PASSWORD_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")
_PASSWORD_HASH = PasswordHash.recommended()


def hash_password(password: str) -> str:
    validate_password(password)
    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _PASSWORD_HASH.verify(password, password_hash)


def validate_password(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not PASSWORD_PATTERN.match(password):
        raise ValueError("비밀번호는 영문과 숫자를 모두 포함해야 합니다.")
