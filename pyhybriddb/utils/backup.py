"""
Backup and Restore utilities for PyHybridDB
"""

import json
import shutil
import gzip
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class BackupManager:
    """Manage database backups and restores"""
    
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, db_path: str, compress: bool = True) -> str:
        """Create a backup of the database"""
        db_path = Path(db_path)
        
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_path.stem}_backup_{timestamp}"
        
        if compress:
            backup_file = self.backup_dir / f"{backup_name}.phdb.gz"
            
            # Compress and backup
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            backup_file = self.backup_dir / f"{backup_name}.phdb"
            shutil.copy2(db_path, backup_file)
        
        # Create metadata file
        metadata = {
            "original_path": str(db_path),
            "backup_time": datetime.now().isoformat(),
            "compressed": compress,
            "size": backup_file.stat().st_size
        }
        
        metadata_file = backup_file.with_suffix('.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(backup_file)
    
    def restore_backup(self, backup_file: str, target_path: Optional[str] = None) -> str:
        """Restore a database from backup"""
        backup_file = Path(backup_file)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {backup_file}")
        
        # Load metadata
        metadata_file = backup_file.with_suffix('.json')
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {"compressed": backup_file.suffix == '.gz'}
        
        # Determine target path
        if target_path is None:
            target_path = metadata.get('original_path', str(backup_file.with_suffix('.phdb')))
        
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Restore
        if metadata.get('compressed', False):
            with gzip.open(backup_file, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup_file, target_path)
        
        return str(target_path)
    
    def list_backups(self, db_name: Optional[str] = None) -> list:
        """List all available backups"""
        backups = []
        
        pattern = f"{db_name}_backup_*" if db_name else "*_backup_*"
        
        for backup_file in self.backup_dir.glob(f"{pattern}.phdb*"):
            if backup_file.suffix in ['.phdb', '.gz']:
                metadata_file = backup_file.with_suffix('.json')
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                else:
                    metadata = {}
                
                backups.append({
                    "file": str(backup_file),
                    "name": backup_file.stem,
                    "size": backup_file.stat().st_size,
                    "created": metadata.get('backup_time', 'Unknown'),
                    "compressed": metadata.get('compressed', False)
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def delete_backup(self, backup_file: str) -> bool:
        """Delete a backup file"""
        backup_file = Path(backup_file)
        
        if not backup_file.exists():
            return False
        
        # Delete backup file
        backup_file.unlink()
        
        # Delete metadata if exists
        metadata_file = backup_file.with_suffix('.json')
        if metadata_file.exists():
            metadata_file.unlink()
        
        return True
    
    def auto_backup(self, db_path: str, max_backups: int = 5) -> str:
        """Create automatic backup and maintain max_backups limit"""
        backup_file = self.create_backup(db_path, compress=True)
        
        # Get database name
        db_name = Path(db_path).stem
        
        # List all backups for this database
        backups = self.list_backups(db_name)
        
        # Delete old backups if exceeding limit
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                self.delete_backup(backup['file'])
        
        return backup_file
