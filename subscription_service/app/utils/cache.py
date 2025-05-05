from typing import List, Optional


async def get_cached_feed(user_id: int) -> Optional[List[dict]]:
    return None

async def set_cached_feed(user_id: int, posts: List[dict]) -> None:
    pass

async def invalidate_feeds_of_followers(follower_ids: List[int]) -> None:
    pass