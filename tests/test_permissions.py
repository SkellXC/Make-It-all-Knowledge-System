"""Checks on authentication/permissions.py. No database or Qt needed."""
import re

from authentication.permissions import (
    ADMIN_ROLE,
    DEFAULT_ROLE_PERMISSIONS,
    PERMISSIONS,
    ROLES,
    can,
)


def test_can_is_false_without_a_user():
    assert can(None, "projects.view_own") is False


def test_administrator_has_every_permission_without_loading_any():
    admin = {"role": ADMIN_ROLE}
    assert all(can(admin, key) for key in PERMISSIONS)


def test_other_roles_only_have_what_was_loaded_at_login():
    user = {"role": "employee", "permissions": {"projects.view_own"}}
    assert can(user, "projects.view_own")
    assert not can(user, "projects.create")


def test_user_dict_without_permissions_has_none():
    # This is the bug that happens if login_user() forgets to include them.
    assert not can({"role": "employee"}, "projects.view_own")


def test_default_grants_only_name_real_permissions():
    for role, keys in DEFAULT_ROLE_PERMISSIONS.items():
        unknown = set(keys) - set(PERMISSIONS)
        assert not unknown, f"{role} is given permissions that don't exist: {unknown}"


def test_default_grants_only_name_real_roles():
    role_names = {name for name, _icon, _locked in ROLES}
    assert set(DEFAULT_ROLE_PERMISSIONS) <= role_names


def test_administrator_is_locked_and_has_no_default_list():
    locked = {name: is_locked for name, _icon, is_locked in ROLES}
    assert locked[ADMIN_ROLE] is True
    assert ADMIN_ROLE not in DEFAULT_ROLE_PERMISSIONS


def test_permission_keys_look_like_area_dot_action():
    # The Roles & Permissions page groups checkboxes by the part before the dot.
    for key in PERMISSIONS:
        assert re.fullmatch(r"[a-z_]+\.[a-z_]+", key), f"bad permission key: {key}"