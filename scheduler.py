"""
Batch Scheduler for Deals Aggregation
Runs 24X7 to scrape latest deals every hour
"""

import os
import sys
import time
import signal
import logging
import argparse
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deals_bot import DealsAggregator, logger
from deals_bot.amazon_scraper import AmazonScraper
from deals_bot.flipkart_scraper import FlipkartScraper


class DealsBatchScheduler:
    """Scheduler that runs deals scraping at regular intervals"""
    
    def __init__(self, interval_hours: float = 1.0):
        self.interval_hours = interval_hours
        self.interval_seconds = interval_hours * 3600
        self.running = False
        self.iteration = 0
        self.aggregator = DealsAggregator()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _setup_scrapers(self):
        """Initialize all scrapers"""
        self.aggregator.add_scraper(AmazonScraper())
        self.aggregator.add_scraper(FlipkartScraper())
        logger.info("Scrapers initialized")
    
    def run_once(self) -> bool:
        """Run one iteration of scraping"""
        self.iteration += 1
        logger.info(f"=== Starting iteration {self.iteration} at {datetime.now().isoformat()} ===")
        
        try:
            results = self.aggregator.run()
            
            # Log results
            success_count = sum(1 for r in results.values() if r.get('status') == 'success')
            logger.info(f"Iteration {self.iteration} completed: {success_count}/{len(results)} sources successful")
            
            for source, result in results.items():
                status = result.get('status', 'unknown')
                deals_count = result.get('deals_count', 0)
                logger.info(f"  - {source}: {status} - {deals_count} deals")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in iteration {self.iteration}: {str(e)}", exc_info=True)
            return False
    
    def run(self, max_iterations: Optional[int] = None):
        """Run the scheduler continuously"""
        self.running = True
        self._setup_scrapers()
        
        logger.info(f"Deals Batch Scheduler started")
        logger.info(f"Interval: {self.interval_hours} hour(s)")
        logger.info(f"Max iterations: {max_iterations if max_iterations else 'unlimited'}")
        logger.info("Press Ctrl+C to stop")
        
        # Run once immediately
        self.run_once()
        
        # Main loop
        while self.running:
            if max_iterations and self.iteration >= max_iterations:
                logger.info(f"Reached max iterations ({max_iterations}), stopping")
                break
            
            # Sleep until next iteration
            logger.info(f"Next iteration in {self.interval_hours} hour(s)")
            time.sleep(self.interval_seconds)
            
            if self.running:
                self.run_once()
        
        logger.info("Scheduler stopped")
    
    def run_forever(self):
        """Alias for run with no max iterations"""
        self.run(max_iterations=None)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deals Batch Scheduler")
    parser.add_argument(
        '--interval', 
        type=float, 
        default=12.0,
        help='Interval in hours between scrapes (default: 12.0)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of iterations (default: unlimited)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run only once and exit'
    )
    args = parser.parse_args()
    
    scheduler = DealsBatchScheduler(interval_hours=args.interval)
    
    if args.once:
        # Run once only
        scheduler._setup_scrapers()
        scheduler.run_once()
    else:
        # Run continuously
        scheduler.run(max_iterations=args.max_iterations)


if __name__ == "__main__":
    main()
