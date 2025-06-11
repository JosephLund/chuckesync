from flask import Blueprint, request, jsonify, session
from models import Shift, Store, UserStore
from datetime import datetime

shifts_bp = Blueprint('shifts', __name__)

@shifts_bp.route('/api/shifts', methods=['GET'])
def get_shifts():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({"error": "Unauthorized"}), 401

    # Optional query params: store_id, start_date, end_date
    store_id = request.args.get('store_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Shift.query.filter_by(user_email=user_email)

    if store_id:
        query = query.filter_by(store_id=store_id)

    if start_date:
        query = query.filter(Shift.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
    if end_date:
        query = query.filter(Shift.date <= datetime.strptime(end_date, "%Y-%m-%d").date())

    shifts = query.order_by(Shift.date.asc(), Shift.start_time.asc()).all()

    result = []
    for shift in shifts:
        store = Store.query.get(shift.store_id)
        result.append({
            "id": shift.id,
            "store_id": shift.store_id,
            "store_name": store.name if store else "Unknown",
            "date": shift.date.strftime("%Y-%m-%d"),
            "start_time": shift.start_time.strftime("%H:%M"),
            "end_time": shift.end_time.strftime("%H:%M"),
        })

    return jsonify(result)
@shifts_bp.route('/api/stores', methods=['GET'])
def get_stores():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({"error": "Unauthorized"}), 401

    store_links = Store.query.join(UserStore).filter(UserStore.user_email == user_email).all()

    result = []
    for store in store_links:
        result.append({
            "id": store.id,
            "number": store.number,
            "name": store.name
        })

    return jsonify(result)