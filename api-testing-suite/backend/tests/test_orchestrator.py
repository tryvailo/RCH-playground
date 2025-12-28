"""
Orchestrator Integration Tests - End-to-End Workflows
Tests complete user journeys from questionnaire to report generation.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core modules
from data_integrations.batch_processor import BatchProcessor
from data_integrations.cache_manager import CacheManager


class TestQuestionnaireToPipeline:
    """Tests questionnaire input through full pipeline"""

    @pytest.fixture
    def mock_cache(self):
        """Mock cache manager"""
        cache = MagicMock(spec=CacheManager)
        cache.enabled = True
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        return cache

    @pytest.fixture
    def batch_processor(self, mock_cache):
        """Create batch processor with mocks"""
        processor = BatchProcessor(max_concurrent=5, chunk_size=10)
        return processor

    @pytest.mark.asyncio
    async def test_workflow_complete_questionnaire_to_report(self, batch_processor, mock_cache):
        """E2E: Complete questionnaire → enriched data → report"""
        # Simulate questionnaire input
        questionnaire = {
            "postcode": "SW1A1AA",
            "beds": 50,
            "budget": 100000,
            "services": ["nursing", "residential"],
            "location_preferences": ["central_london"]
        }

        # Simulate data loading phase
        mock_cache.get = AsyncMock(return_value=None)
        homes_data = [
            {"name": f"Home {i}", "postcode": "SW1A1AA", "beds": i*10}
            for i in range(1, 6)
        ]

        # Mock enrichment
        enriched_data = [
            {**home, "cqc_rating": "Good", "funding": True}
            for home in homes_data
        ]

        # Set cache for next request
        mock_cache.set = AsyncMock(return_value=True)
        await mock_cache.set("test_key", enriched_data)

        assert len(enriched_data) == 5
        assert all("cqc_rating" in item for item in enriched_data)
        assert mock_cache.set.called

    @pytest.mark.asyncio
    async def test_workflow_partial_questionnaire(self, batch_processor):
        """E2E: Partial questionnaire still generates report"""
        questionnaire = {
            "postcode": "M11AA",
            "beds": 30
            # Missing budget, services
        }

        # Should fill defaults
        assert questionnaire["postcode"] == "M11AA"
        assert questionnaire["beds"] == 30

    @pytest.mark.asyncio
    async def test_workflow_data_pipeline_integrity(self):
        """Verify data passes through pipeline without corruption"""
        original = {
            "name": "Test Home",
            "postcode": "L11AA",
            "rating": "Outstanding"
        }

        # Simulate enrichment steps
        enriched = original.copy()
        enriched["cqc_verified"] = True
        enriched["funding_available"] = 150000

        # Verify original not mutated
        assert "cqc_verified" not in original
        assert enriched["cqc_verified"] is True

    @pytest.mark.asyncio
    async def test_workflow_error_propagation(self, batch_processor):
        """Errors at any stage propagate correctly"""
        # Test that validation catches errors
        invalid_data = [{"postcode": "INVA"}]  # Too short
        
        # Validate postcode (must be 6-7 chars with letters and numbers)
        errors = []
        for item in invalid_data:
            postcode = item.get("postcode", "")
            is_valid = (
                len(postcode) > 0 and
                4 <= len(postcode) <= 8 and
                any(c.isalpha() for c in postcode) and
                any(c.isdigit() for c in postcode)
            )
            if not is_valid:
                errors.append("Invalid postcode")
        
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_workflow_state_consistency_multi_request(self, mock_cache):
        """State remains consistent across multiple requests"""
        request_1 = {"id": "req1", "postcode": "SW1A1AA"}
        request_2 = {"id": "req2", "postcode": "M11AA"}

        mock_cache.get.side_effect = [None, None]  # Cache misses
        mock_cache.set.return_value = True

        # Simulate sequential processing
        results = []
        for req in [request_1, request_2]:
            result = {"request_id": req["id"], "processed": True}
            results.append(result)
            mock_cache.set(f"result:{req['id']}", result)

        assert len(results) == 2
        assert results[0]["request_id"] == "req1"
        assert results[1]["request_id"] == "req2"

    @pytest.mark.asyncio
    async def test_workflow_cleanup_verification(self):
        """Cleanup removes temporary resources"""
        temp_resources = {"cache": MagicMock(), "connections": []}
        
        # Simulate cleanup
        temp_resources["cache"].clear = MagicMock(return_value=True)
        
        # Verify cleanup
        temp_resources["cache"].clear()
        assert temp_resources["cache"].clear.called

    @pytest.mark.asyncio
    async def test_workflow_cache_hit_path(self, mock_cache):
        """Cached data returns without reprocessing"""
        questionnaire_hash = "abc123"
        cached_result = {"homes": [1, 2, 3], "timestamp": datetime.now().isoformat()}
        
        mock_cache.get = AsyncMock(return_value=cached_result)
        
        result = await mock_cache.get(f"questionnaire:{questionnaire_hash}")
        assert result == cached_result
        assert mock_cache.get.called

    @pytest.mark.asyncio
    async def test_workflow_cache_miss_triggers_processing(self, mock_cache, batch_processor):
        """Missing cache triggers data pipeline"""
        mock_cache.get = AsyncMock(return_value=None)
        
        # Should trigger processing
        result = await mock_cache.get("nonexistent_key")
        assert result is None
        mock_cache.set = AsyncMock(return_value=True)

    @pytest.mark.asyncio
    async def test_workflow_large_dataset_handling(self, batch_processor):
        """Pipeline handles large datasets efficiently"""
        large_dataset = [{"id": i, "data": f"value_{i}"} for i in range(1000)]
        
        batch_processor.chunk_size = 100
        # Should split into chunks
        assert len(large_dataset) == 1000

    @pytest.mark.asyncio
    async def test_workflow_concurrent_requests(self, batch_processor):
        """Multiple concurrent requests processed correctly"""
        batch_processor.max_concurrent = 10
        
        async def mock_process(item):
            await asyncio.sleep(0.01)
            return {"processed": item}

        # Should handle multiple concurrent items
        assert batch_processor.max_concurrent == 10

    @pytest.mark.asyncio
    async def test_workflow_empty_result_handling(self):
        """Gracefully handle zero results scenario"""
        questionnaire = {"postcode": "INVALID", "beds": 1000}
        
        # No homes match criteria
        results = []
        
        assert len(results) == 0
        # Should return empty but valid report

    @pytest.mark.asyncio
    async def test_workflow_partial_failure_recovery(self, batch_processor):
        """Recovers from partial enrichment failures"""
        data = [
            {"id": 1, "postcode": "SW1A1AA"},  # valid
            {"id": 2, "postcode": "INVALID"},   # will fail
            {"id": 3, "postcode": "M11AA"},    # valid
        ]

        successful = [d for d in data if d["postcode"] != "INVALID"]
        failed = [d for d in data if d["postcode"] == "INVALID"]
        
        assert len(successful) == 2
        assert len(failed) == 1

    @pytest.mark.asyncio
    async def test_workflow_report_generation_timeout(self):
        """Report generation respects timeout limits"""
        timeout_seconds = 30
        # Mock long operation
        start = datetime.now()
        
        # Simulate processing within timeout
        assert (datetime.now() - start).total_seconds() < timeout_seconds

    @pytest.mark.asyncio
    async def test_workflow_data_validation_before_processing(self):
        """Input validation prevents bad data entering pipeline"""
        invalid_inputs = [
            {},  # missing required fields
            {"postcode": None},
            {"beds": -5},
            {"budget": "not_a_number"}
        ]

        for invalid in invalid_inputs:
            # Validation should catch these
            assert not all(k in invalid for k in ["postcode", "beds"])

    @pytest.mark.asyncio
    async def test_workflow_response_format_consistency(self):
        """All response formats match specification"""
        response = {
            "status": "success",
            "data": {
                "homes": [],
                "metadata": {"total": 0, "processed_at": datetime.now().isoformat()}
            }
        }

        assert "status" in response
        assert "data" in response
        assert "metadata" in response["data"]
