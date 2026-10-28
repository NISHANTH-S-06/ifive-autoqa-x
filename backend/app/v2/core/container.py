"""Dependency Injection Framework for Version 2.0."""
from typing import Dict, Any, Type, Callable, Optional


class Provider:
    def get(self) -> Any:
        raise NotImplementedError


class SingletonProvider(Provider):
    def __init__(self, factory_func: Callable[[], Any]):
        self.factory_func = factory_func
        self._instance: Optional[Any] = None

    def get(self) -> Any:
        if self._instance is None:
            self._instance = self.factory_func()
        return self._instance


class FactoryProvider(Provider):
    def __init__(self, factory_func: Callable[[], Any]):
        self.factory_func = factory_func

    def get(self) -> Any:
        return self.factory_func()


class Container:
    def __init__(self):
        self._providers: Dict[Type[Any], Provider] = {}

    def register_singleton(self, service_type: Type[Any], instance_or_factory: Any) -> None:
        if callable(instance_or_factory) and not isinstance(instance_or_factory, type):
            self._providers[service_type] = SingletonProvider(instance_or_factory)
        else:
            self._providers[service_type] = SingletonProvider(lambda: instance_or_factory)

    def register_factory(self, service_type: Type[Any], factory_func: Callable[[], Any]) -> None:
        self._providers[service_type] = FactoryProvider(factory_func)

    def resolve(self, service_type: Type[Any]) -> Any:
        provider = self._providers.get(service_type)
        if not provider:
            raise KeyError(f"Service '{service_type}' is not registered in Container.")
        return provider.get()

    def clear(self) -> None:
        self._providers.clear()


class ServiceLocator:
    _global_container: Optional[Container] = None

    @classmethod
    def set_container(cls, container: Container) -> None:
        cls._global_container = container

    @classmethod
    def get_container(cls) -> Container:
        if cls._global_container is None:
            cls._global_container = Container()
        return cls._global_container


class DependencyResolver:
    def __init__(self, container: Optional[Container] = None):
        self.container = container or ServiceLocator.get_container()

    def resolve(self, service_type: Type[Any]) -> Any:
        return self.container.resolve(service_type)


class ApplicationContext:
    def __init__(self, container: Optional[Container] = None):
        self.container = container or Container()
        ServiceLocator.set_container(self.container)

    def shutdown(self) -> None:
        self.container.clear()
