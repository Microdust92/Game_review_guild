from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from game_Module import GameSession




app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.now(timezone.utc))



class GameReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name2 = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.now(timezone.utc))


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('homepage'))



@app.route('/Homepage', methods=['GET', 'POST'])
def homepage():
    session.clear()
    return render_template('homepage.html')




@app.route('/play', methods=['GET', 'POST'])
def game_play():

    if 'game' not in session:
        session['game'] = {"score": 0, "stage": "intro"}
        session.modified = True

    game = GameSession()
    game.stage = session['game']['stage']
    game.score = session['game']['score']

    user_input = None
    if request.method == 'POST': 
        user_input = request.form.get('user_input', '').strip()

    output = game.next(user_input)

    session["game"]["stage"] = game.stage
    session["game"]["score"] = game.score
    session.modified = True

    if game.stage == "end":
        session['final_score'] = game.final_score
        return redirect(url_for('submit_score'))

    return render_template('game.html', output=output)





@app.route('/submit_score', methods=['GET', 'POST'])
def submit_score():
    final_score = session.get('final_score', 0)
    if request.method == 'POST':
        player_name = request.form['player_name']
        score = Score(name=player_name, score=final_score)
        db.session.add(score)
        db.session.commit()
        session.clear()
        return redirect(url_for('scoreboard'))
    return render_template('submit_score.html', final_score=final_score)



# @app.route('/game_over')
# def game_over():
#     score = session.get('game', {}).get('score', 0)
#     return render_template('game_over.html', score=score)

@app.route('/scoreboard', methods=['GET', 'POST'])
def scoreboard():
    scores = Score.query.order_by(Score.score.desc()).all()
    return render_template('scoreboard.html', scores=scores)


# @app.route('/submit_Review', methods=['GET', 'POST'])
# def submit_review():




@app.route('/review_board', methods=['GET', 'POST'])
def review_board():
    if request.method == 'POST':
        player_name = request.form.get('player_name', '').strip()
        rating = request.form.get('rating', '').strip()
        review_text = request.form.get('review_text', '').strip()

        if not player_name or not rating or not review_text:
            error = "Please fill in all fields."
            reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
            return render_template('review_board.html', reviews=reviews, error=error)

        try:
            new_review = GameReview(
                player_name2=player_name,
                rating=int(rating),
                review_text=review_text
            )   
            db.session.add(new_review)
            db.session.commit()
            return redirect(url_for('submission_success'))
        except Exception as e:
            db.session.rollback()
            error = f"Error submitting review: {str(e)}"
            reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
            return render_template('review_board.html', reviews=reviews, error=error)

    reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
    return render_template('review_board.html', reviews=reviews)


@app.route('/submission_Success')
def submission_success():
    return render_template('submission_Success.html')



@app.route('/admin/maintenance')
def admin_maintenance():
    scores = Score.query.order_by(Score.score.desc()).all()
    reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
    return render_template('admin_maintenance.html', scores=scores, reviews=reviews)

@app.route('/admin/delete_score/<int:score_id>', methods=['POST'])
def admin_delete_score(score_id):
    try:
        score_entry = Score.query.get_or_404(score_id)
        db.session.delete(score_entry)
        db.session.commit()
        return redirect(url_for('admin_maintenance'))
    except Exception as e:
        db.session.rollback()
        errorMsg = f"Error deleting score: {str(e)}"
        scores = Score.query.order_by(Score.score.desc()).all()
        reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
        return render_template('admin_maintenance.html', scores=scores, reviews=reviews, error=errorMsg)


@app.route('/admin/reset_scores')
def admin_reset_scores():
    try:
        Score.query.delete()
        db.session.commit()
        return redirect(url_for('admin_maintenance'))
    except Exception as e:
        db.session.rollback()
        errorMsg = f"Error resetting scores: {str(e)}"
        scores = Score.query.order_by(Score.score.desc()).all()
        reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
        return render_template('admin_maintenance.html', scores=scores, reviews=reviews, error=errorMsg)


@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
def admin_delete_review(review_id):
    try:
        review = GameReview.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        return redirect(url_for('admin_maintenance'))
    except Exception as e:
        db.session.rollback()
        errorMsg = f"Error deleting review: {str(e)}"
        scores = Score.query.order_by(Score.score.desc()).all()
        reviews = GameReview.query.order_by(GameReview.date_submitted.desc()).all()
        return render_template('admin_maintenance.html', scores=scores, reviews=reviews, error=errorMsg)   



@app.route('/admin/edit_review/<int:review_id>', methods=['GET', 'POST'])   
def admin_edit_review(review_id):
    review = GameReview.query.get_or_404(review_id)
    errorMsg = None
    if request.method == 'POST':
        try:
            review.player_name2 = request.form.get('player_name2', review.player_name2).strip()
            review.rating = int(request.form.get('rating', review.rating))
            review.review_text = request.form.get('review_text', review.review_text).strip()

            db.session.commit()
            return redirect(url_for('admin_maintenance'))

        except Exception as e:
            db.session.rollback()
            errorMsg = f"Error updating review: {str(e)}"
            

    return render_template('edit_review.html', review=review, error=errorMsg)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
