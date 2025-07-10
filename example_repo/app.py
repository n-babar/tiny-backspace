from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    # TODO: Add validation
    return jsonify({"message": "User created", "user": user_data})

@app.route('/posts', methods=['POST'])
def create_post():
    post_data = request.get_json()
    # TODO: Add validation
    return jsonify({"message": "Post created", "post": post_data})

@app.route('/comments', methods=['POST'])
def create_comment():
    comment_data = request.get_json()
    # TODO: Add validation
    return jsonify({"message": "Comment created", "comment": comment_data})

if __name__ == '__main__':
    app.run(debug=True) 