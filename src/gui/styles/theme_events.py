"""Theme change event handling module for application-wide theme coordination."""

import logging
from typing import Dict, Any, Optional, List, Callable, Set, Union, cast
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget


class ThemeEventBus(QObject):
    """
    Event bus for theme change notifications across the application.

    This singleton class provides a centralized way for components to subscribe
    to theme change events and respond accordingly, facilitating consistent
    visual appearance throughout the application.

    Like a town crier announcing seasonal fashion changes to the digital populace,
    this class ensures all UI components are informed of aesthetic transitions.
    """

    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)  # theme_id

    # Singleton instance
    _instance = None

    def __new__(cls) -> 'ThemeEventBus':
        """Create or return the singleton instance - a digital immortal that persists."""
        if cls._instance is None:
            cls._instance = super(ThemeEventBus, cls).__new__(cls)
            # Initialize the instance
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the theme event bus (only once), like a phoenix that refuses rebirth."""
        if self._initialized:
            return

        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._initialized = True
        self._subscribers: Set[QObject] = set()
        self.logger.debug("ThemeEventBus initialized - the aesthetic herald stands ready")

    def subscribe(self, subscriber: QObject) -> bool:
        """
        Subscribe an object to theme change notifications.

        Args:
            subscriber: Object that wants to receive theme notifications

        Returns:
            True if subscription was successful, False otherwise

        Like joining a mailing list for aesthetic announcements, this method
        registers objects to receive theme change notifications.
        """
        try:
            if subscriber in self._subscribers:
                return True  # Already subscribed - the void recognizes its child

            # Check if subscriber has a theme_changed attribute that is a signal
            has_signal = hasattr(subscriber, 'theme_changed') and isinstance(
                getattr(subscriber, 'theme_changed'), pyqtSignal
            )

            # Check if subscriber has an apply_theme method
            has_method = hasattr(subscriber, 'apply_theme') and callable(
                getattr(subscriber, 'apply_theme')
            )

            if has_signal:
                # Connect our signal to the subscriber's signal
                self.theme_changed.connect(subscriber.theme_changed)
                self._subscribers.add(subscriber)
                self.logger.debug(f"Subscribed {subscriber.__class__.__name__} via signal")
                return True
            elif has_method:
                # Connect our signal to the subscriber's apply_theme method
                self.theme_changed.connect(subscriber.apply_theme)
                self._subscribers.add(subscriber)
                self.logger.debug(f"Subscribed {subscriber.__class__.__name__} via method")
                return True
            else:
                self.logger.warning(
                    f"Could not subscribe {subscriber.__class__.__name__}: "
                    "missing theme_changed signal or apply_theme method - "
                    "like whispering to the deaf, our aesthetic signals fall on unresponsive components"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error subscribing to theme events: {str(e)}")
            return False

    def unsubscribe(self, subscriber: QObject) -> bool:
        """
        Unsubscribe an object from theme change notifications.

        Args:
            subscriber: Object that no longer wants theme notifications

        Returns:
            True if unsubscription was successful, False otherwise

        Like canceling a subscription to an aesthetic newsletter, this method
        removes objects from the theme change notification list.
        """
        try:
            if subscriber not in self._subscribers:
                return False  # Not subscribed - a stranger to our aesthetic realm

            # Disconnect from signal if it exists
            if hasattr(subscriber, 'theme_changed') and isinstance(
                    getattr(subscriber, 'theme_changed'), pyqtSignal
            ):
                try:
                    self.theme_changed.disconnect(subscriber.theme_changed)
                except TypeError:
                    # Signal might not be connected - the connection that never was
                    pass

            # Disconnect from method if it exists
            if hasattr(subscriber, 'apply_theme') and callable(
                    getattr(subscriber, 'apply_theme')
            ):
                try:
                    self.theme_changed.disconnect(subscriber.apply_theme)
                except TypeError:
                    # Method might not be connected - the bond that never formed
                    pass

            self._subscribers.remove(subscriber)
            self.logger.debug(f"Unsubscribed {subscriber.__class__.__name__} - another listener returns to the void")
            return True

        except Exception as e:
            self.logger.error(f"Error unsubscribing from theme events: {str(e)}")
            return False

    def notify_theme_change(self, theme_id: str) -> None:
        """
        Notify all subscribers of a theme change.

        Args:
            theme_id: Identifier of the new theme being applied

        Like announcing a sudden wardrobe change to attentive onlookers,
        this method broadcasts theme transitions to all interested parties.
        """
        try:
            # Log with subscriber count for better diagnostics
            subscriber_count = len(self._subscribers)
            self.logger.info(f"Broadcasting theme change to {subscriber_count} subscribers: {theme_id}")

            if subscriber_count == 0:
                self.logger.warning("No subscribers to notify - our aesthetic proclamation echoes in an empty hall")

            # Emit the signal to notify subscribers
            self.theme_changed.emit(theme_id)

        except Exception as e:
            self.logger.error(f"Error notifying theme change: {str(e)}")

    def get_subscriber_count(self) -> int:
        """
        Get the number of current subscribers.

        Returns:
            Count of subscribed objects

        Like checking the circulation numbers of our aesthetic newsletter,
        this method reveals how many components are listening for theme changes.
        """
        return len(self._subscribers)

    def get_subscribers(self) -> List[str]:
        """
        Get a list of subscriber class names for debugging.

        Returns:
            List of subscriber class names

        Like taking attendance in our aesthetic lecture hall,
        this method catalogs the eager listeners awaiting our stylistic proclamations.
        """
        try:
            return [subscriber.__class__.__name__ for subscriber in self._subscribers]
        except Exception as e:
            self.logger.error(f"Error getting subscriber list: {str(e)}")
            return ["<Error retrieving subscribers>"]


# Convenience function to get the singleton instance
def get_theme_event_bus() -> ThemeEventBus:
    """
    Get the singleton theme event bus instance.

    Returns:
        ThemeEventBus singleton instance

    Like obtaining the contact details of our town's aesthetic herald,
    this function provides access to the theme notification system.
    """
    return ThemeEventBus()