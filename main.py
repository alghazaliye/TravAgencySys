from app import app  # noqa: F401
import routes  # Import all routes
import os

# إعداد مفتاح الجلسة إذا لم يكن موجودًا
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = os.urandom(24).hex()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
