import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.system import MenuRepository, RoleRepository, UserRoleRepository

class MenuAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, menu_id=None):
        if menu_id:
            menus = MenuRepository.get_all_menus()
            for menu in menus:
                if menu['id'] == int(menu_id):
                    self.write({"success": True, "data": menu})
                    return
            self.write({"success": False, "message": "功能不存在"})
        else:
            tree = MenuRepository.get_menu_tree()
            self.write({"success": True, "data": tree})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            url = data.get("url")
            icon = data.get("icon")
            parent_id = int(data.get("parent_id", 0))
            order_num = int(data.get("order_num", 0))
            
            if not name:
                self.write({"success": False, "message": "功能名称不能为空"})
                return
            
            menu_id = MenuRepository.create_menu(name, url, icon, parent_id, order_num)
            self.write({"success": True, "message": "创建成功", "data": {"id": menu_id}})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, menu_id):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            url = data.get("url")
            icon = data.get("icon")
            order_num = data.get("order_num")
            
            if MenuRepository.update_menu(int(menu_id), name, url, icon, order_num):
                self.write({"success": True, "message": "更新成功"})
            else:
                self.write({"success": False, "message": "更新失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, menu_id):
        if MenuRepository.delete_menu(int(menu_id)):
            self.write({"success": True, "message": "删除成功"})
        else:
            self.write({"success": False, "message": "删除失败"})


class RoleAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, role_id=None):
        if role_id:
            role = RoleRepository.get_role_by_id(int(role_id))
            if role:
                self.write({"success": True, "data": dict(role)})
            else:
                self.write({"success": False, "message": "角色不存在"})
        else:
            roles = RoleRepository.get_all_roles()
            self.write({"success": True, "data": roles})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            code = data.get("code")
            
            if not name or not code:
                self.write({"success": False, "message": "角色名称和代码不能为空"})
                return
            
            role_id = RoleRepository.create_role(name, code)
            if role_id > 0:
                self.write({"success": True, "message": "创建成功", "data": {"id": role_id}})
            else:
                self.write({"success": False, "message": "角色代码已存在"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, role_id):
        try:
            role = RoleRepository.get_role_by_id(int(role_id))
            if role and role['is_system'] == 1:
                self.write({"success": False, "message": "系统角色不能修改"})
                return
            
            data = json.loads(self.request.body)
            name = data.get("name")
            code = data.get("code")
            
            if RoleRepository.update_role(int(role_id), name, code):
                self.write({"success": True, "message": "更新成功"})
            else:
                self.write({"success": False, "message": "更新失败或角色代码已存在"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, role_id):
        role = RoleRepository.get_role_by_id(int(role_id))
        if role and role['is_system'] == 1:
            self.write({"success": False, "message": "系统角色不能删除"})
            return
        
        if RoleRepository.delete_role(int(role_id)):
            self.write({"success": True, "message": "删除成功"})
        else:
            self.write({"success": False, "message": "删除失败"})


class PermissionAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, role_id=None):
        menus = MenuRepository.get_all_menus()
        roles = RoleRepository.get_all_roles()
        
        role_permissions = {}
        for role in roles:
            role_permissions[role['id']] = MenuRepository.get_role_menus(role['id'])
        
        self.write({
            "success": True,
            "data": {
                "menus": menus,
                "roles": roles,
                "rolePermissions": role_permissions
            }
        })
    
    @tornado.web.authenticated
    def post(self, role_id=None):
        try:
            data = json.loads(self.request.body)
            role_id = int(data.get("role_id"))
            menu_ids = data.get("menu_ids", [])
            
            if RoleRepository.get_role_by_id(role_id)['is_system'] == 1:
                self.write({"success": False, "message": "系统角色权限不能修改"})
                return
            
            if MenuRepository.set_role_menus(role_id, menu_ids):
                self.write({"success": True, "message": "权限设置成功"})
            else:
                self.write({"success": False, "message": "权限设置失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})


class UserRoleAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, user_id=None):
        if user_id:
            roles = RoleRepository.get_user_roles(int(user_id))
            self.write({"success": True, "data": roles})
        else:
            roles = RoleRepository.get_all_roles()
            self.write({"success": True, "data": roles})
    
    @tornado.web.authenticated
    def post(self, user_id=None):
        try:
            data = json.loads(self.request.body)
            user_id = int(data.get("user_id"))
            role_ids = data.get("role_ids", [])
            
            if UserRoleRepository.set_user_roles(user_id, role_ids):
                self.write({"success": True, "message": "角色分配成功"})
            else:
                self.write({"success": False, "message": "角色分配失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})