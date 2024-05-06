from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class WordPair(Base):
    __tablename__ = 'word_pairs'
    id = Column(Integer, primary_key=True)
    russian_word = Column(String, nullable=False)
    target_word = Column(String, nullable=False)
    other_words = relationship("OtherWord", back_populates="word_pair")


class OtherWord(Base):
    __tablename__ = 'other_words'
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    word_pair_id = Column(Integer, ForeignKey('word_pairs.id'))
    word_pair = relationship("WordPair", back_populates="other_words")


engine = create_engine('sqlite:///words.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_word(pair):
    session = Session()
    word_pair = WordPair(russian_word=pair['russian_word'],
                        target_word=pair['target_word'])
    session.add(word_pair)
    session.commit()

    for word in pair['other_words']:
        other_word = OtherWord(word=word, word_pair_id=word_pair.id)
        session.add(other_word)

    session.commit()
    session.close()

def get_random_word_pair():
    session = Session()
    word_pair = session.query(WordPair).order_by(func.random()).first()
    other_words = [word.word for word in word_pair.other_words]
    session.close()
    return {"russian_word": word_pair.russian_word,
            "target_word": word_pair.target_word,
            "other_words": other_words}
