from fastapi import Depends, HTTPException, status
from apils.domain.entities.user import User
from apils.core.fastapi_users import current_active_user

get_current_user = current_active_user

class RequirePermissions:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    async def __call__(self, user: User = Depends(current_active_user)):
        user_permissions = []
        for role in user.roles:
            for perm in role.permissions:
                user_permissions.append(perm.name)
        
        # Check if user has all required permissions
        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm}"
                )
        return user
