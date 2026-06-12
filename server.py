"""
YouYu Auth Server - 部署到免费服务器(Vercel/Render)
处理注册/登录/验证码，GitHub/Gitee同步
"""

import hashlib
import json
import os
import random
import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ====== 从环境变量读取密钥(不在代码中暴露) ======
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "youyu551572/drawinline")
GITEE_TOKEN = os.environ.get("GITEE_TOKEN", "")
GITEE_REPO = os.environ.get("GITEE_REPO", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
AUTH_SECRET = os.environ.get("AUTH_SECRET", "youyu-secret-key-change-me")

GITHUB_API = "https://api.github.com"
GITEE_API = "https://gitee.com/api/v5"
MEMBERS_FILE = "auth/members.json"
USERS_FILE = "auth/users.json"

_pending_codes: dict = {}  # qq -> (code, timestamp)
_SALT = "YouYuDrawInline2024!@#"
_PBKDF_ITERATIONS = 200_000


def _hash_password(password: str, salt: str = None):
    if salt is None:
        salt = hex(random.getrandbits(128))[2:]
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _PBKDF_ITERATIONS
    )
    return f"{salt}${key.hex()}"


def _verify_password(password, stored):
    try:
        salt, _ = stored.split("$", 1)
        return _hash_password(password, salt) == stored
    except Exception:
        return (
            hashlib.sha256(f"{_SALT}{password}{_SALT}".encode()).hexdigest() == stored
        )


def _gh_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def _gte_headers():
    return {
        "Authorization": f"token {GITEE_TOKEN}",
        "Content-Type": "application/json;charset=UTF-8",
    }


def _storage_get(path):
    for api, repo, hdrs in [
        (GITHUB_API, GITHUB_REPO, _gh_headers),
        (GITEE_API, GITEE_REPO, _gte_headers) if GITEE_TOKEN else None,
    ]:
        if not hdrs:
            continue
        try:
            resp = requests.get(
                f"{api}/repos/{repo}/contents/{path}", headers=hdrs(), timeout=8
            )
            if resp.status_code == 200:
                import base64

                data = resp.json()
                return json.loads(base64.b64decode(data["content"]).decode()), data[
                    "sha"
                ]
        except Exception:
            pass
    return None, None


def _storage_put(path, data, sha=None, msg="update"):
    import base64

    payload = {
        "message": msg,
        "content": base64.b64encode(
            json.dumps(data, ensure_ascii=False, indent=2).encode()
        ).decode(),
    }
    if sha:
        payload["sha"] = sha
    ok = False
    for api, repo, hdrs in [
        (GITHUB_API, GITHUB_REPO, _gh_headers),
        (GITEE_API, GITEE_REPO, _gte_headers) if GITEE_TOKEN else None,
    ]:
        if not hdrs:
            continue
        try:
            resp = requests.put(
                f"{api}/repos/{repo}/contents/{path}",
                headers=hdrs(),
                json=payload,
                timeout=10,
            )
            if resp.status_code in (200, 201):
                ok = True
        except Exception:
            pass
    return ok


# ====== API ======


@app.route("/api/send_code", methods=["POST"])
def send_code():
    data = request.json
    qq = data.get("qq", "")
    if not qq.isdigit() or len(qq) < 5:
        return jsonify({"ok": False, "msg": "无效QQ号"})

    code = str(random.randint(100000, 999999))
    email = f"{qq}@qq.com"

    msg = MIMEMultipart()
    msg["From"] = Header(SMTP_USER, "utf-8")
    msg["To"] = Header(email, "utf-8")
    msg["Subject"] = Header("YouYu自动绘画 - 邮箱验证码", "utf-8")
    msg.attach(
        MIMEText(
            f"您的验证码是：{code}\n\n有效期5分钟。\n\nYouYu自动绘画团队",
            "plain",
            "utf-8",
        )
    )

    try:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        _pending_codes[qq] = (code, time.time())
        return jsonify({"ok": True, "msg": "验证码已发送"})
    except Exception as e:
        return jsonify({"ok": False, "msg": f"发送失败: {e}"})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    qq = data.get("qq", "")
    pw = data.get("password", "")
    name = data.get("nickname", qq)
    code = data.get("code", "")

    if not qq or not pw or not code:
        return jsonify({"ok": False, "msg": "参数不完整"})

    saved = _pending_codes.get(qq)
    if not saved:
        return jsonify({"ok": False, "msg": "请先获取验证码"})
    if time.time() - saved[1] > 300:
        del _pending_codes[qq]
        return jsonify({"ok": False, "msg": "验证码已过期"})
    if saved[0] != code:
        return jsonify({"ok": False, "msg": "验证码错误"})
    del _pending_codes[qq]

    # Check member list
    m_result = _storage_get(MEMBERS_FILE)
    if not m_result:
        return jsonify({"ok": False, "msg": "成员列表不存在"})
    if qq not in m_result[0].get("members", []):
        return jsonify({"ok": False, "msg": "该QQ号不在授权列表中"})

    # Check existing
    u_result = _storage_get(USERS_FILE)
    users, sha = (u_result[0], u_result[1]) if u_result else ({"users": {}}, None)
    if qq in users.get("users", {}):
        return jsonify({"ok": False, "msg": "该QQ号已注册"})

    users.setdefault("users", {})[qq] = {
        "password": _hash_password(pw),
        "nickname": name,
        "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if _storage_put(USERS_FILE, users, sha, f"register {qq}"):
        return jsonify({"ok": True, "msg": "注册成功"})
    return jsonify({"ok": False, "msg": "注册失败，请稍后重试"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    qq = data.get("qq", "")
    pw = data.get("password", "")

    u_result = _storage_get(USERS_FILE)
    if not u_result:
        return jsonify({"ok": False, "msg": "暂无注册用户"})

    user = u_result[0].get("users", {}).get(qq)
    if not user:
        return jsonify({"ok": False, "msg": "账号未注册"})
    if not _verify_password(pw, user["password"]):
        return jsonify({"ok": False, "msg": "密码错误"})

    return jsonify(
        {
            "ok": True,
            "msg": "登录成功",
            "hash": user["password"],
            "nickname": user.get("nickname", qq),
        }
    )


@app.route("/api/check_login", methods=["POST"])
def check_login():
    data = request.json
    qq = data.get("qq", "")
    pwd_hash = data.get("hash", "")
    if not qq or not pwd_hash:
        return jsonify({"ok": False})

    u_result = _storage_get(USERS_FILE)
    if not u_result:
        return jsonify({"ok": False})

    user = u_result[0].get("users", {}).get(qq)
    if not user or user["password"] != pwd_hash:
        return jsonify({"ok": False})

    return jsonify({"ok": True, "nickname": user.get("nickname", qq)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "time": time.strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
