import datetime

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    DateTime,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import NoResultFound

from settings import settings


Base = declarative_base()


class DefaultModel:

    __table__ = None

    session = settings.db.session

    id = Column(Integer, primary_key=True)

    created = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return repr(f"<{self.__class__.__name__} id={self.id}>")

    @property
    def __args__(self):
        attrs = {}
        for key in self.__class__.__table__.columns:
            value = getattr(self, key.name)
            if value is not None:
                attrs[key.name] = value
        return attrs

    def save(self):
        self.session.add(self)
        self.session.commit()

    @classmethod
    def retreive(cls, where=None):
        # TODO: If multiple rows found
        query = cls.session.query(cls)
        if where is not None:
            query = query.filter(where)
        return query.first()

    def retreive_or_create(self):
        try:
            return (
                self.session.query(self.__class__)
                .filter_by(**self.__args__)
                .one()
            )
        except NoResultFound:
            return self

    def delete(self):
        model = (
            self.session.query(self.__class__).filter_by(**self.__args__).one()
        )
        self.session.delete(model)
        self.session.commit()

    @classmethod
    def list(cls, where=None):
        query = cls.session.query(cls)
        if where is not None:
            query = query.filter(where)
        return query.all()


class Source(Base, DefaultModel):

    __tablename__ = "source"

    name = Column(String, unique=True)

    channels = relationship("Channel", cascade="all,delete")


class Channel(Base, DefaultModel):

    __tablename__ = "channel"

    source_id = Column(Integer, ForeignKey("source.id"))

    external_id = Column(BigInteger, unique=True)

    source = relationship("Source", back_populates="channels")

    posts = relationship(
        "Post", order_by="desc(Post.published)", cascade="all,delete"
    )


class Post(Base, DefaultModel):

    __tablename__ = "post"

    channel_id = Column(Integer, ForeignKey("channel.id"))

    external_id = Column(BigInteger)

    published = Column(DateTime, nullable=False)

    content = Column(Text)

    views = Column(Integer)

    forwards = Column(Integer)

    channel = relationship("Channel", back_populates="posts")

    comments = relationship(
        "Comment", order_by="desc(Comment.published)", cascade="all,delete"
    )


class User(Base, DefaultModel):

    __tablename__ = "user"

    login = Column(String, unique=True)

    external_id = Column(BigInteger, unique=True)

    comments = relationship("Comment", cascade="all,delete")


class Comment(Base, DefaultModel):

    __tablename__ = "comment"

    user_id = Column(Integer, ForeignKey("user.id"))

    channel_id = Column(Integer, ForeignKey("channel.id"))

    post_id = Column(Integer, ForeignKey("post.id"))

    comment_id = Column(Integer, ForeignKey("comment.id"))

    external_id = Column(BigInteger)

    published = Column(DateTime, nullable=False)

    content = Column(Text)

    # TODO: Delete orphan user
    user = relationship("User", back_populates="comments")

    channel = relationship("Channel")

    post = relationship("Post", back_populates="comments")

    comment = relationship("Comment", back_populates="comments")

    comments = relationship("Comment", cascade="all,delete")


Base.metadata.create_all(settings.db.engine)
