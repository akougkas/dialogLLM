"""Persona parsing and validation module."""
import json
import logging
from typing import Dict, List, Optional, Tuple

from dialogllm.models.dialogue import (
    CommunicationStyle,
    InteractionGuidelines,
    PersonaBackground,
    PersonaConfig,
)
from dialogllm.utils.logger import setup_logger

logger = setup_logger(__name__)


class PersonaParsingError(Exception):
    """Raised when persona parsing fails."""
    pass


class PersonaParser:
    """Parser for LLM-generated persona descriptions."""

    EXPECTED_SECTIONS = {
        "background": ["historical_context", "expertise_areas", "philosophical_stance"],
        "communication": ["language_pattern", "reasoning_approach", "typical_references"],
        "interaction": ["response_structure", "engagement_pattern", "knowledge_boundaries"],
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _extract_json_safely(self, content: str) -> Optional[Dict]:
        """Safely extract JSON from the content, handling various formats."""
        try:
            # Try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON-like structure in the text
            try:
                start_idx = content.find("{")
                end_idx = content.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx + 1]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                self.logger.warning("Failed to extract JSON from content", extra={"content": content})
                return None

    def _parse_list_field(self, text: str) -> List[str]:
        """Parse a comma-separated or newline-separated list."""
        if not text:
            return []
        
        # Try different separators
        if "," in text:
            items = [item.strip() for item in text.split(",")]
        else:
            items = [item.strip() for item in text.splitlines()]
        
        return [item for item in items if item]

    def _extract_section(self, content: str, section_name: str) -> Dict:
        """Extract a specific section from the content."""
        try:
            # Split and clean lines
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            section_start = -1
            section_end = -1
            
            # Find section boundaries
            for i, line in enumerate(lines):
                if line.lower().startswith(f"{section_name.lower()}:"):
                    section_start = i
                elif (section_start != -1 and i > section_start and 
                      (not line or any(s.lower() + ":" in line.lower() 
                                     for s in self.EXPECTED_SECTIONS.keys()))):
                    section_end = i
                    break
            
            if section_start == -1:
                # Return empty dict for missing sections
                return {}
            
            if section_end == -1:
                section_end = len(lines)
            
            # Extract and parse section content
            section_content = "\n".join(lines[section_start + 1:section_end])
            return self._parse_section_content(section_content)
            
        except Exception as e:
            self.logger.warning(f"Error extracting section {section_name}: {str(e)}")
            return {}

    def _parse_section_content(self, content: str) -> Dict:
        """Parse the content of a section into a dictionary."""
        result = {}
        current_key = None
        current_lines = []
        
        # Split and clean lines
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        for line in lines:
            # Check if this is a new field
            if ":" in line and not line.startswith(" "):
                # Save previous field if it exists
                if current_key:
                    result[current_key] = "\n".join(current_lines).strip()
                    current_lines = []
                
                # Parse new field
                key, value = [x.strip() for x in line.split(":", 1)]
                current_key = key.lower().replace(" ", "_")
                if value:  # Add first value if it exists
                    current_lines.append(value)
            elif current_key and line:  # Continue previous field
                current_lines.append(line)
        
        # Save last field
        if current_key and current_lines:
            result[current_key] = "\n".join(current_lines).strip()
        
        return result

    def parse_persona_response(
        self, content: str, model_config: Dict
    ) -> Tuple[PersonaConfig, List[str]]:
        """Parse the LLM response into a PersonaConfig object.
        
        Args:
            content: The raw LLM response text
            model_config: Configuration for the model (name, provider, temperature)
            
        Returns:
            Tuple of (PersonaConfig, list of warnings)
        """
        warnings = []
        try:
            # First try JSON parsing
            json_data = self._extract_json_safely(content)
            if json_data:
                return self._parse_from_json(json_data, model_config)
            
            # Fallback to text parsing
            sections = {
                "background": self._extract_section(content, "Background"),
                "communication": self._extract_section(content, "Communication"),
                "interaction": self._extract_section(content, "Interaction"),
            }
            
            # Validate sections
            for section, expected_fields in self.EXPECTED_SECTIONS.items():
                missing = [f for f in expected_fields if f not in sections[section]]
                if missing:
                    warnings.append(f"Missing fields in {section}: {', '.join(missing)}")
            
            # Create the components with default values for missing fields
            background = PersonaBackground(
                historical_context=sections["background"].get("historical_context", "Default historical context"),
                expertise_areas=self._parse_list_field(
                    sections["background"].get("expertise_areas", "General knowledge")
                ),
                philosophical_stance=sections["background"].get("philosophical_stance", "Balanced and objective approach"),
            )
            
            communication = CommunicationStyle(
                language_pattern=sections["communication"].get("language_pattern", "Clear and concise communication"),
                reasoning_approach=sections["communication"].get("reasoning_approach", "Logical and structured thinking"),
                typical_references=self._parse_list_field(
                    sections["communication"].get("typical_references", "")
                ),
            )
            
            interaction = InteractionGuidelines(
                response_structure=sections["interaction"].get("response_structure", "Organized and systematic responses"),
                engagement_pattern=sections["interaction"].get("engagement_pattern", "Professional and respectful engagement"),
                knowledge_boundaries=self._parse_list_field(
                    sections["interaction"].get("knowledge_boundaries", "")
                ),
            )
            
            # Create the full config
            return PersonaConfig(
                name=model_config.get("name", "Unknown"),
                role=sections["background"].get("historical_context", "")[:100],  # Use first 100 chars as role
                style=sections["communication"].get("language_pattern", "")[:100],  # Use first 100 chars as style
                model_name=model_config["model_name"],
                model_provider=model_config["model_provider"],
                temperature=model_config["temperature"],
                background=background,
                communication=communication,
                interaction=interaction,
            ), warnings
            
        except Exception as e:
            raise PersonaParsingError(f"Failed to parse persona: {str(e)}")

    def _parse_from_json(
        self, data: Dict, model_config: Dict
    ) -> Tuple[PersonaConfig, List[str]]:
        """Parse persona from JSON format."""
        warnings = []
        try:
            # Create components from JSON data with default values
            background = PersonaBackground(
                historical_context=data.get("background", {}).get("historical_context", "Default historical context"),
                expertise_areas=data.get("background", {}).get("expertise_areas", ["General knowledge"]),
                philosophical_stance=data.get("background", {}).get("philosophical_stance", "Balanced and objective approach"),
            )
            
            communication = CommunicationStyle(
                language_pattern=data.get("communication", {}).get("language_pattern", "Clear and concise communication"),
                reasoning_approach=data.get("communication", {}).get("reasoning_approach", "Logical and structured thinking"),
                typical_references=data.get("communication", {}).get("typical_references", []),
            )
            
            interaction = InteractionGuidelines(
                response_structure=data.get("interaction", {}).get("response_structure", "Organized and systematic responses"),
                engagement_pattern=data.get("interaction", {}).get("engagement_pattern", "Professional and respectful engagement"),
                knowledge_boundaries=data.get("interaction", {}).get("knowledge_boundaries", []),
            )
            
            return PersonaConfig(
                name=data.get("name", model_config.get("name", "Unknown")),
                role=data.get("role", background.historical_context[:100]),
                style=data.get("style", communication.language_pattern[:100]),
                model_name=model_config["model_name"],
                model_provider=model_config["model_provider"],
                temperature=model_config["temperature"],
                background=background,
                communication=communication,
                interaction=interaction,
            ), warnings
            
        except Exception as e:
            raise PersonaParsingError(f"Failed to parse JSON persona: {str(e)}")