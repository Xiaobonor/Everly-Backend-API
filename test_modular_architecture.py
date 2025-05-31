#!/usr/bin/env python3
"""Test script for the new modular architecture."""

import asyncio
import logging
from app.modules import register_all_modules, module_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_modular_architecture():
    """Test the modular architecture functionality."""
    
    print("🚀 測試模塊化架構")
    print("=" * 50)
    
    # Test 1: Module Registration
    print("\n📦 測試模塊註冊...")
    register_all_modules()
    modules = module_manager.list_modules()
    print(f"✅ 已註冊 {len(modules)} 個模塊: {', '.join(modules)}")
    
    # Test 2: Module Information
    print("\n📋 模塊詳細信息:")
    for info in module_manager.get_modules_info():
        status = "✅ 已初始化" if info["initialized"] else "⏳ 未初始化"
        deps = f" (依賴: {', '.join(info['dependencies'])})" if info["dependencies"] else ""
        print(f"  • {info['name']} v{info['version']}: {info['description']}{deps} - {status}")
    
    # Test 3: Dependency Order
    print("\n🔗 測試依賴順序...")
    try:
        await module_manager._check_dependencies()
        init_order = module_manager._get_initialization_order()
        print(f"✅ 依賴檢查通過，初始化順序: {' → '.join(init_order)}")
    except Exception as e:
        print(f"❌ 依賴檢查失敗: {e}")
        return
    
    # Test 4: Router Creation
    print("\n🛣️  測試路由創建...")
    try:
        # Mock initialization for router test
        for module in module_manager.modules.values():
            module._is_initialized = True
        
        main_router = module_manager.create_main_router()
        print(f"✅ 主路由創建成功，包含 {len(main_router.routes)} 個路由")
        
        # List routes
        for route in main_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'ALL'
                print(f"  • {methods} {route.path}")
    except Exception as e:
        print(f"❌ 路由創建失敗: {e}")
        return
    
    # Test 5: Health Check
    print("\n🏥 測試健康檢查...")
    try:
        health = await module_manager.health_check_all()
        print(f"✅ 整體狀態: {health['status']}")
        print(f"  總模塊數: {health['total_modules']}")
        for module_name, module_health in health['modules'].items():
            status_icon = "✅" if module_health['status'] == 'healthy' else "❌"
            print(f"  {status_icon} {module_name}: {module_health['status']}")
    except Exception as e:
        print(f"❌ 健康檢查失敗: {e}")
        return
    
    print("\n🎉 模塊化架構測試完成！")
    print("=" * 50)
    print("✨ 新架構特點:")
    print("  • 🔧 模塊化設計 - 每個功能獨立封裝")
    print("  • 🔗 依賴管理 - 自動處理模塊間依賴")
    print("  • 🔄 生命週期控制 - 統一的初始化和清理")
    print("  • 🛣️  路由自動註冊 - 無需手動配置")
    print("  • 🏥 健康監控 - 實時模塊狀態檢查")
    print("  • 🚀 插件式開發 - 新功能只需創建新模塊")

if __name__ == "__main__":
    asyncio.run(test_modular_architecture()) 