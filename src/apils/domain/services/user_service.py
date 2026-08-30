from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apils.domain.entities.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()
