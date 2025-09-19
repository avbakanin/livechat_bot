#!/usr/bin/env python3
"""
Simple script to initialize language column for existing users.
This sets default language based on user's first_name/last_name.
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from shared.constants import DATABASE_CONFIG


async def init_languages():
    """Initialize language column for existing users."""
    print("Initializing language preferences for existing users...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            database=DATABASE_CONFIG["database"]
        )
        
        print("Connected to database successfully.")
        
        # Update users with NULL language to have default language based on their names
        result = await conn.fetch("""
            UPDATE public.users 
            SET language = CASE 
                WHEN first_name ~ '^[А-Яа-я]' OR last_name ~ '^[А-Яа-я]' THEN 'ru'
                ELSE 'en'
            END
            WHERE language IS NULL;
        """)
        
        # Get count of updated users
        updated_count = await conn.fetchval("""
            SELECT COUNT(*) FROM public.users 
            WHERE language IS NOT NULL;
        """)
        
        print(f"✅ Updated language preferences for {updated_count} users.")
        
        # Show language distribution
        lang_dist = await conn.fetch("""
            SELECT language, COUNT(*) as count 
            FROM public.users 
            GROUP BY language 
            ORDER BY count DESC;
        """)
        print("\nLanguage distribution:")
        for row in lang_dist:
            print(f"  {row['language']}: {row['count']} users")
        
        await conn.close()
        print("\n🎉 Language initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_languages())
