# 数据库链接与建表
import os
import sqlite3

# 获得项目根路径的方法
def _project_root():
	return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

# 获得数据文件的路径
DB_PATH = os.path.join(_project_root(),"database","app.db")

# 获得数据库连接
def get_connection():
	os.makedirs(os.path.dirname(DB_PATH),exist_ok=True)
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn

# 初始化数据库表
def init_db():
	with get_connection() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS users(
				id integer PRIMARY KEY AUTOINCREMENT,
				username TEXT NOT NULL UNIQUE,
				password_hash TEXT NOT NULL,
				salt TEXT NOT NULL,
				create_at TEXT NOT NULL DEFAULT(datetime('now'))
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS roles(
				id integer PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL UNIQUE,
				code TEXT NOT NULL UNIQUE,
				is_system integer DEFAULT 0,
				create_at TEXT NOT NULL DEFAULT(datetime('now'))
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS menus(
				id integer PRIMARY KEY AUTOINCREMENT,
				parent_id integer DEFAULT 0,
				name TEXT NOT NULL,
				url TEXT,
				icon TEXT,
				order_num integer DEFAULT 0,
				create_at TEXT NOT NULL DEFAULT(datetime('now'))
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS role_menus(
				role_id integer,
				menu_id integer,
				PRIMARY KEY (role_id, menu_id)
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS user_roles(
				user_id integer,
				role_id integer,
				PRIMARY KEY (user_id, role_id)
			)
			"""
		)
		
		# 建立模型引擎表 (ai_models)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS ai_models(
				id integer primary key autoincrement,
				name varchar(100) not null,         -- 别名/展示名
				model_name varchar(100) not null,   -- API实际调用的模型名称 (如 deepseek-v3)
				api_key varchar(255) not null,
				base_url varchar(255) not null,
				is_default integer default 0,       -- 1为系统默认全局优先调用
				total_tokens integer default 0,     -- token消耗统计
				create_at datetime default current_timestamp
			)
			"""
		)

		# 建立瞭望数据源管理表 (spy_sources)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS spy_sources(
				id integer primary key autoincrement,
				name varchar(100) not null,          -- 来源名称，如"百度新闻"
				entry_url text not null,             -- 采集入口 URL 模板
				request_headers text not null,       -- JSON 格式存储的 Headers
				is_active integer default 1,         -- 是否启用
				create_at datetime default current_timestamp
			)
			"""
		)

		# 建立数据仓库表 (spy_data)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS spy_data(
				id integer primary key autoincrement,
				source_id integer not null,          -- 关联的 spy_sources.id
				keyword varchar(255) not null,       -- 采集时用的关键词
				title text not null,                 -- 抓取到的标题
				url text not null,                   -- 抓取到的目标链接
				summary text,                        -- 抓取到的摘要或正文
				create_at datetime default current_timestamp,
				update_at datetime
			)
			"""
		)

		# 历史版本兼容：老表没有 update_at 时补列
		try:
			conn.execute("ALTER TABLE spy_data ADD COLUMN update_at datetime")
		except sqlite3.OperationalError:
			pass

		# 防止重复入库：同一来源下 URL 唯一
		conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_spy_data_source_url ON spy_data(source_id, url)")
