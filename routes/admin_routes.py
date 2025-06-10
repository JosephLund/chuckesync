import json
from flask import Blueprint, current_app, session, redirect, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
import backend
from models import User, db

admin_bp = Blueprint('admin', __name__)






@admin_bp.route("/clear_user/<email>", methods=["POST"])
def clear_user(email):
    protected_email = current_app.config.get("PROTECTED_ADMIN_EMAIL")
    if email == protected_email:
        return "Cannot delete protected admin", 403

    user = User.get_user(email)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for("main.admin"))


@admin_bp.route("/toggle_admin/<email>", methods=["POST"])
def toggle_admin(email):
    protected_email = current_app.config.get("PROTECTED_ADMIN_EMAIL")
    if email == protected_email:
        return "Cannot modify protected admin", 403

    user = User.get_user(email)
    if not user:
        return "User not found", 404

    user.is_admin = not user.is_admin
    db.session.commit()

    return redirect(url_for("main.admin"))


@admin_bp.route("/seed_test_users")
def seed_test_users():
    dummy_emails = [
        "test1@example.com",
        "test2@example.com",
        "test3@example.com"
    ]

    for email in dummy_emails:
        user = User.get_user(email)
        if not user:
            new_user = User(email=email, is_admin=False)
            db.session.add(new_user)

    db.session.commit()
    return "Test users inserted!"

@admin_bp.route("/delete_test_users")
def delete_test_users():
    dummy_emails = [
        "test1@example.com",
        "test2@example.com",
        "test3@example.com"
    ]

    for email in dummy_emails:
        user = User.get_user(email)
        if user:
            db.session.delete(user)

    db.session.commit()
    return "Test users deleted!"