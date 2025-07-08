"""
Клиент для работы с Supabase
"""
from typing import Optional
from supabase import create_client, Client
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Обертка над Supabase клиентом"""
    
    def __init__(self):
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Получить клиент Supabase"""
        if self._client is None:
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key
            )
            logger.info("Supabase client initialized")
        return self._client
    
    async def test_connection(self) -> bool:
        """Проверить соединение с Supabase"""
        try:
            # Простой запрос для проверки соединения
            result = self.client.table("users").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def get_storage_client(self):
        """Получить клиент для работы с файлами"""
        return self.client.storage
    
    def get_table(self, table_name: str):
        """Получить таблицу для работы"""
        return self.client.table(table_name)


# Глобальный экземпляр клиента
_supabase_client = SupabaseClient()


def get_supabase_client() -> SupabaseClient:
    """Получить экземпляр Supabase клиента"""
    return _supabase_client 