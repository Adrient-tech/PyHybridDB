"""
Command-line interface for PyHybridDB
"""

import argparse
import sys
from pathlib import Path

from pyhybriddb import Database
from pyhybriddb.utils.logger import setup_logger
from pyhybriddb.config import Config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PyHybridDB - Hybrid Database System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create database
    create_parser = subparsers.add_parser('create', help='Create a new database')
    create_parser.add_argument('name', help='Database name')
    create_parser.add_argument('--path', help='Database path', default=None)
    
    # Start server
    server_parser = subparsers.add_parser('serve', help='Start API server')
    server_parser.add_argument('--host', default=Config.API_HOST, help='Host address')
    server_parser.add_argument('--port', type=int, default=Config.API_PORT, help='Port number')
    server_parser.add_argument('--reload', action='store_true', default=Config.API_RELOAD, help='Enable auto-reload')
    
    # Start Distributed Node
    node_parser = subparsers.add_parser('node', help='Start a Distributed Node')
    node_parser.add_argument('--name', required=True, help='Node name (e.g., node1)')
    node_parser.add_argument('--path', required=True, help='Data directory for this node')
    node_parser.add_argument('--port', type=int, required=True, help='Port to listen on')

    # Interactive shell
    shell_parser = subparsers.add_parser('shell', help='Interactive shell')
    shell_parser.add_argument('database', help='Database name')
    shell_parser.add_argument('--path', help='Database path', default=None)
    
    # Info
    info_parser = subparsers.add_parser('info', help='Database information')
    info_parser.add_argument('database', help='Database name')
    info_parser.add_argument('--path', help='Database path', default=None)
    
    # Config
    config_parser = subparsers.add_parser('config', help='Show configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    logger = setup_logger()
    
    if args.command == 'create':
        create_database(args.name, args.path, logger)
    elif args.command == 'serve':
        start_server(args.host, args.port, args.reload, logger)
    elif args.command == 'node':
        start_node(args.name, args.path, args.port, logger)
    elif args.command == 'shell':
        interactive_shell(args.database, args.path, logger)
    elif args.command == 'info':
        show_info(args.database, args.path, logger)
    elif args.command == 'config':
        show_config()


def create_database(name: str, path: str, logger):
    """Create a new database"""
    try:
        db = Database(name=name, path=path)
        db.create()
        db.close()
        
        logger.info(f"Database '{name}' created successfully at {db.db_file}")
        print(f"✓ Database '{name}' created at {db.db_file}")
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


def start_server(host: str, port: int, reload: bool, logger):
    """Start the API server"""
    try:
        import uvicorn
        from pyhybriddb.api.server import app
        
        logger.info(f"Starting server on {host}:{port}")
        print(f"🚀 Starting PyHybridDB server on http://{host}:{port}")
        print(f"📚 API docs available at http://{host}:{port}/docs")
        
        uvicorn.run(
            "pyhybriddb.api.server:app",
            host=host,
            port=port,
            reload=reload
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


def start_node(name: str, path: str, port: int, logger):
    """Start a Distributed Node"""
    try:
        import uvicorn
        import os

        # Pass config via Env Vars
        os.environ["PHDB_NODE_NAME"] = name
        os.environ["PHDB_NODE_PATH"] = path

        logger.info(f"Starting Node '{name}' on port {port}")
        print(f"🌐 Starting Distributed Node '{name}' at http://0.0.0.0:{port}")

        uvicorn.run(
            "pyhybriddb.distributed.node:app",
            host="0.0.0.0",
            port=port,
            reload=False
        )
    except Exception as e:
        logger.error(f"Failed to start node: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


def interactive_shell(db_name: str, path: str, logger):
    """Start interactive shell"""
    try:
        db = Database(name=db_name, path=path)
        
        if not db.db_file.exists():
            print(f"✗ Database '{db_name}' not found")
            sys.exit(1)
        
        db.open()
        
        print(f"PyHybridDB Interactive Shell")
        print(f"Database: {db_name}")
        print(f"Type 'help' for commands, 'exit' to quit\n")
        
        from pyhybriddb.query.parser import QueryParser
        parser = QueryParser(db)
        
        while True:
            try:
                query = input("phdb> ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'exit':
                    break
                
                if query.lower() == 'help':
                    print_help()
                    continue
                
                if query.lower() == 'tables':
                    print("Tables:", db.list_tables())
                    continue
                
                if query.lower() == 'collections':
                    print("Collections:", db.list_collections())
                    continue
                
                # Execute query
                result = parser.parse_and_execute(query)
                print(result)
                db.commit()
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")
                db.rollback()
        
        db.close()
        print("Goodbye!")
        
    except Exception as e:
        logger.error(f"Shell error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


def show_info(db_name: str, path: str, logger):
    """Show database information"""
    try:
        db = Database(name=db_name, path=path)
        
        if not db.db_file.exists():
            print(f"✗ Database '{db_name}' not found")
            sys.exit(1)
        
        db.open()
        stats = db.get_stats()
        
        print(f"\nDatabase: {db_name}")
        print(f"Path: {stats['path']}")
        print(f"File Size: {stats['file_size']} bytes")
        print(f"Tables: {stats['table_count']}")
        print(f"Collections: {stats['collection_count']}")
        print(f"Indexes: {stats['indexes']}")
        
        if stats['table_count'] > 0:
            print(f"\nTables:")
            for table_name in db.list_tables():
                table = db.get_table(table_name)
                print(f"  - {table_name} ({table.count()} records)")
        
        if stats['collection_count'] > 0:
            print(f"\nCollections:")
            for coll_name in db.list_collections():
                collection = db.get_collection(coll_name)
                print(f"  - {coll_name} ({collection.count_documents()} documents)")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Info error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


def show_config():
    """Show current configuration"""
    print("\n" + "=" * 60)
    print("  PyHybridDB Configuration")
    print("=" * 60 + "\n")
    
    Config.display()
    
    print("\n" + "=" * 60)
    print("\nTo change configuration:")
    print("  1. Copy config.env to .env")
    print("  2. Edit .env with your values")
    print("  3. Restart the application")
    print("\n" + "=" * 60 + "\n")


def print_help():
    """Print help message"""
    print("""
Available commands:
  help                  - Show this help message
  exit                  - Exit the shell
  tables                - List all tables
  collections           - List all collections
  
SQL queries:
  CREATE TABLE name (col type, ...)
  SELECT * FROM table WHERE col=val
  INSERT INTO table (cols) VALUES (vals)
  UPDATE table SET col=val WHERE col=val
  DELETE FROM table WHERE col=val
  
NoSQL queries:
  db.collection.insertOne({...})
  db.collection.find({...})
  db.collection.updateOne({...}, {...})
  db.collection.deleteOne({...})
""")


if __name__ == '__main__':
    main()
