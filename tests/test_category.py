"""Test category models and functionality."""

import pytest
from pydantic import ValidationError

from truledgr_api.models.category import CategoryCreate, CategoryUpdate, CategoryType


def test_valid_category_types():
    """Test that valid category types are accepted."""
    # Test DEBIT
    category = CategoryCreate(
        name="Groceries",
        category_type=CategoryType.DEBIT
    )
    assert category.category_type == CategoryType.DEBIT
    
    # Test CREDIT
    category = CategoryCreate(
        name="Salary",
        category_type=CategoryType.CREDIT
    )
    assert category.category_type == CategoryType.CREDIT
    
    # Test INCOME
    category = CategoryCreate(
        name="Freelance",
        category_type=CategoryType.INCOME
    )
    assert category.category_type == CategoryType.INCOME


def test_category_creation_defaults():
    """Test default values in category creation."""
    category = CategoryCreate(name="Test Category")
    assert category.category_type == CategoryType.OTHER
    assert category.parent_id is None
    assert category.color is None
    assert category.icon is None
    assert category.description is None


def test_category_update():
    """Test category update functionality."""
    update = CategoryUpdate(
        name="Updated Name",
        color="#FF5733"
    )
    assert update.name == "Updated Name"
    assert update.color == "#FF5733"
    assert update.category_type is None  # Not updated


def test_category_hierarchy():
    """Test category parent-child relationships."""
    parent = CategoryCreate(
        name="Food",
        category_type=CategoryType.DEBIT
    )
    
    child = CategoryCreate(
        name="Groceries",
        category_type=CategoryType.DEBIT,
        parent_id="parent_id_placeholder"  # Would be actual parent ID
    )
    
    assert parent.parent_id is None
    assert child.parent_id == "parent_id_placeholder"
