"""
Experiment service - Business logic for experiments
"""
import asyncio
import itertools
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.response_repository import ResponseRepository
from app.repositories.metric_repository import MetricRepository
from app.services.llm_service import LLMService
from app.services.metric_calculator import MetricCalculator
from app.services.response_validator import ResponseValidator
from app.schemas.experiment import ExperimentCreate
from app.core.constants import DEFAULT_BATCH_SIZE
from app.core.exceptions import LLMServiceError
from app.db.database import SessionLocal


class ExperimentService:
    """Service for experiment business logic"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.metric_calculator = MetricCalculator()
        self.validator = ResponseValidator()
    
    async def create_experiment(
        self,
        db: Session,
        experiment_data: ExperimentCreate
    ) -> dict:
        """
        Create a new experiment and generate responses
        
        Args:
            db: Database session
            experiment_data: Experiment creation data
            
        Returns:
            Dictionary with experiment data
        """
        # Create experiment record
        experiment = ExperimentRepository.create(
            db=db,
            name=experiment_data.name,
            prompt=experiment_data.prompt
        )
        
        # Generate parameter combinations
        param_combinations = list(itertools.product(
            experiment_data.temperature_range,
            experiment_data.top_p_range
        ))
        
        print(f"[EXPERIMENT {experiment.id}] Starting parallel generation of {len(param_combinations)} responses...")
        
        # Generate responses in batches
        success_count = await self._generate_responses_batch(
            experiment_id=experiment.id,
            prompt=experiment_data.prompt,
            param_combinations=param_combinations,
            max_tokens=experiment_data.max_tokens
        )
        
        print(f"[EXPERIMENT {experiment.id}] Generation complete: {success_count}/{len(param_combinations)} successful")
        
        return {
            "id": experiment.id,
            "name": experiment.name,
            "prompt": experiment.prompt,
            "created_at": experiment.created_at.isoformat() if experiment.created_at else ""
        }
    
    async def _generate_responses_batch(
        self,
        experiment_id: int,
        prompt: str,
        param_combinations: List[Tuple[float, float]],
        max_tokens: int
    ) -> int:
        """
        Generate responses in parallel batches
        
        Args:
            experiment_id: ID of the experiment
            prompt: Input prompt
            param_combinations: List of (temperature, top_p) tuples
            max_tokens: Maximum tokens per response
            
        Returns:
            Number of successful responses
        """
        tasks = [
            self._generate_single_response(
                experiment_id=experiment_id,
                prompt=prompt,
                temperature=temp,
                top_p=top_p,
                max_tokens=max_tokens,
                idx=idx
            )
            for idx, (temp, top_p) in enumerate(param_combinations, 1)
        ]
        
        # Process in batches to respect rate limits
        success_count = 0
        for i in range(0, len(tasks), DEFAULT_BATCH_SIZE):
            batch = tasks[i:i + DEFAULT_BATCH_SIZE]
            batch_num = i // DEFAULT_BATCH_SIZE + 1
            total_batches = (len(tasks) + DEFAULT_BATCH_SIZE - 1) // DEFAULT_BATCH_SIZE
            
            print(f"[EXPERIMENT {experiment_id}] Processing batch {batch_num}/{total_batches}")
            results = await asyncio.gather(*batch, return_exceptions=True)
            batch_success = sum(1 for r in results if r is True)
            success_count += batch_success
            print(f"[EXPERIMENT {experiment_id}] Batch complete: {batch_success}/{len(batch)} successful")
        
        return success_count
    
    async def _generate_single_response(
        self,
        experiment_id: int,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        idx: int
    ) -> bool:
        """
        Generate a single response and save to database
        
        Args:
            experiment_id: ID of the experiment
            prompt: Input prompt
            temperature: Temperature parameter
            top_p: Top-p parameter
            max_tokens: Maximum tokens
            idx: Response index (for logging)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"[EXPERIMENT {experiment_id}] Generating response {idx}: temp={temperature}, top_p={top_p}")
            
            # Generate LLM response
            llm_response = await self.llm_service.generate_response(
                prompt=prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
            
            print(f"[EXPERIMENT {experiment_id}] LLM response {idx} received (length: {len(llm_response['text'])}, finish_reason: {llm_response.get('finish_reason', 'stop')})")
            
            # Validate response
            validation = self.validator.validate_response(
                llm_response["text"],
                llm_response.get("finish_reason", "stop")
            )
            
            if validation["warnings"]:
                print(f"[EXPERIMENT {experiment_id}] Response {idx} warnings: {', '.join(validation['warnings'])}")
            
            # Use cleaned text for metrics calculation
            response_text = validation.get("cleaned_text") or llm_response["text"]
            
            # Calculate metrics
            metrics = self.metric_calculator.calculate_all_metrics(response_text)
            print(f"[EXPERIMENT {experiment_id}] Metrics calculated for response {idx}: {list(metrics.keys())}")
            
            # Save to database with new session (thread-safe)
            local_db = SessionLocal()
            try:
                # Prepare validation metadata
                validation_metadata = {
                    "is_valid": validation["is_valid"],
                    "is_corrupted": validation["is_corrupted"],
                    "is_truncated": validation["is_truncated"],
                    "corruption_score": validation["corruption_score"],
                    "warnings": validation["warnings"]
                }
                
                # Create response
                response = ResponseRepository.create(
                    db=local_db,
                    experiment_id=experiment_id,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    text=response_text,
                    finish_reason=llm_response.get("finish_reason", "stop"),
                    validation_metadata=validation_metadata
                )
                
                # Create metrics
                MetricRepository.create_batch(
                    db=local_db,
                    response_id=response.id,
                    metrics=metrics
                )
                
                print(f"[EXPERIMENT {experiment_id}] Response {idx} saved successfully (ID: {response.id})")
                return True
                
            except Exception as db_error:
                local_db.rollback()
                print(f"[EXPERIMENT {experiment_id}] DB error for response {idx}: {str(db_error)}")
                raise
            finally:
                local_db.close()
                
        except Exception as e:
            import traceback
            print(f"[EXPERIMENT {experiment_id}] ERROR generating response {idx} (temp={temperature}, top_p={top_p}): {str(e)}")
            traceback.print_exc()
            return False
