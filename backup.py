"""
Complete Project Backup Utility
Creates timestamped backups of your entire project with compression
"""
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import json
import argparse

class ProjectBackup:
    def __init__(self, project_root=None, backup_dir=None):
        """
        Initialize backup utility
        
        Args:
            project_root: Root directory of project (defaults to current directory)
            backup_dir: Directory to store backups (defaults to project_root/backups)
        """
        self.project_root = Path(project_root or os.getcwd())
        self.backup_dir = Path(backup_dir or self.project_root / "backups")
        
        # Directories/files to exclude from backup
        self.exclude_patterns = {
            '__pycache__',
            '*.pyc',
            '.git',
            '.gitignore',
            'node_modules',
            '.venv',
            'venv',
            'env',
            '.env.local',
            '*.log',
            '.DS_Store',
            'backups',  # Don't backup the backup folder itself
            '*.tmp',
            '.pytest_cache',
            '.coverage',
            'htmlcov'
        }
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def should_exclude(self, path):
        """Check if a path should be excluded from backup"""
        path_str = str(path)
        path_name = path.name
        
        for pattern in self.exclude_patterns:
            if pattern.startswith('*.'):
                # File extension pattern
                if path_name.endswith(pattern[1:]):
                    return True
            else:
                # Directory or exact name pattern
                if pattern in path_str or path_name == pattern:
                    return True
        
        return False
    
    def get_backup_filename(self, backup_type="full"):
        """Generate timestamped backup filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"project_backup_{backup_type}_{timestamp}.zip"
    
    def create_backup(self, backup_type="full", description=""):
        """
        Create a backup of the project
        
        Args:
            backup_type: Type of backup (full, code_only, data_only)
            description: Optional description for the backup
        
        Returns:
            Path to the created backup file
        """
        backup_filename = self.get_backup_filename(backup_type)
        backup_path = self.backup_dir / backup_filename
        
        print(f"Creating {backup_type} backup...")
        print(f"Source: {self.project_root}")
        print(f"Destination: {backup_path}")
        
        files_backed_up = 0
        total_size = 0
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_root):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Skip excluded files
                    if self.should_exclude(file_path):
                        continue
                    
                    # Skip if it's the backup file itself
                    if file_path == backup_path:
                        continue
                    
                    # Apply backup type filters
                    if backup_type == "code_only":
                        # Only backup code files
                        if not self._is_code_file(file_path):
                            continue
                    elif backup_type == "data_only":
                        # Only backup data files
                        if not self._is_data_file(file_path):
                            continue
                    
                    # Add file to zip
                    arcname = file_path.relative_to(self.project_root)
                    zipf.write(file_path, arcname)
                    
                    files_backed_up += 1
                    total_size += file_path.stat().st_size
                    
                    if files_backed_up % 100 == 0:
                        print(f"  Backed up {files_backed_up} files...")
        
        # Create metadata file
        metadata = {
            'backup_date': datetime.now().isoformat(),
            'backup_type': backup_type,
            'description': description,
            'files_count': files_backed_up,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'source_path': str(self.project_root),
            'backup_file': backup_filename
        }
        
        metadata_file = backup_path.with_suffix('.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
        
        print(f"\n✅ Backup completed successfully!")
        print(f"   Files backed up: {files_backed_up}")
        print(f"   Original size: {metadata['total_size_mb']} MB")
        print(f"   Backup size: {backup_size_mb:.2f} MB")
        print(f"   Compression: {(1 - backup_size_mb/metadata['total_size_mb'])*100:.1f}%")
        print(f"   Location: {backup_path}")
        
        return backup_path
    
    def _is_code_file(self, path):
        """Check if file is a code file"""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', 
                          '.json', '.yml', '.yaml', '.md', '.txt', '.sh', '.bat'}
        return path.suffix.lower() in code_extensions
    
    def _is_data_file(self, path):
        """Check if file is a data file"""
        data_extensions = {'.db', '.sqlite', '.sqlite3', '.csv', '.xlsx', '.json',
                          '.pdf', '.docx', '.txt', '.mp3', '.wav', '.mp4'}
        data_dirs = {'data', 'uploads', 'processed', 'databases'}
        
        # Check if in data directory
        for parent in path.parents:
            if parent.name in data_dirs:
                return True
        
        return path.suffix.lower() in data_extensions
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("project_backup_*.zip"):
            metadata_file = backup_file.with_suffix('.json')
            
            metadata = {
                'filename': backup_file.name,
                'size_mb': round(backup_file.stat().st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat()
            }
            
            # Load metadata if exists
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    file_metadata = json.load(f)
                    metadata.update(file_metadata)
            
            backups.append(metadata)
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def restore_backup(self, backup_filename, restore_path=None):
        """
        Restore a backup
        
        Args:
            backup_filename: Name of the backup file to restore
            restore_path: Path to restore to (defaults to project_root/restored)
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        if restore_path is None:
            restore_path = self.project_root / "restored" / backup_filename.replace('.zip', '')
        else:
            restore_path = Path(restore_path)
        
        restore_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Restoring backup: {backup_filename}")
        print(f"To: {restore_path}")
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_path)
        
        print(f"✅ Backup restored successfully to: {restore_path}")
        
        return restore_path
    
    def delete_old_backups(self, keep_last=5):
        """Delete old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_last:
            print(f"No backups to delete (have {len(backups)}, keeping {keep_last})")
            return
        
        backups_to_delete = backups[keep_last:]
        
        print(f"Deleting {len(backups_to_delete)} old backup(s)...")
        
        for backup in backups_to_delete:
            backup_path = self.backup_dir / backup['filename']
            metadata_path = backup_path.with_suffix('.json')
            
            if backup_path.exists():
                backup_path.unlink()
                print(f"  Deleted: {backup['filename']}")
            
            if metadata_path.exists():
                metadata_path.unlink()
        
        print(f"✅ Cleanup complete. Kept {keep_last} most recent backups.")
    
    def create_incremental_backup(self, last_backup_date=None):
        """Create backup of only files modified since last backup"""
        if last_backup_date is None:
            backups = self.list_backups()
            if not backups:
                print("No previous backups found. Creating full backup instead.")
                return self.create_backup("full", "First incremental backup")
            
            last_backup_date = datetime.fromisoformat(backups[0]['created'])
        
        backup_filename = self.get_backup_filename("incremental")
        backup_path = self.backup_dir / backup_filename
        
        print(f"Creating incremental backup...")
        print(f"Including files modified after: {last_backup_date}")
        
        files_backed_up = 0
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    if self.should_exclude(file_path):
                        continue
                    
                    # Check if file was modified after last backup
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime > last_backup_date:
                        arcname = file_path.relative_to(self.project_root)
                        zipf.write(file_path, arcname)
                        files_backed_up += 1
        
        print(f"✅ Incremental backup complete: {files_backed_up} modified files")
        print(f"   Location: {backup_path}")
        
        return backup_path


def main():
    parser = argparse.ArgumentParser(description="Project Backup Utility")
    parser.add_argument('action', choices=['backup', 'list', 'restore', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--type', choices=['full', 'code_only', 'data_only', 'incremental'],
                       default='full', help='Type of backup')
    parser.add_argument('--description', help='Backup description')
    parser.add_argument('--backup-file', help='Backup file to restore')
    parser.add_argument('--keep', type=int, default=5, help='Number of backups to keep')
    parser.add_argument('--project-root', help='Project root directory')
    parser.add_argument('--backup-dir', help='Backup directory')
    
    args = parser.parse_args()
    
    backup = ProjectBackup(args.project_root, args.backup_dir)
    
    if args.action == 'backup':
        if args.type == 'incremental':
            backup.create_incremental_backup()
        else:
            backup.create_backup(args.type, args.description or "")
    
    elif args.action == 'list':
        backups = backup.list_backups()
        print(f"\n📦 Available Backups ({len(backups)}):")
        print("=" * 80)
        for i, b in enumerate(backups, 1):
            print(f"\n{i}. {b['filename']}")
            print(f"   Created: {b['created']}")
            print(f"   Size: {b['size_mb']} MB")
            if 'backup_type' in b:
                print(f"   Type: {b['backup_type']}")
            if 'description' in b and b['description']:
                print(f"   Description: {b['description']}")
    
    elif args.action == 'restore':
        if not args.backup_file:
            print("Error: --backup-file required for restore")
            return
        backup.restore_backup(args.backup_file)
    
    elif args.action == 'cleanup':
        backup.delete_old_backups(args.keep)


if __name__ == "__main__":
    # If run directly without arguments, show interactive menu
    import sys
    
    if len(sys.argv) == 1:
        print("\n🔧 Project Backup Utility")
        print("=" * 50)
        print("\n1. Create Full Backup")
        print("2. Create Code-Only Backup")
        print("3. Create Data-Only Backup")
        print("4. Create Incremental Backup")
        print("5. List All Backups")
        print("6. Cleanup Old Backups")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ")
        
        backup = ProjectBackup()
        
        if choice == '1':
            desc = input("Enter description (optional): ")
            backup.create_backup("full", desc)
        elif choice == '2':
            desc = input("Enter description (optional): ")
            backup.create_backup("code_only", desc)
        elif choice == '3':
            desc = input("Enter description (optional): ")
            backup.create_backup("data_only", desc)
        elif choice == '4':
            backup.create_incremental_backup()
        elif choice == '5':
            backups = backup.list_backups()
            print(f"\n📦 Available Backups ({len(backups)}):")
            for i, b in enumerate(backups, 1):
                print(f"\n{i}. {b['filename']}")
                print(f"   Created: {b['created']}")
                print(f"   Size: {b['size_mb']} MB")
        elif choice == '6':
            keep = input("How many backups to keep? (default: 5): ")
            keep = int(keep) if keep else 5
            backup.delete_old_backups(keep)
        else:
            print("Exiting...")
    else:
        main()