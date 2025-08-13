from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import math  # JANGAN LUPA IMPORT INI
from models import Base, Keylog, Posture, User

app = Flask(__name__)
CORS(app)

# Konfigurasi koneksi ke PostgreSQL
DB_URL = 'postgresql://postgres:123@proxy.bccdev.id:11015/riset_db'
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)


# Base.metadata.create_all(engine) # Sebaiknya tidak dijalankan setiap kali server start di produksi

# --- FUNGSI HELPER PAGINATION DITARUH DI SINI ---
def paginate_query(query, request):
    """
    Fungsi helper untuk menerapkan pagination pada query SQLAlchemy.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page
    results = query.offset(offset).limit(per_page).all()

    data = [item.as_dict() for item in results]

    pagination_meta = {
        'total': total,
        'per_page': per_page,
        'page': page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
    }
    return {
        "data": data,
        "pagination": pagination_meta
    }


# -----------------------------------------------

@app.route('/')
def index():
    return "Riset API is Running!"


@app.route('/keylog', methods=['GET'])
def get_keylogs():
    session = Session()
    try:
        email_filter = request.args.get('email')
        query = session.query(Keylog)

        if email_filter:
            query = query.filter(Keylog.user_email == email_filter)

        paginated_data = paginate_query(query, request)
        return jsonify(paginated_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


from sqlalchemy import asc

@app.route('/posture', methods=['GET'])
def get_postures():
    session = Session()
    try:
        email_filter = request.args.get('email')
        query = session.query(Posture)

        if email_filter:
            query = query.filter(Posture.user_email == email_filter)

        query = query.order_by(asc(Posture.timestamp))

        paginated_data = paginate_query(query, request)
        return jsonify(paginated_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/users', methods=['GET'])
def get_users():
    session = Session()
    try:
        query = session.query(User).all()

        users = [user.as_dict() for user in query]

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)