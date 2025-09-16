"""
Script to clean up test data from metrics and sync with real users.
"""

import asyncio
import logging
import sys
from typing import Set

import asyncpg

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCleaner:
    """Clean up test data from metrics."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        
    async def get_real_user_ids(self) -> Set[int]:
        """Get all real user IDs from users table."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT id FROM users")
                user_ids = {row['id'] for row in rows}
                logger.info(f"Found {len(user_ids)} real users in database")
                return user_ids
        except Exception as e:
            logger.error(f"Error getting real user IDs: {e}")
            return set()
            
    async def get_current_daily_user_ids(self) -> Set[int]:
        """Get current daily user IDs from metrics."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT metric_text FROM public.bot_metrics WHERE metric_name = 'daily_user_ids'"
                )
                
                if row and row['metric_text']:
                    user_ids_str = row['metric_text']
                    if user_ids_str.strip():
                        user_ids = {
                            int(uid.strip()) 
                            for uid in user_ids_str.split(",") 
                            if uid.strip()
                        }
                        logger.info(f"Found {len(user_ids)} daily user IDs in metrics")
                        return user_ids
                        
                logger.info("No daily user IDs found in metrics")
                return set()
                
        except Exception as e:
            logger.error(f"Error getting daily user IDs: {e}")
            return set()
            
    async def clean_daily_user_ids(self, real_user_ids: Set[int]) -> int:
        """Clean daily user IDs to only include real users."""
        try:
            # Get current daily user IDs
            current_daily_ids = await self.get_current_daily_user_ids()
            
            # Filter to only real users
            cleaned_ids = current_daily_ids.intersection(real_user_ids)
            removed_count = len(current_daily_ids) - len(cleaned_ids)
            
            if removed_count > 0:
                logger.info(f"Removing {removed_count} test/fake user IDs from metrics")
                logger.info(f"Remaining {len(cleaned_ids)} real user IDs")
                
                # Update metrics with cleaned data
                cleaned_ids_str = ",".join(map(str, sorted(cleaned_ids)))
                
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO public.bot_metrics (metric_name, metric_text, updated_at) "
                        "VALUES ($1, $2, CURRENT_TIMESTAMP) "
                        "ON CONFLICT (metric_name) DO UPDATE SET "
                        "metric_text = $2, updated_at = CURRENT_TIMESTAMP",
                        'daily_user_ids',
                        cleaned_ids_str
                    )
                    
                logger.info("Successfully cleaned daily user IDs in metrics")
                return removed_count
            else:
                logger.info("No test data found - all daily user IDs are real users")
                return 0
                
        except Exception as e:
            logger.error(f"Error cleaning daily user IDs: {e}")
            return 0
            
    async def reset_daily_metrics(self) -> None:
        """Reset daily metrics to start fresh."""
        try:
            async with self.pool.acquire() as conn:
                # Reset daily counters
                daily_metrics = [
                    'total_interactions_today',
                    'unique_active_users_today', 
                    'new_users_today',
                    'messages_sent_today',
                    'commands_used_today',
                    'ai_responses_sent_today',
                    'callback_queries_today',
                    'premium_users_active_today'
                ]
                
                for metric_name in daily_metrics:
                    await conn.execute(
                        "SELECT public.set_metric($1, $2)", metric_name, 0
                    )
                    
                # Clear daily user IDs
                await conn.execute(
                    "INSERT INTO public.bot_metrics (metric_name, metric_text, updated_at) "
                    "VALUES ($1, $2, CURRENT_TIMESTAMP) "
                    "ON CONFLICT (metric_name) DO UPDATE SET "
                    "metric_text = $2, updated_at = CURRENT_TIMESTAMP",
                    'daily_user_ids',
                    ''
                )
                
                logger.info("Successfully reset all daily metrics")
                
        except Exception as e:
            logger.error(f"Error resetting daily metrics: {e}")
            
    async def show_metrics_summary(self) -> None:
        """Show current metrics summary."""
        try:
            async with self.pool.acquire() as conn:
                # Get daily user IDs
                daily_ids = await self.get_current_daily_user_ids()
                
                # Get daily counters
                counters = {}
                counter_names = [
                    'total_interactions_today',
                    'unique_active_users_today',
                    'new_users_today', 
                    'messages_sent_today',
                    'commands_used_today'
                ]
                
                for counter_name in counter_names:
                    value = await conn.fetchval("SELECT public.get_metric($1)", counter_name)
                    counters[counter_name] = value or 0
                    
                # Show summary
                print("\n" + "="*50)
                print("📊 CURRENT METRICS SUMMARY")
                print("="*50)
                print(f"Daily User IDs Count: {len(daily_ids)}")
                print(f"Daily User IDs: {sorted(daily_ids) if daily_ids else 'None'}")
                print()
                print("Daily Counters:")
                for name, value in counters.items():
                    print(f"  {name}: {value}")
                print("="*50)
                
        except Exception as e:
            logger.error(f"Error showing metrics summary: {e}")


async def main():
    """Main function to clean metrics."""
    print("🧹 METRICS CLEANER - Removing Test Data")
    print("="*50)
    
    # Database connection
    try:
        pool = await asyncpg.create_pool(
            host="localhost",
            port=5432,
            user="postgres", 
            password="postgres",
            database="lifechat_db",
            min_size=1,
            max_size=5
        )
        
        cleaner = MetricsCleaner(pool)
        
        # Show current state
        print("\n📊 BEFORE CLEANING:")
        await cleaner.show_metrics_summary()
        
        # Get real user IDs
        real_user_ids = await cleaner.get_real_user_ids()
        
        if not real_user_ids:
            print("❌ No real users found in database!")
            return
            
        print(f"\n👥 Found {len(real_user_ids)} real users: {sorted(real_user_ids)}")
        
        # Clean daily user IDs
        removed_count = await cleaner.clean_daily_user_ids(real_user_ids)
        
        if removed_count > 0:
            print(f"\n✅ Removed {removed_count} test/fake user IDs")
        else:
            print("\n✅ No test data found - all user IDs are real")
            
        # Show final state
        print("\n📊 AFTER CLEANING:")
        await cleaner.show_metrics_summary()
        
        # Ask if user wants to reset daily metrics
        print("\n🔄 OPTIONS:")
        print("1. Keep current daily counters")
        print("2. Reset all daily metrics to start fresh")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            await cleaner.reset_daily_metrics()
            print("✅ All daily metrics reset to start fresh")
            print("\n📊 FINAL STATE:")
            await cleaner.show_metrics_summary()
        else:
            print("✅ Daily counters kept as is")
            
        print("\n🎉 METRICS CLEANING COMPLETED!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")
    finally:
        if 'pool' in locals():
            await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
