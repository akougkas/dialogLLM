"""Tests for the persona parser module."""
import json
import pytest

from dialogllm.core.persona_parser import PersonaParser, PersonaParsingError
from dialogllm.models.dialogue import PersonaConfig


@pytest.fixture
def parser():
    return PersonaParser()


@pytest.fixture
def model_config():
    return {
        "name": "TestModel",
        "model_name": "test-model",
        "model_provider": "test-provider",
        "temperature": 0.7,
    }


@pytest.fixture
def valid_json_response():
    return json.dumps({
        "name": "Historical Scholar",
        "role": "Academic Historian",
        "style": "Formal and analytical",
        "background": {
            "historical_context": "Decades of academic research in medieval history",
            "expertise_areas": ["Medieval Europe", "Renaissance Art", "Ancient Rome"],
            "philosophical_stance": "Empirical and evidence-based approach"
        },
        "communication": {
            "language_pattern": "Formal academic discourse with precise terminology",
            "reasoning_approach": "Systematic analysis of historical evidence",
            "typical_references": ["Primary sources", "Archaeological findings", "Academic papers"]
        },
        "interaction": {
            "response_structure": "Clear thesis followed by supporting evidence",
            "engagement_pattern": "Socratic questioning and detailed explanations",
            "knowledge_boundaries": ["Modern history", "Scientific topics", "Current events"]
        }
    })


@pytest.fixture
def valid_text_response():
    return """
Background:
Historical Context: Decades of academic research in medieval history
Expertise Areas: Medieval Europe, Renaissance Art, Ancient Rome
Philosophical Stance: Empirical and evidence-based approach

Communication:
Language Pattern: Formal academic discourse with precise terminology
Reasoning Approach: Systematic analysis of historical evidence
Typical References: Primary sources, Archaeological findings, Academic papers

Interaction:
Response Structure: Clear thesis followed by supporting evidence
Engagement Pattern: Socratic questioning and detailed explanations
Knowledge Boundaries: Modern history, Scientific topics, Current events
"""


def test_parse_json_response(parser, model_config, valid_json_response):
    """Test parsing a valid JSON response."""
    config, warnings = parser.parse_persona_response(valid_json_response, model_config)
    
    assert isinstance(config, PersonaConfig)
    assert not warnings
    assert config.name == "Historical Scholar"
    assert config.role == "Academic Historian"
    assert config.style == "Formal and analytical"
    assert len(config.background.expertise_areas) == 3
    assert len(config.communication.typical_references) == 3
    assert len(config.interaction.knowledge_boundaries) == 3


def test_parse_text_response(parser, model_config, valid_text_response):
    """Test parsing a valid text response."""
    config, warnings = parser.parse_persona_response(valid_text_response, model_config)
    
    assert isinstance(config, PersonaConfig)
    assert config.model_name == model_config["model_name"]
    assert config.model_provider == model_config["model_provider"]
    assert config.temperature == model_config["temperature"]
    assert len(config.background.expertise_areas) == 3
    assert len(config.communication.typical_references) == 3
    assert len(config.interaction.knowledge_boundaries) == 3


def test_parse_invalid_json(parser, model_config):
    """Test parsing invalid JSON."""
    invalid_json = "{invalid json"
    with pytest.raises(PersonaParsingError):
        parser.parse_persona_response(invalid_json, model_config)


def test_parse_missing_sections(parser, model_config):
    """Test parsing response with missing sections."""
    incomplete_response = """
Background:
Historical Context: Some context
Expertise Areas: Area1, Area2
Philosophical Stance: Some stance

Communication:
Language Pattern: Some pattern
Reasoning Approach: Some approach
Typical References: Ref1, Ref2
"""
    config, warnings = parser.parse_persona_response(incomplete_response, model_config)
    
    assert isinstance(config, PersonaConfig)
    assert len(warnings) > 0  # Should have warnings about missing sections
    assert config.background.historical_context == "Some context"
    assert len(config.background.expertise_areas) == 2


def test_parse_list_field(parser):
    """Test parsing different list field formats."""
    # Comma-separated
    result = parser._parse_list_field("item1, item2, item3")
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)
    
    # Newline-separated
    result = parser._parse_list_field("item1\nitem2\nitem3")
    assert len(result) == 3
    assert all(isinstance(item, str) for item in result)
    
    # Empty input
    result = parser._parse_list_field("")
    assert len(result) == 0


def test_extract_section(parser):
    """Test extracting sections from content."""
    content = """
Background:
Historical Context: Some background info
More background

Communication:
Language Pattern: Some communication info
"""
    section = parser._extract_section(content, "Background")
    assert isinstance(section, dict)
    assert "Some background info" in section.get("historical_context", "")
    
    # Test missing section returns empty dict
    section = parser._extract_section(content, "NonexistentSection")
    assert section == {}
