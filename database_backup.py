#!/usr/bin/env python3
"""
Database Backup and Restore Script for TradeWise AI
Automated backup solution with compression and versioning
"""

import os
import sys
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Database backup and restore management"""
    
    def __init__(self):
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        self.database_url = os.environ.get('DATABASE_URL')
        self.max_backups = 30  # Keep 30 days of backups
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
    
    def create_backup(self, description=""):
        """Create a database backup with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"tradewise_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        compressed_path = self.backup_dir / f"{backup_filename}.gz"
        
        try:
            logger.info(f"Creating database backup: {backup_filename}")
            
            if self.database_url.startswith('postgresql://'):
                # PostgreSQL backup
                self._backup_postgresql(backup_path)
            elif self.database_url.startswith('sqlite:///'):
                # SQLite backup
                self._backup_sqlite(backup_path)
            else:
                raise ValueError(f"Unsupported database type: {self.database_url}")
            
            # Compress the backup
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            backup_path.unlink()
            
            # Create metadata file
            metadata = {
                'timestamp': timestamp,
                'description': description,
                'filename': compressed_path.name,
                'size_bytes': compressed_path.stat().st_size,
                'database_url': self.database_url.split('@')[0] + '@***'  # Hide credentials
            }
            
            metadata_path = self.backup_dir / f"{backup_filename}.meta"
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Backup created successfully: {compressed_path}")
            logger.info(f"Backup size: {compressed_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            # Clean up partial files
            for path in [backup_path, compressed_path]:
                if path.exists():
                    path.unlink()
            raise
    
    def _backup_postgresql(self, backup_path):
        """Create PostgreSQL backup using pg_dump"""
        try:
            # Parse database URL
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port or 5432),
                '-U', parsed.username,
                '-d', parsed.path.lstrip('/'),
                '--no-password',
                '--verbose',
                '--clean',
                '--create'
            ]
            
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, text=True)
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
                
        except FileNotFoundError:
            raise ValueError("pg_dump not found. Install PostgreSQL client tools.")
    
    def _backup_sqlite(self, backup_path):
        """Create SQLite backup using .dump command"""
        db_file = self.database_url.replace('sqlite:///', '')
        
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"SQLite database not found: {db_file}")
        
        cmd = ['sqlite3', db_file, '.dump']
        
        with open(backup_path, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    
    def restore_backup(self, backup_file):
        """Restore database from backup file"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Create temporary uncompressed file
        temp_sql = backup_path.with_suffix('.temp.sql')
        
        try:
            logger.info(f"Restoring database from: {backup_path}")
            
            # Decompress if needed
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_sql, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                sql_file = temp_sql
            else:
                sql_file = backup_path
            
            if self.database_url.startswith('postgresql://'):
                self._restore_postgresql(sql_file)
            elif self.database_url.startswith('sqlite:///'):
                self._restore_sqlite(sql_file)
            else:
                raise ValueError(f"Unsupported database type: {self.database_url}")
            
            logger.info("✅ Database restore completed successfully")
            
        finally:
            # Clean up temporary file
            if temp_sql.exists():
                temp_sql.unlink()
    
    def _restore_postgresql(self, sql_file):
        """Restore PostgreSQL database"""
        from urllib.parse import urlparse
        parsed = urlparse(self.database_url)
        
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        cmd = [
            'psql',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '--no-password',
            '-f', str(sql_file)
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    
    def _restore_sqlite(self, sql_file):
        """Restore SQLite database"""
        db_file = self.database_url.replace('sqlite:///', '')
        
        # Backup existing database
        if os.path.exists(db_file):
            backup_existing = f"{db_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_file, backup_existing)
            logger.info(f"Existing database backed up to: {backup_existing}")
        
        cmd = ['sqlite3', db_file]
        
        with open(sql_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    
    def cleanup_old_backups(self):
        """Remove backups older than max_backups days"""
        cutoff_date = datetime.now() - timedelta(days=self.max_backups)
        cleaned = 0
        
        for backup_file in self.backup_dir.glob('tradewise_backup_*.sql.gz'):
            # Extract timestamp from filename
            try:
                timestamp_str = backup_file.stem.split('_')[2] + '_' + backup_file.stem.split('_')[3]
                file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if file_date < cutoff_date:
                    backup_file.unlink()
                    # Also remove metadata file
                    metadata_file = backup_file.with_suffix('.sql.meta')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    cleaned += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
                    
            except (ValueError, IndexError):
                logger.warning(f"Could not parse timestamp from: {backup_file.name}")
        
        if cleaned > 0:
            logger.info(f"✅ Cleaned up {cleaned} old backup(s)")
        else:
            logger.info("No old backups to clean up")
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('tradewise_backup_*.sql.gz')):
            metadata_file = backup_file.with_suffix('.sql.meta')
            metadata = {}
            
            if metadata_file.exists():
                try:
                    import json
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size_mb': backup_file.stat().st_size / 1024 / 1024,
                'created': metadata.get('timestamp', 'Unknown'),
                'description': metadata.get('description', '')
            })
        
        return backups

def main():
    """Command line interface for database backup management"""
    parser = argparse.ArgumentParser(description='TradeWise AI Database Backup Management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a database backup')
    backup_parser.add_argument('--description', '-d', default='', help='Backup description')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Backup file to restore from')
    
    # List command
    subparsers.add_parser('list', help='List available backups')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Remove old backups')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        backup_manager = DatabaseBackup()
        
        if args.command == 'backup':
            backup_file = backup_manager.create_backup(args.description)
            print(f"✅ Backup created: {backup_file}")
            
        elif args.command == 'restore':
            backup_manager.restore_backup(args.backup_file)
            print("✅ Database restored successfully")
            
        elif args.command == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print("\nAvailable backups:")
                print("-" * 80)
                for backup in backups:
                    print(f"{backup['filename']:<30} {backup['size_mb']:>8.2f} MB  {backup['created']}")
                    if backup['description']:
                        print(f"  Description: {backup['description']}")
                print()
            else:
                print("No backups found.")
                
        elif args.command == 'cleanup':
            backup_manager.cleanup_old_backups()
            
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()