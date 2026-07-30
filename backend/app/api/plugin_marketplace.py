from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.plugin_marketplace import PluginMarketplaceService

router = APIRouter(prefix='/plugins', tags=['plugin-marketplace'], dependencies=[Depends(get_auth_context)])


@router.get('/', summary='List Plugin Marketplace Packages')
def list_packages(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = PluginMarketplaceService(db)
    service.seed_marketplace()
    return service.list_packages()


@router.post('/{package_id}/install', summary='Install Plugin Package')
def install_package(
    package_id: int = Path(...),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = PluginMarketplaceService(db)
    return service.install_package(package_id)


@router.post('/{package_id}/uninstall', summary='Uninstall Plugin Package')
def uninstall_package(
    package_id: int = Path(...),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = PluginMarketplaceService(db)
    return service.uninstall_package(package_id)
