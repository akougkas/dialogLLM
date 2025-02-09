class HealthMonitor:
    def __init__(self, client):
        self.client = client

    async def check_health(self):
        """Perform health checks on client components."""
        queue_status = await self._check_queue_connection()
        # Add checks for other components like message processor if needed
        status = "healthy" if queue_status == "connected" else "unhealthy"
        return {
            "status": status,
            "queue_connection": queue_status,
            # "message_processor": processor_status,
        }

    async def _check_queue_connection(self):
        """Check the status of the queue connection."""
        try:
            await self.client.queue_manager._redis_client.ping()
            return "connected"
        except Exception as e:
            return "disconnected"

    # Add other health check methods as needed