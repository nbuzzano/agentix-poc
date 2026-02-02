"""Data models for the translation pipeline"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import json


class QueryType(str, Enum):
    """Types of SQL queries"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"
    OTHER = "OTHER"


class TranslationStatus(str, Enum):
    """Status of translation attempt"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRIED = "RETRIED"


class ValidationStatus(str, Enum):
    """Status of validation"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class QueryMetadata:
    """Metadata about a query file"""
    file_name: str
    file_path: str
    folder_name: str
    table_name: str
    query_type: QueryType
    original_query: str
    complexity_score: float = 0.0
    has_teradata_functions: bool = False
    teradata_functions: list[str] = None
    parsed_at: str = None

    def __post_init__(self):
        if self.teradata_functions is None:
            self.teradata_functions = []
        if self.parsed_at is None:
            self.parsed_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TranslationResult:
    """Result of a translation attempt"""
    query_metadata: QueryMetadata
    translated_query: Optional[str] = None
    status: TranslationStatus = TranslationStatus.PENDING
    attempt_number: int = 1
    strategy_used: str = "basic"
    error_message: Optional[str] = None
    error_details: Optional[str] = None
    translated_at: str = None
    execution_time_ms: float = 0.0

    def __post_init__(self):
        if self.translated_at is None:
            self.translated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query_metadata": self.query_metadata.to_dict(),
            "translated_query": self.translated_query,
            "status": self.status.value,
            "attempt_number": self.attempt_number,
            "strategy_used": self.strategy_used,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "translated_at": self.translated_at,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class ValidationResult:
    """Result of query validation"""
    translation_result: TranslationResult
    status: ValidationStatus = ValidationStatus.PENDING
    passed: bool = False
    error_message: Optional[str] = None
    execution_details: Optional[str] = None
    synthetic_data_generated: bool = False
    rows_compared: int = 0
    validation_timestamp: str = None
    execution_time_ms: float = 0.0

    def __post_init__(self):
        if self.validation_timestamp is None:
            self.validation_timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "translation_result": self.translation_result.to_dict(),
            "status": self.status.value,
            "passed": self.passed,
            "error_message": self.error_message,
            "execution_details": self.execution_details,
            "synthetic_data_generated": self.synthetic_data_generated,
            "rows_compared": self.rows_compared,
            "validation_timestamp": self.validation_timestamp,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class StepResult:
    """Result of a processing step"""
    step_name: str
    status: str  # SUCCESS, FAILED, PARTIAL
    total_items: int
    successful_items: int
    failed_items: int
    details: Dict[str, Any]
    timestamp: str = None
    execution_time_ms: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100
