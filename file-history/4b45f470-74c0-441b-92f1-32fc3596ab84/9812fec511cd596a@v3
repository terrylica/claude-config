"""
Batch processing orchestration for MQL5 article extraction.

Features:
- Checkpoint-based progress tracking
- Resume capability
- Rate limiting
- Statistics generation
- Progress reporting
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .logger import get_logger
from .config_manager import Config
from .extractor import MQL5Extractor, ExtractionError, ValidationError

logger = get_logger(__name__)


class BatchProcessor:
    """
    Orchestrates batch extraction of multiple articles.

    Features:
    - Checkpoint system for resume capability
    - Rate limiting between requests
    - Statistics aggregation
    - Error handling with continue-on-error
    """

    def __init__(self, config: Config, extractor: MQL5Extractor):
        """
        Initialize batch processor.

        Args:
            config: Configuration object
            extractor: Configured extractor instance
        """
        self.config = config
        self.extractor = extractor
        self.checkpoint_file = Path(config.batch.checkpoint_file)

        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "failed_articles": [],
            "content_stats": {
                "total_words": 0,
                "total_images": 0,
                "total_code_blocks": 0,
                "users": set()
            }
        }

        logger.info("Initialized BatchProcessor", extra={
            "checkpoint_file": str(self.checkpoint_file),
            "rate_limit": config.batch.rate_limit_seconds
        })

    async def process_urls(self, urls: List[str], resume: bool = None) -> Dict[str, Any]:
        """
        Process a list of article URLs.

        Args:
            urls: List of article URLs to process
            resume: Whether to resume from checkpoint (defaults to config)

        Returns:
            Statistics dictionary with results
        """
        if resume is None:
            resume = self.config.batch.resume_on_restart

        self.stats["total"] = len(urls)
        self.stats["start_time"] = datetime.now().isoformat()

        logger.info(f"Starting batch processing", extra={
            "total_urls": len(urls),
            "resume": resume
        })

        # Load checkpoint if resuming
        checkpoint = self._load_checkpoint() if resume else {}
        processed_urls = set(checkpoint.get("processed_urls", []))

        for i, url in enumerate(urls, 1):
            article_id = self.extractor._extract_id_from_url(url)

            # Skip if already processed
            if url in processed_urls:
                logger.info(f"Skipping already processed article [{i}/{len(urls)}]",
                           extra={"article_id": article_id, "url": url})
                self.stats["skipped"] += 1
                continue

            # Check if already exists on disk
            if self._is_already_extracted(article_id):
                logger.info(f"Skipping already extracted article [{i}/{len(urls)}]",
                           extra={"article_id": article_id})
                processed_urls.add(url)
                self.stats["skipped"] += 1
                self._save_checkpoint(list(processed_urls))
                continue

            # Extract article
            try:
                logger.info(f"Processing article [{i}/{len(urls)}]",
                           extra={"article_id": article_id, "url": url})

                result = await self.extractor.extract_article(url)

                # Update statistics
                self._update_stats(result)
                processed_urls.add(url)
                self.stats["successful"] += 1

                logger.info(f"Article extracted successfully [{i}/{len(urls)}]",
                           extra={"article_id": article_id})

            except (ExtractionError, ValidationError) as e:
                logger.error(f"Article extraction failed [{i}/{len(urls)}]: {e}",
                            extra={"article_id": article_id})

                self.stats["failed"] += 1
                self.stats["failed_articles"].append({
                    "article_id": article_id,
                    "url": url,
                    "error": str(e)
                })

                # Continue or stop based on config
                if not self.config.batch.continue_on_error:
                    logger.error("Stopping batch processing due to error")
                    break

            # Save checkpoint after each article
            self._save_checkpoint(list(processed_urls))

            # Rate limiting
            if i < len(urls):  # Don't sleep after last article
                await asyncio.sleep(self.config.batch.rate_limit_seconds)

        # Finalize statistics
        self.stats["end_time"] = datetime.now().isoformat()
        start = datetime.fromisoformat(self.stats["start_time"])
        end = datetime.fromisoformat(self.stats["end_time"])
        self.stats["duration_seconds"] = (end - start).total_seconds()

        # Convert set to list for JSON serialization
        self.stats["content_stats"]["users"] = list(self.stats["content_stats"]["users"])

        logger.info(f"Batch processing completed", extra={
            "total": self.stats["total"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "skipped": self.stats["skipped"],
            "duration": f"{self.stats['duration_seconds']:.1f}s"
        })

        return self.stats

    def _is_already_extracted(self, article_id: str) -> bool:
        """
        Check if article already exists on disk.

        Args:
            article_id: Article ID to check

        Returns:
            True if article folder exists
        """
        # Check in all user folders
        results_dir = Path(self.config.extraction.output_dir)

        if not results_dir.exists():
            return False

        for user_folder in results_dir.iterdir():
            if not user_folder.is_dir():
                continue

            article_folder = user_folder / f"article_{article_id}"
            if article_folder.exists():
                # Verify it has content
                md_file = article_folder / "article.md"
                if md_file.exists():
                    return True

        return False

    def _update_stats(self, result: Dict[str, Any]):
        """
        Update statistics with extraction result.

        Args:
            result: Extraction result dictionary
        """
        content = result.get("content", {})

        # Update content stats
        self.stats["content_stats"]["total_words"] += content.get("word_count", 0)
        self.stats["content_stats"]["total_code_blocks"] += len(content.get("code_blocks", []))

        images = content.get("images", [])
        successful_images = len([img for img in images if img.get("local_path")])
        self.stats["content_stats"]["total_images"] += successful_images

        user_id = content.get("user_id")
        if user_id and user_id != "unknown":
            self.stats["content_stats"]["users"].add(user_id)

    def _save_checkpoint(self, processed_urls: List[str]):
        """
        Save checkpoint to file.

        Args:
            processed_urls: List of processed URLs
        """
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "processed_urls": processed_urls,
            "stats": {
                "successful": self.stats["successful"],
                "failed": self.stats["failed"],
                "skipped": self.stats["skipped"]
            }
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        logger.debug(f"Checkpoint saved", extra={"processed_count": len(processed_urls)})

    def _load_checkpoint(self) -> Dict:
        """
        Load checkpoint from file.

        Returns:
            Checkpoint dictionary or empty dict if not found
        """
        if not self.checkpoint_file.exists():
            logger.debug("No checkpoint file found")
            return {}

        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)

            logger.info(f"Loaded checkpoint", extra={
                "processed_urls": len(checkpoint.get("processed_urls", [])),
                "timestamp": checkpoint.get("timestamp")
            })

            return checkpoint

        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return {}

    def clear_checkpoint(self):
        """Delete checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.info("Checkpoint cleared")

    async def save_summary(self, output_file: str = "extraction_summary.json"):
        """
        Save extraction summary to file.

        Args:
            output_file: Output file path (relative to results directory)
        """
        output_path = Path(self.config.extraction.output_dir) / output_file

        summary = {
            "summary": {
                "total": self.stats["total"],
                "successful": self.stats["successful"],
                "failed": self.stats["failed"],
                "skipped": self.stats["skipped"],
                "duration_seconds": self.stats["duration_seconds"],
                "start_time": self.stats["start_time"],
                "end_time": self.stats["end_time"]
            },
            "statistics": {
                "total_words": self.stats["content_stats"]["total_words"],
                "total_images": self.stats["content_stats"]["total_images"],
                "total_code_blocks": self.stats["content_stats"]["total_code_blocks"],
                "unique_users": len(self.stats["content_stats"]["users"]),
                "users": self.stats["content_stats"]["users"]
            },
            "failed_articles": self.stats["failed_articles"]
        }

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Summary saved to {output_path}")

        return summary

    def print_summary(self):
        """Print human-readable summary to console."""
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total articles:     {self.stats['total']}")
        print(f"Successful:         {self.stats['successful']}")
        print(f"Failed:             {self.stats['failed']}")
        print(f"Skipped:            {self.stats['skipped']}")
        print(f"Duration:           {self.stats['duration_seconds']:.1f}s")
        print()
        print("CONTENT STATISTICS")
        print("-"*60)
        print(f"Total words:        {self.stats['content_stats']['total_words']:,}")
        print(f"Total images:       {self.stats['content_stats']['total_images']}")
        print(f"Total code blocks:  {self.stats['content_stats']['total_code_blocks']}")
        print(f"Unique users:       {len(self.stats['content_stats']['users'])}")
        print("="*60)

        if self.stats["failed_articles"]:
            print("\nFAILED ARTICLES:")
            for failed in self.stats["failed_articles"]:
                print(f"  - Article {failed['article_id']}: {failed['error']}")
            print()
