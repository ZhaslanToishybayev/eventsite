"""
PostgreSQL specific migrations and optimizations
"""

from django.db import migrations, models
import django.contrib.postgres.fields as postgres_fields
import django.contrib.postgres.indexes as postgres_indexes
import django.contrib.postgres.operations as postgres_operations


class Migration(migrations.Migration):
    """PostgreSQL optimization migrations"""

    dependencies = [
        ('clubs', '0001_initial'),  # Зависит от ваших текущих миграций
        ('ai_consultant', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # UUID индексы для оптимизации
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_uuid ON clubs_club (id);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_uuid;"
        ),

        # Индексы для часто используемых полей
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_members_count_desc ON clubs_club (members_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_members_count_desc;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_likes_count_desc ON clubs_club (likes_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_likes_count_desc;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_created_at_desc ON clubs_club (created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_created_at_desc;"
        ),

        # Композитные индексы для популярных запросов
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_active_featured ON clubs_club (is_active, is_featured, members_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_active_featured;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_category_active ON clubs_club (category_id, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_category_active;"
        ),

        # Индексы для AI чата
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chatsession_created_desc ON ai_consultant_chatsession (created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_chatsession_created_desc;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chatmessage_session_created ON ai_consultant_chatmessage (session_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_chatmessage_session_created;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_phone_email ON accounts_user (phone, email);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_phone_email;"
        ),

        # Полнотекстовый поиск для клубов (PostgreSQL)
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_search
            ON clubs_club USING gin(to_tsvector('russian', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(tags, '')));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_club_search;"
        ),

        # Индексы для рекомендательной системы
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_club_recommendation_score ON clubs_club (recommendation_score DESC, members_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_club_recommendation_score;"
        ),

        # Индексы для JOIN запросов
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clubmember_user_club ON clubs_club_members (user_id, club_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_clubmember_user_club;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clublike_user_club ON clubs_club_likes (user_id, club_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_clublike_user_club;"
        ),

        # Частичные индексы для эффективности
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_active_clubs ON clubs_club (created_at DESC) WHERE is_active = true;",
            reverse_sql="DROP INDEX IF EXISTS idx_active_clubs;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_private_clubs ON clubs_club (created_at DESC) WHERE is_private = true;",
            reverse_sql="DROP INDEX IF EXISTS idx_private_clubs;"
        ),

        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_featured_clubs ON clubs_club (members_count DESC) WHERE is_featured = true;",
            reverse_sql="DROP INDEX IF EXISTS idx_featured_clubs;"
        ),
    ]


class TriggersMigration(migrations.Migration):
    """Triggers для автоматического обновления счетчиков"""

    dependencies = [
        Migration,
    ]

    operations = [
        # Триггер для автоматического обновления members_count
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION update_club_members_count()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE clubs_club SET members_count = members_count + 1 WHERE id = NEW.club_id;
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE clubs_club SET members_count = members_count - 1 WHERE id = OLD.club_id;
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_club_members_count ON clubs_club_members;
            CREATE TRIGGER trigger_update_club_members_count
                AFTER INSERT OR DELETE ON clubs_club_members
                FOR EACH ROW EXECUTE FUNCTION update_club_members_count();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS trigger_update_club_members_count ON clubs_club_members;
                DROP FUNCTION IF EXISTS update_club_members_count();
            """
        ),

        # Триггер для автоматического обновления likes_count
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION update_club_likes_count()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE clubs_club SET likes_count = likes_count + 1 WHERE id = NEW.club_id;
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE clubs_club SET likes_count = likes_count - 1 WHERE id = OLD.club_id;
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trigger_update_club_likes_count ON clubs_club_likes;
            CREATE TRIGGER trigger_update_club_likes_count
                AFTER INSERT OR DELETE ON clubs_club_likes
                FOR EACH ROW EXECUTE FUNCTION update_club_likes_count();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS trigger_update_club_likes_count ON clubs_club_likes;
                DROP FUNCTION IF EXISTS update_club_likes_count();
            """
        ),

        # Функция для поиска клубов
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION search_clubs(query_text TEXT, limit_count INTEGER DEFAULT 10)
            RETURNS TABLE(id UUID, name VARCHAR, description TEXT, members_count INTEGER, rank REAL) AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    c.id,
                    c.name,
                    c.description,
                    c.members_count,
                    ts_rank(search_vector, plainto_tsquery('russian', query_text)) as rank
                FROM (
                    SELECT
                        c.*,
                        to_tsvector('russian', c.name || ' ' || COALESCE(c.description, '') || ' ' || COALESCE(c.tags, '')) as search_vector
                    FROM clubs_club c
                    WHERE c.is_active = true
                ) c
                WHERE search_vector @@ plainto_tsquery('russian', query_text)
                ORDER BY rank DESC, c.members_count DESC
                LIMIT limit_count;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS search_clubs;"
        ),
    ]