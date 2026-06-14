"""
YouYu 中转服务器 - 统一版（支持 VPS 自托管 + AWS Lambda Serverless）
自动根据环境变量选择存储和邮件后端：
  VPS 模式:   SQLite + SMTP
  Lambda 模式: DynamoDB + SES (自动检测 AWS_LAMBDA_FUNCTION_NAME)
"""

import hashlib
import hmac
import json
import os
import random
import secrets
import smtplib
import sqlite3
import time
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from pathlib import Path

import requests
from flask import Flask, g, jsonify, request

# ============================================================
# 环境检测
# ============================================================

IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
USE_DYNAMODB = os.environ.get("USE_DYNAMODB", str(IS_LAMBDA)).lower() == "true"
USE_SES = os.environ.get("USE_SES", str(IS_LAMBDA)).lower() == "true"

# ====== 自动加载 .env 文件（非 Lambda 环境） ======
if not IS_LAMBDA:
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        with open(_env_path, "r", encoding="utf-8-sig") as _fh:  # utf-8-sig 兼容 BOM
            for _ln in _fh:
                _ln = _ln.strip()
                if _ln and not _ln.startswith("#") and "=" in _ln:
                    _k, _, _v = _ln.partition("=")
                    _k, _v = _k.strip(), _v.strip().strip("'\"")
                    if _k:
                        os.environ[_k] = _v

# ============================================================
# 配置
# ============================================================

SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
API_KEY = os.environ.get("API_KEY", "")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

# SMTP 配置
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# GitHub 配置（服务器持有，用于读写）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_API = "https://api.github.com"

# Gitee 配置（镜像备份）
GITEE_TOKEN = os.environ.get("GITEE_TOKEN", "")
GITEE_REPO = os.environ.get("GITEE_REPO", "")
GITEE_API = "https://gitee.com/api/v5"

# SES 配置
SES_REGION = os.environ.get("SES_REGION", "us-east-1")
SES_SENDER = os.environ.get("SES_SENDER", "")  # 需在 SES 中验证的发件邮箱

# DynamoDB 配置
DYNAMODB_TABLE_USERS = os.environ.get("DYNAMODB_TABLE_USERS", "drawinline-users")
DYNAMODB_TABLE_MEMBERS = os.environ.get("DYNAMODB_TABLE_MEMBERS", "drawinline-members")
DYNAMODB_TABLE_CODES = os.environ.get("DYNAMODB_TABLE_CODES", "drawinline-codes")

# SQLite 路径
DB_PATH = os.environ.get("DB_PATH", str(Path(__file__).parent / "data.db"))

# ============================================================
# Flask 应用
# ============================================================

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


# ============================================================
# 数据库层（SQLite / DynamoDB 自动切换）
# ============================================================

# ============================================================
# GitHub/Gitee 同步层
# ============================================================


def _gh_get(path: str, timeout: int = 10) -> tuple[dict | None, str | None]:
    """从 GitHub 读取文件"""
    if not GITHUB_TOKEN:
        return None, None
    try:
        import base64

        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
        resp = requests.get(
            url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content), data.get("sha")
    except Exception as e:
        print(f"[GitHub] 读取失败: {e}")
    return None, None


def _gh_put(path: str, data: dict, sha: str = None, msg: str = "update") -> bool:
    """写入文件到 GitHub"""
    if not GITHUB_TOKEN:
        return False
    try:
        import base64

        payload = {
            "message": msg,
            "content": base64.b64encode(
                json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            ).decode("ascii"),
        }
        if sha:
            payload["sha"] = sha
        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
        resp = requests.put(
            url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json=payload,
            timeout=10,
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[GitHub] 写入失败: {e}")
        return False


def _gitee_get(path: str, timeout: int = 10) -> tuple[dict | None, str | None]:
    """从 Gitee 读取文件"""
    if not GITEE_TOKEN:
        return None, None
    try:
        import base64

        url = f"{GITEE_API}/repos/{GITEE_REPO}/contents/{path}"
        resp = requests.get(
            url,
            headers={"Authorization": f"token {GITEE_TOKEN}"},
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content), data.get("sha")
    except Exception as e:
        print(f"[Gitee] 读取失败: {e}")
    return None, None


def _gitee_put(path: str, data: dict, sha: str = None, msg: str = "update") -> bool:
    """写入文件到 Gitee"""
    if not GITEE_TOKEN:
        return False
    try:
        import base64

        payload = {
            "access_token": GITEE_TOKEN,
            "content": base64.b64encode(
                json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            ).decode("ascii"),
            "message": msg,
        }
        if sha:
            payload["sha"] = sha
        url = f"{GITEE_API}/repos/{GITEE_REPO}/contents/{path}"
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[Gitee] 写入失败: {e}")
        return False


# ============================================================
# 数据库
# ============================================================


def _get_storage():
    """延迟初始化存储后端"""
    if USE_DYNAMODB:
        return _DynamoDBStorage()
    return _SQLiteStorage()


class _SQLiteStorage:
    """SQLite 存储（VPS 部署）"""

    def __init__(self):
        db = sqlite3.connect(DB_PATH)
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                qq_number   TEXT PRIMARY KEY,
                password    TEXT NOT NULL,
                nickname    TEXT NOT NULL,
                registered_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS members (
                qq_number TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS verify_codes (
                qq_number  TEXT PRIMARY KEY,
                code       TEXT NOT NULL,
                expires_at REAL NOT NULL
            );
        """)
        db.commit()
        db.close()

    def _conn(self):
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        return db

    # -- verify_codes --

    def save_code(self, qq: str, code: str):
        db = self._conn()
        db.execute(
            "INSERT OR REPLACE INTO verify_codes VALUES (?, ?, ?)",
            (qq, code, time.time() + 300),
        )
        db.commit()
        db.close()

    def check_code(self, qq: str, code: str) -> bool:
        db = self._conn()
        row = db.execute(
            "SELECT code, expires_at FROM verify_codes WHERE qq_number = ?", (qq,)
        ).fetchone()
        db.close()
        if not row:
            return False
        if time.time() > row["expires_at"]:
            return False
        return row["code"] == code

    def delete_code(self, qq: str):
        db = self._conn()
        db.execute("DELETE FROM verify_codes WHERE qq_number = ?", (qq,))
        db.commit()
        db.close()

    # -- members --

    def member_exists(self, qq: str) -> bool:
        db = self._conn()
        row = db.execute("SELECT 1 FROM members WHERE qq_number = ?", (qq,)).fetchone()
        db.close()
        return row is not None

    def add_member(self, qq: str):
        db = self._conn()
        db.execute("INSERT OR IGNORE INTO members VALUES (?)", (qq,))
        db.commit()
        db.close()

    def remove_member(self, qq: str):
        db = self._conn()
        db.execute("DELETE FROM members WHERE qq_number = ?", (qq,))
        db.commit()
        db.close()

    def list_members(self) -> list:
        db = self._conn()
        rows = db.execute("SELECT qq_number FROM members ORDER BY qq_number").fetchall()
        db.close()
        return [r["qq_number"] for r in rows]

    def bulk_add_members(self, qqs: list) -> int:
        db = self._conn()
        count = 0
        for qq in qqs:
            try:
                db.execute("INSERT OR IGNORE INTO members VALUES (?)", (qq,))
                count += 1
            except Exception:
                pass
        db.commit()
        db.close()
        return count

    def count_members(self) -> int:
        db = self._conn()
        row = db.execute("SELECT COUNT(*) as c FROM members").fetchone()
        db.close()
        return row["c"] if row else 0

    # -- users --

    def get_user(self, qq: str) -> dict | None:
        db = self._conn()
        row = db.execute("SELECT * FROM users WHERE qq_number = ?", (qq,)).fetchone()
        db.close()
        if row:
            return dict(row)
        return None

    def create_user(self, qq: str, password_hash: str, nickname: str):
        db = self._conn()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
            (qq, password_hash, nickname, now),
        )
        db.commit()
        db.close()

    def user_exists(self, qq: str) -> bool:
        db = self._conn()
        row = db.execute("SELECT 1 FROM users WHERE qq_number = ?", (qq,)).fetchone()
        db.close()
        return row is not None


class _DynamoDBStorage:
    """DynamoDB 存储（AWS Lambda 部署）"""

    def __init__(self):
        import boto3
        from botocore.exceptions import ClientError

        self.dynamodb = boto3.resource("dynamodb")
        self.users_table = self._ensure_table(DYNAMODB_TABLE_USERS, "qq_number")
        self.members_table = self._ensure_table(DYNAMODB_TABLE_MEMBERS, "qq_number")
        self.codes_table = self._ensure_table(
            DYNAMODB_TABLE_CODES, "qq_number", ttl="expires_at"
        )
        self._boto3 = boto3
        self._ClientError = ClientError

    def _ensure_table(self, name: str, pk: str, ttl: str = None):
        try:
            table = self.dynamodb.Table(name)
            table.table_status  # 触发检查
            return table
        except self._ClientError:
            params = {
                "TableName": name,
                "KeySchema": [{"AttributeName": pk, "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": pk, "AttributeType": "S"}],
                "BillingMode": "PAY_PER_REQUEST",
            }
            if ttl:
                params["TimeToLiveSpecification"] = {
                    "AttributeName": ttl,
                    "Enabled": True,
                }
            table = self.dynamodb.create_table(**params)
            table.wait_until_exists()
            print(f"[DynamoDB] 创建表: {name}")
            return table

    # -- verify_codes --

    def save_code(self, qq: str, code: str):
        self.codes_table.put_item(
            Item={
                "qq_number": qq,
                "code": code,
                "expires_at": int(time.time()) + 300,
            }
        )

    def check_code(self, qq: str, code: str) -> bool:
        resp = self.codes_table.get_item(Key={"qq_number": qq})
        item = resp.get("Item")
        if not item:
            return False
        if time.time() > item["expires_at"]:
            return False
        return item["code"] == code

    def delete_code(self, qq: str):
        self.codes_table.delete_item(Key={"qq_number": qq})

    # -- members --

    def member_exists(self, qq: str) -> bool:
        resp = self.members_table.get_item(Key={"qq_number": qq})
        return "Item" in resp

    def add_member(self, qq: str):
        self.members_table.put_item(Item={"qq_number": qq})

    def remove_member(self, qq: str):
        self.members_table.delete_item(Key={"qq_number": qq})

    def list_members(self) -> list:
        items = []
        resp = self.members_table.scan()
        for item in resp.get("Items", []):
            items.append(item["qq_number"])
        while "LastEvaluatedKey" in resp:
            resp = self.members_table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
            for item in resp.get("Items", []):
                items.append(item["qq_number"])
        return sorted(items)

    def bulk_add_members(self, qqs: list) -> int:
        count = 0
        with self.members_table.batch_writer() as batch:
            for qq in qqs:
                batch.put_item(Item={"qq_number": qq})
                count += 1
        return count

    def count_members(self) -> int:
        return len(self.list_members())

    # -- users --

    def get_user(self, qq: str) -> dict | None:
        resp = self.users_table.get_item(Key={"qq_number": qq})
        return resp.get("Item")

    def create_user(self, qq: str, password_hash: str, nickname: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.users_table.put_item(
            Item={
                "qq_number": qq,
                "password": password_hash,
                "nickname": nickname,
                "registered_at": now,
            }
        )

    def user_exists(self, qq: str) -> bool:
        resp = self.users_table.get_item(Key={"qq_number": qq})
        return "Item" in resp


# ============================================================
# 邮件发送层（SMTP / SES 自动切换）
# ============================================================


def _send_email(to_email: str, subject: str, body: str) -> bool:
    """发送邮件，自动选择 SMTP 或 SES"""
    if USE_SES and SES_SENDER:
        return _send_via_ses(to_email, subject, body)
    return _send_via_smtp(to_email, subject, body)


def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP] 发送失败: {e}")
        return False


def _send_via_ses(to_email: str, subject: str, body: str) -> bool:
    try:
        import boto3

        client = boto3.client("ses", region_name=SES_REGION)
        client.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        return True
    except Exception as e:
        print(f"[SES] 发送失败: {e}")
        # 回退到 SMTP
        if not USE_SES:  # 避免无限回退
            return _send_via_smtp(to_email, subject, body)
        return False


# ============================================================
# 密码加密（与客户端 auth.py 保持一致）
# ============================================================

PBKDF_ITERATIONS = 200_000


def _hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF_ITERATIONS
    )
    return f"{salt}${key.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    if "$" not in stored:
        return False
    try:
        salt, _ = stored.split("$", 1)
        return _hash_password(password, salt) == stored
    except Exception:
        return False


# ============================================================
# 认证中间件
# ============================================================


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not API_KEY:
            return jsonify({"error": "服务器未配置 API_KEY"}), 500
        client_key = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(client_key, API_KEY):
            return jsonify({"error": "未授权"}), 401
        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ADMIN_KEY:
            return jsonify({"error": "管理功能未启用"}), 403
        admin_key = request.headers.get("X-Admin-Key", "")
        if not hmac.compare_digest(admin_key, ADMIN_KEY):
            return jsonify({"error": "未授权"}), 401
        return f(*args, **kwargs)

    return decorated


# ============================================================
# 速率限制
# ============================================================

_rate_limits: dict[str, list[float]] = {}


def rate_limit(key: str, max_requests: int = 10, window: int = 60) -> bool:
    now = time.time()
    if key not in _rate_limits:
        _rate_limits[key] = []
    timestamps = [t for t in _rate_limits[key] if now - t < window]
    _rate_limits[key] = timestamps
    if len(timestamps) >= max_requests:
        return False
    _rate_limits[key].append(now)
    return True


# ============================================================
# API 路由
# ============================================================


@app.route("/api/health", methods=["GET"])
def health():
    mode = "dynamodb+ses" if IS_LAMBDA else ("dynamodb" if USE_DYNAMODB else "sqlite")
    return jsonify({"status": "ok", "mode": mode, "time": datetime.now().isoformat()})


@app.route("/api/send_code", methods=["POST"])
@require_api_key
def send_code():
    if not rate_limit("send_code", max_requests=5, window=60):
        return jsonify({"ok": False, "msg": "请求太频繁，请60秒后再试"}), 429

    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()

    if not qq_number.isdigit() or len(qq_number) < 5:
        return jsonify({"ok": False, "msg": "无效的QQ号"})

    storage = _get_storage()
    code = str(random.randint(100000, 999999))
    email = f"{qq_number}@qq.com"

    subject = "YouYu Auto Draw - Verify Code"
    body = f"""您好！

您的验证码是：{code}

有效期 5 分钟，请勿泄露给他人。

YouYu 自动绘画团队"""

    if _send_email(email, subject, body):
        storage.save_code(qq_number, code)
        print(f"[验证码] {qq_number} -> {email} 发送成功")
        return jsonify({"ok": True, "msg": "验证码已发送，请查收QQ邮箱"})
    else:
        return jsonify({"ok": False, "msg": "邮件发送失败，请联系管理员"}), 500


@app.route("/api/register", methods=["POST"])
@require_api_key
def register_user():
    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()
    password = data.get("password", "")
    nickname = data.get("nickname", qq_number)
    verify_code = str(data.get("verify_code", "")).strip()

    if not qq_number.isdigit() or len(qq_number) < 5:
        return jsonify({"ok": False, "msg": "无效的QQ号"})
    if len(password) < 6:
        return jsonify({"ok": False, "msg": "密码至少6位"})

    storage = _get_storage()

    # 验证码检查
    if not storage.check_code(qq_number, verify_code):
        return jsonify({"ok": False, "msg": "验证码错误或已过期"})

    storage.delete_code(qq_number)

    # 检查白名单
    if not storage.member_exists(qq_number):
        return jsonify({"ok": False, "msg": "该QQ号不在授权列表中"})

    # 检查是否已注册
    if storage.user_exists(qq_number):
        return jsonify({"ok": False, "msg": "该QQ号已注册"})

    # 写入本地数据库
    storage.create_user(qq_number, _hash_password(password), nickname)
    print(f"[注册] {qq_number} ({nickname}) 注册成功")

    # 同步到 GitHub（后台，失败不影响注册）
    try:
        result, sha = _gh_get("auth/users.json")
        users = result if result else {}
        users.setdefault("users", {})[qq_number] = {
            "password": _hash_password(password),
            "nickname": nickname,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        _gh_put("auth/users.json", users, sha, f"register {qq_number}")
        print(f"[注册] 已同步到GitHub")
    except Exception as e:
        print(f"[注册] GitHub同步异常: {e}")

    return jsonify({"ok": True, "msg": "注册成功！"})


@app.route("/api/login", methods=["POST"])
@require_api_key
def login_user():
    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()
    password = data.get("password", "")

    if not qq_number or not password:
        return jsonify({"ok": False, "msg": "请输入QQ号和密码"})

    storage = _get_storage()

    # -------- 以 GitHub/Gitee 为唯一信源 --------
    remote_user = None
    remote_members = None
    gh_available = False
    try:
        users_data = _fetch_json_from_github_gitee("auth/users.json")
        members_data = _fetch_json_from_github_gitee("auth/members.json")
        if users_data is not None:
            gh_available = True
            remote_user = users_data.get("users", {}).get(qq_number)
            remote_members = (
                set(members_data.get("members", [])) if members_data else None
            )
    except Exception:
        pass

    if gh_available:
        if not remote_user:
            if storage.user_exists(qq_number):
                print(f"[登录] {qq_number} 授权已撤销")
            return jsonify({"ok": False, "msg": "账号未注册"})
        if not _verify_password(password, remote_user.get("password", "")):
            return jsonify({"ok": False, "msg": "密码错误"})

        # 实时查 GitHub 白名单（不用本地缓存）
        if remote_members is not None and qq_number not in remote_members:
            print(f"[登录] {qq_number} 不在 GitHub 白名单中，拒绝")
            return jsonify({"ok": False, "msg": "该QQ号授权已被撤回"})
        elif remote_members is None and not storage.member_exists(qq_number):
            print(f"[登录] {qq_number} 不在本地白名单中，拒绝")
            return jsonify({"ok": False, "msg": "该QQ号授权已被撤回"})

        # 同步到本地
        storage.create_user(
            qq_number, remote_user["password"], remote_user.get("nickname", qq_number)
        )
        return jsonify(
            {
                "ok": True,
                "msg": "登录成功",
                "password_hash": remote_user["password"],
                "nickname": remote_user.get("nickname", qq_number),
            }
        )

    # -------- GitHub 不可达 → 用本地缓存 --------
    user = storage.get_user(qq_number)
    if (
        user
        and storage.member_exists(qq_number)
        and _verify_password(password, user.get("password", ""))
    ):
        print(f"[登录] GitHub 不可达，使用本地缓存: {qq_number}")
        return jsonify(
            {
                "ok": True,
                "msg": "登录成功",
                "password_hash": user["password"],
                "nickname": user.get("nickname", qq_number),
            }
        )

    if not user:
        return jsonify({"ok": False, "msg": "账号未注册"})
    return jsonify({"ok": False, "msg": "密码错误"})


@app.route("/api/check_login", methods=["POST"])
@require_api_key
def check_login_user():
    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()
    password_hash = data.get("password_hash", "")

    storage = _get_storage()

    # -------- 以 GitHub/Gitee 为唯一信源 --------
    try:
        users_data = _fetch_json_from_github_gitee("auth/users.json")
        members_data = _fetch_json_from_github_gitee("auth/members.json")
        if users_data is not None:
            remote_user = users_data.get("users", {}).get(qq_number)
            remote_members = (
                set(members_data.get("members", [])) if members_data else None
            )

            if not remote_user:
                if storage.user_exists(qq_number):
                    print(f"[自动登录] {qq_number} 授权已撤销")
                return jsonify({"ok": False})

            # 实时查 GitHub 白名单
            if remote_members is not None and qq_number not in remote_members:
                print(f"[自动登录] {qq_number} 不在 GitHub 白名单中")
                return jsonify({"ok": False})
            elif remote_members is None and not storage.member_exists(qq_number):
                print(f"[自动登录] {qq_number} 不在本地白名单中")
                return jsonify({"ok": False})
            # GitHub 存在 → 验证哈希
            ok = remote_user.get("password") == password_hash
            if ok:
                storage.create_user(
                    qq_number,
                    remote_user["password"],
                    remote_user.get("nickname", qq_number),
                )
            return jsonify({"ok": ok})
    except Exception:
        pass

    # -------- GitHub 不可达 → 用本地缓存 --------
    user = storage.get_user(qq_number)
    if (
        not user
        or not storage.member_exists(qq_number)
        or user.get("password") != password_hash
    ):
        return jsonify({"ok": False})
    return jsonify({"ok": True})


@app.route("/api/user_info", methods=["POST"])
@require_api_key
def user_info():
    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()

    storage = _get_storage()

    # 实时查 GitHub/Gitee
    try:
        users_data = _fetch_json_from_github_gitee("auth/users.json")
        if users_data is not None:
            remote_user = users_data.get("users", {}).get(qq_number)
            if remote_user:
                return jsonify(
                    {
                        "ok": True,
                        "nickname": remote_user.get("nickname", qq_number),
                        "registered_at": remote_user.get("registered_at", ""),
                    }
                )
            return jsonify({"ok": False, "msg": "用户不存在"})
    except Exception:
        pass

    # 回退本地
    user = storage.get_user(qq_number)
    if not user:
        return jsonify({"ok": False, "msg": "用户不存在"})
    return jsonify(
        {
            "ok": True,
            "nickname": user.get("nickname", qq_number),
            "registered_at": user.get("registered_at", ""),
        }
    )


@app.route("/api/check_member", methods=["POST"])
@require_api_key
def check_member():
    data = request.get_json(force=True)
    qq_number = str(data.get("qq_number", "")).strip()

    storage = _get_storage()

    # 实时查 GitHub/Gitee
    try:
        members_data = _fetch_json_from_github_gitee("auth/members.json")
        if members_data is not None:
            remote_members = set(members_data.get("members", []))
            if qq_number in remote_members:
                return jsonify({"ok": True, "msg": "验证通过"})
            return jsonify({"ok": False, "msg": "该QQ号不在授权列表中"})
    except Exception:
        pass

    # 回退本地
    if storage.member_exists(qq_number):
        return jsonify({"ok": True, "msg": "验证通过"})
    return jsonify({"ok": False, "msg": "该QQ号不在授权列表中"})


# ============================================================
# 管理接口
# ============================================================


@app.route("/api/admin/members", methods=["GET"])
@require_admin
def list_members():
    storage = _get_storage()
    return jsonify({"members": storage.list_members()})


@app.route("/api/admin/members", methods=["POST"])
@require_admin
def add_member():
    data = request.get_json(force=True)
    qq = str(data.get("qq_number", "")).strip()
    if not qq.isdigit():
        return jsonify({"error": "无效QQ号"}), 400
    _get_storage().add_member(qq)
    return jsonify({"ok": True, "msg": f"已添加 {qq}"})


@app.route("/api/admin/members", methods=["DELETE"])
@require_admin
def remove_member():
    data = request.get_json(force=True)
    qq = str(data.get("qq_number", "")).strip()
    _get_storage().remove_member(qq)
    return jsonify({"ok": True, "msg": f"已移除 {qq}"})


@app.route("/api/admin/import_members", methods=["POST"])
@require_admin
def import_members():
    data = request.get_json(force=True)
    members_list = data.get("members", [])
    if not isinstance(members_list, list):
        return jsonify({"error": "members 必须是数组"}), 400

    valid = [str(m).strip() for m in members_list if str(m).strip().isdigit()]
    count = _get_storage().bulk_add_members(valid)
    return jsonify({"ok": True, "msg": f"成功导入 {count} 个成员"})


# ============================================================
# 启动时自动从 GitHub 公库导入白名单
# ============================================================


def _auto_import_members():
    """如果 members 表为空，从 GitHub/Gitee 公库拉取"""
    if IS_LAMBDA:
        return
    storage = _get_storage()

    # -------- 导入白名单 --------
    if storage.count_members() == 0:
        print("[启动] members 为空，从 GitHub/Gitee 拉取白名单...")
        members_data = _fetch_json_from_github_gitee("auth/members.json")
        if members_data:
            members = members_data.get("members", [])
            count = storage.bulk_add_members(members)
            print(f"[启动] 成功导入 {count} 个白名单成员")
    else:
        print(f"[启动] members 已有 {storage.count_members()} 人，跳过导入")

    # -------- 导入已有用户 --------
    users_data = _fetch_json_from_github_gitee("auth/users.json")
    if users_data:
        imported = 0
        for qq, info in users_data.get("users", {}).items():
            if not storage.user_exists(qq):
                storage.create_user(
                    qq, info.get("password", ""), info.get("nickname", qq)
                )
                imported += 1
        if imported > 0:
            print(f"[启动] 从 GitHub 导入 {imported} 个已有用户")


def _fetch_json_from_github_gitee(path: str) -> dict | None:
    """从 GitHub 或 Gitee 拉取 JSON（国内 GitHub 慢则自动切 Gitee）"""
    import base64

    # 1. GitHub（5秒超时，国内不行快速跳过）
    if GITHUB_TOKEN:
        try:
            result, _ = _gh_get(path, timeout=5)
            if result:
                return result
        except Exception:
            pass
    # 2. Gitee（国内快）
    if GITEE_TOKEN:
        try:
            result, _ = _gitee_get(path, timeout=8)
            if result:
                return result
        except Exception:
            pass
    # 3. GitHub 公开访问（无 token 兜底）
    try:
        url = f"https://api.github.com/repos/youyu551572/drawinline/contents/{path}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content)
    except Exception:
        pass
    return None


_auto_import_members()


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("YouYu 中转服务器")
    print(
        f"模式: {'DynamoDB+SES (Lambda)' if IS_LAMBDA else ('DynamoDB' if USE_DYNAMODB else 'SQLite')}"
    )
    if not API_KEY:
        print("⚠️  API_KEY 未设置！")
    else:
        print(f"🔑 API_KEY 已加载: {API_KEY[:12]}...{API_KEY[-4:]}")
    print(f"📧 SMTP: {'已配置' if SMTP_USER else '❌ 未配置'}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
