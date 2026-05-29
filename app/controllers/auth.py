import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.user import UserRepository
from app.models.system import UserRoleRepository
from app.models.db import init_db

init_db()

class AdminLoginHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        # Disable XSRF verification for testing
        pass
    
    def get(self):
        xsrf_token = self.xsrf_token
        self.render("admin_login.html", xsrf_token=xsrf_token)
    
    def post(self):
        try:
            username = self.get_argument("username", "")
            password = self.get_argument("password", "")
            
            print(f"登录尝试: username={username}, password={password}")
            
            if UserRepository.verify(username, password):
                self.set_secure_cookie("username", username)
                print("登录成功")
                self.write({"success": True, "message": "登录成功"})
            else:
                print("登录失败：用户名或密码错误")
                self.write({"success": False, "message": "用户名或密码错误"})
        except Exception as e:
            print(f"登录异常: {str(e)}")
            self.write({"success": False, "message": str(e)})

class AdminIndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.current_user
        xsrf_token = self.xsrf_token
        user_info = self.get_current_user_info()
        menus = self.get_user_menus()
        
        # 获取用户角色名称
        role_name = '未分配'
        if user_info and user_info.get('roles'):
            role_name = user_info['roles'][0]['name']
        
        self.render("admin_index.html", username=username, xsrf_token=xsrf_token, menus=menus, role_name=role_name)

class AdminLogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        self.clear_cookie("username")
        self.redirect("/admin/login")

class AdminUsersHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # 检查权限
        if not self.has_permission('/admin/users'):
            self.redirect('/admin/index')
            return
        self.render("admin_users.html")

class UsersAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, user_id=None):
        if user_id:
            user = UserRepository.get_user_by_username(user_id)
            if user:
                self.write({
                    "success": True,
                    "data": {
                        "id": user['id'],
                        "username": user['username'],
                        "create_at": user['create_at']
                    }
                })
            else:
                user_data = None
                users = UserRepository.get_all_users()
                for u in users:
                    if u['id'] == int(user_id):
                        user_data = u
                        break
                if user_data:
                    self.write({"success": True, "data": user_data})
                else:
                    self.write({"success": False, "message": "用户不存在"})
        else:
            page = int(self.get_argument("page", 1))
            page_size = int(self.get_argument("page_size", 20))
            username = self.get_argument("username", "")
            
            users = UserRepository.get_all_users(page, page_size)
            total = UserRepository.get_user_count()
            
            if username:
                users = [u for u in users if username.lower() in u['username'].lower()]
            
            self.write({
                "success": True,
                "data": users,
                "total": total
            })
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            username = data.get("username")
            password = data.get("password")
            role_id = data.get("role_id")
            
            if not username or not password:
                self.write({"success": False, "message": "用户名和密码不能为空"})
                return
            
            if UserRepository.create_user(username, password, role_id):
                self.write({"success": True, "message": "用户创建成功"})
            else:
                self.write({"success": False, "message": "用户名已存在"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, user_id):
        try:
            data = json.loads(self.request.body)
            username = data.get("username")
            password = data.get("password")
            role_id = data.get("role_id")
            
            if UserRepository.update_user(int(user_id), username, password):
                if role_id:
                    UserRoleRepository.set_user_roles(int(user_id), [role_id])
                self.write({"success": True, "message": "用户更新成功"})
            else:
                self.write({"success": False, "message": "更新失败，用户名可能已存在"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, user_id):
        if user_id == "batch":
            try:
                data = json.loads(self.request.body)
                ids = data.get("ids", [])
                if UserRepository.batch_delete_users(ids):
                    self.write({"success": True, "message": "批量删除成功"})
                else:
                    self.write({"success": False, "message": "删除失败"})
            except Exception as e:
                self.write({"success": False, "message": str(e)})
        else:
            if UserRepository.delete_user(int(user_id)):
                self.write({"success": True, "message": "删除成功"})
            else:
                self.write({"success": False, "message": "删除失败"})