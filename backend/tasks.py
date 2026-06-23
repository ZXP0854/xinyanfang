"""
定时任务模块
使用 APScheduler 执行周期任务：数据库备份、日志清理、健康检查
"""

import os
import shutil
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)


def init_scheduler(app):
    """初始化并启动定时任务调度器"""

    @scheduler.scheduled_job('cron', hour=3, minute=0, id='db_backup')
    def backup_database():
        """每日凌晨 3:00 备份数据库"""
        try:
            from models import db
            backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if 'sqlite' in db_uri:
                # SQLite: 直接复制文件
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    backup_name = f'data_backup_{timestamp}.db'
                    shutil.copy2(db_path, os.path.join(backup_dir, backup_name))
                    app.logger.info(f'SQLite backup: {backup_name}')

                    # 只保留最近 7 天的备份
                    _cleanup_old_files(backup_dir, 'data_backup_*.db', keep=7)
            elif 'mysql' in db_uri:
                # MySQL: 导出 SQL（需要 mysqldump 命令）
                import subprocess
                import re
                m = re.match(r'mysql\+pymysql://(\w+):(\S+)@(\S+)/(\w+)', db_uri)
                if m:
                    user, password, host, database = m.groups()
                    backup_name = f'mysql_backup_{timestamp}.sql'
                    backup_path = os.path.join(backup_dir, backup_name)
                    cmd = f'mysqldump -u{user} -p{password} -h{host} {database} > {backup_path}'
                    subprocess.run(cmd, shell=True, check=False)
                    app.logger.info(f'MySQL backup: {backup_name}')
                    _cleanup_old_files(backup_dir, 'mysql_backup_*.sql', keep=7)
        except Exception as e:
            app.logger.error(f'Database backup failed: {e}')

    @scheduler.scheduled_job('cron', hour=4, minute=0, id='cleanup_old_logs')
    def cleanup_old_audit_logs():
        """每日凌晨 4:00 清理 90 天前的审计日志"""
        try:
            from models import db, AuditLog
            cutoff = datetime.utcnow() - timedelta(days=90)
            deleted = AuditLog.query.filter(AuditLog.created_at < cutoff).delete()
            db.session.commit()
            if deleted:
                app.logger.info(f'Cleaned up {deleted} old audit log entries')
        except Exception as e:
            app.logger.error(f'Audit log cleanup failed: {e}')

    @scheduler.scheduled_job('interval', minutes=15, id='health_check')
    def health_check():
        """每 15 分钟健康检查"""
        try:
            from models import db
            db.session.execute(db.text('SELECT 1'))
            app.logger.debug('Health check: OK')
        except Exception as e:
            app.logger.error(f'Health check failed: {e}')

    scheduler.start()
    app.logger.info('Scheduler started with tasks: db_backup, cleanup_old_logs, health_check')


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)


def _cleanup_old_files(directory: str, pattern: str, keep: int):
    """清理旧备份文件，保留最近 keep 个"""
    import glob
    files = sorted(glob.glob(os.path.join(directory, pattern)))
    while len(files) > keep:
        old = files.pop(0)
        try:
            os.remove(old)
        except OSError:
            pass
