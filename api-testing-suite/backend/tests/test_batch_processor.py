"""
Tests for Batch Processor and Neighbourhood Analyzer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_integrations.batch_processor import (
    BatchProcessor, 
    NeighbourhoodAnalyzer,
    BatchProgress
)


class TestBatchProgress:
    """Tests for BatchProgress dataclass"""
    
    def test_percent_complete(self):
        """Test percentage calculation"""
        progress = BatchProgress(total=100, completed=50)
        assert progress.percent_complete == 50.0
    
    def test_percent_complete_zero_total(self):
        """Test percentage with zero total"""
        progress = BatchProgress(total=0, completed=0)
        assert progress.percent_complete == 0
    
    def test_items_per_second(self):
        """Test throughput calculation"""
        from datetime import datetime, timedelta
        
        progress = BatchProgress(
            total=100,
            completed=50,
            started_at=datetime.now() - timedelta(seconds=10)
        )
        
        assert progress.items_per_second == 5.0
    
    def test_estimated_remaining(self):
        """Test remaining time estimation"""
        from datetime import datetime, timedelta
        
        progress = BatchProgress(
            total=100,
            completed=50,
            started_at=datetime.now() - timedelta(seconds=10)
        )
        
        # 50 items in 10 seconds = 5/sec
        # 50 remaining / 5 per sec = 10 seconds
        assert progress.estimated_remaining_seconds == 10.0


class TestBatchProcessor:
    """Tests for BatchProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create test processor"""
        return BatchProcessor(max_concurrent=2, chunk_size=5)
    
    def test_initialization(self, processor):
        """Test processor initialization"""
        assert processor.max_concurrent == 2
        assert processor.chunk_size == 5
        assert processor.progress.total == 0
    
    def test_progress_callback(self, processor):
        """Test progress callback setting"""
        callback_called = []
        
        def callback(progress):
            callback_called.append(progress)
        
        processor.set_progress_callback(callback)
        processor._update_progress("test", success=True)
        
        assert len(callback_called) == 1
        assert callback_called[0].completed == 1
    
    def test_update_progress_success(self, processor):
        """Test progress update on success"""
        processor.progress.total = 10
        processor._update_progress("home1", success=True)
        
        assert processor.progress.completed == 1
        assert processor.progress.failed == 0
    
    def test_update_progress_failure(self, processor):
        """Test progress update on failure"""
        processor.progress.total = 10
        processor._update_progress("home1", success=False, error="Test error")
        
        assert processor.progress.completed == 0
        assert processor.progress.failed == 1
        assert len(processor.progress.errors) == 1
    
    def test_calculate_composite_score(self, processor):
        """Test composite score calculation"""
        data = {
            'ons': {'wellbeing_score': 75},
            'osm': {'walk_score': 80, 'care_home_relevance': 70},
            'nhsbsa': {'health_index': 65}
        }
        
        result = processor._calculate_composite_score(data)
        
        assert 'score' in result
        assert 'rating' in result
        assert 60 < result['score'] < 80
        assert result['components'] == 4
    
    def test_calculate_composite_score_missing_data(self, processor):
        """Test composite score with missing data"""
        data = {
            'ons': {'wellbeing_score': 75}
        }
        
        result = processor._calculate_composite_score(data)
        
        assert result['components'] == 1
        assert result['confidence'] == 'Low'
    
    def test_calculate_composite_score_no_data(self, processor):
        """Test composite score with no data"""
        result = processor._calculate_composite_score({})
        
        assert result['score'] is None
        assert result['rating'] == 'Insufficient Data'
    
    @pytest.mark.asyncio
    async def test_process_care_homes_empty(self, processor):
        """Test processing empty list"""
        results = await processor.process_care_homes([])
        
        assert results['statistics']['total'] == 0
        assert results['results'] == []
    
    @pytest.mark.asyncio
    async def test_enrich_care_home(self, processor):
        """Test enriching a single care home"""
        # Mock the loaders
        with patch('data_integrations.batch_processor.OSPlacesLoader') as mock_os, \
             patch('data_integrations.batch_processor.ONSLoader') as mock_ons, \
             patch('data_integrations.batch_processor.OSMLoader') as mock_osm, \
             patch('data_integrations.batch_processor.NHSBSALoader') as mock_nhsbsa:
            
            # Setup mocks
            mock_os.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                get_coordinates=AsyncMock(return_value={'latitude': 52.48, 'longitude': -1.89})
            ))
            mock_os.return_value.__aexit__ = AsyncMock()
            
            mock_ons.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                get_full_area_profile=AsyncMock(return_value={
                    'geography': {'lsoa_code': 'E01'},
                    'wellbeing': {'social_wellbeing_index': {'score': 70}},
                    'economic': {'economic_stability_index': {'score': 65}},
                    'demographics': {'elderly_care_context': {'over_65_percent': 18}}
                })
            ))
            mock_ons.return_value.__aexit__ = AsyncMock()
            
            mock_osm.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                calculate_walk_score=AsyncMock(return_value={
                    'walk_score': 75,
                    'rating': 'Very Walkable',
                    'care_home_relevance': {'score': 72, 'healthcare_access': 'Good'}
                })
            ))
            mock_osm.return_value.__aexit__ = AsyncMock()
            
            mock_nhsbsa.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                get_area_health_profile=AsyncMock(return_value={
                    'health_index': {'score': 68, 'rating': 'Average'},
                    'practices_analyzed': 5,
                    'care_home_considerations': []
                })
            ))
            mock_nhsbsa.return_value.__aexit__ = AsyncMock()
            
            home = {'postcode': 'B1 1BB', 'name': 'Test Home'}
            result = await processor.enrich_care_home(home)
            
            assert result.get('success') or 'data' in result


class TestNeighbourhoodAnalyzer:
    """Tests for NeighbourhoodAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create test analyzer"""
        analyzer = NeighbourhoodAnalyzer()
        analyzer.cache = MagicMock()
        analyzer.cache.get.return_value = None
        analyzer.cache.set.return_value = True
        return analyzer
    
    def test_calculate_overall_score(self, analyzer):
        """Test overall score calculation"""
        data = {
            'social': {
                'wellbeing': {'score': 75}
            },
            'walkability': {
                'score': 80,
                'care_home_relevance': {'score': 70}
            },
            'health': {
                'index': {'score': 65}
            }
        }
        
        result = analyzer._calculate_overall_score(data)
        
        assert 'score' in result
        assert 'rating' in result
        assert 'breakdown' in result
        assert len(result['breakdown']) == 4
    
    def test_calculate_overall_score_empty(self, analyzer):
        """Test overall score with no data"""
        result = analyzer._calculate_overall_score({})
        
        assert result['score'] is None
        assert result['rating'] == 'Insufficient Data'
    
    def test_overall_score_ratings(self, analyzer):
        """Test rating thresholds"""
        # Excellent
        data = {
            'social': {'wellbeing': {'score': 85}},
            'walkability': {'score': 90, 'care_home_relevance': {'score': 85}},
            'health': {'index': {'score': 80}}
        }
        result = analyzer._calculate_overall_score(data)
        assert result['rating'] == 'Excellent Neighbourhood'
        
        # Below Average
        data = {
            'social': {'wellbeing': {'score': 30}},
            'walkability': {'score': 35, 'care_home_relevance': {'score': 30}},
            'health': {'index': {'score': 25}}
        }
        result = analyzer._calculate_overall_score(data)
        assert result['rating'] == 'Below Average Neighbourhood'


class TestIntegration:
    """Integration tests (require network)"""
    
    @pytest.mark.skip(reason="Requires network access")
    @pytest.mark.asyncio
    async def test_real_neighbourhood_analysis(self):
        """Test real neighbourhood analysis"""
        analyzer = NeighbourhoodAnalyzer()
        result = await analyzer.analyze("B1 1BB")
        
        assert 'overall' in result
        assert result['overall'].get('score') is not None
    
    @pytest.mark.skip(reason="Requires network access")
    @pytest.mark.asyncio
    async def test_real_batch_processing(self):
        """Test real batch processing"""
        processor = BatchProcessor(max_concurrent=2)
        
        homes = [
            {'postcode': 'B1 1BB', 'name': 'Home 1'},
            {'postcode': 'SW1A 1AA', 'name': 'Home 2'}
        ]
        
        results = await processor.process_care_homes(homes)
        
        assert results['statistics']['total'] == 2
        assert results['statistics']['completed'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
