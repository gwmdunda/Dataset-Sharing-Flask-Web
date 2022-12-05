from email.policy import default
from flask_login import UserMixin
from datetime import datetime
from time import time
import re
from __init__ import db

class CuratorAssociation(db.Model):
    __tablename__ = "invitation_association"
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.ForeignKey('post.id'), primary_key=True)
    accepted = db.Column(db.Boolean)
    curator = db.relationship("User", back_populates="posts", foreign_keys="CuratorAssociation.user_id")
    post = db.relationship("Post", back_populates="curators")

# association_table = db.Table(
#     "association",
#     db.Model.metadata,
#     db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
#     db.Column("post_id", db.ForeignKey("post.id"), primary_key=True),
# )

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(30))
    name = db.Column(db.String(60))
    username = db.Column(db.String(15), unique=True)
    occupation = db.Column(db.String(100))
    country = db.Column(db.String(100))
    # posts = db.relationship('Post', backref='admin', cascade="all,delete")
    posts = db.relationship("CuratorAssociation", back_populates="curator")

def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '_', s)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    filename = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.now())
    admin_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    admin = db.relationship('User', backref=db.backref('posts_', cascade="all,delete"), foreign_keys="Post.admin_id")
    #curators = db.relationship("User", secondary=association_table, backref="submission", lazy='dynamic')
    curators = db.relationship("CuratorAssociation", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.generate_slug()
    
    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        else:
            self.slug = str(int(time()))

class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    filename = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    collaborator_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    collaborator = db.relationship('User', backref='submissions_collab', foreign_keys=[collaborator_id])
    curator_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    curator = db.relationship('User', backref='submissions_curate', foreign_keys=[curator_id])


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.generate_slug()
    
    def generate_slug(self):
        self.slug = slugify(str(int(time())))

