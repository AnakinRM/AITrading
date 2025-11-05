"""
新闻数据存储管理模块

负责新闻数据的存储、检索和管理
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class NewsStorage:
    """新闻数据存储管理器"""
    
    def __init__(self, base_dir: str = "news_data"):
        """
        初始化新闻存储管理器
        
        Args:
            base_dir: 新闻数据存储根目录
        """
        self.base_dir = Path(base_dir)
        self.hourly_dir = self.base_dir / "hourly"
        self.daily_dir = self.base_dir / "daily"
        self.archive_dir = self.base_dir / "archive"
        
        # 创建目录
        self.hourly_dir.mkdir(parents=True, exist_ok=True)
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"NewsStorage initialized with base_dir: {self.base_dir}")
    
    def save_hourly_news(self, news_data: Dict, timestamp: Optional[datetime] = None) -> Path:
        """
        保存每小时新闻数据
        
        Args:
            news_data: 新闻数据字典
            timestamp: 时间戳,默认为当前时间
            
        Returns:
            保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 生成文件名: news_2025-11-04_15-00-00.json
        filename = f"news_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        filepath = self.hourly_dir / filename
        
        # 添加元数据
        news_data['_metadata'] = {
            'saved_at': datetime.now().isoformat(),
            'data_type': 'hourly',
            'timestamp': timestamp.isoformat()
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Hourly news saved: {filepath}")
        return filepath
    
    def save_daily_summary(self, summary_data: Dict, date: Optional[datetime] = None) -> Path:
        """
        保存每日新闻汇总
        
        Args:
            summary_data: 汇总数据字典
            date: 日期,默认为当前日期
            
        Returns:
            保存的文件路径
        """
        if date is None:
            date = datetime.now()
        
        # 生成文件名: daily_summary_2025-11-04.json
        filename = f"daily_summary_{date.strftime('%Y-%m-%d')}.json"
        filepath = self.daily_dir / filename
        
        # 添加元数据
        summary_data['_metadata'] = {
            'saved_at': datetime.now().isoformat(),
            'data_type': 'daily',
            'date': date.strftime('%Y-%m-%d')
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Daily summary saved: {filepath}")
        return filepath
    
    def get_hourly_news(self, timestamp: datetime) -> Optional[Dict]:
        """
        获取指定时间的hourly news
        
        Args:
            timestamp: 时间戳
            
        Returns:
            新闻数据字典,如果不存在返回None
        """
        # 查找匹配的文件
        pattern = f"news_{timestamp.strftime('%Y-%m-%d_%H')}-*.json"
        files = list(self.hourly_dir.glob(pattern))
        
        if not files:
            logger.warning(f"No hourly news found for {timestamp}")
            return None
        
        # 如果有多个文件,取最新的
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_hourly_news_range(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        获取指定时间范围内的所有hourly news
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            新闻数据列表,按时间排序
        """
        all_news = []
        
        # 遍历时间范围内的每个小时
        current = start_time.replace(minute=0, second=0, microsecond=0)
        while current <= end_time:
            news = self.get_hourly_news(current)
            if news:
                all_news.append(news)
            current += timedelta(hours=1)
        
        logger.info(f"Retrieved {len(all_news)} hourly news items from {start_time} to {end_time}")
        return all_news
    
    def get_daily_summary(self, date: datetime) -> Optional[Dict]:
        """
        获取指定日期的daily summary
        
        Args:
            date: 日期
            
        Returns:
            汇总数据字典,如果不存在返回None
        """
        filename = f"daily_summary_{date.strftime('%Y-%m-%d')}.json"
        filepath = self.daily_dir / filename
        
        if not filepath.exists():
            logger.warning(f"No daily summary found for {date.strftime('%Y-%m-%d')}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_latest_hourly_news(self) -> Optional[Dict]:
        """
        获取最新的hourly news
        
        Returns:
            最新的新闻数据字典,如果不存在返回None
        """
        files = list(self.hourly_dir.glob("news_*.json"))
        
        if not files:
            logger.warning("No hourly news files found")
            return None
        
        # 获取最新的文件
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_latest_daily_summary(self) -> Optional[Dict]:
        """
        获取最新的daily summary
        
        Returns:
            最新的汇总数据字典,如果不存在返回None
        """
        files = list(self.daily_dir.glob("daily_summary_*.json"))
        
        if not files:
            logger.warning("No daily summary files found")
            return None
        
        # 获取最新的文件
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_today_hourly_news(self) -> List[Dict]:
        """
        获取今天所有的hourly news
        
        Returns:
            今天的所有hourly news列表,按时间排序
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        return self.get_hourly_news_range(today, tomorrow)
    
    def get_past_n_days_summaries(self, n: int = 7) -> List[Dict]:
        """
        获取过去N天的daily summaries
        
        Args:
            n: 天数,默认7天
            
        Returns:
            过去N天的daily summaries列表,按时间倒序(最新的在前)
        """
        summaries = []
        current_date = datetime.now()
        
        for i in range(1, n + 1):  # 从昨天开始往前数N天
            date = current_date - timedelta(days=i)
            summary = self.get_daily_summary(date)
            if summary:
                summaries.append(summary)
        
        logger.info(f"Retrieved {len(summaries)} daily summaries from past {n} days")
        return summaries
    
    def archive_old_news(self, days_to_keep: int = 7):
        """
        归档旧的新闻数据
        
        Args:
            days_to_keep: 保留最近N天的数据,更早的归档
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        archived_count = 0
        
        # 归档hourly news
        for file in self.hourly_dir.glob("news_*.json"):
            # 从文件名提取日期
            try:
                date_str = file.stem.split('_')[1]  # news_2025-11-04_15-00-00 -> 2025-11-04
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    # 移动到archive目录
                    archive_path = self.archive_dir / file.name
                    file.rename(archive_path)
                    archived_count += 1
                    logger.debug(f"Archived: {file.name}")
            except Exception as e:
                logger.error(f"Error archiving {file.name}: {e}")
        
        # 归档daily summaries
        for file in self.daily_dir.glob("daily_summary_*.json"):
            try:
                date_str = file.stem.split('_')[2]  # daily_summary_2025-11-04 -> 2025-11-04
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    archive_path = self.archive_dir / file.name
                    file.rename(archive_path)
                    archived_count += 1
                    logger.debug(f"Archived: {file.name}")
            except Exception as e:
                logger.error(f"Error archiving {file.name}: {e}")
        
        logger.info(f"Archived {archived_count} old news files (older than {days_to_keep} days)")
    
    def get_storage_stats(self) -> Dict:
        """
        获取存储统计信息
        
        Returns:
            统计信息字典
        """
        hourly_files = list(self.hourly_dir.glob("news_*.json"))
        daily_files = list(self.daily_dir.glob("daily_summary_*.json"))
        archive_files = list(self.archive_dir.glob("*.json"))
        
        # 计算总大小
        hourly_size = sum(f.stat().st_size for f in hourly_files)
        daily_size = sum(f.stat().st_size for f in daily_files)
        archive_size = sum(f.stat().st_size for f in archive_files)
        
        stats = {
            'hourly_news': {
                'count': len(hourly_files),
                'size_mb': hourly_size / (1024 * 1024),
                'oldest': min((f.stat().st_mtime for f in hourly_files), default=None),
                'newest': max((f.stat().st_mtime for f in hourly_files), default=None)
            },
            'daily_summaries': {
                'count': len(daily_files),
                'size_mb': daily_size / (1024 * 1024),
                'oldest': min((f.stat().st_mtime for f in daily_files), default=None),
                'newest': max((f.stat().st_mtime for f in daily_files), default=None)
            },
            'archived': {
                'count': len(archive_files),
                'size_mb': archive_size / (1024 * 1024)
            },
            'total_size_mb': (hourly_size + daily_size + archive_size) / (1024 * 1024)
        }
        
        return stats
    
    def cleanup_storage(self, max_size_mb: int = 1000):
        """
        清理存储空间,如果超过限制则删除最旧的归档文件
        
        Args:
            max_size_mb: 最大存储空间(MB)
        """
        stats = self.get_storage_stats()
        
        if stats['total_size_mb'] <= max_size_mb:
            logger.info(f"Storage size {stats['total_size_mb']:.2f}MB is within limit {max_size_mb}MB")
            return
        
        logger.warning(f"Storage size {stats['total_size_mb']:.2f}MB exceeds limit {max_size_mb}MB, cleaning up...")
        
        # 删除最旧的归档文件
        archive_files = sorted(
            self.archive_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime
        )
        
        deleted_count = 0
        deleted_size = 0
        
        for file in archive_files:
            if stats['total_size_mb'] - deleted_size / (1024 * 1024) <= max_size_mb:
                break
            
            file_size = file.stat().st_size
            file.unlink()
            deleted_count += 1
            deleted_size += file_size
            logger.debug(f"Deleted: {file.name}")
        
        logger.info(f"Deleted {deleted_count} archived files, freed {deleted_size / (1024 * 1024):.2f}MB")


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建存储管理器
    storage = NewsStorage()
    
    # 示例: 保存hourly news
    sample_hourly_news = {
        "search_time": "2025-11-04 15:00:00",
        "total_news_found": 3,
        "news_items": [
            {
                "title": "Sample news 1",
                "category": "Bitcoin",
                "summary": "This is a sample news item",
                "market_impact": "Bullish"
            }
        ]
    }
    storage.save_hourly_news(sample_hourly_news)
    
    # 示例: 保存daily summary
    sample_daily_summary = {
        "analysis_time": "2025-11-05 00:00:00",
        "total_news_analyzed": 87,
        "daily_summary": {
            "overview": "Sample daily overview"
        }
    }
    storage.save_daily_summary(sample_daily_summary)
    
    # 示例: 获取最新新闻
    latest = storage.get_latest_hourly_news()
    print(f"Latest hourly news: {latest}")
    
    # 示例: 获取存储统计
    stats = storage.get_storage_stats()
    print(f"Storage stats: {json.dumps(stats, indent=2)}")
    
    # 示例: 归档旧新闻
    storage.archive_old_news(days_to_keep=7)
