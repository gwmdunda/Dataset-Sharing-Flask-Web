from flask import Blueprint, render_template, flash, request, redirect, url_for, send_file
from flask_login import login_required, current_user
from models import *
from forms import *
from __init__ import db, allowed_file
from werkzeug.utils import secure_filename
import os
import sys
import pandas as pd
import re
import shutil

detail = Blueprint('detail', __name__)

@detail.route('/<slug>/description')
def description(slug):
    post = Post.query.filter(Post.slug==slug).first()
    submissions = Submission.query.order_by(Submission.created.desc())
    return render_template('detail/description.html', post=post, submissions=submissions)

@detail.route('/<slug>/submission', methods=['GET', 'POST'])
def submission(slug):
    post = Post.query.filter(Post.slug==slug).first()
    curator_id_list = [ca.user_id for ca in post.curators.all()]
    form = SubmissionForm()
    submissions = Submission.query.order_by(Submission.created.desc()).all()
    if request.method == "POST":
        file = request.files['csv_file']
        comment = request.form.get('comment')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = secure_filename(f'{filename.split(".")[0]}_{str(datetime.now())}.csv')
            try:
                submission = Submission(comment=comment, filename=new_filename, collaborator=current_user)
                if not os.path.exists(os.path.join('uploads', post.slug, 'curate')):
                    os.mkdir(os.path.join('uploads', post.slug, 'curate'))
                file.save(os.path.join('uploads', post.slug, 'curate', new_filename))
                db.session.add(submission)
                db.session.commit()
                flash('Submission is successful!')
                return redirect(url_for('detail.submission', slug=post.slug))
            except:
                flash('There is something wrong with our backend, please try again later!')
                return redirect(url_for('detail.submission', slug=post.slug))
        elif file and not allowed_file(file.filename):
            flash('Please submit a valid file!')
            return redirect(url_for('detail.submission', slug=post.slug))
        if current_user.id == post.admin_id or current_user.id in curator_id_list:
            resp = request.form.get("action")
            which = request.form.get("act")
            f = request.files.get("file")
            if resp and not which and not f:
                resp = int(resp)
                selected_submission = Submission.query.filter(Submission.id == resp).first()
                file_dir = os.path.join('uploads', post.slug, 'curate', selected_submission.filename)
                selected_submission.curator = current_user
                db.session.commit()
                return send_file(file_dir , as_attachment=True)

            if f and allowed_file(f.filename):
                resp = int(resp)
                selected_submission = Submission.query.filter(Submission.id == resp).first()
                filename = secure_filename(f.filename)
                base_name = re.split("_\d{4}-\d{2}-\d{2}", filename.split(".")[0])[0]
                new_filename = secure_filename(f'{base_name}_{str(datetime.now())}.csv')
                loc = os.path.join('uploads', slug)
                exst_file = os.path.join(loc, "curate", selected_submission.filename)
                os.remove(exst_file)
                selected_submission.filename = new_filename
                db.session.commit()
                f.save(os.path.join(loc, "curate", new_filename))
                submissions = Submission.query.order_by(Submission.created.desc()).all()

            if which and which == "accept":
                resp = int(resp)
                selected_submission = Submission.query.filter(Submission.id == resp).first()
                loc = os.path.join('uploads', slug)
                current_csv_fn = [f for f in os.listdir(loc) if os.path.isfile(os.path.join(loc, f))][0]
                base_name = re.split("_\d{4}-\d{2}-\d{2}", current_csv_fn.split(".")[0])[0]
                new_filename = secure_filename(f'{base_name}_{str(datetime.now())}.csv')
                current_csv_fn = os.path.join(loc, current_csv_fn)
                current_csv = pd.read_csv(current_csv_fn)
                sel_fn = os.path.join(loc, "curate", selected_submission.filename)
                curated_csv = pd.read_csv(sel_fn)
                merged = pd.concat([current_csv, curated_csv])
                merged.to_csv(os.path.join(loc, new_filename), index=False)
                post.filename = new_filename
                os.remove(current_csv_fn)
                os.remove(os.path.join(loc, "curate", selected_submission.filename))
                db.session.delete(selected_submission)
                db.session.commit()
                submissions = Submission.query.order_by(Submission.created.desc()).all()
                
            
            if which and which == "decline":
                resp = int(resp)
                selected_submission = Submission.query.filter(Submission.id == resp).first()
                loc = os.path.join('uploads', slug)
                exst_file = os.path.join(loc, "curate", selected_submission.filename)
                db.session.delete(selected_submission)
                db.session.commit()
                os.remove(exst_file)
                

    if current_user.id != post.admin_id and current_user.id not in curator_id_list:
        return render_template('detail/submission.html', post=post, submissions=submissions, form=form, sub=False)
    else:
        return render_template('detail/submission.html', post=post, submissions=submissions, form=form, sub=True)
    

@detail.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = Post.query.filter(Post.slug==slug).first()
    if request.method == "POST":
        form = PostForm(formdata=request.form, obj=post)
        form.populate_obj(post)
        db.session.commit()
        return redirect(url_for('detail.description', slug=post.slug))
    form = PostForm(obj=post)
    return render_template('detail/edit.html', post=post, form=form)

@detail.route('/<slug>/manage_curators', methods=['GET', 'POST'])
@login_required
def manage_curators(slug):
    if request.method == "GET":
        post = Post.query.filter(Post.slug==slug).first()
        if post.admin_id != current_user.id:
            flash('You have no permission to access the specified resource!')
            return redirect(url_for('detail.description', slug=slug))
        assocs = post.curators
        return render_template('detail/manage_curators.html', post=post, assocs=assocs)
    else:
        curator_id_str = request.form.get('curator_id_str')
        if curator_id_str:
            try:
                user = User.query.filter(User.id==int(curator_id_str)).first()
                post = Post.query.filter(Post.slug==slug).first()
                assoc_del = CuratorAssociation.query.filter((CuratorAssociation.user_id==user.id) & (CuratorAssociation.post_id==post.id)).first()
                post.curators.remove(assoc_del)
                db.session.commit()
                flash("Removal successful!", category="success")
            except:
                flash("There is something wrong with our backend, try again later!", category="error")
            return redirect(url_for('detail.manage_curators', slug=slug))
        flash("Cannot find such user in db!", category="error")
        redirect(url_for('detail.manage_curators', slug=slug))

@detail.route('/<slug>/search_curators', methods=['GET', 'POST'])
def search_curators(slug):
    if request.method == "GET":
        q = request.args.get('q')
        post = Post.query.filter(Post.slug==slug).first()
        if post.admin_id != current_user.id:
            flash('You have no permission to access the specified resource!')
            return redirect(url_for('detail.description', slug=slug))
        if q:
            all_user = User.query.filter(User.username.contains(q) & User.id.not_in([current_user.id]))
        else:
            all_user = User.query.filter(User.id.not_in([current_user.id]))
        return render_template('detail/search_curators.html', post=post, all_user=all_user)
    else:
        user_id_str = request.form.get('user_id_str')
        if user_id_str:
            try:
                user = User.query.filter(User.id==int(user_id_str)).first()
                post = Post.query.filter(Post.slug==slug).first()
                a = CuratorAssociation(accepted=False)
                a.curator = user
                a.post = post
                db.session.add(a)
                db.session.commit()
                flash("Invitation sent!", category="success")
            except:
                flash("Duplicate invitations are not allowed!", category="error")
            return redirect(url_for('detail.manage_curators', slug=slug))

@detail.route('/<slug>/view_dataset', methods=['GET', 'POST'])
def view_dataset(slug):
    post = Post.query.filter(Post.slug==slug).first()
    if request.method == 'GET':
        fname = os.path.join("uploads", slug, post.filename)
        df = pd.read_csv(fname)
        column_name = df.columns.values.tolist()
        fsize = os.path.getsize(fname)
        nrows = len(df.index)
        return render_template('detail/view_dataset.html', post=post, column_name=column_name, fsize=fsize, nrows=nrows)
    else:
        loc = os.path.join('uploads', slug)
        csv_file = [f for f in os.listdir(loc) if os.path.isfile(os.path.join(loc, f))][0]
        return send_file(os.path.join(loc, csv_file) , as_attachment=True)