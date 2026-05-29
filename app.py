import tornado.ioloop
import tornado.web
import json
from tornado.httpserver import HTTPServer
from tornado.gen import coroutine
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from app.controllers.base import BaseHandler
from app.controllers.auth import (
    AdminLoginHandler,
    AdminIndexHandler,
    AdminLogoutHandler,
    AdminUsersHandler,
    UsersAPIHandler
)
from app.controllers.system import (
    MenuAPIHandler,
    RoleAPIHandler,
    PermissionAPIHandler,
    UserRoleAPIHandler
)
from app.models.system import ModelRepository, SpySourceRepository, SpyDataRepository, ForgeryTemplateRepository, AttackLogRepository, StorageConfigRepository, SpySourceRepositoryDefense

class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "ok"})

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(f"""<h3>模拟登录验证测试BaesHandler</h3>
            <form method="post">
            {self.xsrf_form_html()}
            <button type="submit">登录admin</button>
            </form>
            """)

    def post(self):
        next_url = self.get_argument("next", "/private")
        self.set_secure_cookie("username", "admin")
        self.redirect(next_url)

class PrivateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(self.current_user)

class AdminFunctionsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/functions'):
            self.redirect('/admin/index')
            return
        self.render("admin_functions.html")

class AdminRolesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/roles'):
            self.redirect('/admin/index')
            return
        self.render("admin_roles.html")

class AdminPermissionsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/permissions'):
            self.redirect('/admin/index')
            return
        self.render("admin_permissions.html")

class AdminDigitalStaffHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/digital-staff'):
            self.redirect('/admin/index')
            return
        self.write("<h1>数字员工 - 开发中</h1>")

class AdminModelEngineHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/model-engine'):
            self.redirect('/admin/index')
            return
        self.render("admin_model_engine.html")

class AdminSpySourcesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/spy-sources'):
            self.redirect('/admin/index')
            return
        self.render("admin_spy_sources.html")

class AdminWatchtowerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/watchtower'):
            self.redirect('/admin/index')
            return
        self.render("admin_watchtower.html")

class AdminDataWarehouseHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/data-warehouse'):
            self.redirect('/admin/index')
            return
        self.render("admin_data_warehouse.html")

class AdminDeepCollectionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/deep-collection'):
            self.redirect('/admin/index')
            return
        self.write("<h1>深度采集 - 开发中</h1>")

class AdminAPIManagementHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/api-management'):
            self.redirect('/admin/index')
            return
        self.write("<h1>接口管理 - 开发中</h1>")

class AdminDashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/dashboard'):
            self.redirect('/admin/index')
            return
        self.write("<h1>数智大屏 - 开发中</h1>")

class AdminSystemSettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/system-settings'):
            self.redirect('/admin/index')
            return
        self.write("<h1>系统设置 - 开发中</h1>")

class AdminSystemStatsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.has_permission('/admin/system-stats'):
            self.redirect('/admin/index')
            return
        self.write("<h1>系统统计 - 开发中</h1>")


class ModelAPIHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=10)
    
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, model_id=None):
        if model_id:
            model = ModelRepository.get_model_by_id(int(model_id))
            if model:
                self.write({"success": True, "data": model})
            else:
                self.write({"success": False, "message": "模型不存在"})
        else:
            models = ModelRepository.get_all_models()
            self.write({"success": True, "data": models})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            model_name = data.get("model_name")
            api_key = data.get("api_key")
            base_url = data.get("base_url")
            is_default = data.get("is_default", False)
            
            if not all([name, model_name, api_key, base_url]):
                self.write({"success": False, "message": "请填写完整信息"})
                return
            
            model_id = ModelRepository.create_model(name, model_name, api_key, base_url, is_default)
            if model_id > 0:
                self.write({"success": True, "message": "创建成功", "data": {"id": model_id}})
            else:
                self.write({"success": False, "message": "创建失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, model_id):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            model_name = data.get("model_name")
            api_key = data.get("api_key")
            base_url = data.get("base_url")
            is_default = data.get("is_default")
            
            if ModelRepository.update_model(int(model_id), name, model_name, api_key, base_url, is_default):
                self.write({"success": True, "message": "更新成功"})
            else:
                self.write({"success": False, "message": "更新失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, model_id):
        if ModelRepository.delete_model(int(model_id)):
            self.write({"success": True, "message": "删除成功"})
        else:
            self.write({"success": False, "message": "删除失败"})


class ModelChatHandler(BaseHandler):
    
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            message = data.get("message", "")
            model_id = data.get("model_id")
            
            if not model_id:
                self.write({"success": False, "message": "请选择模型"})
                return
            
            model = ModelRepository.get_model_by_id(int(model_id))
            if not model:
                self.write({"success": False, "message": "模型不存在"})
                return
            
            result = self.sync_call_openai(model, message)
            if "error" in result:
                self.write({"success": False, "message": result["error"]})
            else:
                self.write({"success": True, "data": result})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    def sync_call_openai(self, model, message):
        try:
            import openai
            client = openai.OpenAI(
                api_key=model['api_key'],
                base_url=model['base_url']
            )
            response = client.chat.completions.create(
                model=model['model_name'],
                messages=[{"role": "user", "content": message}]
            )
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            ModelRepository.update_tokens(model['id'], tokens)
            return {"content": content, "tokens": tokens}
        except Exception as e:
            return {"error": str(e)}


class ModelStreamChatHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=10)
    
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    @coroutine
    def post(self, model_id=None):
        try:
            data = json.loads(self.request.body)
            message = data.get("message", "")
            model_id = data.get("model_id")
            
            if not model_id:
                self.write({"success": False, "message": "请选择模型"})
                return
            
            model = ModelRepository.get_model_by_id(int(model_id))
            if not model:
                self.write({"success": False, "message": "模型不存在"})
                return
            
            self.set_header('Content-Type', 'text/event-stream')
            self.set_header('Cache-Control', 'no-cache')
            self.set_header('Connection', 'keep-alive')
            self.set_header('X-Accel-Buffering', 'no')
            
            result = yield self.stream_call_openai(model, message)
            self.finish()
        except Exception as e:
            self.write(f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n")
            self.finish()
    
    @run_on_executor
    def stream_call_openai(self, model, message):
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=model['api_key'],
                base_url=model['base_url']
            )
            stream = client.chat.completions.create(
                model=model['model_name'],
                messages=[{"role": "user", "content": message}],
                stream=True
            )
            total_tokens = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    self.write(f"event: message\ndata: {json.dumps({'content': content})}\n\n")
                    self.flush()
                if chunk.usage:
                    total_tokens = chunk.usage.total_tokens
            ModelRepository.update_tokens(model['id'], total_tokens)
            self.write(f"event: done\ndata: {json.dumps({'tokens': total_tokens})}\n\n")
            self.flush()
        except Exception as e:
            self.write(f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n")
            self.flush()


class SetDefaultModelHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            model_id = data.get("model_id")
            
            if not model_id:
                self.write({"success": False, "message": "请选择模型"})
                return
            
            if ModelRepository.set_default_model(int(model_id)):
                self.write({"success": True, "message": "设置成功"})
            else:
                self.write({"success": False, "message": "设置失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})


class SpySourceAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, source_id=None):
        if source_id:
            source = SpySourceRepository.get_source_by_id(int(source_id))
            self.write({"success": True, "data": source})
        else:
            sources = SpySourceRepository.get_all_sources()
            self.write({"success": True, "data": sources})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            entry_url = data.get("entry_url")
            request_headers = data.get("request_headers")
            
            source_id = SpySourceRepository.create_source(name, entry_url, request_headers)
            if source_id > 0:
                self.write({"success": True, "message": "创建成功", "data": {"id": source_id}})
            else:
                self.write({"success": False, "message": "创建失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, source_id):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            entry_url = data.get("entry_url")
            request_headers = data.get("request_headers")
            is_active = data.get("is_active")
            
            if SpySourceRepository.update_source(int(source_id), name, entry_url, request_headers, is_active):
                self.write({"success": True, "message": "更新成功"})
            else:
                self.write({"success": False, "message": "更新失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, source_id):
        if SpySourceRepository.delete_source(int(source_id)):
            self.write({"success": True, "message": "删除成功"})
        else:
            self.write({"success": False, "message": "删除失败"})


class SpyDataAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self):
        try:
            page = int(self.get_argument("page", 1))
            page_size = int(self.get_argument("page_size", 20))
            data, total = SpyDataRepository.get_paginated_data(page, page_size)
            self.write({"success": True, "data": data, "total": total})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, data_id):
        if SpyDataRepository.delete_data(int(data_id)):
            self.write({"success": True, "message": "删除成功"})
        else:
            self.write({"success": False, "message": "删除失败"})


class SpyBatchDeleteHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            ids = data.get("ids", [])
            if SpyDataRepository.batch_delete_data(ids):
                self.write({"success": True, "message": "删除成功"})
            else:
                self.write({"success": False, "message": "删除失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})


class SpyCollectHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            import traceback
            import re
            import json
            
            data = json.loads(self.request.body)
            keyword = data.get("keyword")
            source_ids = data.get("source_ids", [])
            max_count = data.get("max_count", 10)
            max_pages = data.get("max_pages", 1)
            
            collected = 0
            sources = SpySourceRepository.get_active_sources()
            debug_info = []
            
            for source in sources:
                if source["id"] not in source_ids:
                    continue
                
                debug_info.append(f"正在处理源: {source['name']}")
                
                # 解析 headers
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                try:
                    saved_headers = json.loads(source["request_headers"])
                    headers.update(saved_headers)
                except:
                    pass
                
                entry_url_tpl = source["entry_url"]
                
                for page in range(int(max_pages)):
                    if collected >= max_count:
                        break
                    
                    pn = page * 10
                    keyword_encoded = urllib.parse.quote(keyword)
                    
                    # 替换 URL 模板 - 先尝试中文，再尝试英文
                    url = entry_url_tpl
                    try:
                        url = url.format(关键字=keyword_encoded, 分页步进=pn)
                    except (KeyError, IndexError):
                        try:
                            url = url.format(keyword=keyword_encoded, pn=pn)
                        except:
                            pass
                    
                    debug_info.append(f"请求 URL: {url}")
                    
                    try:
                        resp = requests.get(url, headers=headers, timeout=15)
                        debug_info.append(f"响应状态: {resp.status_code}")
                        
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.text, "html.parser")
                            
                            # 针对百度新闻的特定解析
                            news_items = soup.select(".c-container")
                            debug_info.append(f"找到 {len(news_items)} 条内容")
                            
                            for item in news_items[:min(max_count - collected, len(news_items))]:
                                try:
                                    # 查找标题 - 支持多种类名
                                    title_el = (item.select_one("h3 a") or 
                                               item.select_one(".news-title_1YtI1 a") or
                                               item.select_one("a"))
                                    title = title_el.get_text(strip=True) if title_el else ""
                                    
                                    # 查找链接
                                    item_url = ""
                                    if title_el:
                                        item_url = title_el.get("href", "")
                                    
                                    # 查找摘要 - 支持多种选择器
                                    summary_el = (item.select_one(".c-abstract") or 
                                                 item.select_one(".content_BL3zl") or 
                                                 item.select_one(".c-color-text") or
                                                 item.select_one("p"))
                                    summary = summary_el.get_text(strip=True) if summary_el else ""
                                    
                                    # 如果还没找到，尝试从 data 中获取
                                    if not title or not item_url:
                                        # 尝试从 data 注释中提取
                                        data_comment = item.find(string=lambda s: s and 'title' in s and 'titleUrl' in s)
                                        if data_comment:
                                            try:
                                                # 查找 s-data: 后的 JSON
                                                match = re.search(r's-data:\s*({.+})', data_comment)
                                                if match:
                                                    s_data = json.loads(match.group(1))
                                                    if not title:
                                                        title = s_data.get("title", "")
                                                    if not item_url:
                                                        item_url = s_data.get("titleUrl", "")
                                                    if not summary:
                                                        summary = s_data.get("summary", "")
                                            except:
                                                pass
                                    
                                    # 清理标题中的强调标签
                                    if title:
                                        title = title.replace("<em>", "").replace("</em>", "")
                                    
                                    if title and len(title) > 2 and item_url:
                                        # 清理摘要
                                        if summary:
                                            summary = summary.replace("<em>", "").replace("</em>", "")
                                        SpyDataRepository.insert_data(source["id"], keyword, title, item_url, summary)
                                        collected += 1
                                except Exception as e:
                                    debug_info.append(f"解析单个项目失败: {e}")
                                    continue
                    except Exception as e:
                        debug_info.append(f"采集失败: {e}\n{traceback.format_exc()}")
                        continue
            
            self.write({
                "success": True, 
                "message": f"成功采集 {collected} 条数据", 
                "count": collected,
                "debug": debug_info
            })
        except Exception as e:
            self.write({"success": False, "message": str(e)})


def make_app():
    return tornado.web.Application([
        (r"/", LoginHandler),
        (r"/login", LoginHandler),
        (r"/abc", HealthHandler),
        (r"/private", PrivateHandler),
        
        (r"/admin/login", AdminLoginHandler),
        (r"/admin/index", AdminIndexHandler),
        (r"/admin/logout", AdminLogoutHandler),
        (r"/admin/users", AdminUsersHandler),
        (r"/admin/functions", AdminFunctionsHandler),
        (r"/admin/roles", AdminRolesHandler),
        (r"/admin/permissions", AdminPermissionsHandler),
        (r"/admin/digital-staff", AdminDigitalStaffHandler),
        (r"/admin/model-engine", AdminModelEngineHandler),
        (r"/admin/spy-sources", AdminSpySourcesHandler),
        (r"/admin/watchtower", AdminWatchtowerHandler),
        (r"/admin/data-warehouse", AdminDataWarehouseHandler),
        (r"/admin/deep-collection", AdminDeepCollectionHandler),
        (r"/admin/api-management", AdminAPIManagementHandler),
        (r"/admin/dashboard", AdminDashboardHandler),
        (r"/admin/system-settings", AdminSystemSettingsHandler),
        (r"/admin/system-stats", AdminSystemStatsHandler),
        
        (r"/api/users", UsersAPIHandler),
        (r"/api/users/(.*)", UsersAPIHandler),
        (r"/api/menus", MenuAPIHandler),
        (r"/api/menus/(.*)", MenuAPIHandler),
        (r"/api/roles", RoleAPIHandler),
        (r"/api/roles/(.*)", RoleAPIHandler),
        (r"/api/permissions", PermissionAPIHandler),
        (r"/api/permissions/(.*)", PermissionAPIHandler),
        (r"/api/user-roles", UserRoleAPIHandler),
        (r"/api/user-roles/(.*)", UserRoleAPIHandler),
        (r"/api/models/chat", ModelChatHandler),
        (r"/api/models/chat/stream", ModelStreamChatHandler),
        (r"/api/models/set-default", SetDefaultModelHandler),
        (r"/api/models", ModelAPIHandler),
        (r"/api/models/(.*)", ModelAPIHandler),
        (r"/api/spy-sources", SpySourceAPIHandler),
        (r"/api/spy-sources/(.*)", SpySourceAPIHandler),
        (r"/api/spy-data", SpyDataAPIHandler),
        (r"/api/spy-data/(.*)", SpyDataAPIHandler),
        (r"/api/spy-data/batch-delete", SpyBatchDeleteHandler),
        (r"/api/spy-collect", SpyCollectHandler),
        (r"/api/forgery-templates", ForgeryTemplateAPIHandler),
        (r"/api/forgery-templates/(.*)", ForgeryTemplateAPIHandler),
        (r"/api/attack-test", AttackTestHandler),
        (r"/api/attack-logs", AttackLogAPIHandler),
        (r"/api/storage-configs", StorageConfigAPIHandler),
        (r"/api/storage-configs/(.*)", StorageConfigAPIHandler),
        (r"/api/storage-test", StorageTestHandler),
        
        (r"/admin/forgery-defense", AdminForgeryDefenseHandler),
        (r"/admin/storage-manager", AdminStorageManagerHandler),
        
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "app/static"}),
    ],
    cookie_secret="demo-cookie-secret-change-me",
    login_url="/admin/login",
    xsrf_cookies=True,
    debug=True,
    template_path="app/templates"
    )

# --------------------------
# 任务六：请求伪造与安全防护
# --------------------------
class ForgeryTemplateAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, template_id=None):
        if template_id:
            template = ForgeryTemplateRepository.get_template_by_id(int(template_id))
            self.write({"success": True, "data": template})
        else:
            templates = ForgeryTemplateRepository.get_all_templates()
            self.write({"success": True, "data": templates})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            attack_type = data.get("attack_type")
            description = data.get("description")
            headers = data.get("headers")
            params = data.get("params")
            payloads = data.get("payloads")
            
            template_id = ForgeryTemplateRepository.create_template(
                name, attack_type, description,
                json.dumps(headers) if headers else None,
                json.dumps(params) if params else None,
                json.dumps(payloads) if payloads else None
            )
            if template_id > 0:
                self.write({"success": True, "data": {"id": template_id}})
            else:
                self.write({"success": False, "message": "创建失败"})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, template_id):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            attack_type = data.get("attack_type")
            description = data.get("description")
            headers = data.get("headers")
            params = data.get("params")
            payloads = data.get("payloads")
            is_active = data.get("is_active")
            
            success = ForgeryTemplateRepository.update_template(
                int(template_id),
                name, attack_type, description,
                json.dumps(headers) if headers else None,
                json.dumps(params) if params else None,
                json.dumps(payloads) if payloads else None,
                is_active
            )
            self.write({"success": success})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, template_id):
        if ForgeryTemplateRepository.delete_template(int(template_id)):
            self.write({"success": True})
        else:
            self.write({"success": False})


class AttackTestHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            import requests
            
            data = json.loads(self.request.body)
            template_id = data.get("template_id")
            target_url = data.get("target_url")
            attack_type = data.get("attack_type")
            source_id = data.get("source_id")
            
            # 获取模板
            template = None
            headers = {}
            payload = {}
            if template_id:
                template = ForgeryTemplateRepository.get_template_by_id(int(template_id))
                if template:
                    if template.get("headers"):
                        headers = json.loads(template["headers"])
                    if template.get("payloads"):
                        payload = json.loads(template["payloads"])
            
            # 应用手动参数
            if data.get("headers"):
                headers.update(data["headers"])
            
            # 安全防护检查
            is_blocked = False
            if source_id:
                source = SpySourceRepository.get_source_by_id(int(source_id))
                if source and source.get("enable_defense"):
                    # 简单的防护规则
                    dangerous_hosts = ["localhost", "127.0.0.1", "169.254.169.254"]
                    for host in dangerous_hosts:
                        if host in target_url:
                            is_blocked = True
                            break
            
            if is_blocked:
                # 记录阻断日志
                AttackLogRepository.create_log(
                    source_id if source_id else None,
                    template_id,
                    attack_type,
                    target_url,
                    json.dumps({"headers": headers, "payload": payload}),
                    json.dumps({"blocked": True, "reason": "Security rule blocked"}),
                    403,
                    True
                )
                self.write({"success": True, "blocked": True, "message": "攻击已被安全防护阻断"})
                return
            
            # 执行测试请求
            response_status = 0
            response_text = ""
            try:
                resp = requests.post(target_url, json=payload, headers=headers, timeout=5)
                response_status = resp.status_code
                response_text = resp.text
            except Exception as e:
                response_text = str(e)
            
            # 记录日志
            AttackLogRepository.create_log(
                source_id if source_id else None,
                template_id,
                attack_type,
                target_url,
                json.dumps({"headers": headers, "payload": payload}),
                response_text[:2000],
                response_status,
                False
            )
            
            self.write({
                "success": True,
                "status_code": response_status,
                "response": response_text[:500]
            })
        except Exception as e:
            self.write({"success": False, "message": str(e)})


class AttackLogAPIHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page", "1"))
        page_size = int(self.get_argument("page_size", "20"))
        data, total = AttackLogRepository.get_paginated_logs(page, page_size)
        self.write({"success": True, "data": data, "total": total})


# --------------------------
# 任务七：多类型存储配置
# --------------------------
class StorageConfigAPIHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, config_id=None):
        if config_id:
            config = StorageConfigRepository.get_config_by_id(int(config_id))
            self.write({"success": True, "data": config})
        else:
            configs = StorageConfigRepository.get_all_configs()
            self.write({"success": True, "data": configs})
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            storage_type = data.get("storage_type")
            connection_string = data.get("connection_string")
            config = data.get("config")
            
            config_id = StorageConfigRepository.create_config(
                name, storage_type, connection_string,
                json.dumps(config) if config else None
            )
            self.write({"success": True, "data": {"id": config_id}})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def put(self, config_id):
        try:
            data = json.loads(self.request.body)
            name = data.get("name")
            storage_type = data.get("storage_type")
            connection_string = data.get("connection_string")
            config = data.get("config")
            is_active = data.get("is_active")
            
            success = StorageConfigRepository.update_config(
                int(config_id),
                name, storage_type, connection_string,
                json.dumps(config) if config else None,
                is_active
            )
            self.write({"success": success})
        except Exception as e:
            self.write({"success": False, "message": str(e)})
    
    @tornado.web.authenticated
    def delete(self, config_id):
        if StorageConfigRepository.delete_config(int(config_id)):
            self.write({"success": True})
        else:
            self.write({"success": False})


class StorageTestHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            config_id = data.get("config_id")
            config = StorageConfigRepository.get_config_by_id(int(config_id))
            
            if not config:
                self.write({"success": False, "message": "配置不存在"})
                return
            
            # 模拟连接测试
            test_result = True
            test_message = "连接成功（模拟）"
            
            # 更新测试时间
            import datetime
            StorageConfigRepository.update_config(
                int(config_id),
                last_test_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            self.write({"success": test_result, "message": test_message})
        except Exception as e:
            self.write({"success": False, "message": str(e)})


# 页面处理程序
class AdminForgeryDefenseHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("admin_forgery_defense.html")


class AdminStorageManagerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("admin_storage_manager.html")


if __name__ == "__main__":
    app = make_app()
    server = HTTPServer(app)
    server.bind(10086)
    server.start()

    print("====Server 启动成功 =======端口：10086=======", flush=True)
    tornado.ioloop.IOLoop.current().start()
