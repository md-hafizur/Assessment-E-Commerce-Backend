from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.category import Category
from app.core.cache import cache


class CategoryTree:
    """DFS-based category tree traversal with caching"""
    
    @staticmethod
    def build_tree(db: Session, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Build complete category tree using DFS traversal"""
        
        # Try to get from cache first
        if use_cache:
            cached_tree = cache.get("category_tree")
            if cached_tree:
                return cached_tree
        
        # Get all categories from database
        categories = db.query(Category).all()
        
        # Build category map for O(1) lookup
        category_map = {cat.id: cat for cat in categories}
        
        # Find root categories (no parent)
        root_categories = [cat for cat in categories if cat.parent_id is None]
        
        # Build tree using DFS
        tree = []
        for root in root_categories:
            tree.append(CategoryTree._dfs_traverse(root, category_map))
        
        # Cache the tree
        if use_cache:
            cache.set("category_tree", tree)
        
        return tree
    
    @staticmethod
    def _dfs_traverse(category: Category, category_map: Dict[int, Category]) -> Dict[str, Any]:
        """DFS recursive traversal to build category tree"""
        
        # Build current node
        node = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "parent_id": category.parent_id,
            "children": []
        }
        
        # Find all children
        children = [cat for cat in category_map.values() if cat.parent_id == category.id]
        
        # Recursively traverse children
        for child in children:
            node["children"].append(CategoryTree._dfs_traverse(child, category_map))
        
        return node
    
    @staticmethod
    def get_category_path(db: Session, category_id: int) -> List[Dict[str, Any]]:
        """Get path from root to specific category"""
        
        path = []
        current_category = db.query(Category).filter(Category.id == category_id).first()
        
        if not current_category:
            return path
        
        # Traverse up to root
        while current_category:
            path.insert(0, {
                "id": current_category.id,
                "name": current_category.name,
                "slug": current_category.slug
            })
            
            if current_category.parent_id:
                current_category = db.query(Category).filter(
                    Category.id == current_category.parent_id
                ).first()
            else:
                break
        
        return path
    
    @staticmethod
    def get_related_categories(db: Session, category_id: int) -> List[int]:
        """Get all related category IDs (siblings and children) using DFS"""
        
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return []
        
        related_ids = [category_id]
        
        # Get siblings (same parent)
        if category.parent_id:
            siblings = db.query(Category).filter(
                Category.parent_id == category.parent_id,
                Category.id != category_id
            ).all()
            related_ids.extend([sib.id for sib in siblings])
        
        # Get all descendants using DFS
        descendants = CategoryTree._get_descendants_dfs(db, category_id)
        related_ids.extend(descendants)
        
        return list(set(related_ids))
    
    @staticmethod
    def _get_descendants_dfs(db: Session, category_id: int) -> List[int]:
        """Get all descendant category IDs using DFS"""
        
        descendants = []
        children = db.query(Category).filter(Category.parent_id == category_id).all()
        
        for child in children:
            descendants.append(child.id)
            # Recursive DFS
            descendants.extend(CategoryTree._get_descendants_dfs(db, child.id))
        
        return descendants
    
    @staticmethod
    def invalidate_cache():
        """Invalidate category tree cache"""
        cache.delete("category_tree")