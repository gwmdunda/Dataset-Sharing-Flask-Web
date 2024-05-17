from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from __init__ import create_app, db, allowed_file
from models import *
from forms import *
import os

main = Blueprint('main', __name__)

@main.route('/') # home page that return 'index'
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form.get('title')
        description = request.form.get('description')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = secure_filename(f'{filename.split(".")[0]}_{str(datetime.now())}.csv')
            try:
                post = Post(title=title, description=description, filename=new_filename, admin=current_user)
                if not os.path.exists('uploads'):
                    os.makedirs('uploads')
                os.mkdir(os.path.join('uploads', str(post.slug)))
                file.save(os.path.join('uploads', post.slug, new_filename))
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('main.explore'))
            except Exception as e:
                print(e)
                flash('There is something wrong with our backend, please try again later!')
                return redirect(url_for('main.upload'))
        else:
            flash('File format should be csv!')
            return redirect(url_for('main.upload'))
    else:
        form = PostForm()
        return render_template('upload.html', form=form)

@main.route('/profile', methods=['GET', 'POST']) # profile page that return 'profile'
@login_required
def profile():
    if request.method == "GET":
        posts = Post.query.filter(Post.admin_id==current_user.id)
        invs = CuratorAssociation.query.filter((CuratorAssociation.user_id == current_user.id) & ~CuratorAssociation.accepted).all()
        return render_template('profile.html', posts=posts, invs=invs)
    else:
        post_id = request.form.get('post_id')
        post_id_acc = request.form.get('post_id_acc')
        if post_id:
            post_id = int(post_id)
            post = Post.query.filter(Post.id == post_id).first()
            if post:
                return redirect(url_for('detail.description', slug=post.slug))
            else:
                return redirect(url_for('main.profile'))
        elif post_id_acc:
            post_id_acc = int(post_id_acc)
            post = Post.query.filter(Post.id == post_id_acc).first()
            accept = int(request.form.get('accept'))
            if accept:
                inv = CuratorAssociation.query.filter((CuratorAssociation.user_id == current_user.id) & (CuratorAssociation.post_id == post.id)).first()
                inv.accepted = True
                db.session.commit()
                flash('Request accepted!', category="success")
                return redirect(url_for('main.profile'))
            else:
                assoc_del = CuratorAssociation.query.filter((CuratorAssociation.user_id == current_user.id) & (CuratorAssociation.post_id == post.id)).first()
                post.curators.remove(assoc_del)
                db.session.commit()
                flash('Request declined!', category="success")
                return redirect(url_for('main.profile'))

@main.route('/explore')
def explore():
    q = request.args.get('q')
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.description.contains(q))
    else:
        posts = Post.query.order_by(Post.created.desc())
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = posts.paginate(page=page, per_page=2)
    return render_template('explore.html', posts=posts, pages=pages)


app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    # db.create_all(app=app) # create the SQLite database
    with app.app_context():
        db.create_all()
    app.run(debug=True) # run the flask app on debug mode