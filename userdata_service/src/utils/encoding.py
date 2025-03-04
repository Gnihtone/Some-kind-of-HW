def encode_password(password: str) -> str:
    hsh = 0
    p = 107
    mod = 1000000007
    for ch in password:
        hsh *= p
        hsh += ord(ch)
        hsh %= mod
    return str(hsh)
