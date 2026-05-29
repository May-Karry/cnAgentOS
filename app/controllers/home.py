import tornado.web

from app.controllers.base import BaseHandler
# from app.models.menu import MenuRepository

class IndexHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		# user = self.current_user
		# role_id = user.get('role_id') if user else None
		# # 传入 role_id 以获取经过权限过滤的菜单树
		# tree = MenuRepository.get_menu_tree(role_id)
		self.render("index.html", title="后台",username=self.current_user)
		# self.render("index.html", title="AI智能瞭望系统 - 后台管理", username=user.get('username') if user else '', menus=tree)

# class DashboardHandler(BaseHandler):
# 	@tornado.web.authenticated
# 	def get(self):
# 		self.render("dashboard.html",title="控制台")