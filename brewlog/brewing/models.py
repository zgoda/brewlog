import datetime

from brewlog import Model
from brewlog.brewing import choices
from brewlog.users.models import BrewerProfile

from sqlalchemy import Table, Column, Integer, String, Text, Date, DateTime, ForeignKey, Float, Enum, Boolean
from sqlalchemy import event
from sqlalchemy.orm import relationship
import markdown


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
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    brewer = relationship('BrewerProfile', backref='breweries')
    other_brewers = relationship('BrewerProfile',
        secondary=brewers_breweries, backref='other_breweries')

    def __repr__(self):
        return '<Brewery %s>' % self.name.encode('utf-8')

    @property
    def absolute_url(self):
        return ''


class Fermentable(Model):
    __tablename__ = 'fermentable'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)
    unit = Column(String(20))
    amount = Column(Float(precision=3))
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='fermentables')


class Hop(Model):
    __tablename__ = 'hop'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    year = Column(Integer)
    aa_content = Column(Float(precision=2))
    amount = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='hops')


class Yeast(Model):
    __tablename__ = 'yeast'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(50), nullable=False, index=True)
    manufacturer = Column(String(50))
    use = Column(Enum(*choices.YEAST_USE_KEYS), nullable=False)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='yeasts')


class Misc(Model):
    __tablename__ = 'misc'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    amount = Column(Float(precision=2))
    use = Column(Enum(*choices.MISC_USE_KEYS), nullable=False)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='misc_items')


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
    brew = relationship('Brew', backref='mash_steps')


class HoppingStep(Model):
    __tablename__ = 'hopping_step'
    id = Column(Integer, primary_key=True)
    addition_type = Column(Enum(*choices.HOPSTEP_TYPE_KEYS), nullable=False)
    time = Column(Integer, index=True, nullable=False)
    variety = Column(String(50))
    amount = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='hopping_steps')


class AdditionalFermentationStep(Model):
    __tablename__ = 'fermentation_step'
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    amount = Column(Float(precision=1))
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    fermentation_temperature = Column(Integer)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='fermentation_steps')


class TastingNote(Model):
    __tablename__ = 'tasting_note'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    author = relationship('BrewerProfile', backref='tasting_notes')
    date = Column(Date, nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew', backref='tasting_notes')


class Brew(Model):
    __tablename__ = 'brew'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    name = Column(String(200), nullable=False)
    style = Column(String(200))
    bjcp_style_code = Column(String(20), default=u'')
    bjcp_style_name = Column(String(50), default=u'')
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
    brewery_id = Column(Integer, ForeignKey('brewery.id'), nullable=False)
    brewery = relationship('Brewery', backref='brews')

    def __repr__(self):
        return '<Brew %s by %s>' % (self.name.encode('utf-8'), self.brewery.name.encode('utf-8'))

    @property
    def absolute_url(self):
        return ''


## events: Brewery model
def brewery_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description, safe_mode='remove')
    else:
        target.description_html = None
    if target.updated is None:
        target.updated = target.created
    if target.established_date:
        target.est_year = target.established_date.year
        target.est_month = target.established_date.month
        target.est_day = target.established_date.day

event.listen(Brewery, 'before_insert', brewery_pre_save)
event.listen(Brewery, 'before_update', brewery_pre_save)

## events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = u'%s %s' % (target.bjcp_style_code, target.bjcp_style_name)
    target.bjcp_style = bjcp_style.strip()
    target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created

event.listen(Brew, 'before_insert', brew_pre_save)
event.listen(Brew, 'before_update', brew_pre_save)
