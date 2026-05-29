# 程序的主入口
# 承担服务器容器+程序作用
# 服务器容器：提供http容器服务，程序放置于该容器中运行
# 程序：本体-智能瞭望与智能问数系统 B/s架构
import os
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

# from app.controllers.base import BaseHandler
# 引入auth - controller层
from app.controllers.auth import LoginHandler  # ,LogoutHandler
# from app.controllers.home import IndexHandler, DashboardHandler
# from app.controllers.user import UserPageHandler, UserApiHandler
# from app.controllers.menu import MenuPageHandler, MenuApiHandler
# from app.controllers.role import RolePageHandler, RoleApiHandler
# from app.controllers.model_engine import ModelEnginePageHandler, ModelEngineApiHandler, ModelTestApiHandler
# from app.controllers.spy_source import SpySourcePageHandler, SpySourceApiHandler
# from app.controllers.data_warehouse import DataWarehousePageHandler, DataWarehouseApiHandler
# from app.controllers.spy import SpyPageHandler, SpyRunApiHandler, SpyCommitApiHandler
# 引入db - model层
from app.models.db import init_db  # , get_connection
# from app.models.user import UserRepository
# from app.models.role import RoleRepository
# from app.models.menu import MenuRepository

# class HealthHandler(tornado.web.RequestHandler):
# 	def get(self):
# 		self.write({"status":"ok"})

# class LoginHandler(tornado.web.RequestHandler):
# 	def get(self):
# 		self.write(f"""<h3>模拟登录验证测试BaesHandler</h3>

# 			<form method="post">

			
# 			<button type="submit">登录admin</button>
# 			"""
# 			+  self.xsrf_form_html() +
# 			"""
# 			</form>
# 			""")

# 	def post(self):
# 		next_url = self.get_argument("next","/private")
# 		self.set_secure_cookie("username","admin")
# 		# 写完安全的cookie以后，跳转到目标地址
# 		self.redirect(next_url)


# class PrivateHandler(BaseHandler):
# 	@tornado.web.authenticated
# 	def get(self):
# 		self.write(self.current_user)


def make_app():
	# return tornado.web.Application([
	# 	("/abc",HealthHandler),
	# 	("/login.jsp",HealthHandler),
	# 	("/",HealthHandler),
	# 	("/login.php",HealthHandler)
	# ],debug=True)
	# return tornado.web.Application([
	# 		(r"/",LoginHandler),
	# 		(r"/login",LoginHandler),
	# 		(r"/abc",HealthHandler),
	# 		(r"/private",PrivateHandler)
	# 	],
	# 	cookie_secret="demo-cookie-secret-change-me",
	# 	login_url="/",
	# 	xsrf_cookies=True,
	# 	debug=True
	# )
	base_url = os.path.dirname(os.path.abspath(__file__))
	settings = dict(
		# 预留view 层的内容配置
		template_path=os.path.join(base_url,"app","templates"),
		static_path=os.path.join(base_url,"app","static"),
		cookie_secret="demo-cookie-secret-change-me",
		login_url="/auth/login",
		xsrf_cookies=True,
		debug=True,
		autoreload=True
	)
	return tornado.web.Application([
			# (r"/",IndexHandler),
			# (r"/dashboard", DashboardHandler),
			(r"/auth/login",LoginHandler),
			# (r"/auth/logout",LogoutHandler),
			# (r"/user/list", UserPageHandler),
			# (r"/api/user", UserApiHandler),
			# (r"/menu/list", MenuPageHandler),
			# (r"/api/menu", MenuApiHandler),
			# (r"/role/list", RolePageHandler),
			# (r"/api/role", RoleApiHandler),
			# (r"/model_engine/list", ModelEnginePageHandler),
			# (r"/api/model_engine", ModelEngineApiHandler),
			# (r"/api/model_engine/test", ModelTestApiHandler),
			# # 瞭望数据源管理路由
			# (r"/spy_source/list", SpySourcePageHandler),
			# (r"/api/spy_source", SpySourceApiHandler),
			# # 数据仓库路由
			# (r"/data_warehouse/list", DataWarehousePageHandler),
			# (r"/api/data_warehouse", DataWarehouseApiHandler),
			# # 独立瞭望采集界面路由
			# (r"/spy", SpyPageHandler),
			# (r"/api/spy/run", SpyRunApiHandler),
			# (r"/api/spy/commit", SpyCommitApiHandler)
		],
		**settings
	)

if __name__ == "__main__":
	# 启动服务之前,检查并初始化数据库表
	init_db()
	
# 	# 注入默认超管角色
# 	roles = RoleRepository.get_all_roles()
# 	super_role_id = None
# 	for r in roles:
# 		if r['code'] == 'super_admin':
# 			super_role_id = r['id']
# 			break
# 	if not super_role_id:
# 		super_role_id = RoleRepository.create_role("超级管理员", "super_admin", is_system=1)
		
# 	# 注入默认菜单
# 	menus = MenuRepository.get_all_menus()
# 	if not menus:
# 		sys_id = MenuRepository.create_menu("系统管理", "", "layui-icon-set", 0, 1)
# 		MenuRepository.create_menu("用户管理", "/user/list", "layui-icon-user", sys_id, 1)
# 		MenuRepository.create_menu("角色管理", "/role/list", "layui-icon-group", sys_id, 2)
# 		MenuRepository.create_menu("功能管理", "/menu/list", "layui-icon-app", sys_id, 3)
# 		# 给超管赋权
# 		all_menus = MenuRepository.get_all_menus()
# 		RoleRepository.assign_role_menus(super_role_id, [m['id'] for m in all_menus])

# 	# 注入默认管理员
# 	admin_user = UserRepository.get_user_by_username("admin")
# 	if not admin_user:
# 		UserRepository.create_user("admin", "admin888", super_role_id)
# 	else:
# 		# 确保已存在的 admin 绑定了超管角色
# 		with get_connection() as conn:
# 			conn.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (admin_user['id'], super_role_id))
		
# 	with get_connection() as conn:
# 		# 插入默认菜单
# 		conn.execute("INSERT OR IGNORE INTO menus (id, parent_id, name, icon, url, order_num) VALUES (?, ?, ?, ?, ?, ?)", (5, 0, '模型引擎', 'layui-icon-engine', '/model_engine/list', 5))
# 		conn.execute("INSERT OR IGNORE INTO menus (id, parent_id, name, icon, url, order_num) VALUES (?, ?, ?, ?, ?, ?)", (6, 0, '瞭望管理', 'layui-icon-find-fill', '', 6))
# 		conn.execute("INSERT OR IGNORE INTO menus (id, parent_id, name, icon, url, order_num) VALUES (?, ?, ?, ?, ?, ?)", (7, 6, '数据源管理', '', '/spy_source/list', 1))
# 		conn.execute("INSERT OR IGNORE INTO menus (id, parent_id, name, icon, url, order_num) VALUES (?, ?, ?, ?, ?, ?)", (8, 6, '瞭望采集', '', '/spy', 2))
# 		conn.execute("INSERT OR IGNORE INTO menus (id, parent_id, name, icon, url, order_num) VALUES (?, ?, ?, ?, ?, ?)", (9, 0, '数据仓库', 'layui-icon-table', '/data_warehouse/list', 7))
		
# 		# 确保超级管理员拥有上述菜单权限
# 		for mid in [5, 6, 7, 8, 9]:
# 			conn.execute("INSERT OR IGNORE INTO role_menus (role_id, menu_id) VALUES (?, ?)", (super_role_id, mid))

# 		# 注入默认的百度新闻采集源
# 		baidu_source = conn.execute("SELECT id FROM spy_sources WHERE name='百度新闻'").fetchone()
# 		if not baidu_source:
# 			headers_str = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
# Accept-Encoding: gzip, deflate, br, zstd
# Accept-Language: zh-CN,zh;q=0.9
# Cache-Control: no-cache
# Connection: keep-alive
# Cookie: BIDUPSID=5CFCC8D701BF7571598CE9F66EE8E6B5; PSTM=1775407070; BD_UPN=1a314753; BAIDUID=5CFCC8D701BF75717E6B8B51D00D380F:SL=0:NR=10:FG=1;
# Host: www.baidu.com
# Pragma: no-cache
# Referer: https://news.baidu.com/
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 QQBrowser/21.1.8743.400"""
			
# 			conn.execute(
# 				"INSERT INTO spy_sources (name, entry_url, request_headers, is_active) VALUES (?, ?, ?, ?)",
# 				("百度新闻", "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={关键字}&pn={分页步进}", headers_str, 1)
# 			)		
	app = make_app()
	server = HTTPServer(app)
	server.bind(10086)
	# 自动CPU核心数
	server.start()

	# try:
	print("====== Server 启动成功 ======== 端口：10086 ======", flush=True)
	# except OSError:
	# 	pass
	tornado.ioloop.IOLoop.current().start()