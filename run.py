import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules after path setup
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper


def run_scheduler(args):
    """Run the batch scheduler"""
    from scheduler import DealsBatchScheduler
    
    scheduler = DealsBatchScheduler(interval_hours=args.interval)
    
    if args.once:
        scheduler._setup_scrapers()
        scheduler.run_once()
    else:
        scheduler.run(max_iterations=args.max_iterations)


def run_dashboard(args):
    """Run the web dashboard"""
    from web_app import run_server
    
    run_server(host=args.host, port=args.port)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="India Deals Aggregator - Scraper for Amazon India & Flipkart deals"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser('scheduler', help='Run batch scheduler')
    scheduler_parser.add_argument(
        '--interval', 
        type=float, 
        default=1.0,
        help='Interval in hours between scrapes (default: 1.0)'
    )
    scheduler_parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of iterations'
    )
    scheduler_parser.add_argument(
        '--once',
        action='store_true',
        help='Run only once and exit'
    )
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Run web dashboard')
    dashboard_parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    dashboard_parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape deals once')
    
    # Both command - run scheduler and dashboard together
    both_parser = subparsers.add_parser('both', help='Run both scheduler and dashboard')
    both_parser.add_argument(
        '--interval', 
        type=float, 
        default=1.0,
        help='Interval in hours (default: 1.0)'
    )
    both_parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Dashboard port (default: 5000)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'scheduler':
        run_scheduler(args)
    elif args.command == 'dashboard':
        run_dashboard(args)
    elif args.command == 'scrape':
        from deals_bot import DealsAggregator
        
        aggregator = DealsAggregator()
        aggregator.add_scraper(AmazonScraper())
        aggregator.add_scraper(FlipkartScraper())
        results = aggregator.run()
        
        print("\n=== Results ===")
        for source, result in results.items():
            print(f"{source}: {result}")
    elif args.command == 'both':
        import threading
        from scheduler import DealsBatchScheduler
        
        # Run scheduler in background thread
        scheduler = DealsBatchScheduler(interval_hours=args.interval)
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()
        
        # Run dashboard in main thread
        run_dashboard(args)
    else:
        # Default help or run: show scrape
        parser.print_help()
        print("\n\nExamples:")
        print("  python deals_bot/run.py scrape           # Scrape deals once")
        print("  python deals_bot/run.py scheduler         # Run scheduler 24X7")
        print("  python deals_bot/run.py dashboard         # Run web dashboard")
        print("  python deals_bot/run.py both             # Run both scheduler and dashboard")
        print("  python deals_bot/run.py scheduler --once  # Run once and exit")


if __name__ == "__main__":
    main()
