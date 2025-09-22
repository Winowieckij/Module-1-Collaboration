from flask import Flask, request, jsonify, abort, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "book_name": self.book_name,
            "author": self.author,
            "publisher": self.publisher
        }

@app.before_first_request
def init_db():
    db.create_all()

@app.route("/api/books", methods=["GET"])
def list_books():
    books = Book.query.order_by(Book.id).all()
    return jsonify([b.to_dict() for b in books])

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    b = Book.query.get_or_404(book_id)
    return jsonify(b.to_dict())

@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}
    for field in ("book_name", "author", "publisher"):
        if field not in data or not str(data[field]).strip():
            abort(400, f"Missing field: {field}")
    b = Book(book_name=data["book_name"].strip(),
             author=data["author"].strip(),
             publisher=data["publisher"].strip())
    db.session.add(b)
    db.session.commit()
    resp = jsonify(b.to_dict())
    resp.status_code = 201
    resp.headers["Location"] = url_for("get_book", book_id=b.id, _external=True)
    return resp

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    b = Book.query.get_or_404(book_id)
    data = request.get_json(silent=True) or {}
    for field in ("book_name", "author", "publisher"):
        if field not in data or not str(data[field]).strip():
            abort(400, f"Missing field: {field}")
    b.book_name = data["book_name"].strip()
    b.author = data["author"].strip()
    b.publisher = data["publisher"].strip()
    db.session.commit()
    return jsonify(b.to_dict())

@app.route("/api/books/<int:book_id>", methods=["PATCH"])
def patch_book(book_id):
    b = Book.query.get_or_404(book_id)
    data = request.get_json(silent=True) or {}
    if "book_name" in data:
        b.book_name = str(data["book_name"]).strip()
    if "author" in data:
        b.author = str(data["author"]).strip()
    if "publisher" in data:
        b.publisher = str(data["publisher"]).strip()
    db.session.commit()
    return jsonify(b.to_dict())

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    b = Book.query.get_or_404(book_id)
    db.session.delete(b)
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
