"""Modules package for feature modules."""

from app.core.module_manager import module_manager

# Import all modules here to register them
from app.modules.auth import AuthModule
from app.modules.user import UserModule  
from app.modules.diary import DiaryModule
from app.modules.media import MediaModule

# Register modules
def register_all_modules():
    """Register all available modules."""
    # Core modules that others depend on
    module_manager.register_module(AuthModule())
    module_manager.register_module(UserModule())
    
    # Feature modules
    module_manager.register_module(MediaModule())
    module_manager.register_module(DiaryModule())

__all__ = ["module_manager", "register_all_modules"] 