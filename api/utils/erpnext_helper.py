"""
ERPNext Sync Helper Functions
Optimized for 4GB RAM constraint with efficient query handling
"""
from django.utils import timezone
from django.db import transaction
from .models import ERPNextSyncLog
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ERPNextSyncHelper:
    """Helper class for managing ERPNext synchronization logs"""
    
    @staticmethod
    def start_sync(action: str, message: str = None) -> ERPNextSyncLog:
        """
        Create a new sync log entry when synchronization starts
        
        Args:
            action: The synchronization action being performed
            message: Optional message describing the sync operation
            
        Returns:
            ERPNextSyncLog: The created log entry
        """
        try:
            with transaction.atomic():
                sync_log = ERPNextSyncLog.objects.create(
                    action=action,
                    status='running',
                    message=message or f"Starting {action}",
                    records_synced=0
                )
                logger.info(f"Started sync: {action} - ID: {sync_log.id}")
                return sync_log
        except Exception as e:
            logger.error(f"Failed to create sync log for {action}: {str(e)}")
            raise
    
    @staticmethod
    def complete_sync(
        sync_log: ERPNextSyncLog, 
        records_synced: int = 0, 
        message: str = None
    ) -> ERPNextSyncLog:
        """
        Update sync log when synchronization completes successfully
        
        Args:
            sync_log: The sync log entry to update
            records_synced: Number of records synchronized
            message: Optional completion message
            
        Returns:
            ERPNextSyncLog: The updated log entry
        """
        try:
            with transaction.atomic():
                sync_log.status = 'completed'
                sync_log.records_synced = records_synced
                sync_log.message = message or f"Successfully completed {sync_log.action}"
                sync_log.error_message = None
                sync_log.save()
                logger.info(f"Completed sync: {sync_log.action} - ID: {sync_log.id} - Records: {records_synced}")
                return sync_log
        except Exception as e:
            logger.error(f"Failed to update sync log {sync_log.id}: {str(e)}")
            raise
    
    @staticmethod
    def fail_sync(
        sync_log: ERPNextSyncLog, 
        error_message: str, 
        records_synced: int = 0
    ) -> ERPNextSyncLog:
        """
        Update sync log when synchronization fails
        
        Args:
            sync_log: The sync log entry to update
            error_message: Error message describing the failure
            records_synced: Number of records synced before failure
            
        Returns:
            ERPNextSyncLog: The updated log entry
        """
        try:
            with transaction.atomic():
                sync_log.status = 'failed'
                sync_log.records_synced = records_synced
                sync_log.error_message = error_message
                sync_log.message = f"Failed to complete {sync_log.action}"
                sync_log.save()
                logger.error(f"Failed sync: {sync_log.action} - ID: {sync_log.id} - Error: {error_message}")
                return sync_log
        except Exception as e:
            logger.error(f"Failed to update sync log {sync_log.id} with failure: {str(e)}")
            raise
    
    @staticmethod
    def get_recent_logs(limit: int = 50, status_filter: str = None) -> list:
        """
        Get recent synchronization logs with optional status filtering
        Optimized for memory efficiency with select_related and defer
        
        Args:
            limit: Maximum number of logs to retrieve
            status_filter: Optional status filter ('running', 'completed', 'failed')
            
        Returns:
            list: List of ERPNextSyncLog objects
        """
        try:
            queryset = ERPNextSyncLog.objects.all()
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Optimize query for memory efficiency
            logs = queryset.select_related().defer(
                'message',  # Defer large text fields unless needed
                'error_message'
            ).order_by('-timestamp')[:limit]
            
            return list(logs)
        except Exception as e:
            logger.error(f"Failed to retrieve sync logs: {str(e)}")
            return []
    
    @staticmethod
    def get_sync_statistics() -> Dict[str, Any]:
        """
        Get synchronization statistics for dashboard display
        Uses efficient aggregation queries
        
        Returns:
            Dict with sync statistics
        """
        try:
            from django.db.models import Count, Q
            
            stats = ERPNextSyncLog.objects.aggregate(
                total_syncs=Count('id'),
                completed_syncs=Count('id', filter=Q(status='completed')),
                failed_syncs=Count('id', filter=Q(status='failed')),
                running_syncs=Count('id', filter=Q(status='running')),
                total_records_synced=Sum('records_synced')
            )
            
            # Calculate success rate
            total_completed = stats['completed_syncs'] + stats['failed_syncs']
            success_rate = (stats['completed_syncs'] / total_completed * 100) if total_completed > 0 else 0
            
            return {
                **stats,
                'success_rate': round(success_rate, 2),
                'last_sync': ERPNextSyncLog.objects.order_by('-timestamp').first()
            }
        except Exception as e:
            logger.error(f"Failed to get sync statistics: {str(e)}")
            return {}
    
    @staticmethod
    def cleanup_old_logs(days_to_keep: int = 30) -> int:
        """
        Clean up old sync logs to prevent database bloat
        Optimized for batch processing to avoid memory issues
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            int: Number of logs deleted
        """
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
            
            # Use bulk delete with batches to avoid memory issues
            deleted_count = 0
            batch_size = 1000
            
            while True:
                batch_ids = ERPNextSyncLog.objects.filter(
                    timestamp__lt=cutoff_date
                ).values_list('id', flat=True)[:batch_size]
                
                if not batch_ids:
                    break
                
                deleted, _ = ERPNextSyncLog.objects.filter(id__in=batch_ids).delete()
                deleted_count += deleted
                
                logger.info(f"Cleaned up {deleted} old sync logs (total: {deleted_count})")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old sync logs: {str(e)}")
            return 0


# Import Sum for statistics
from django.db.models import Sum
