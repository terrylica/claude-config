#!/usr/bin/env python3
"""
MQL5 Article Extraction CLI

Production-ready command-line interface for extracting MQL5 trading articles.

Modes:
    single              Extract a single article
    batch               Extract multiple articles from file
    discover-and-extract   Auto-discover and extract all articles

Examples:
    # Extract single article
    python mql5_extract.py single https://www.mql5.com/en/articles/19625

    # Batch processing from file
    python mql5_extract.py batch urls.txt

    # Auto-discover and extract all articles for a user
    python mql5_extract.py discover-and-extract --user-id 29210372

    # Resume interrupted batch
    python mql5_extract.py batch urls.txt --resume

    # Custom configuration
    python mql5_extract.py batch urls.txt --config custom.yaml --verbose
"""

import argparse
import asyncio
import sys
from pathlib import Path

from lib import (
    setup_logger,
    ConfigManager,
    MQL5Extractor,
    URLDiscovery,
    BatchProcessor
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MQL5 Article Extraction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Global options
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Override output directory'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser with UI (for debugging)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose logging (DEBUG level)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (ERROR level only)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Single article extraction
    single_parser = subparsers.add_parser(
        'single',
        help='Extract a single article'
    )
    single_parser.add_argument(
        'url',
        type=str,
        help='Article URL to extract'
    )

    # Batch extraction
    batch_parser = subparsers.add_parser(
        'batch',
        help='Extract multiple articles from file'
    )
    batch_parser.add_argument(
        'urls_file',
        type=str,
        help='File containing article URLs (one per line)'
    )
    batch_parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint'
    )
    batch_parser.add_argument(
        '--no-checkpoint',
        action='store_true',
        help='Disable checkpoint system'
    )
    batch_parser.add_argument(
        '--max-articles',
        type=int,
        help='Limit to N articles (for testing)'
    )

    # Discover and extract
    discover_parser = subparsers.add_parser(
        'discover-and-extract',
        help='Auto-discover and extract all articles'
    )
    discover_parser.add_argument(
        '--user-id',
        type=str,
        help='MQL5 user ID (defaults to config value)'
    )
    discover_parser.add_argument(
        '--save-urls',
        type=str,
        help='Save discovered URLs to file'
    )
    discover_parser.add_argument(
        '--max-articles',
        type=int,
        help='Limit to N articles (for testing)'
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    # Validate command
    if not args.command:
        print("Error: No command specified. Use --help for usage information.")
        sys.exit(1)

    # Load configuration
    try:
        config_mgr = ConfigManager(args.config if Path(args.config).exists() else None)
        config = config_mgr.load()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Apply CLI overrides
    overrides = {}
    if args.output:
        overrides["extraction.output_dir"] = args.output
    if args.headless:
        overrides["extraction.headless"] = True
    if args.no_headless:
        overrides["extraction.headless"] = False

    if overrides:
        config = config_mgr.apply_overrides(overrides)

    # Setup logging
    log_level = "DEBUG" if args.verbose else ("ERROR" if args.quiet else config.logging.level)
    logger = setup_logger(
        __name__,
        log_file=config.logging.file if not args.dry_run else None,
        level=log_level,
        console=config.logging.console
    )

    if args.dry_run:
        logger.info("DRY RUN MODE - No actual extraction will be performed")

    # Execute command
    try:
        if args.command == 'single':
            await handle_single(args, config, logger)
        elif args.command == 'batch':
            await handle_batch(args, config, logger)
        elif args.command == 'discover-and-extract':
            await handle_discover_and_extract(args, config, logger)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


async def handle_single(args, config, logger):
    """Handle single article extraction."""
    logger.info(f"Extracting single article: {args.url}")

    if args.dry_run:
        logger.info(f"Would extract: {args.url}")
        return

    extractor = MQL5Extractor(config)

    try:
        result = await extractor.extract_article(args.url)

        print("\n✅ Extraction successful!")
        print(f"   Article ID: {result['article_id']}")
        print(f"   Title: {result['content']['title']}")
        print(f"   Author: {result['content']['author']}")
        print(f"   User ID: {result['content']['user_id']}")
        print(f"   Word count: {result['content']['word_count']}")
        print(f"   Code blocks: {len(result['content']['code_blocks'])}")
        print(f"   Images: {len([img for img in result['content']['images'] if img.get('local_path')])}")
        print(f"   Output: {result.get('article_folder')}")

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        sys.exit(1)


async def handle_batch(args, config, logger):
    """Handle batch extraction from file."""
    urls_file = Path(args.urls_file)

    if not urls_file.exists():
        logger.error(f"URLs file not found: {urls_file}")
        sys.exit(1)

    # Load URLs
    discovery = URLDiscovery(config)
    urls = discovery.load_urls(str(urls_file))

    # Limit if specified
    if args.max_articles:
        urls = urls[:args.max_articles]
        logger.info(f"Limited to {args.max_articles} articles")

    logger.info(f"Loaded {len(urls)} URLs from {urls_file}")

    if args.dry_run:
        print(f"\nWould extract {len(urls)} articles:")
        for i, url in enumerate(urls[:5], 1):
            print(f"  {i}. {url}")
        if len(urls) > 5:
            print(f"  ... and {len(urls) - 5} more")
        return

    # Process batch
    extractor = MQL5Extractor(config)
    processor = BatchProcessor(config, extractor)

    # Clear checkpoint if not resuming
    if args.no_checkpoint:
        processor.clear_checkpoint()
        resume = False
    else:
        resume = args.resume

    stats = await processor.process_urls(urls, resume=resume)

    # Save summary
    await processor.save_summary()

    # Print results
    processor.print_summary()


async def handle_discover_and_extract(args, config, logger):
    """Handle auto-discovery and extraction."""
    user_id = args.user_id or config.discovery.default_user_id

    logger.info(f"Discovering articles for user: {user_id}")

    if args.dry_run:
        logger.info(f"Would discover and extract articles for user {user_id}")
        return

    # Discover URLs
    discovery = URLDiscovery(config)
    urls = await discovery.discover_articles(user_id)

    logger.info(f"Discovered {len(urls)} articles")

    # Save URLs if requested
    if args.save_urls:
        await discovery.save_urls(urls, args.save_urls)
        logger.info(f"URLs saved to {args.save_urls}")

    # Limit if specified
    if args.max_articles:
        urls = urls[:args.max_articles]
        logger.info(f"Limited to {args.max_articles} articles")

    # Extract all
    extractor = MQL5Extractor(config)
    processor = BatchProcessor(config, extractor)

    stats = await processor.process_urls(urls, resume=True)

    # Save summary
    await processor.save_summary()

    # Print results
    processor.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
