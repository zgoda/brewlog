import datetime

from brewlog import Model
from brewlog.brewing import choices

from sqlalchemy import Table, Column, Integer, String, Text, Date, DateTime, ForeignKey, Float, Enum, Boolean
from sqlalchemy.orm import relationship


brewers_breweries = Table('brewers_breweries', Model.metadata,
    Column('brewer_id', Integer, ForeignKey('brewer_profile.id')),
    Column('brewery_id', Integer, ForeignKey('brewery.id')),
)


class Brewery(Model):
    __tablename__ = 'brewery'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    description_html = Column(Text)
    established_date = Column(Date)
    est_year = Column(Integer)
    est_month = Column(Integer)
    est_day = Column(Integer)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    brewer = relationship('brewlog.users.models.BrewerProfile', backref='breweries')
    other_brewers = relationship('brewlog.users.models.BrewerProfile',
        secondary=brewers_breweries, backref='other_breweries')


class Fermentable(Model):
    __tablename__ = 'fermentable'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)
    unit = Column(String(20))
    amount = Column(Float(precision=3))
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='fermentables')


class Hop(Model):
    __tablename__ = 'hop'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    year = Column(Integer)
    aa_content = Column(Float(precision=2))
    amount = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='hops')


class Yeast(Model):
    __tablename__ = 'yeast'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(50), nullable=False, index=True)
    manufacturer = Column(String(50))
    use = Column(Enum(*choices.YEAST_USE_KEYS), nullable=False)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='yeasts')


class Misc(Model):
    __tablename__ = 'misc'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    amount = Column(Float(precision=2))
    use = Column(Enum(*choices.MISC_USE_KEYS), nullable=False)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='misc_items')


class MashStep(Model):
    __tablename__ = 'mash_step'
    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    temperature = Column(Integer)
    time = Column(Integer)
    step_type = Column(Enum(*choices.STEP_TYPE_KEYS), nullable=False)
    amount = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='mash_steps')


class HoppingStep(Model):
    __tablename__ = 'hopping_step'
    id = Column(Integer, primary_key=True)
    addition_type = Column(Enum(*choices.HOPSTEP_TYPE_KEYS), nullable=False)
    time = Column(Integer, index=True, nullable=False)
    variety = Column(String(50))
    amount = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='hopping_steps')


class AdditionalFermentationStem(Model):
    __tablename__ = 'fermentation_step'
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    amount = Column(Float(precision=1))
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    fermentation_temperature = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='fermentation_steps')


class TastingNote(Model):
    __tablename__ = 'tasting_note'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    author = relationship('brewlog.users.models.BrewerProfile', backref='tasting_notes')
    date = Column(Date, nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('brewlog.brewing.models.Brew', backref='tasting_notes')


class Brew(Model):
    __tablename__ = 'brew'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    name = Column(String(200), nullable=False)
    style = Column(String(200))
    bjcp_style_code = Column(String(20))
    bjcp_style_name = Column(String(50))
    bjcp_style = Column(String(100))
    date_brewed = Column(Date, index=True)
    notes = Column(Text)
    notes_html = Column(Text)
    boil_time = Column(Integer)
    fermentation_start_date = Column(Date)
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    brew_length = Column(Float(precision=2))
    fermentation_temperature = Column(Integer)
    final_amount = Column(Float(precision=2))
    bottling_date = Column(Date)
    carbonation_type = Column(Enum(*choices.CARBONATION_KEYS))
    carbonation_used = Column(Text)
    is_public = Column(Boolean, default=True)
    is_draft = Column(Boolean, default=False)
