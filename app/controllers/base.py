# Controller 公共基础类（BaseHandler）
"""
在tornado中
- 每一个Url对应一个RequestHandler 可以理解为Controller
- RequestHandler 提供 post / get 等方法来处理http请求

本程序可以提供一个统一的基础类，用于处理一些公共业务，如登录态的处理或获得逻辑，供其他Handler继承使用
"""
import tornado.web
from app.models.user import UserRepository
from app.models.system import RoleRepository

class BaseHandler(tornado.web.RequestHandler):
	# 公共类的用户态认证机制：
	# - 框架会通过 xxxx() 的返回值来判断是否"已经登录"
	# - 如果返回None 则 @tornado.web.authenticated 触发跳转到指定的路由URL：login_url
	def get_current_user(self):
		# 返回当前登录用户的字符串 或 None
		username = self.get_secure_cookie("username")
		if not username:
			return None
		return username.decode('utf-8')
	
	def get_current_user_info(self):
		"""获取当前登录用户的完整信息（包括角色）"""
		username = self.get_current_user()
		if not username:
			return None
		
		user = UserRepository.get_user_by_username(username)
		if not user:
			return None
		
		# 获取用户的角色
		roles = RoleRepository.get_user_roles(user['id'])
		user_info = dict(user)
		user_info['roles'] = roles
		return user_info
	
	def get_user_menus(self):
		"""获取当前登录用户有权访问的菜单"""
		user_info = self.get_current_user_info()
		if not user_info:
			return []
		
		from app.models.system import MenuRepository
		
		# 获取用户所有角色的菜单权限
		all_menu_ids = set()
		for role in user_info.get('roles', []):
			menu_ids = MenuRepository.get_role_menus(role['id'])
			all_menu_ids.update(menu_ids)
		
		# 如果没有角色，返回空列表
		if not all_menu_ids:
			return []
		
		# 获取所有菜单并过滤
		all_menus = MenuRepository.get_all_menus()
		# 构建菜单树
		tree = []
		menu_map = {}
		
		for menu in all_menus:
			if menu['id'] in all_menu_ids:
				menu['children'] = []
				menu_map[menu['id']] = menu
		
		for menu in menu_map.values():
			if menu['parent_id'] == 0:
				tree.append(menu)
			else:
				parent = menu_map.get(menu['parent_id'])
				if parent:
					parent['children'].append(menu)
		
		return tree
	
	def has_permission(self, url):
		"""检查当前用户是否有访问指定URL的权限"""
		menus = self.get_user_menus()
		
		def check_menu(menu_list, target_url):
			for menu in menu_list:
				if menu['url'] == target_url:
					return True
				if menu.get('children') and check_menu(menu['children'], target_url):
					return True
			return False
		
		return check_menu(menus, url)