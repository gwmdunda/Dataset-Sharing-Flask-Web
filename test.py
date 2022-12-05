import os
import unittest

from __init__ import db, create_app
from models import *

app = create_app()
class TestDB(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # def test_post_admin_association(self): 
    #     with app.app_context():
    #         u = User(email='jamie@a', name='jamie', username='jamie', password='secret', country="AZ", occupation="a")
    #         db.session.add(u)
    #         post = Post(title="hello", description='description', filename='new_filename.csv', admin=u)
    #         db.session.add(post)
    #         db.session.commit()
    #         db.session.delete(db.session.query(User).filter(User.name=='jamie').first())
    #         db.session.commit()
    #         assert Post.query.filter(Post.title=='hello').count() == 0
    
    def test_curator_access(self):
         with app.app_context():
            u1 = User(email='jamie@a', name='jamie', username='jamie', password='secret', country="AZ", occupation="a")
            u2 = User(email='kalda@a', name='kalda', username='kalda', password='secret', country="HK", occupation="a")
            u3 = User(email='skunk@a', name='skunk', username='skunk', password='secret', country="HK", occupation="a")
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()
            post = Post(title="hello", description='description', filename='new_filename.csv', admin=u1)
            db.session.add(post)
            db.session.commit()
            a1, a2 = CuratorAssociation(accepted=False), CuratorAssociation(accepted=False)
            a1.curator = u2
            a1.post = post
            db.session.add(a1)
        
            a2.curator = u3
            a2.post = post
            db.session.add(a2)
            db.session.commit()


            assert post.admin_id == u1.id
            assert len(post.curators.all()) == 2
            curator_del = CuratorAssociation.query.filter(CuratorAssociation.user_id==u3.id).first()
            post.curators.remove(curator_del)
            
            db.session.commit()
            assert len(post.curators.all()) == 1
            for assoc in post.curators:
                print(assoc.curator.name)

if __name__ == '__main__':
    unittest.main()