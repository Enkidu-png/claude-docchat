"""
File system monitoring service with watchdog integration.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent, FileMovedEvent
except ImportError:
    raise ImportError("watchdog is required for file monitoring. Install with: pip install watchdog")

from ..config.settings import get_settings
from ..models.enums import DocumentType, FileMonitorEventType


class DocumentEventHandler(FileSystemEventHandler):
    """Custom event handler for document file changes."""

    def __init__(self, callback: Callable, supported_extensions: Set[str]):
        super().__init__()
        self.callback = callback
        self.supported_extensions = supported_extensions
        self.logger = logging.getLogger(__name__)

    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._is_supported_file(event.src_path):
            asyncio.create_task(self.callback(
                event_type=FileMonitorEventType.CREATED,
                file_path=event.src_path,
                event_time=datetime.utcnow()
            ))

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._is_supported_file(event.src_path):
            asyncio.create_task(self.callback(
                event_type=FileMonitorEventType.MODIFIED,
                file_path=event.src_path,
                event_time=datetime.utcnow()
            ))

    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and self._is_supported_file(event.src_path):
            asyncio.create_task(self.callback(
                event_type=FileMonitorEventType.DELETED,
                file_path=event.src_path,
                event_time=datetime.utcnow()
            ))

    def on_moved(self, event):
        """Handle file move/rename events."""
        if not event.is_directory:
            # Handle both source and destination if supported
            if self._is_supported_file(event.src_path):
                asyncio.create_task(self.callback(
                    event_type=FileMonitorEventType.DELETED,
                    file_path=event.src_path,
                    event_time=datetime.utcnow()
                ))

            if self._is_supported_file(event.dest_path):
                asyncio.create_task(self.callback(
                    event_type=FileMonitorEventType.MOVED,
                    file_path=event.dest_path,
                    event_time=datetime.utcnow()
                ))


class FileMonitorService:
    """Service for monitoring file system changes and triggering re-indexing."""

    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.observer = Observer()
        self.watched_folders: Dict[str, bool] = {}  # folder_path -> recursive
        self.event_callbacks: List[Callable] = []
        self.supported_extensions = set(DocumentType.get_supported_extensions())
        self._is_running = False

        # Debouncing to avoid multiple events for the same file
        self._pending_events: Dict[str, datetime] = {}
        self._debounce_delay = 2.0  # seconds

    async def add_event_callback(self, callback: Callable) -> None:
        """
        Add callback function to be called on file events.

        Args:
            callback: Async function that takes (event_type, file_path, event_time)
        """
        self.event_callbacks.append(callback)

    async def watch_folder(self, folder_path: str, recursive: bool = True) -> bool:
        """
        Start monitoring a folder for document changes.

        Args:
            folder_path: Path to folder to monitor
            recursive: Whether to monitor subfolders

        Returns:
            True if monitoring started successfully

        Raises:
            FileNotFoundError: If folder doesn't exist
        """
        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        if not folder.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        # Check if already watching
        if folder_path in self.watched_folders:
            self.logger.info(f"Already monitoring folder: {folder_path}")
            return True

        try:
            # Create event handler
            event_handler = DocumentEventHandler(
                callback=self._handle_file_event,
                supported_extensions=self.supported_extensions
            )

            # Start watching
            self.observer.schedule(
                event_handler,
                str(folder),
                recursive=recursive
            )

            self.watched_folders[folder_path] = recursive

            # Start observer if not already running
            if not self._is_running:
                self.observer.start()
                self._is_running = True

            self.logger.info(f"Started monitoring folder: {folder_path} (recursive: {recursive})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start monitoring {folder_path}: {e}")
            return False

    async def stop_watching_folder(self, folder_path: str) -> bool:
        """
        Stop monitoring a specific folder.

        Args:
            folder_path: Path to folder to stop monitoring

        Returns:
            True if successfully stopped
        """
        if folder_path not in self.watched_folders:
            return False

        try:
            # Remove from watched folders
            del self.watched_folders[folder_path]

            # If no more folders being watched, stop observer
            if not self.watched_folders and self._is_running:
                self.observer.stop()
                self.observer.join()
                self._is_running = False

            self.logger.info(f"Stopped monitoring folder: {folder_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring {folder_path}: {e}")
            return False

    async def stop_all_monitoring(self) -> None:
        """Stop monitoring all folders."""
        try:
            if self._is_running:
                self.observer.stop()
                self.observer.join()
                self._is_running = False

            self.watched_folders.clear()
            self.logger.info("Stopped all file monitoring")

        except Exception as e:
            self.logger.error(f"Failed to stop file monitoring: {e}")

    async def _handle_file_event(self, event_type: FileMonitorEventType, file_path: str, event_time: datetime) -> None:
        """
        Handle file system events with debouncing.

        Args:
            event_type: Type of file system event
            file_path: Path to affected file
            event_time: When event occurred
        """
        # Debouncing - avoid duplicate events for same file
        if file_path in self._pending_events:
            time_diff = (event_time - self._pending_events[file_path]).total_seconds()
            if time_diff < self._debounce_delay:
                return  # Skip duplicate event

        self._pending_events[file_path] = event_time

        try:
            self.logger.info(f"File event: {event_type.value} - {file_path}")

            # Call all registered callbacks
            for callback in self.event_callbacks:
                try:
                    await callback(event_type, file_path, event_time)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")

            # Clean up old pending events
            await self._cleanup_pending_events(event_time)

        except Exception as e:
            self.logger.error(f"Error handling file event: {e}")

    async def _cleanup_pending_events(self, current_time: datetime) -> None:
        """Clean up old pending events to prevent memory buildup."""
        cutoff_time = current_time.timestamp() - (self._debounce_delay * 2)

        to_remove = [
            file_path for file_path, event_time in self._pending_events.items()
            if event_time.timestamp() < cutoff_time
        ]

        for file_path in to_remove:
            del self._pending_events[file_path]

    def get_watched_folders(self) -> Dict[str, bool]:
        """Get currently watched folders and their recursive settings."""
        return self.watched_folders.copy()

    def is_monitoring(self, folder_path: str) -> bool:
        """Check if a folder is currently being monitored."""
        return folder_path in self.watched_folders

    def is_file_indexed(self, file_path: str) -> bool:
        """
        Check if a file has been indexed (placeholder implementation).

        Args:
            file_path: Path to file

        Returns:
            True if file is indexed
        """
        # This is a placeholder - in real implementation, this would
        # check with the indexing service
        return False

    async def force_rescan(self, folder_path: str) -> int:
        """
        Force a manual rescan of a monitored folder.

        Args:
            folder_path: Path to folder to rescan

        Returns:
            Number of documents found

        Raises:
            ValueError: If folder is not being monitored
        """
        if folder_path not in self.watched_folders:
            raise ValueError(f"Folder is not being monitored: {folder_path}")

        folder = Path(folder_path)
        recursive = self.watched_folders[folder_path]
        documents_found = 0

        try:
            # Discover all supported documents
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"

            for ext in self.supported_extensions:
                for file_path in folder.glob(f"{pattern}{ext}"):
                    if file_path.is_file():
                        # Trigger created event for each document
                        await self._handle_file_event(
                            FileMonitorEventType.CREATED,
                            str(file_path),
                            datetime.utcnow()
                        )
                        documents_found += 1

            self.logger.info(f"Forced rescan of {folder_path}: found {documents_found} documents")
            return documents_found

        except Exception as e:
            self.logger.error(f"Error during forced rescan: {e}")
            return 0