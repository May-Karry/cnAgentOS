from app.models.db import init_db, get_connection
from app.models.system import ModelRepository

def init_default_model():
    init_db()
    
    models = ModelRepository.get_all_models()
    if len(models) == 0:
        model_id = ModelRepository.create_model(
            name="DeepSeek V3",
            model_name="deepseek-v3",
            api_key="sk-aigc-d6a0ab7b85e6dcb24bd8bbf43dac1bb22295beab",
            base_url="https://aigc-api.aitoolcore.com/api/v1",
            is_default=True
        )
        if model_id > 0:
            print("已创建默认模型：DeepSeek V3")
        else:
            print("创建默认模型失败")
    else:
        print(f"已存在 {len(models)} 个模型")

if __name__ == "__main__":
    init_default_model()
