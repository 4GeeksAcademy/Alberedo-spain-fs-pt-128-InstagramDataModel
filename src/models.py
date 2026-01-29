from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

follower_table = Table(
    "followers",
    db.Model.metadata,
    Column("user_from_id", ForeignKey("user.id"), primary_key=True),
    Column("user_to_id", ForeignKey("user.id"), primary_key=True),
)

# region:User


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=follower_table,
        primaryjoin=(follower_table.c.user_from_id == id),
        secondaryjoin=(follower_table.c.user_to_id == id),
        back_populates="followed_by"
    )
    followed_by: Mapped[list["User"]] = relationship(
        "User",
        secondary=follower_table,
        primaryjoin=(follower_table.c.user_to_id == id),
        secondaryjoin=(follower_table.c.user_from_id == id),
        back_populates="following"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="author"
    )
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "following": [user.email for user in self.following],
            "followed_by": [user.email for user in self.followed_by],
            "comments": [comment.comment_text for comment in self.comments],
            "posts": [post.serialize() for post in self.posts]
            # do not serialize the password, its a security breach
        }


# region:Comment
class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(240), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    author: Mapped["User"] = relationship(
        "User",
        back_populates="comments"
    )
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="comments"
        )
    
    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }

# region:Post


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped["User"] = relationship(
        "User",
        back_populates="posts"
    )
    media_posted: Mapped[list["Media"]] = relationship(
        "Media",
        back_populates="posted_in"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="post"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media": [media.serialize() for media in self.media_posted],
            "comments": [comment.serialize() for comment in self.comments]
        }

# region:Media


class Media(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    posted_in: Mapped["Post"] = relationship(
        "Post",
        back_populates="media_posted"
    )

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "post_id": self.post_id
        }
