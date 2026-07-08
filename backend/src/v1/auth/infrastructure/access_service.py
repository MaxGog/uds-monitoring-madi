import logging

from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

logger = logging.getLogger(__file__)

class AccessManager:
    def __init__(self, user_repo: IUserRepo):
        self.user_repo = user_repo


    async def has_permission(self, user_id: str, required_entity: EntityType, required_action: ActionType) -> bool:
        try:
            user: User = await self.user_repo.get_by_id(user_id)
            if not user or not user.role:
                return False
                
            role = user.role
            
            for perm in role.permissions:
                entity_match = (perm.entity == EntityType.ALL or perm.entity == required_entity)
                action_match = (perm.action == ActionType.MANAGE or perm.action == required_action)

                if entity_match and action_match:
                    return True
                        
            return False
        except Exception as e:
            logger.error(e)
            
    async def get_allowed_scope(self, user_id: str, required_entity: EntityType, required_action: ActionType) -> ScopeType | None:
        try:
            user: User = await self.user_repo.get_by_id(user_id)
            if not user or not user.role:
                return None
                
            role = user.role
            
            for perm in role.permissions:
                entity_match = (perm.entity == EntityType.ALL or perm.entity == required_entity)
                action_match = (perm.action == ActionType.MANAGE or perm.action == required_action)
                
                if entity_match and action_match:
                    return role.scope
                    
            return None
        except Exception as e:
            logger.error(e)
    
    