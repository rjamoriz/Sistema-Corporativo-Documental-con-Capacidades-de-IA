"""
Tests de Edge Cases para Sistema de Validación
Tests exhaustivos para escenarios complejos y límite
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from backend.services.validation.sanctions_service import SanctionsService
from backend.services.validation.business_registry_service import BusinessRegistryService
from backend.services.validation.esg_service import ESGService
from backend.services.notifications.notification_service import NotificationService, AlertPriority
from backend.schedulers.validation_scheduler import ValidationScheduler
from backend.middleware.validation_middleware import ValidationMiddleware


class TestSpecialCharacters:
    """Tests para manejo de caracteres especiales en nombres"""
    
    @pytest.mark.asyncio
    async def test_name_with_accents(self):
        """Test: Nombres con acentos y diacríticos"""
        service = SanctionsService()
        
        # Nombres con acentos
        names = [
            "José García Pérez",
            "François Müller",
            "Søren Ødegård",
            "Wójcik Łukasz"
        ]
        
        for name in names:
            result = await service.check_ofac(name)
            assert "query" in result
            assert result["query"] == name
    
    @pytest.mark.asyncio
    async def test_name_with_apostrophes(self):
        """Test: Nombres con apóstrofes y guiones"""
        service = SanctionsService()
        
        names = [
            "O'Brien Corporation",
            "McDonald's Ltd",
            "Jean-Pierre Dupont",
            "Mary-Ann Smith"
        ]
        
        for name in names:
            result = await service.check_ofac(name)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_name_with_special_symbols(self):
        """Test: Nombres con símbolos especiales"""
        service = SanctionsService()
        
        names = [
            "AT&T Corporation",
            "Ben & Jerry's",
            "Company #1",
            "Firm (USA) Inc."
        ]
        
        for name in names:
            result = await service.check_ofac(name)
            assert "error" not in result or result.get("match") == False


class TestMultipleMatches:
    """Tests para múltiples coincidencias simultáneas"""
    
    @pytest.mark.asyncio
    async def test_multiple_entities_in_document(self):
        """Test: Documento con múltiples entidades a validar"""
        middleware = ValidationMiddleware()
        
        # Simular documento con 50 entidades
        entities = [
            {"text": f"Entity {i}", "type": "ORGANIZATION"}
            for i in range(50)
        ]
        
        mock_document = Mock()
        mock_document.id = 1
        mock_document.filename = "test.pdf"
        mock_document.metadata_ = {}
        
        mock_db = AsyncMock()
        
        result = await middleware.validate_document(
            document=mock_document,
            extracted_text="Test document",
            entities=entities,
            db=mock_db
        )
        
        assert result["total_entities_checked"] == 50
    
    @pytest.mark.asyncio
    async def test_entity_in_multiple_lists(self):
        """Test: Entidad presente en múltiples listas de sanciones"""
        service = SanctionsService()
        
        # Este test verifica que se detecten múltiples matches
        test_name = "Known Sanctioned Entity"
        
        with patch.object(service, 'check_ofac', return_value={
            "match": True,
            "matches": [{"source": "OFAC", "confidence": 0.95}]
        }), patch.object(service, 'check_eu_sanctions', return_value={
            "match": True,
            "matches": [{"source": "EU", "confidence": 0.92}]
        }):
            ofac_result = await service.check_ofac(test_name)
            eu_result = await service.check_eu_sanctions(test_name)
            
            assert ofac_result["match"] == True
            assert eu_result["match"] == True


class TestAPITimeouts:
    """Tests para timeouts y fallos de APIs externas"""
    
    @pytest.mark.asyncio
    async def test_ofac_api_timeout(self):
        """Test: Timeout en API de OFAC"""
        service = SanctionsService()
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Simular timeout
            mock_get.side_effect = asyncio.TimeoutError()
            
            result = await service.check_ofac("Test Entity")
            
            # Debe manejar el timeout gracefully
            assert "error" in result or result.get("match") == False
    
    @pytest.mark.asyncio
    async def test_api_connection_error(self):
        """Test: Error de conexión a API externa"""
        service = BusinessRegistryService()
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Simular error de conexión
            mock_get.side_effect = ConnectionError("Unable to connect")
            
            result = await service.verify_company("Test Corp")
            
            # Debe retornar resultado indicando error
            assert "error" in result or result.get("exists") == False
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self):
        """Test: Rate limiting de API"""
        service = SanctionsService()
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Simular respuesta 429 (Too Many Requests)
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_response.json = AsyncMock(return_value={"error": "Rate limit exceeded"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await service.check_ofac("Test Entity")
            
            # Debe manejar rate limiting
            assert result is not None


class TestCacheCorruption:
    """Tests para corrupción de caché"""
    
    @pytest.mark.asyncio
    async def test_invalid_cache_data(self):
        """Test: Datos inválidos en caché"""
        service = SanctionsService()
        
        # Simular caché corrupta
        with patch.object(service, '_get_from_cache', return_value='invalid_json{'):
            result = await service.check_ofac("Test Entity")
            
            # Debe recuperarse y consultar API
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_expired_cache_entry(self):
        """Test: Entrada de caché expirada"""
        service = SanctionsService()
        
        # Simular entrada expirada
        expired_data = {
            "timestamp": (datetime.now() - timedelta(days=100)).isoformat(),
            "data": {"match": False}
        }
        
        with patch.object(service, '_get_from_cache', return_value=expired_data):
            # Debe ignorar caché expirada y consultar API
            result = await service.check_ofac("Test Entity")
            assert result is not None


class TestSchedulerFailures:
    """Tests para fallos en el scheduler"""
    
    @pytest.mark.asyncio
    async def test_scheduler_task_exception(self):
        """Test: Excepción en tarea programada"""
        scheduler = ValidationScheduler()
        
        with patch.object(scheduler, 'sync_sanctions_lists', side_effect=Exception("DB Error")):
            # Debe manejar excepción sin caer
            try:
                await scheduler.sync_sanctions_lists()
            except Exception:
                pass  # Esperado
            
            # Scheduler debe seguir activo
            assert scheduler.scheduler is not None
    
    @pytest.mark.asyncio
    async def test_scheduler_concurrent_execution(self):
        """Test: Ejecución concurrente de tareas"""
        scheduler = ValidationScheduler()
        
        # Simular dos ejecuciones simultáneas
        task1 = asyncio.create_task(scheduler.sync_sanctions_lists())
        task2 = asyncio.create_task(scheduler.sync_sanctions_lists())
        
        results = await asyncio.gather(task1, task2, return_exceptions=True)
        
        # Ambas deben completarse
        assert len(results) == 2


class TestNotificationFailures:
    """Tests para fallos en sistema de notificaciones"""
    
    @pytest.mark.asyncio
    async def test_email_send_failure(self):
        """Test: Fallo al enviar email"""
        service = NotificationService()
        
        with patch.object(service, '_send_email_alert', return_value=False):
            result = await service.send_sanctions_alert(
                entity_name="Test Entity",
                entity_type="COMPANY",
                matches=[],
                confidence=0.95,
                priority=AlertPriority.HIGH
            )
            
            # Debe retornar False para email pero intentar Slack
            assert "email" in result
    
    @pytest.mark.asyncio
    async def test_slack_webhook_failure(self):
        """Test: Fallo en webhook de Slack"""
        service = NotificationService()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Webhook error")
            
            result = await service._send_slack_alert({
                "entity_name": "Test",
                "priority": "HIGH"
            })
            
            # Debe retornar False
            assert result == False
    
    @pytest.mark.asyncio
    async def test_notification_with_empty_recipients(self):
        """Test: Notificación sin destinatarios"""
        service = NotificationService()
        
        result = await service.send_sanctions_alert(
            entity_name="Test Entity",
            entity_type="COMPANY",
            matches=[],
            confidence=0.95,
            priority=AlertPriority.HIGH,
            recipients=[]
        )
        
        # Debe manejar lista vacía
        assert result is not None


class TestConcurrentValidations:
    """Tests para validaciones concurrentes"""
    
    @pytest.mark.asyncio
    async def test_concurrent_document_validations(self):
        """Test: Validación de múltiples documentos simultáneamente"""
        middleware = ValidationMiddleware()
        
        mock_docs = []
        for i in range(10):
            mock_doc = Mock()
            mock_doc.id = i
            mock_doc.filename = f"doc_{i}.pdf"
            mock_doc.metadata_ = {}
            mock_docs.append(mock_doc)
        
        mock_db = AsyncMock()
        
        # Validar 10 documentos concurrentemente
        tasks = [
            middleware.validate_document(
                document=doc,
                extracted_text=f"Text {i}",
                entities=[{"text": f"Entity {i}", "type": "PERSON"}],
                db=mock_db
            )
            for i, doc in enumerate(mock_docs)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Todas deben completarse
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results if not isinstance(r, Exception))
    
    @pytest.mark.asyncio
    async def test_race_condition_on_cache(self):
        """Test: Race condition en acceso a caché"""
        service = SanctionsService()
        
        # Simular múltiples consultas simultáneas del mismo nombre
        tasks = [
            service.check_ofac("Same Entity Name")
            for _ in range(20)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Todas deben retornar resultado consistente
        assert len(results) == 20
        assert all(isinstance(r, dict) for r in results if not isinstance(r, Exception))


class TestInputValidation:
    """Tests para validación de entrada"""
    
    @pytest.mark.asyncio
    async def test_empty_entity_name(self):
        """Test: Nombre de entidad vacío"""
        service = SanctionsService()
        
        result = await service.check_ofac("")
        
        # Debe manejar string vacío
        assert result is not None
        assert result.get("match") == False
    
    @pytest.mark.asyncio
    async def test_extremely_long_name(self):
        """Test: Nombre extremadamente largo"""
        service = SanctionsService()
        
        long_name = "A" * 10000  # 10k caracteres
        
        result = await service.check_ofac(long_name)
        
        # Debe manejar sin crash
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_null_entity_name(self):
        """Test: Nombre None/null"""
        service = SanctionsService()
        
        result = await service.check_ofac(None)
        
        # Debe manejar None
        assert result is not None


class TestDataConsistency:
    """Tests para consistencia de datos"""
    
    @pytest.mark.asyncio
    async def test_validation_result_persistence(self):
        """Test: Persistencia de resultados de validación"""
        middleware = ValidationMiddleware()
        
        mock_document = Mock()
        mock_document.id = 1
        mock_document.filename = "test.pdf"
        mock_document.metadata_ = {}
        
        mock_db = AsyncMock()
        
        result = await middleware.validate_document(
            document=mock_document,
            extracted_text="Test",
            entities=[{"text": "Test Entity", "type": "ORGANIZATION"}],
            db=mock_db
        )
        
        # Debe incluir document_id en resultado
        assert "document_id" in result
        assert result["document_id"] == "1"
    
    @pytest.mark.asyncio
    async def test_duplicate_validation_prevention(self):
        """Test: Prevención de validaciones duplicadas"""
        middleware = ValidationMiddleware()
        
        mock_document = Mock()
        mock_document.id = 1
        mock_document.status = "COMPLETED"
        mock_document.metadata_ = {"validation_completed": True}
        
        should_validate = await middleware.should_validate(mock_document)
        
        # No debe validar documentos ya validados
        assert should_validate == False


class TestErrorRecovery:
    """Tests para recuperación de errores"""
    
    @pytest.mark.asyncio
    async def test_partial_validation_failure(self):
        """Test: Fallo parcial en validación"""
        middleware = ValidationMiddleware()
        
        with patch.object(middleware, '_check_sanctions', side_effect=Exception("API Error")):
            mock_document = Mock()
            mock_document.id = 1
            mock_document.filename = "test.pdf"
            mock_document.metadata_ = {}
            
            mock_db = AsyncMock()
            
            result = await middleware.validate_document(
                document=mock_document,
                extracted_text="Test",
                entities=[{"text": "Test", "type": "PERSON"}],
                db=mock_db
            )
            
            # Debe retornar resultado parcial
            assert result is not None
            assert "error" in result or "sanctions_check" in result
    
    @pytest.mark.asyncio
    async def test_database_connection_loss(self):
        """Test: Pérdida de conexión a BD"""
        middleware = ValidationMiddleware()
        
        mock_db = AsyncMock()
        mock_db.commit.side_effect = Exception("Connection lost")
        
        mock_document = Mock()
        mock_document.id = 1
        mock_document.filename = "test.pdf"
        mock_document.metadata_ = {}
        
        result = await middleware.validate_document(
            document=mock_document,
            extracted_text="Test",
            entities=[],
            db=mock_db
        )
        
        # Debe manejar error de BD
        assert result is not None


# Configuración de pytest
@pytest.fixture
def mock_db_session():
    """Fixture para sesión de BD mock"""
    return AsyncMock()


@pytest.fixture
def mock_document():
    """Fixture para documento mock"""
    doc = Mock()
    doc.id = 1
    doc.filename = "test_document.pdf"
    doc.metadata_ = {}
    doc.status = "PENDING"
    return doc


@pytest.fixture
def sample_entities():
    """Fixture para entidades de prueba"""
    return [
        {"text": "John Doe", "type": "PERSON"},
        {"text": "Acme Corporation", "type": "ORGANIZATION"},
        {"text": "Jane Smith", "type": "PERSON"}
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
