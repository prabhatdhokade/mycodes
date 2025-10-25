"""Hot topics API routes for social media trending analysis."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/hot-topics", tags=["hot-topics"])

# Redis client for caching
redis_client = None
try:
    import redis
    redis_client = redis.from_url(settings.redis_url)
except ImportError:
    print("Redis not installed, caching disabled")
except Exception as e:
    print(f"Redis not available: {e}")


class HotTopicsService:
    """Service for managing trending topics and posts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis_client
        self.cache_ttl = 60  # 1 minute cache
    
    def calculate_engagement_score(self, post: Dict[str, Any]) -> float:
        """Calculate engagement score for a post."""
        likes = post.get("likes", 0)
        views = post.get("views", 0)
        comments = post.get("comments", 0)
        
        # Engagement formula: (likes*2 + views*0.5 + comments*3)
        return (likes * 2) + (views * 0.5) + (comments * 3)
    
    def get_trending_posts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending posts sorted by engagement score."""
        cache_key = f"trending_posts_{limit}"
        
        # Try to get from cache first
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        # Generate mock data if not cached
        posts = self._generate_mock_posts()
        
        # Calculate engagement scores and sort
        for post in posts:
            post["engagement_score"] = self.calculate_engagement_score(post)
        
        # Sort by engagement score (descending)
        trending_posts = sorted(posts, key=lambda x: x["engagement_score"], reverse=True)[:limit]
        
        # Cache the results
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(trending_posts)
                )
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        return trending_posts
    
    def get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all categories with their top 3 trending posts."""
        cache_key = "categories_trending"
        
        # Try to get from cache first
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        # Get all trending posts
        all_posts = self._generate_mock_posts()
        
        # Calculate engagement scores
        for post in all_posts:
            post["engagement_score"] = self.calculate_engagement_score(post)
        
        # Group by category
        categories = {}
        for post in all_posts:
            category = post["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(post)
        
        # Sort each category by engagement score and take top 3
        for category in categories:
            categories[category] = sorted(
                categories[category],
                key=lambda x: x["engagement_score"],
                reverse=True
            )[:3]
        
        # Cache the results
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(categories)
                )
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        return categories
    
    def _generate_mock_posts(self) -> List[Dict[str, Any]]:
        """Generate mock social media posts for testing."""
        import random
        
        categories = [
            "Technology", "Sports", "Entertainment", "Politics", "Business",
            "Health", "Science", "Travel", "Food", "Fashion", "Music", "Gaming"
        ]
        
        posts = []
        for i in range(100):  # Generate 100 mock posts
            post = {
                "post_id": f"post_{i+1:03d}",
                "category": random.choice(categories),
                "title": f"Mock Post {i+1}",
                "content": f"This is mock content for post {i+1}",
                "likes": random.randint(0, 1000),
                "views": random.randint(100, 10000),
                "comments": random.randint(0, 200),
                "created_at": datetime.utcnow().isoformat(),
                "author": f"user_{random.randint(1, 50)}"
            }
            posts.append(post)
        
        return posts


@router.get("/trending")
async def get_trending_posts(
    limit: int = Query(20, ge=1, le=100, description="Number of trending posts to return"),
    db: Session = Depends(get_db)
):
    """Get top trending posts sorted by engagement score."""
    service = HotTopicsService(db)
    trending_posts = service.get_trending_posts(limit)
    
    return {
        "trending_posts": trending_posts,
        "total_count": len(trending_posts),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/categories")
async def get_categories_with_trending(
    db: Session = Depends(get_db)
):
    """Get all categories with their top 3 trending posts."""
    service = HotTopicsService(db)
    categories = service.get_categories()
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/categories/{category}")
async def get_category_trending(
    category: str,
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    db: Session = Depends(get_db)
):
    """Get trending posts for a specific category."""
    service = HotTopicsService(db)
    all_posts = service._generate_mock_posts()
    
    # Filter by category
    category_posts = [post for post in all_posts if post["category"].lower() == category.lower()]
    
    if not category_posts:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Calculate engagement scores and sort
    for post in category_posts:
        post["engagement_score"] = service.calculate_engagement_score(post)
    
    trending_posts = sorted(category_posts, key=lambda x: x["engagement_score"], reverse=True)[:limit]
    
    return {
        "category": category,
        "trending_posts": trending_posts,
        "total_count": len(trending_posts),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/stats")
async def get_hot_topics_stats(db: Session = Depends(get_db)):
    """Get statistics about hot topics system."""
    service = HotTopicsService(db)
    all_posts = service._generate_mock_posts()
    
    # Calculate engagement scores
    for post in all_posts:
        post["engagement_score"] = service.calculate_engagement_score(post)
    
    # Get top 10 posts
    top_posts = sorted(all_posts, key=lambda x: x["engagement_score"], reverse=True)[:10]
    
    # Calculate average engagement by category
    categories = {}
    for post in all_posts:
        category = post["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(post["engagement_score"])
    
    category_stats = {}
    for category, scores in categories.items():
        category_stats[category] = {
            "post_count": len(scores),
            "avg_engagement": sum(scores) / len(scores),
            "max_engagement": max(scores),
            "min_engagement": min(scores)
        }
    
    return {
        "total_posts": len(all_posts),
        "total_categories": len(categories),
        "top_10_posts": top_posts,
        "category_statistics": category_stats,
        "generated_at": datetime.utcnow().isoformat()
    }