"""Models for dialogue configuration and management."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class DialoguePhase(str, Enum):
    """Phases of a dialogue."""
    INTRODUCTION = "introduction"
    EXPLORATION = "exploration"
    CHALLENGE = "challenge"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class DialogueConfig(BaseModel):
    """Configuration for dialogue execution."""
    duration_minutes: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Duration of the dialogue in minutes"
    )
    exchange_count: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of exchanges between models"
    )
    pause_between_exchanges: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Pause duration between exchanges in seconds"
    )


class PersonaBackground(BaseModel):
    """Background information for a persona."""
    historical_context: str = Field(..., min_length=10)
    expertise_areas: List[str] = Field(..., min_items=1)
    philosophical_stance: str = Field(..., min_length=10)


class CommunicationStyle(BaseModel):
    """Communication style for a persona."""
    language_pattern: str = Field(..., min_length=10)
    reasoning_approach: str = Field(..., min_length=10)
    typical_references: List[str] = Field(default_factory=list)


class InteractionGuidelines(BaseModel):
    """Guidelines for persona interaction."""
    response_structure: str = Field(..., min_length=10)
    engagement_pattern: str = Field(..., min_length=10)
    knowledge_boundaries: List[str] = Field(default_factory=list)


class PersonaConfig(BaseModel):
    """Configuration for a dialogue persona."""
    name: str = Field(..., min_length=1)
    role: str = Field(..., min_length=10)
    style: str = Field(..., min_length=10)
    model_name: str = Field(..., min_length=1)
    model_provider: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=0.0, le=1.0)
    background: PersonaBackground
    communication: CommunicationStyle
    interaction: InteractionGuidelines
    created_at: datetime = Field(default_factory=datetime.now)

    @validator("temperature")
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class StoryConstraints(BaseModel):
    """Constraints for story generation."""
    topic_areas: List[str] = Field(..., min_items=1)
    complexity: str = Field(..., min_length=5)
    tone: str = Field(..., min_length=5)


class DialoguePhaseConfig(BaseModel):
    """Configuration for a dialogue phase."""
    name: DialoguePhase
    description: str = Field(..., min_length=10)
    min_exchanges: int = Field(default=1, ge=1)
    max_exchanges: int = Field(default=5, ge=1)

    @validator("max_exchanges")
    def validate_max_exchanges(cls, v: int, values: Dict) -> int:
        """Ensure max_exchanges is greater than min_exchanges."""
        if "min_exchanges" in values and v < values["min_exchanges"]:
            raise ValueError("max_exchanges must be greater than min_exchanges")
        return v


class DialogueProgressionConfig(BaseModel):
    """Configuration for dialogue progression."""
    phases: List[DialoguePhaseConfig] = Field(..., min_items=1)
    current_phase: DialoguePhase = Field(default=DialoguePhase.INTRODUCTION)
    phase_transition_rules: Dict[str, str] = Field(default_factory=dict)


class DialogueState(BaseModel):
    """Current state of the dialogue."""
    config: DialogueConfig
    progression: DialogueProgressionConfig
    personas: List[PersonaConfig]
    start_time: datetime = Field(default_factory=datetime.now)
    last_exchange_time: Optional[datetime] = None
    exchange_count: int = Field(default=0, ge=0)
    is_concluded: bool = Field(default=False)

    def is_time_exceeded(self) -> bool:
        """Check if dialogue duration has been exceeded."""
        if not self.start_time:
            return False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed >= (self.config.duration_minutes * 60)

    def is_exchanges_exceeded(self) -> bool:
        """Check if maximum exchanges have been reached."""
        return self.exchange_count >= self.config.exchange_count

    def should_conclude(self) -> bool:
        """Check if dialogue should conclude."""
        return (
            self.is_time_exceeded() or
            self.is_exchanges_exceeded() or
            self.is_concluded
        )
