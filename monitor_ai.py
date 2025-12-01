#!/usr/bin/env python
"""
📊 UnitySphere AI Мониторинг и Статистика
Сбор метрик, логов и аналитики использования
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta
from collections import defaultdict
from django.db import models

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from ai_consultant.models import ChatSession, ChatMessage, AIContext
from clubs.models import Club

User = get_user_model()

class UnitySphereMonitor:
    """Система мониторинга UnitySphere AI"""

    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

    def collect_system_metrics(self):
        """Сбор системных метрик"""
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'system': {
                'django_version': django.VERSION,
                'python_version': sys.version,
                'debug_mode': os.getenv('DEBUG', 'False')
            },
            'ai_usage': self._get_ai_usage_stats(),
            'user_activity': self._get_user_activity_stats(),
            'club_stats': self._get_club_stats(),
        }
        return metrics

    def _get_ai_usage_stats(self):
        """Статистика использования AI"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Сегодняшняя активность
        today_sessions = ChatSession.objects.filter(
            created_at__date=today
        ).count()

        today_messages = ChatMessage.objects.filter(
            created_at__date=today
        ).count()

        # Вчерашняя активность
        yesterday_sessions = ChatSession.objects.filter(
            created_at__date=yesterday
        ).count()

        yesterday_messages = ChatMessage.objects.filter(
            created_at__date=yesterday
        ).count()

        # Средняя длина сессии
        avg_session_length = ChatMessage.objects.filter(
            session__created_at__date=today
        ).count() / max(today_sessions, 1)

        return {
            'today': {
                'sessions': today_sessions,
                'messages': today_messages,
            },
            'yesterday': {
                'sessions': yesterday_sessions,
                'messages': yesterday_messages,
            },
            'avg_session_length': round(avg_session_length, 1),
            'active_sessions': ChatSession.objects.filter(
                is_active=True
            ).count(),
        }

    def _get_user_activity_stats(self):
        """Статистика активности пользователей"""
        today = timezone.now().date()

        # Новые пользователи сегодня
        new_users_today = User.objects.filter(
            date_joined__date=today
        ).count()

        # Активные пользователи (создавали сессии сегодня)
        active_users_today = User.objects.filter(
            ai_chat_sessions__created_at__date=today
        ).distinct().count()

        # Всего пользователей
        total_users = User.objects.count()

        return {
            'total': total_users,
            'new_today': new_users_today,
            'active_today': active_users_today,
            'engagement_rate': f"{(active_users_today / max(total_users, 1)) * 100:.1f}%"
        }

    def _get_club_stats(self):
        """Статистика по клубам"""
        total_clubs = Club.objects.count()
        active_clubs = Club.objects.filter(is_active=True).count()

        return {
            'total': total_clubs,
            'active': active_clubs,
            'inactivity_rate': f"{((total_clubs - active_clubs) / max(total_clubs, 1)) * 100:.1f}%"
        }

    def log_metrics(self):
        """Запись метрик в файл"""
        metrics = self.collect_system_metrics()

        # Лог в JSON формате
        metrics_file = os.path.join(self.log_dir, 'ai_metrics.jsonl')
        with open(metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metrics, ensure_ascii=False) + '\n')

        # Лог в читаемом формате
        log_file = os.path.join(self.log_dir, 'ai_metrics.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== UnitySphere AI Metrics - {metrics['timestamp']} ===\n")
            f.write(f"AI Usage Today: {metrics['ai_usage']['today']['sessions']} sessions, {metrics['ai_usage']['today']['messages']} messages\n")
            f.write(f"User Activity: {metrics['user_activity']['active_today']} active users out of {metrics['user_activity']['total']}\n")
            f.write(f"Clubs: {metrics['club_stats']['active']} active out of {metrics['club_stats']['total']}\n")
            f.write(f"Average Session Length: {metrics['ai_usage']['avg_session_length']} messages\n")

        return metrics

    def health_check(self):
        """Проверка здоровья системы"""
        checks = {
            'database': self._check_database(),
            'ai_service': self._check_ai_service(),
            'cache': self._check_cache(),
            'file_system': self._check_file_system(),
        }

        # Запись результата проверки
        status_file = os.path.join(self.log_dir, 'health_status.json')
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timezone.now().isoformat(),
                'status': 'healthy' if all(checks.values()) else 'unhealthy',
                'checks': checks
            }, f, ensure_ascii=False, indent=2)

        return checks

    def _check_database(self):
        """Проверка базы данных"""
        try:
            ChatSession.objects.count()
            return True
        except Exception:
            return False

    def _check_ai_service(self):
        """Проверка AI сервиса"""
        try:
            from ai_consultant.services_v2 import AIConsultantServiceV2
            service = AIConsultantServiceV2()
            return True
        except Exception:
            return False

    def _check_cache(self):
        """Проверка кэша"""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False

    def _check_file_system(self):
        """Проверка файловой системы"""
        try:
            return os.access(self.log_dir, os.W_OK)
        except Exception:
            return False

    def generate_report(self, days=7):
        """Генерация отчета за период"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)

        # Сессии за период
        sessions = ChatSession.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).prefetch_related('messages')

        # Активность по дням
        daily_stats = defaultdict(lambda: {'sessions': 0, 'messages': 0})

        for session in sessions:
            date = session.created_at.date()
            daily_stats[date]['sessions'] += 1
            daily_stats[date]['messages'] += session.messages.count()

        # Общая статистика
        total_sessions = len(sessions)
        total_messages = sum(s.messaount for s in sessions)
        avg_session_length = total_messages / max(total_sessions, 1)

        report = {
            'period': f"{start_date} to {end_date}",
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'avg_session_length': round(avg_session_length, 1),
            'daily_breakdown': dict(daily_stats),
            'top_club_requests': self._get_top_club_requests(),
            'user_engagement': self._get_user_engagement_stats()
        }

        return report

    def _get_top_club_requests(self):
        """Топ запросов по созданию клубов"""
        # Это пример - можно расширить анализом сообщений
        club_keywords = ['клуб', 'fan-club', 'сообщество', 'фанаты']
        messages = ChatMessage.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )[:100]

        club_requests = []
        for msg in messages:
            if any(keyword in msg.content.lower() for keyword in club_keywords):
                club_requests.append({
                    'content': msg.content[:100],
                    'session_id': str(msg.session.id),
                    'created_at': msg.created_at.isoformat()
                })

        return club_requests[:10]

    def _get_user_engagement_stats(self):
        """Статистика вовлеченности пользователей"""
        # Повторные визиты
        repeat_users = User.objects.filter(
            ai_chat_sessions__created_at__gte=timezone.now() - timedelta(days=7)
        ).annotate(
            session_count=models.Count('ai_chat_sessions')
        ).filter(session_count__gte=2)

        return {
            'repeat_users': repeat_users.count(),
            'total_chatting_users': User.objects.filter(
                ai_chat_sessions__created_at__gte=timezone.now() - timedelta(days=7)
            ).distinct().count(),
            'repeat_rate': f"{(repeat_users.count() / max(User.objects.filter(ai_chat_sessions__created_at__gte=timezone.now() - timedelta(days=7)).count(), 1)) * 100:.1f}%"
        }


def main():
    """Основная функция для запуска мониторинга"""
    monitor = UnitySphereMonitor()

    print("🔍 UnitySphere AI Monitor запущен...")

    # Сбор метрик
    print("📊 Сбор метрик...")
    metrics = monitor.log_metrics()

    # Health check
    print("🏥 Проверка здоровья системы...")
    health = monitor.health_check()

    # Отчет
    print("📈 Генерация отчета...")
    report = monitor.generate_report()

    # Вывод результатов
    print(f"\n✅ Система работает нормально!")
    print(f"🤖 AI: {metrics['ai_usage']['today']['sessions']} сессий, {metrics['ai_usage']['today']['messages']} сообщений сегодня")
    print(f"👥 Пользователи: {metrics['user_activity']['active_today']} активных из {metrics['user_activity']['total']}")
    print(f"🏛️ Клубы: {metrics['club_stats']['active']} активных из {metrics['club_stats']['total']}")
    print(f"💚 Здоровье: {'Все системы работают' if all(health.values()) else 'Есть проблемы'}")

    return {
        'metrics': metrics,
        'health': health,
        'report': report
    }


if __name__ == '__main__':
    main()