# 🏗️ 模塊化架構說明

## 概述

Everly 後端採用了全新的模塊化架構設計，每個功能模塊都是獨立的、可插拔的組件。這種設計大幅提升了代碼的可維護性、可擴展性和可測試性。

## 🎯 設計目標

- **模塊化**: 每個功能獨立封裝，互不干擾
- **可擴展**: 新功能只需創建新模塊，無需修改現有代碼
- **依賴管理**: 自動處理模塊間的依賴關係
- **生命週期控制**: 統一的初始化和清理機制
- **插件式開發**: 支持動態加載和卸載模塊

## 📁 目錄結構

```
backend/
├── app/
│   ├── core/                    # 核心系統
│   │   ├── base_module.py      # 基礎模塊類
│   │   ├── module_manager.py   # 模塊管理器
│   │   └── ...
│   ├── modules/                # 功能模塊
│   │   ├── auth/              # 認證模塊
│   │   │   ├── api/           # API 路由
│   │   │   ├── services/      # 業務邏輯
│   │   │   ├── schemas/       # 數據驗證
│   │   │   ├── config.py      # 模塊配置
│   │   │   └── module.py      # 模塊主類
│   │   ├── user/              # 用戶管理模塊
│   │   ├── diary/             # 日記功能模塊
│   │   ├── media/             # 媒體處理模塊
│   │   └── __init__.py        # 模塊註冊
│   └── main.py                # 主應用程序
```

## 🧩 核心組件

### BaseModule (基礎模塊類)

所有功能模塊都繼承自 `BaseModule`，提供統一的接口：

```python
class BaseModule(ABC):
    def __init__(self, name, version, description, dependencies):
        # 模塊基本信息
    
    @abstractmethod
    def get_router(self) -> APIRouter:
        # 返回模塊的 FastAPI 路由
    
    @abstractmethod
    async def initialize(self, db, redis):
        # 模塊初始化邏輯
    
    @abstractmethod
    async def cleanup(self):
        # 模塊清理邏輯
```

### ModuleManager (模塊管理器)

負責管理所有模塊的生命週期：

- 模塊註冊和發現
- 依賴關係檢查
- 初始化順序控制
- 路由自動註冊
- 健康狀態監控

## 📦 現有模塊

### 1. Auth Module (認證模塊)
- **功能**: 用戶認證和授權
- **依賴**: 無
- **API**: `/auth/google`, `/auth/me`

### 2. User Module (用戶模塊)
- **功能**: 用戶資料管理、頭像上傳、偏好設定
- **依賴**: auth
- **API**: `/users/me`, `/users/me/profile-picture`, `/users/me/preferences`

### 3. Media Module (媒體模塊)
- **功能**: 文件上傳和管理
- **依賴**: auth
- **狀態**: 基礎框架已完成

### 4. Diary Module (日記模塊)
- **功能**: 日記條目管理
- **依賴**: auth, users
- **狀態**: 基礎框架已完成

## 🚀 如何添加新模塊

### 1. 創建模塊目錄結構

```bash
mkdir -p app/modules/your_module/{api,services,schemas}
```

### 2. 創建模塊主類

```python
# app/modules/your_module/module.py
from app.core.base_module import BaseModule

class YourModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="your_module",
            version="1.0.0",
            description="Your module description",
            dependencies=["auth"]  # 依賴的其他模塊
        )
    
    def get_router(self) -> APIRouter:
        from app.modules.your_module.api import router
        return router
    
    async def initialize(self, db, redis):
        # 初始化邏輯
        self.logger.info("Your module initialized")
    
    async def cleanup(self):
        # 清理邏輯
        self.logger.info("Your module cleaned up")
```

### 3. 創建 API 路由

```python
# app/modules/your_module/api/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint")
async def your_endpoint():
    return {"message": "Hello from your module!"}
```

### 4. 註冊模塊

```python
# app/modules/__init__.py
from app.modules.your_module import YourModule

def register_all_modules():
    # ... 其他模塊
    module_manager.register_module(YourModule())
```

### 5. 完成！

新模塊會自動：
- 按依賴順序初始化
- 註冊 API 路由到 `/your_module/*`
- 包含在健康檢查中
- 支持生命週期管理

## 🔧 配置管理

每個模塊都有自己的配置類：

```python
# app/modules/your_module/config.py
class YourModuleConfig:
    SETTING_1: str = "default_value"
    SETTING_2: int = 100
    
    @classmethod
    def from_env(cls):
        config = cls()
        config.SETTING_1 = os.getenv("YOUR_MODULE_SETTING_1", config.SETTING_1)
        return config
```

## 🏥 健康檢查

每個模塊都可以實現自定義的健康檢查：

```python
async def health_check(self) -> dict:
    base_health = await super().health_check()
    
    # 添加模塊特定的健康檢查
    module_health = {
        "database_connected": self.check_database(),
        "external_service_available": await self.check_external_service()
    }
    
    base_health.update(module_health)
    return base_health
```

## 🧪 測試

運行模塊化架構測試：

```bash
python test_modular_architecture.py
```

## 📈 優勢

1. **可維護性**: 每個模塊職責單一，易於理解和修改
2. **可擴展性**: 新功能通過新模塊添加，不影響現有代碼
3. **可測試性**: 模塊間解耦，便於單元測試和集成測試
4. **可重用性**: 模塊可以在不同項目間重用
5. **團隊協作**: 不同團隊可以並行開發不同模塊
6. **部署靈活性**: 可以選擇性部署特定模塊

## 🔮 未來計劃

- [ ] 實現動態模塊加載/卸載
- [ ] 添加模塊間事件通信機制
- [ ] 實現模塊配置熱重載
- [ ] 添加模塊性能監控
- [ ] 支持模塊版本管理和升級

---

*這個模塊化架構為 Everly 提供了堅實的技術基礎，支持快速迭代和長期維護。*