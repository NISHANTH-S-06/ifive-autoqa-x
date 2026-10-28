"""Pytest Unit Test Suite for Version 2.0 Platform Foundation."""
import pytest
import asyncio
from app.v2.agents import BaseAgent, AgentContext, AgentResult, AgentCapability, AgentRegistry, AgentFactory
from app.v2.events import EventBus, EventStore, EventPublisher, AgentStarted, BaseEvent
from app.v2.plugins import PluginBase, PluginManifest, PluginContext, PluginResult, PluginRegistry, PluginManager
from app.v2.config import v2_settings, V2_VERSION, PHASE_MARKER
from app.v2.core import Container, ServiceLocator, BaseException, AgentException
from app.v2.utils import LoggerFactory


# Mock Agent Implementation for Testing
class DummyAgent(BaseAgent):
    async def initialize(self, config: dict) -> bool:
        self._is_initialized = True
        return True

    async def execute_task(self, context: AgentContext) -> AgentResult:
        return AgentResult(agent_id=self.agent_id, status="SUCCESS", output={"test": "pass"})

    async def evaluate_result(self, result: AgentResult) -> dict:
        return {"confidence": 1.0}

    async def shutdown(self) -> None:
        self._is_initialized = False


# Mock Plugin Implementation for Testing
class DummyPlugin(PluginBase):
    async def initialize(self, config: dict) -> bool:
        return True

    async def handle_event(self, context: PluginContext) -> PluginResult:
        return PluginResult(plugin_id=self.plugin_id, status="SUCCESS", data={"handled": True})

    async def health_check(self) -> dict:
        return {"status": "ok"}


@pytest.mark.anyio
async def test_agent_framework_registry_and_factory():
    registry = AgentRegistry()
    registry.register("dummy", DummyAgent)
    assert "dummy" in registry.list_registered()

    factory = AgentFactory(registry)
    agent = factory.create_agent("dummy", name="Dummy Agent", capabilities=[AgentCapability.PLANNING])
    assert agent.name == "Dummy Agent"

    ctx = AgentContext(run_id="run-101", project_id=1)
    res = await agent.execute_task(ctx)
    assert res.status == "SUCCESS"
    assert res.output["test"] == "pass"


@pytest.mark.anyio
async def test_event_framework_bus_and_publisher():
    store = EventStore()
    bus = EventBus(store=store)
    received = []

    async def handler(event: BaseEvent):
        received.append(event)

    bus.subscribe("AgentStarted", handler)

    event = AgentStarted(payload={"agent_id": "agent-1"})
    await bus.publish(event)

    assert len(received) == 1
    assert received[0].payload["agent_id"] == "agent-1"
    assert len(store.get_all()) == 1


@pytest.mark.anyio
async def test_plugin_sdk_manager_and_dispatch():
    manifest = PluginManifest(
        plugin_id="org.ifive.dummy",
        name="Dummy Plugin",
        supported_target="Jira",
        supported_events=["TaskCreated"],
    )
    plugin = DummyPlugin(manifest)
    registry = PluginRegistry()
    registry.register(plugin)

    manager = PluginManager(registry)
    results = await manager.dispatch_event("TaskCreated", {"task_name": "Test Task"})
    assert len(results) == 1
    assert results[0].plugin_id == "org.ifive.dummy"
    assert results[0].status == "SUCCESS"


def test_configuration_settings():
    assert v2_settings.version == V2_VERSION
    assert v2_settings.phase == PHASE_MARKER
    assert v2_settings.features.enable_v2_platform is True


def test_dependency_injection_container():
    container = Container()
    container.register_singleton(str, "TestSingleton")
    assert container.resolve(str) == "TestSingleton"

    ServiceLocator.set_container(container)
    assert ServiceLocator.get_container().resolve(str) == "TestSingleton"


def test_logging_and_error_framework():
    logger = LoggerFactory.get_logger("v2.test")
    assert logger is not None

    err = AgentException("Agent failed", agent_id="agent-99")
    assert err.error_code == "AGENT_ERROR"
    assert err.agent_id == "agent-99"
