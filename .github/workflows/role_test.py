"""Roles and permissions in the database, plus login."""
import pytest

from authentication.login_backend import login_user
from authentication.permissions import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS

ADMIN = {"role": "administrator"}


def permissions_of(db, role):
    return db.get_permissions_for_role(role)


def test_roles_and_permissions_are_seeded(db):
    roles = {name for _id, name, _icon, _locked in db.get_all_roles()}
    assert roles == {"employee", "team leader", "manager", "administrator"}
    assert {key for key, _description in db.get_all_permissions()} == set(PERMISSIONS)


def test_default_permissions_are_applied(db):
    for role, keys in DEFAULT_ROLE_PERMISSIONS.items():
        assert permissions_of(db, role) == set(keys)


def test_administrator_gets_everything(db):
    assert permissions_of(db, "administrator") == set(PERMISSIONS)


def test_starting_up_again_does_not_change_anything(db):
    before = {role: permissions_of(db, role) for role in DEFAULT_ROLE_PERMISSIONS}
    db.create_tables()
    after = {role: permissions_of(db, role) for role in DEFAULT_ROLE_PERMISSIONS}
    assert before == after


def test_admin_can_grant_and_revoke(db):
    db.set_role_permission(ADMIN, "employee", "projects.create", True)
    assert "projects.create" in permissions_of(db, "employee")
    db.set_role_permission(ADMIN, "employee", "projects.create", False)
    assert "projects.create" not in permissions_of(db, "employee")


def test_user_without_roles_manage_is_refused(db):
    manager = {"role": "manager", "permissions": permissions_of(db, "manager")}
    with pytest.raises(PermissionError):
        db.set_role_permission(manager, "employee", "projects.create", True)
    assert "projects.create" not in permissions_of(db, "employee")


def test_locked_role_cannot_be_changed(db):
    with pytest.raises(PermissionError):
        db.set_role_permission(ADMIN, "administrator", "projects.create", False)


def test_unknown_role_or_permission_is_rejected(db):
    with pytest.raises(ValueError):
        db.set_role_permission(ADMIN, "ghost role", "projects.create", True)
    with pytest.raises(ValueError):
        db.set_role_permission(ADMIN, "employee", "nope.nope", True)


def test_roles_manage_can_be_delegated(db):
    db.set_role_permission(ADMIN, "manager", "roles.manage", True)
    manager = {"role": "manager", "permissions": permissions_of(db, "manager")}
    db.set_role_permission(manager, "employee", "projects.create", True)
    assert "projects.create" in permissions_of(db, "employee")


def test_login_returns_the_users_permissions(db, accounts):
    email, password = accounts["manager"]
    user = login_user(email, password)
    assert user["role"] == "manager"
    assert user["permissions"] == permissions_of(db, "manager")


def test_login_rejects_bad_credentials(db, accounts):
    email, password = accounts["employee"]
    assert login_user(email, "wrong password") is None
    assert login_user("nobody@makeitall.com", password) is None