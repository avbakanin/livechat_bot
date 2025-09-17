# app/shared/security/rate_limiter.py
"""
Улучшенная система rate limiting и защиты от спама.
"""

import time
from typing import Dict
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class RateLimitRule:
    """Правило ограничения скорости."""
    max_requests: int
    time_window: int  # в секундах
    block_duration: int = 300  # время блокировки в секундах


class RateLimiter:
    """Улучшенный rate limiter с различными правилами."""
    
    def __init__(self):
        self.user_requests: Dict[int, deque] = defaultdict(deque)
        self.user_blocks: Dict[int, float] = {}
        self.rules: Dict[str, RateLimitRule] = {
            "message": RateLimitRule(max_requests=30, time_window=60, block_duration=300),
            "command": RateLimitRule(max_requests=10, time_window=60, block_duration=180),
            "callback": RateLimitRule(max_requests=20, time_window=60, block_duration=120),
            "language_change": RateLimitRule(max_requests=5, time_window=300, block_duration=600),
        }
    
    def is_allowed(self, user_id: int, action_type: str) -> Dict[str, Any]:
        """
        Проверяет, разрешено ли действие пользователю.
        
        Args:
            user_id: ID пользователя
            action_type: Тип действия
            
        Returns:
            Словарь с результатом проверки
        """
        current_time = time.time()
        
        # Проверяем, не заблокирован ли пользователь
        if user_id in self.user_blocks:
            block_until = self.user_blocks[user_id]
            if current_time < block_until:
                remaining_block = block_until - current_time
                return {
                    "allowed": False,
                    "reason": "blocked",
                    "block_until": block_until,
                    "remaining_block": remaining_block,
                    "message": f"Вы заблокированы на {int(remaining_block)} секунд"
                }
            else:
                # Блокировка истекла
                del self.user_blocks[user_id]
        
        # Получаем правило для типа действия
        rule = self.rules.get(action_type)
        if not rule:
            return {"allowed": True, "reason": "no_rule"}
        
        # Очищаем старые запросы
        user_queue = self.user_requests[user_id]
        while user_queue and user_queue[0] <= current_time - rule.time_window:
            user_queue.popleft()
        
        # Проверяем лимит
        if len(user_queue) >= rule.max_requests:
            # Блокируем пользователя
            self.user_blocks[user_id] = current_time + rule.block_duration
            
            return {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "requests_count": len(user_queue),
                "max_requests": rule.max_requests,
                "time_window": rule.time_window,
                "block_duration": rule.block_duration,
                "message": f"Слишком много запросов. Лимит: {rule.max_requests} за {rule.time_window} сек"
            }
        
        # Добавляем текущий запрос
        user_queue.append(current_time)
        
        return {
            "allowed": True,
            "reason": "allowed",
            "requests_count": len(user_queue),
            "max_requests": rule.max_requests,
            "remaining_requests": rule.max_requests - len(user_queue)
        }
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получает статистику пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Статистика пользователя
        """
        current_time = time.time()
        
        stats = {
            "user_id": user_id,
            "is_blocked": user_id in self.user_blocks,
            "block_until": self.user_blocks.get(user_id),
            "requests_by_type": {}
        }
        
        if stats["is_blocked"]:
            stats["remaining_block"] = self.user_blocks[user_id] - current_time
        
        # Статистика по типам действий
        user_queue = self.user_requests[user_id]
        for action_type, rule in self.rules.items():
            # Подсчитываем запросы за последнее окно времени
            recent_requests = sum(1 for req_time in user_queue 
                                if req_time > current_time - rule.time_window)
            
            stats["requests_by_type"][action_type] = {
                "recent_requests": recent_requests,
                "max_requests": rule.max_requests,
                "time_window": rule.time_window,
                "remaining": rule.max_requests - recent_requests
            }
        
        return stats
    
    def unblock_user(self, user_id: int) -> bool:
        """
        Разблокирует пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если пользователь был заблокирован, False иначе
        """
        if user_id in self.user_blocks:
            del self.user_blocks[user_id]
            return True
        return False
    
    def clear_user_history(self, user_id: int) -> None:
        """
        Очищает историю запросов пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.user_requests:
            del self.user_requests[user_id]
        
        if user_id in self.user_blocks:
            del self.user_blocks[user_id]
    
    def get_global_stats(self) -> Dict[str, Any]:
        """
        Получает глобальную статистику rate limiter.
        
        Returns:
            Глобальная статистика
        """
        current_time = time.time()
        
        total_users = len(self.user_requests)
        blocked_users = len(self.user_blocks)
        
        # Подсчитываем активных пользователей (с запросами за последние 5 минут)
        active_users = 0
        for user_queue in self.user_requests.values():
            if any(req_time > current_time - 300 for req_time in user_queue):
                active_users += 1
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "blocked_users": blocked_users,
            "rules": {name: {
                "max_requests": rule.max_requests,
                "time_window": rule.time_window,
                "block_duration": rule.block_duration
            } for name, rule in self.rules.items()}
        }


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()
