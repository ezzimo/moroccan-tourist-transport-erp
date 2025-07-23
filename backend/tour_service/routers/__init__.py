"""
API routers for the tour operations microservice
"""
from .tour_templates import router as tour_templates_router
from .tour_instances import router as tour_instances_router
from .itinerary import router as itinerary_router
from .incidents import router as incidents_router

__all__ = ["tour_templates_router", "tour_instances_router", "itinerary_router", "incidents_router"]