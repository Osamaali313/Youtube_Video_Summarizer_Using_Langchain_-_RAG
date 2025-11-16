"""
Fact-Checker Agent - Validates claims and statements
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from loguru import logger

from app.agents.base import BaseAgent
from app.agents.research import ResearchAgent


class VerificationStatus(str, Enum):
    """Verification status for claims"""
    VERIFIED = "verified"
    PARTIALLY_TRUE = "partially_true"
    UNVERIFIED = "unverified"
    FALSE = "false"
    MISLEADING = "misleading"


class FactCheckerAgent(BaseAgent):
    """Agent specialized in fact-checking claims"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="fact_checker", **kwargs)
        self.research_agent = ResearchAgent(**kwargs)

    async def fact_check_summary(
        self,
        summary: str,
        transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fact-check claims in a summary

        Args:
            summary: Video summary to fact-check
            transcript: Optional full transcript for context

        Returns:
            Dictionary with fact-check results
        """
        try:
            self.log_execution("Starting fact-check", "Extracting claims")

            # Extract factual claims
            claims = await self._extract_claims(summary)

            if not claims:
                return {
                    "claims": [],
                    "overall_assessment": "No specific factual claims found to verify.",
                    "credibility_score": 1.0
                }

            # Fact-check each claim
            checked_claims = []
            for claim in claims[:10]:  # Limit to 10 claims
                result = await self._verify_claim(claim, transcript)
                checked_claims.append(result)

            # Calculate overall credibility
            credibility = self._calculate_credibility(checked_claims)

            # Generate assessment
            assessment = await self._generate_assessment(checked_claims, summary)

            return {
                "claims": checked_claims,
                "overall_assessment": assessment,
                "credibility_score": credibility,
                "total_claims": len(claims),
                "checked_claims": len(checked_claims)
            }

        except Exception as e:
            logger.error(f"Fact-check error: {e}")
            return {
                "claims": [],
                "overall_assessment": f"Fact-checking failed: {str(e)}",
                "credibility_score": 0.0
            }

    async def _extract_claims(self, summary: str) -> List[str]:
        """Extract factual claims from summary"""
        prompt = f"""Extract specific factual claims from this summary that can be verified.

Summary:
{summary}

Extract claims that:
1. Make specific assertions
2. Include statistics, dates, or numbers
3. Reference events or facts
4. Can be verified against external sources

DO NOT extract:
- Opinions or subjective statements
- General observations
- Predictions or speculations

Format: Return only the claims, one per line, keeping them brief and specific.

Claims:"""

        response = await self.invoke(prompt)

        # Parse claims
        claims = [
            line.strip()
            for line in response.split('\n')
            if line.strip() and not line.strip().startswith(('#', '-', '*', 'Claims:'))
        ]

        self.log_execution("Extracted claims", f"{len(claims)} claims found")
        return claims

    async def _verify_claim(
        self,
        claim: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a single claim

        Args:
            claim: The claim to verify
            context: Optional context

        Returns:
            Dictionary with verification result
        """
        try:
            self.log_execution("Verifying claim", claim[:50])

            # Research the claim
            research_result = await self.research_agent.research_topic(
                topic=claim,
                context=context
            )

            # Analyze findings and determine status
            verification = await self._analyze_verification(
                claim=claim,
                research_findings=research_result["summary"],
                sources=research_result["sources"]
            )

            return {
                "claim": claim,
                "status": verification["status"],
                "explanation": verification["explanation"],
                "sources": research_result["sources"][:3],  # Top 3 sources
                "confidence": verification["confidence"]
            }

        except Exception as e:
            logger.error(f"Error verifying claim: {e}")
            return {
                "claim": claim,
                "status": VerificationStatus.UNVERIFIED,
                "explanation": f"Could not verify: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

    async def _analyze_verification(
        self,
        claim: str,
        research_findings: str,
        sources: List[str]
    ) -> Dict[str, Any]:
        """Analyze research findings to determine verification status"""
        prompt = f"""Analyze whether this claim is supported by the research findings.

Claim: {claim}

Research Findings:
{research_findings}

Sources: {len(sources)} sources checked

Determine the verification status:
- VERIFIED: Strong evidence from multiple reliable sources confirms the claim
- PARTIALLY_TRUE: Some elements are correct, but context or details are missing
- UNVERIFIED: Insufficient evidence found
- FALSE: Contradicted by reliable sources
- MISLEADING: Technically true but missing important context

Provide:
1. Status (one of the above)
2. Brief explanation (2-3 sentences)
3. Confidence level (0.0-1.0)

Format your response as:
STATUS: [status]
EXPLANATION: [explanation]
CONFIDENCE: [0.0-1.0]
"""

        response = await self.invoke(prompt)

        # Parse response
        status = VerificationStatus.UNVERIFIED
        explanation = "Unable to determine verification status"
        confidence = 0.5

        for line in response.split('\n'):
            if line.startswith('STATUS:'):
                status_text = line.split(':', 1)[1].strip().lower()
                for s in VerificationStatus:
                    if s.value in status_text or s.name.lower() in status_text:
                        status = s
                        break

            elif line.startswith('EXPLANATION:'):
                explanation = line.split(':', 1)[1].strip()

            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))
                except:
                    pass

        return {
            "status": status,
            "explanation": explanation,
            "confidence": confidence
        }

    def _calculate_credibility(self, checked_claims: List[Dict[str, Any]]) -> float:
        """Calculate overall credibility score"""
        if not checked_claims:
            return 1.0

        status_scores = {
            VerificationStatus.VERIFIED: 1.0,
            VerificationStatus.PARTIALLY_TRUE: 0.7,
            VerificationStatus.UNVERIFIED: 0.5,
            VerificationStatus.MISLEADING: 0.3,
            VerificationStatus.FALSE: 0.0
        }

        total_score = sum(
            status_scores.get(claim["status"], 0.5)
            for claim in checked_claims
        )

        return round(total_score / len(checked_claims), 2)

    async def _generate_assessment(
        self,
        checked_claims: List[Dict[str, Any]],
        summary: str
    ) -> str:
        """Generate overall credibility assessment"""
        # Count by status
        status_counts = {}
        for claim in checked_claims:
            status = claim["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        prompt = f"""Generate a brief overall assessment of this summary's factual accuracy.

Summary: {summary[:500]}

Fact-check Results:
- Total claims checked: {len(checked_claims)}
- Verified: {status_counts.get(VerificationStatus.VERIFIED, 0)}
- Partially True: {status_counts.get(VerificationStatus.PARTIALLY_TRUE, 0)}
- Unverified: {status_counts.get(VerificationStatus.UNVERIFIED, 0)}
- Misleading: {status_counts.get(VerificationStatus.MISLEADING, 0)}
- False: {status_counts.get(VerificationStatus.FALSE, 0)}

Write a 2-3 sentence assessment of the overall credibility and accuracy.

Assessment:"""

        assessment = await self.invoke(prompt)
        return assessment.strip()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the fact-checker agent

        Args:
            input_data: {
                "summary": str,
                "transcript": Optional[str]
            }

        Returns:
            Dictionary with fact-check results
        """
        try:
            summary = input_data.get("summary", "")
            transcript = input_data.get("transcript")

            if not summary:
                return self.format_output(
                    success=False,
                    data=None,
                    error="No summary provided"
                )

            self.log_execution("Starting fact-check", f"{len(summary)} chars")

            # Perform fact-check
            result = await self.fact_check_summary(summary, transcript)

            self.log_execution(
                "Fact-check complete",
                f"Credibility: {result['credibility_score']}"
            )

            return self.format_output(
                success=True,
                data=result,
                metadata={
                    "credibility_score": result["credibility_score"],
                    "claims_checked": result.get("checked_claims", 0)
                }
            )

        except Exception as e:
            logger.error(f"Fact-checker agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
