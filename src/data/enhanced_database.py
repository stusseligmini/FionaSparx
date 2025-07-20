import sqlite3
import json
import logging
from datetime import datetime, timedelta
import io
import statistics
from PIL import Image

logger = logging.getLogger(__name__)

class EnhancedDatabase:
    """Forbedret database med avanserte funksjoner og analytics"""
    
    def __init__(self, config):
        self.db_path = config.get("path", "data/fiona_sparx.db")
        self.backup_enabled = config.get("backup_enabled", True)
        self.retention_days = config.get("retention_days", 30)
        self.setup_database()
        logger.info(f"🗄️  Enhanced Database initialisert: {self.db_path}")
    
    def setup_database(self):
        """Opprett forbedret database med alle tabeller"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hovedtabell for innhold
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                type TEXT,
                caption TEXT,
                image_data BLOB,
                metadata TEXT,
                theme TEXT,
                created_at TIMESTAMP,
                published BOOLEAN DEFAULT FALSE,
                platforms TEXT,
                performance TEXT
            )
        ''')
        
        # Tabell for publiseringshistorikk
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publish_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                platform TEXT,
                published_at TIMESTAMP,
                engagement_data TEXT,
                success BOOLEAN,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        # Tabell for ytelsesdata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                platform TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                recorded_at TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        # Tabell for AI-læring og trender
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme TEXT,
                prompt_data TEXT,
                performance_score REAL,
                engagement_metrics TEXT,
                trends_data TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Tabell for daglig statistikk
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                content_created INTEGER DEFAULT 0,
                content_published INTEGER DEFAULT 0,
                total_engagement INTEGER DEFAULT 0,
                best_performing_theme TEXT,
                notes TEXT
            )
        ''')
        
        # Tabell for brukerinnstillinger og konfigurering
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
        ''')
        
        # Indekser for bedre ytelse
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_created_at ON content (created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_theme ON content (theme)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_content_id ON performance_metrics (content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_publish_history_platform ON publish_history (platform)')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database tabeller opprettet/oppdatert")
    
    def save_content(self, content_item):
        """Lagre innhold med utvidet metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Konverter bilde til bytes
            image_bytes = None
            if content_item.get("image"):
                img_byte_arr = io.BytesIO()
                content_item["image"].save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content 
                (id, type, caption, image_data, metadata, theme, created_at, published, platforms, performance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_item["id"],
                content_item.get("type", "image"),
                content_item.get("caption", ""),
                image_bytes,
                json.dumps(content_item.get("metadata", {})),
                content_item.get("theme", "lifestyle"),
                content_item.get("created_at", datetime.now()),
                content_item.get("published", False),
                json.dumps(content_item.get("platforms", {})),
                json.dumps(content_item.get("performance", {}))
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Lagret innhold: {content_item['id']}")
            
        except Exception as e:
            logger.error(f"❌ Feil ved lagring av innhold: {e}")
    
    def get_ready_to_publish_content(self, limit=10):
        """Hent innhold klart for publisering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM content 
            WHERE published = FALSE 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        content_items = []
        
        for row in rows:
            item = self._row_to_content_item(row)
            content_items.append(item)
        
        conn.close()
        return content_items
    
    def mark_as_published(self, content_id, platform):
        """Marker som publisert med utvidet tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Oppdater content-tabellen
            cursor.execute('SELECT platforms FROM content WHERE id = ?', (content_id,))
            result = cursor.fetchone()
            
            if result:
                platforms = json.loads(result[0] or '{}')
                platforms[platform] = {
                    "published_at": datetime.now().isoformat(),
                    "status": "published"
                }
                
                cursor.execute('''
                    UPDATE content 
                    SET published = TRUE, platforms = ?
                    WHERE id = ?
                ''', (json.dumps(platforms), content_id))
                
                # Legg til i publiseringshistorikk
                cursor.execute('''
                    INSERT INTO publish_history 
                    (content_id, platform, published_at, success)
                    VALUES (?, ?, ?, ?)
                ''', (content_id, platform, datetime.now(), True))
                
                conn.commit()
                logger.info(f"✅ Markert som publisert: {content_id} på {platform}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Feil ved markering som publisert: {e}")
    
    def record_performance_metrics(self, content_id, platform, metrics):
        """Registrer ytelsesmålinger"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Beregn engagement rate
            total_interactions = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)
            views = metrics.get("views", 1)  # Unngå divisjon med null
            engagement_rate = (total_interactions / views) * 100 if views > 0 else 0
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (content_id, platform, likes, comments, shares, views, engagement_rate, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_id,
                platform,
                metrics.get("likes", 0),
                metrics.get("comments", 0),
                metrics.get("shares", 0),
                metrics.get("views", 0),
                engagement_rate,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Registrerte metrics for {content_id}: {engagement_rate:.2f}% engagement")
            
        except Exception as e:
            logger.error(f"❌ Feil ved registrering av metrics: {e}")
    
    def get_performance_analytics(self, days=30):
        """Hent omfattende ytelsesanalyse"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # Hent grunnleggende metrics
            cursor.execute('''
                SELECT 
                    c.theme,
                    AVG(pm.engagement_rate) as avg_engagement,
                    COUNT(*) as post_count,
                    AVG(pm.likes) as avg_likes,
                    AVG(pm.comments) as avg_comments,
                    AVG(pm.shares) as avg_shares
                FROM content c
                JOIN performance_metrics pm ON c.id = pm.content_id
                WHERE c.created_at >= ?
                GROUP BY c.theme
                ORDER BY avg_engagement DESC
            ''', (since_date,))
            
            theme_performance = cursor.fetchall()
            
            # Hent plattformanalyse
            cursor.execute('''
                SELECT 
                    platform,
                    AVG(engagement_rate) as avg_engagement,
                    COUNT(*) as post_count,
                    SUM(likes + comments + shares) as total_interactions
                FROM performance_metrics
                WHERE recorded_at >= ?
                GROUP BY platform
                ORDER BY avg_engagement DESC
            ''', (since_date,))
            
            platform_performance = cursor.fetchall()
            
            # Hent trenddata
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as posts_created,
                    theme,
                    AVG(pm.engagement_rate) as daily_engagement
                FROM content c
                LEFT JOIN performance_metrics pm ON c.id = pm.content_id
                WHERE c.created_at >= ?
                GROUP BY DATE(created_at), theme
                ORDER BY date DESC
            ''', (since_date,))
            
            trend_data = cursor.fetchall()
            
            conn.close()
            
            analytics = {
                "theme_performance": [
                    {
                        "theme": row[0],
                        "avg_engagement": row[1] or 0,
                        "post_count": row[2],
                        "avg_likes": row[3] or 0,
                        "avg_comments": row[4] or 0,
                        "avg_shares": row[5] or 0
                    }
                    for row in theme_performance
                ],
                "platform_performance": [
                    {
                        "platform": row[0],
                        "avg_engagement": row[1] or 0,
                        "post_count": row[2],
                        "total_interactions": row[3] or 0
                    }
                    for row in platform_performance
                ],
                "trend_data": [
                    {
                        "date": row[0],
                        "posts_created": row[1],
                        "theme": row[2],
                        "daily_engagement": row[3] or 0
                    }
                    for row in trend_data
                ],
                "analysis_period": f"Siste {days} dager",
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Feil ved henting av analytics: {e}")
            return {}
    
    def get_recent_performance_data(self, days=7):
        """Hent nylig ytelsesdata for trendanalyse"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    c.id,
                    c.theme,
                    c.metadata,
                    AVG(pm.engagement_rate) as engagement_rate,
                    SUM(pm.likes + pm.comments + pm.shares) as total_interactions
                FROM content c
                LEFT JOIN performance_metrics pm ON c.id = pm.content_id
                WHERE c.created_at >= ?
                GROUP BY c.id
                ORDER BY engagement_rate DESC
            ''', (since_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "theme": row[1],
                    "metadata": json.loads(row[2] or '{}'),
                    "engagement_rate": row[3] or 0,
                    "total_interactions": row[4] or 0
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"❌ Feil ved henting av nylig data: {e}")
            return []
    
    def analyze_yesterday_performance(self):
        """Analyser gårsdagens ytelse"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hent gårsdagens data
            cursor.execute('''
                SELECT 
                    c.theme,
                    AVG(pm.engagement_rate) as avg_engagement,
                    COUNT(*) as post_count
                FROM content c
                LEFT JOIN performance_metrics pm ON c.id = pm.content_id
                WHERE DATE(c.created_at) = ?
                GROUP BY c.theme
                ORDER BY avg_engagement DESC
            ''', (yesterday_str,))
            
            results = cursor.fetchall()
            
            if results:
                best_theme = results[0][0]
                best_engagement = results[0][1] or 0
                total_posts = sum(row[2] for row in results)
                
                # Oppdater daglig statistikk
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_stats 
                    (date, content_created, best_performing_theme, notes)
                    VALUES (?, ?, ?, ?)
                ''', (
                    yesterday_str,
                    total_posts,
                    best_theme,
                    f"Beste engagement: {best_engagement:.2f}%"
                ))
                
                conn.commit()
                logger.info(f"📈 Analyserte gårsdagens ytelse: {best_theme} presterte best")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Feil ved analyse av gårsdagens ytelse: {e}")
    
    def update_learning_data(self, content_items, published_count):
        """Oppdater læringsdaten for AI-forbedring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in content_items:
                # Beregn foreløpig performance score
                metadata = item.get("metadata", {})
                theme = item.get("theme", "lifestyle")
                
                # Simpel score basert på at innholdet ble publisert
                performance_score = 1.0 if published_count > 0 else 0.5
                
                cursor.execute('''
                    INSERT INTO learning_data 
                    (theme, prompt_data, performance_score, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    theme,
                    json.dumps(metadata),
                    performance_score,
                    datetime.now()
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🧠 Oppdaterte læringsdaten for {len(content_items)} elementer")
            
        except Exception as e:
            logger.error(f"❌ Feil ved oppdatering av læringsdaten: {e}")
    
    def cleanup_old_content(self):
        """Rydd opp gammelt innhold"""
        if not self.retention_days:
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tell elementer som skal slettes
            cursor.execute('SELECT COUNT(*) FROM content WHERE created_at < ?', (cutoff_date,))
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete > 0:
                # Slett gammelt innhold
                cursor.execute('DELETE FROM content WHERE created_at < ?', (cutoff_date,))
                
                # Slett tilhørende metrics
                cursor.execute('''
                    DELETE FROM performance_metrics 
                    WHERE content_id NOT IN (SELECT id FROM content)
                ''')
                
                # Slett tilhørende publiseringshistorikk
                cursor.execute('''
                    DELETE FROM publish_history 
                    WHERE content_id NOT IN (SELECT id FROM content)
                ''')
                
                conn.commit()
                logger.info(f"🧹 Slettet {count_to_delete} gamle innholdselementer")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Feil ved cleanup: {e}")
    
    def get_performance_metrics(self):
        """Hent samlet ytelsesmålinger"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generelle metrics
            cursor.execute('SELECT COUNT(*) FROM content')
            total_content = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM content WHERE published = TRUE')
            published_content = cursor.fetchone()[0]
            
            # Gjennomsnittlig engagement
            cursor.execute('SELECT AVG(engagement_rate) FROM performance_metrics')
            avg_engagement = cursor.fetchone()[0] or 0
            
            # Beste presterende tema
            cursor.execute('''
                SELECT c.theme, AVG(pm.engagement_rate) as avg_eng
                FROM content c
                JOIN performance_metrics pm ON c.id = pm.content_id
                GROUP BY c.theme
                ORDER BY avg_eng DESC
                LIMIT 1
            ''')
            
            best_theme_data = cursor.fetchone()
            best_theme = best_theme_data[0] if best_theme_data else "N/A"
            
            # Siste 7 dagers trend
            week_ago = datetime.now() - timedelta(days=7)
            cursor.execute('''
                SELECT AVG(engagement_rate) 
                FROM performance_metrics 
                WHERE recorded_at >= ?
            ''', (week_ago,))
            
            week_avg_engagement = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_content": total_content,
                "published_content": published_content,
                "publish_rate": (published_content / total_content * 100) if total_content > 0 else 0,
                "avg_engagement_rate": round(avg_engagement, 2),
                "week_avg_engagement": round(week_avg_engagement, 2),
                "best_performing_theme": best_theme,
                "engagement_trend": "📈" if week_avg_engagement > avg_engagement else "📉"
            }
            
        except Exception as e:
            logger.error(f"❌ Feil ved henting av ytelsesmålinger: {e}")
            return {}
    
    def _row_to_content_item(self, row):
        """Konverter database-rad til innholdsobjekt"""
        item = {
            "id": row[0],
            "type": row[1],
            "caption": row[2],
            "metadata": json.loads(row[4] or '{}'),
            "theme": row[5],
            "created_at": row[6],
            "published": row[7],
            "platforms": json.loads(row[8] or '{}'),
            "performance": json.loads(row[9] or '{}')
        }
        
        # Last inn bilde hvis det finnes
        if row[3]:
            try:
                image = Image.open(io.BytesIO(row[3]))
                item["image"] = image
            except Exception as e:
                logger.error(f"❌ Feil ved lasting av bilde: {e}")
        
        return item
    
    def get_content_count(self):
        """Hent totalt antall innholdselementer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM content')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_today_published_count(self):
        """Hent antall publiserte elementer i dag"""
        today = datetime.now().date()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM content 
            WHERE published = TRUE AND DATE(created_at) = ?
        ''', (today,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def update_daily_stats(self, content_created):
        """Oppdater daglig statistikk"""
        today = datetime.now().date()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats (date, content_created)
            VALUES (?, ?)
        ''', (today, content_created))
        
        conn.commit()
        conn.close()
    
    def get_last_run_time(self):
        """Hent tidspunkt for siste kjøring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(created_at) FROM content')
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else "Aldri"
    
    def close(self):
        """Lukk database-tilkobling"""
        # SQLite lukker automatisk, men kan implementere cleanup her
        logger.info("🔒 Database stengt")
