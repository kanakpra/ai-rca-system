import time
import logging
import functools
import threading
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerOpenError(Exception):
    """Exception raised when a circuit breaker is open."""
    pass

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to detect and prevent retry storms.
    """
    def __init__(self,
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 30,
                 half_open_test_attempts: int = 1):
        """
        Initializes a Circuit Breaker.

        Args:
            name: A unique name for this circuit breaker instance.
            failure_threshold: Number of consecutive failures before opening the circuit.
            recovery_timeout: Time in seconds the circuit stays open before transitioning to half-open.
            half_open_test_attempts: Number of successful attempts required in half-open state to close the circuit.
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than 0")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be greater than 0")
        if half_open_test_attempts <= 0:
            raise ValueError("half_open_test_attempts must be greater than 0")

        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_test_attempts = half_open_test_attempts

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_success_count = 0
        self._lock = threading.Lock() # For in-process thread safety. For distributed systems, use a distributed lock/state store.

        logger.info(f"Circuit Breaker '{self.name}' initialized: "
                    f"failure_threshold={self.failure_threshold}, "
                    f"recovery_timeout={self.recovery_timeout}s, "
                    f"half_open_test_attempts={self.half_open_test_attempts}")

    def _change_state(self, new_state: CircuitBreakerState):
        """Changes the state of the circuit breaker."""
        if self._state != new_state:
            log_level = logging.WARNING
            message = f"Circuit Breaker '{self.name}' state changed from {self._state.value} to {new_state.value}"
            if new_state == CircuitBreakerState.OPEN:
                log_level = logging.ERROR
                message += f". Blocking calls for {self.recovery_timeout}s. Retry storm detected!"
            logger.log(log_level, message)
            self._state = new_state
            if new_state == CircuitBreakerState.CLOSED:
                self._reset()

    def _reset(self):
        """Resets failure counts and timestamps."""
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_success_count = 0

    def _is_open(self) -> bool:
        """
        Checks if the circuit is currently open or should transition to half-open.
        Returns True if the circuit is open and should block calls.
        """
        if self._state == CircuitBreakerState.CLOSED:
            return False

        if self._state == CircuitBreakerState.OPEN:
            if self._last_failure_time is not None and \
               (time.monotonic() - self._last_failure_time) > self.recovery_timeout:
                # Time to transition to half-open
                self._change_state(CircuitBreakerState.HALF_OPEN)
                return False  # Allow one test call in half-open
            return True  # Still open, block call

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Allow calls in half-open, decisions on success/failure will drive state changes
            return False

        return False

    def _record_success(self):
        """Records a successful operation."""
        with self._lock:
            if self._state == CircuitBreakerState.CLOSED:
                self._reset()  # Reset consecutive failure count on success
            elif self._state == CircuitBreakerState.HALF_OPEN:
                self._half_open_success_count += 1
                if self._half_open_success_count >= self.half_open_test_attempts:
                    self._change_state(CircuitBreakerState.CLOSED)
                    logger.info(f"Circuit Breaker '{self.name}' closed after successful half-open tests.")

    def _record_failure(self):
        """Records a failed operation."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitBreakerState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._change_state(CircuitBreakerState.OPEN)
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # If a failure occurs in half-open, immediately go back to open
                self._change_state(CircuitBreakerState.OPEN)
                logger.warning(f"Circuit Breaker '{self.name}' re-opened after failure in half-open state.")


    def __call__(self, func):
        """Decorator for circuit breaker."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with self._lock:
                if self._is_open():
                    logger.warning(f"Circuit Breaker '{self.name}' is {self._state.value}. Blocking call to {func.__name__}.")
                    raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is {self._state.value}.")

            try:
                # Execute the wrapped function
                result = await func(*args, **kwargs)
                self._record_success()
                return result
            except CircuitBreakerOpenError:
                # Re-raise our own exception without recording a failure again
                raise
            except Exception as e:
                self._record_failure()
                logger.error(f"Circuit Breaker '{self.name}': Call to {func.__name__} failed with {type(e).__name__}: {e}")
                raise # Re-raise the original exception

        return wrapper

# Global (or module-level) instances of circuit breakers.
# In a real application, these might be managed by a dependency injection system or a factory.
# Each external dependency or critical internal operation that can fail independently
# should have its own circuit breaker instance.

ai_inference_breaker = CircuitBreaker(
    name="AI_Inference_Service_Breaker",
    failure_threshold=3,      # Fail 3 times consecutively
    recovery_timeout=60,      # Stay open for 60 seconds
    half_open_test_attempts=1 # One successful call to close
)

timeline_db_breaker = CircuitBreaker(
    name="Timeline_DB_Query_Breaker",
    failure_threshold=5,
    recovery_timeout=30,
    half_open_test_attempts=2
)

class AIRCACorrelationEngine:
    """
    Simulated AI RCA Correlation Engine.
    This class would typically contain methods for:
    - Fetching raw events
    - Preprocessing events
    - Correlating events based on time, entities, etc.
    - Calling AI models for reasoning
    - Storing correlated timelines
    - Scoring severity
    """

    def __init__(self):
        logger.info("AIRCACorrelationEngine initialized.")

    @ai_inference_breaker
    async def _call_ai_reasoning_service(self, event_data: dict) -> dict:
        """
        Simulates calling an external AI reasoning service.
        This is where retry storms could occur if the service is unstable.
        """
        logger.debug(f"Calling AI reasoning service for data: {event_data.get('id', 'N/A')}")
        # Simulate an external call that might fail
        # For demonstration: if 'fail_ai' is True in event_data, raise an error
        if event_data.get('fail_ai'):
           logger.error(f"Simulated AI service failure for event {event_data.get('id')}!")
           raise ConnectionError("AI service unavailable")

        await asyncio.sleep(0.1) # Simulate network latency or processing time
        return {"rca_result": f"Reasoning for {event_data.get('id')}", "confidence": 0.95}

    @timeline_db_breaker
    async def _store_correlated_timeline(self, correlated_data: dict) -> bool:
        """
        Simulates storing correlated timeline data into a database.
        This is another point of failure where a retry storm could happen against the DB.
        """
        logger.debug(f"Storing correlated timeline: {correlated_data.get('timeline_id', 'N/A')}")
        # Simulate database operation that might fail
        # For demonstration: if 'fail_db' is True in correlated_data, raise an error
        if correlated_data.get('fail_db'):
           logger.error(f"Simulated DB storage failure for timeline {correlated_data.get('timeline_id')}!")
           raise ConnectionRefusedError("Database connection lost")

        await asyncio.sleep(0.05) # Simulate database write time
        return True

    async def perform_rca_correlation(self, raw_events: list[dict]) -> list[dict]:
        """
        Main method to perform RCA correlation.
        """
        correlated_results = []
        for event in raw_events:
            try:
                # Step 1: Call AI for initial reasoning (protected by ai_inference_breaker)
                reasoning = await self._call_ai_reasoning_service(event)

                # Step 2: Perform timeline correlation logic
                timeline_id = f"timeline_{event.get('id')}_{int(time.time())}"
                correlated_event = {
                    "event_id": event.get('id'),
                    "timestamp": event.get('timestamp'),
                    "reasoning": reasoning,
                    "timeline_id": timeline_id,
                    "correlated_components": ["service_A", "db_B"] # Example
                }

                # Step 3: Store the correlated timeline (protected by timeline_db_breaker)
                stored = await self._store_correlated_timeline(correlated_event)
                if stored:
                    correlated_results.append(correlated_event)
                else:
                    logger.error(f"Failed to store correlated event for {event.get('id')}")

            except CircuitBreakerOpenError as cboe:
                logger.error(f"Operation blocked by circuit breaker: {cboe}. Skipping event {event.get('id')}")
                # Depending on business logic, here you might:
                # - Queue the event for later processing
                # - Return a partial result or a specific error code
                # - Degrade functionality (e.g., use a cached/fallback reasoning)
            except Exception as e:
                logger.error(f"Unhandled error processing event {event.get('id')}: {e}", exc_info=True)
                # General error handling for other exceptions not caught by circuit breaker