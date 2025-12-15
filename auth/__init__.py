from fastapi import APIRouter

from .basic.views import router as basic_auth_router

router=APIRouter()
router.include_router(router=basic_auth_router)