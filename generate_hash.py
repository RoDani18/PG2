from backend.auth.security import get_password_hash

password = "123456"
hashed = get_password_hash(password)
print(f"🔐 Hash para '{password}':\n{hashed}")
