"""
Quality Assurance Framework for CMS A2A Multi-Agent System

This module provides comprehensive testing and validation for:
1. Model output quality (accuracy, relevance, completeness)
2. Hallucination detection
3. Response consistency across agents
4. Performance benchmarking
5. Compliance validation (HIPAA, CMS regulations)

Usage:
    from shared.qa_framework import QualityAssuranceValidator
    
    qa = QualityAssuranceValidator()
    
    # Validate model output
    result = qa.validate_output(
        prompt="Validate this prior authorization",
        response=model_response,
        expected_schema={"status": str, "reason": str}
    )
    
    if not result.passed:
        logger.error(f"QA failed: {result.failures}")
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class QACheckType(Enum):
    """Types of QA checks"""
    SCHEMA_VALIDATION = "schema_validation"
    HALLUCINATION_DETECTION = "hallucination_detection"
    CONSISTENCY_CHECK = "consistency_check"
    COMPLIANCE_CHECK = "compliance_check"
    PERFORMANCE_CHECK = "performance_check"
    COMPLETENESS_CHECK = "completeness_check"
    ACCURACY_CHECK = "accuracy_check"


@dataclass
class QACheckResult:
    """Result of a single QA check"""
    check_type: QACheckType
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAValidationResult:
    """Overall QA validation result"""
    passed: bool
    overall_score: float
    checks: List[QACheckResult]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def failures(self) -> List[QACheckResult]:
        """Get list of failed checks"""
        return [c for c in self.checks if not c.passed]
    
    @property
    def summary(self) -> Dict:
        """Get summary of validation results"""
        return {
            'passed': self.passed,
            'overall_score': self.overall_score,
            'total_checks': len(self.checks),
            'passed_checks': len([c for c in self.checks if c.passed]),
            'failed_checks': len(self.failures),
            'timestamp': self.timestamp
        }


class QualityAssuranceValidator:
    """Comprehensive QA validator for model outputs"""
    
    def __init__(self, min_passing_score: float = 0.7):
        self.min_passing_score = min_passing_score
        
        # Healthcare-specific compliance patterns
        self.compliance_patterns = {
            'hipaa_violations': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[1-9]\d{2}-\d{2}-\d{4}[A-Z]?\b',  # HICN
            ],
            'required_disclaimers': [
                'not medical advice',
                'consult healthcare provider',
                'for informational purposes'
            ]
        }
        
        # Hallucination indicators
        self.hallucination_indicators = [
            'I am certain',
            'I guarantee',
            'definitely will',
            'always results in',
            'never fails',
            '100% accurate',
            'I know for a fact'
        ]
    
    def validate_output(
        self,
        prompt: str,
        response: str,
        expected_schema: Optional[Dict] = None,
        reference_data: Optional[Dict] = None,
        agent_name: Optional[str] = None
    ) -> QAValidationResult:
        """
        Comprehensive validation of model output
        
        Args:
            prompt: Original user prompt
            response: Model response to validate
            expected_schema: Expected JSON schema (if applicable)
            reference_data: Reference data for accuracy checks
            agent_name: Name of the agent that generated the response
        
        Returns:
            QAValidationResult with all check results
        """
        checks = []
        
        # 1. Schema validation (if JSON response expected)
        if expected_schema:
            checks.append(self._validate_schema(response, expected_schema))
        
        # 2. Hallucination detection
        checks.append(self._detect_hallucinations(response))
        
        # 3. Completeness check
        checks.append(self._check_completeness(prompt, response))
        
        # 4. Compliance check (HIPAA, CMS regulations)
        checks.append(self._check_compliance(response))
        
        # 5. Consistency check (if reference data provided)
        if reference_data:
            checks.append(self._check_consistency(response, reference_data))
        
        # 6. Accuracy check (if reference data provided)
        if reference_data:
            checks.append(self._check_accuracy(response, reference_data))
        
        # Calculate overall score
        overall_score = sum(c.score for c in checks) / len(checks)
        passed = overall_score >= self.min_passing_score
        
        return QAValidationResult(
            passed=passed,
            overall_score=overall_score,
            checks=checks
        )
    
    def _validate_schema(self, response: str, expected_schema: Dict) -> QACheckResult:
        """Validate response against expected JSON schema"""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            # Check required fields
            missing_fields = []
            type_mismatches = []
            
            for field, expected_type in expected_schema.items():
                if field not in data:
                    missing_fields.append(field)
                elif not isinstance(data[field], expected_type):
                    type_mismatches.append({
                        'field': field,
                        'expected': expected_type.__name__,
                        'actual': type(data[field]).__name__
                    })
            
            if missing_fields or type_mismatches:
                return QACheckResult(
                    check_type=QACheckType.SCHEMA_VALIDATION,
                    passed=False,
                    score=0.5,
                    message="Schema validation failed",
                    details={
                        'missing_fields': missing_fields,
                        'type_mismatches': type_mismatches
                    }
                )
            
            return QACheckResult(
                check_type=QACheckType.SCHEMA_VALIDATION,
                passed=True,
                score=1.0,
                message="Schema validation passed"
            )
            
        except json.JSONDecodeError as e:
            return QACheckResult(
                check_type=QACheckType.SCHEMA_VALIDATION,
                passed=False,
                score=0.0,
                message="Invalid JSON response",
                details={'error': str(e)}
            )
    
    def _detect_hallucinations(self, response: str) -> QACheckResult:
        """Detect potential hallucinations in response"""
        hallucination_count = 0
        detected_phrases = []
        
        response_lower = response.lower()
        
        for indicator in self.hallucination_indicators:
            if indicator.lower() in response_lower:
                hallucination_count += 1
                detected_phrases.append(indicator)
        
        # Score based on number of hallucination indicators
        score = max(0.0, 1.0 - (hallucination_count * 0.2))
        passed = score >= 0.7
        
        return QACheckResult(
            check_type=QACheckType.HALLUCINATION_DETECTION,
            passed=passed,
            score=score,
            message=f"Detected {hallucination_count} potential hallucination indicators",
            details={'detected_phrases': detected_phrases}
        )
    
    def _check_completeness(self, prompt: str, response: str) -> QACheckResult:
        """Check if response adequately addresses the prompt"""
        # Extract key entities from prompt
        prompt_entities = self._extract_entities(prompt)
        response_entities = self._extract_entities(response)
        
        # Calculate coverage
        if not prompt_entities:
            coverage = 1.0
        else:
            covered = len(prompt_entities & response_entities)
            coverage = covered / len(prompt_entities)
        
        # Check minimum response length
        min_length = max(50, len(prompt) * 0.5)
        length_adequate = len(response) >= min_length
        
        # Combined score
        score = (coverage * 0.7) + (0.3 if length_adequate else 0.0)
        passed = score >= 0.6
        
        return QACheckResult(
            check_type=QACheckType.COMPLETENESS_CHECK,
            passed=passed,
            score=score,
            message=f"Response completeness: {score:.2%}",
            details={
                'entity_coverage': coverage,
                'length_adequate': length_adequate,
                'response_length': len(response)
            }
        )
    
    def _check_compliance(self, response: str) -> QACheckResult:
        """Check compliance with HIPAA and CMS regulations"""
        violations = []
        
        # Check for HIPAA violations (unredacted PII)
        for pattern_name, patterns in self.compliance_patterns.items():
            if pattern_name == 'hipaa_violations':
                for pattern in patterns:
                    matches = re.findall(pattern, response)
                    if matches:
                        violations.append({
                            'type': 'hipaa_violation',
                            'pattern': pattern_name,
                            'matches': len(matches)
                        })
        
        # Check for required disclaimers (if medical content detected)
        medical_keywords = ['diagnosis', 'treatment', 'medication', 'prescription', 'therapy']
        has_medical_content = any(kw in response.lower() for kw in medical_keywords)
        
        if has_medical_content:
            has_disclaimer = any(
                disclaimer.lower() in response.lower()
                for disclaimer in self.compliance_patterns['required_disclaimers']
            )
            if not has_disclaimer:
                violations.append({
                    'type': 'missing_disclaimer',
                    'message': 'Medical content without required disclaimer'
                })
        
        score = 1.0 if not violations else 0.0
        passed = score >= 0.9
        
        return QACheckResult(
            check_type=QACheckType.COMPLIANCE_CHECK,
            passed=passed,
            score=score,
            message=f"Compliance check: {len(violations)} violations",
            details={'violations': violations}
        )
    
    def _check_consistency(self, response: str, reference_data: Dict) -> QACheckResult:
        """Check consistency with reference data"""
        inconsistencies = []
        
        # Check for contradictions with reference data
        for key, ref_value in reference_data.items():
            if str(ref_value).lower() in response.lower():
                # Value mentioned in response
                continue
            else:
                # Check if contradictory value mentioned
                response_lower = response.lower()
                if key.lower() in response_lower:
                    inconsistencies.append({
                        'field': key,
                        'reference_value': ref_value,
                        'note': 'Field mentioned but value may differ'
                    })
        
        score = max(0.0, 1.0 - (len(inconsistencies) * 0.2))
        passed = score >= 0.7
        
        return QACheckResult(
            check_type=QACheckType.CONSISTENCY_CHECK,
            passed=passed,
            score=score,
            message=f"Consistency check: {len(inconsistencies)} potential inconsistencies",
            details={'inconsistencies': inconsistencies}
        )
    
    def _check_accuracy(self, response: str, reference_data: Dict) -> QACheckResult:
        """Check accuracy against reference data"""
        # Extract structured data from response if possible
        try:
            response_data = json.loads(response)
            
            matches = 0
            total = len(reference_data)
            
            for key, ref_value in reference_data.items():
                if key in response_data and response_data[key] == ref_value:
                    matches += 1
            
            accuracy = matches / total if total > 0 else 1.0
            passed = accuracy >= 0.8
            
            return QACheckResult(
                check_type=QACheckType.ACCURACY_CHECK,
                passed=passed,
                score=accuracy,
                message=f"Accuracy: {accuracy:.2%} ({matches}/{total} fields match)",
                details={'matches': matches, 'total': total}
            )
            
        except json.JSONDecodeError:
            # Fallback: check if reference values mentioned in text
            mentions = sum(
                1 for value in reference_data.values()
                if str(value).lower() in response.lower()
            )
            accuracy = mentions / len(reference_data) if reference_data else 1.0
            
            return QACheckResult(
                check_type=QACheckType.ACCURACY_CHECK,
                passed=accuracy >= 0.6,
                score=accuracy,
                message=f"Accuracy (text-based): {accuracy:.2%}",
                details={'mentions': mentions, 'total': len(reference_data)}
            )
    
    def _extract_entities(self, text: str) -> set:
        """Extract key entities from text (simple implementation)"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stopwords and short words
        entities = {w for w in words if w not in stopwords and len(w) > 3}
        
        return entities


class PerformanceBenchmark:
    """Performance benchmarking for model responses"""
    
    def __init__(self):
        self.benchmarks = []
    
    def record_benchmark(
        self,
        agent_name: str,
        operation: str,
        duration_ms: float,
        token_count: int,
        success: bool
    ) -> None:
        """Record a performance benchmark"""
        self.benchmarks.append({
            'agent_name': agent_name,
            'operation': operation,
            'duration_ms': duration_ms,
            'token_count': int,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_statistics(self, agent_name: Optional[str] = None) -> Dict:
        """Get performance statistics"""
        data = self.benchmarks
        if agent_name:
            data = [b for b in data if b['agent_name'] == agent_name]
        
        if not data:
            return {}
        
        durations = [b['duration_ms'] for b in data]
        success_rate = sum(1 for b in data if b['success']) / len(data)
        
        return {
            'total_operations': len(data),
            'avg_duration_ms': sum(durations) / len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'success_rate': success_rate,
            'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
        }
