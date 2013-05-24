import datetime

from flask import url_for
import peewee as pw
from flask_login import UserMixin
import markdown

from brewlog import Model
from brewlog.brewing import choices
from brewlog.utils.models import DataModelMixin


class BrewerProfile(UserMixin, DataModelMixin, Model):
    first_name = pw.CharField(max_length=50, null=True)
    last_name = pw.CharField(max_length=50, null=True)
    nick = pw.CharField(max_length=50, null=True)
    email = pw.CharField(max_length=80, index=True)
    full_name = pw.CharField(max_length=100, null=True)
    location = pw.CharField(max_length=100, null=True)
    about_me = pw.TextField(null=True)
    is_public = pw.BooleanField(default=True)
    created = pw.DateTimeField(default=datetime.datetime.utcnow)
    updated = pw.DateTimeField(index=True)
    access_token = pw.TextField(null=True) # for OAuth2
    oauth_token = pw.TextField(null=True) # for OAuth1a
    oauth_token_secret = pw.TextField(null=True) # for OAuth1a
    oauth_service = pw.CharField(max_length=50, null=True)
    remote_userid = pw.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'brewer_profile'
        indexes = (
            (('oauth_service', 'remote_userid'), False),
        )

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()
        self.updated = datetime.datetime.utcnow()
        return super(BrewerProfile, self).save(*args, **kwargs)

    def get_id(self):
        """This has to be overwritten because flask-login wants to convert
        it to unicode, no matter what"""
        if self.id is None:
            return self.id
        return super(BrewerProfile, self).get_id()

    @property
    def absolute_url(self):
        return url_for('profile-details', userid=self.id)

    @property
    def name(self):
        return self.full_name or self.email

    @property
    def other_breweries(self):
        from brewlog.brewing.models import BrewerBrewery, Brewery
        return Brewery.select().join(BrewerBrewery).join(BrewerProfile).where(BrewerProfile.id == self.id).order_by(Brewery.name)

    @classmethod
    def last_created(cls, limit=5):
        return cls.select().order_by(cls.created.desc()).limit(limit)

    @classmethod
    def last_updated(cls, limit=5):
        return cls.select().order_by(cls.updated.desc()).limit(limit)


class Brewery(Model):
    name = pw.CharField(max_length=200)
    description = pw.TextField(null=True)
    description_html = pw.TextField(null=True)
    established_date = pw.DateField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.utcnow)
    updated = pw.DateTimeField(index=True)
    brewer = pw.ForeignKeyField(BrewerProfile, related_name='breweries')

    class Meta:
        db_table = 'brewery'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.description:
            self.description_html = markdown.markdown(self.description, safe_mode='remove')
        self.updated = datetime.datetime.utcnow()
        return super(Brewery, self).save(*args, **kwargs)

    @property
    def absolute_url(self):
        return url_for('brewery-details', brewery_id=self.id)

    @property
    def other_brewers(self):
        return BrewerProfile.select().join(BrewerBrewery).join(Brewery).where(BrewerBrewery.id == self.id).order_by(BrewerProfile.nick)

    def recent_brews(self, limit=10):
        return self.brews.order_by(Brew.created.desc()).limit(limit)

    @property
    def render_fields(self):
        return {
            'name': self.name,
            'description': self.description_html,
            'established': self.established_date,
        }

    @classmethod
    def last_updated(cls, limit=5):
        return cls.select().order_by(cls.updated.desc()).limit(limit)

    @classmethod
    def last_created(cls, limit=5):
        return cls.select().order_by(cls.created.desc()).limit(limit)


class BrewerBrewery(Model):
    brewer = pw.ForeignKeyField(BrewerProfile)
    brewery = pw.ForeignKeyField(Brewery)

    class Meta:
        db_table = 'brewer_brewery'


class Brew(Model):
    created = pw.DateTimeField(default=datetime.datetime.utcnow)
    updated = pw.DateTimeField(index=True)
    name = pw.CharField(max_length=200)
    code = pw.CharField(max_length=20, null=True)
    style = pw.CharField(max_length=200, null=True)
    bjcp_style_code = pw.CharField(max_length=20, default=u'')
    bjcp_style_name = pw.CharField(max_length=50, default=u'')
    bjcp_style = pw.CharField(max_length=100)
    date_brewed = pw.DateField(null=True, index=True)
    notes = pw.TextField(null=True)
    notes_html = pw.TextField(null=True)
    fermentables = pw.TextField(null=True)
    hops = pw.TextField(null=True)
    yeast = pw.TextField(null=True)
    misc = pw.TextField(null=True)
    mash_steps = pw.TextField(null=True)
    hopping_steps = pw.TextField(null=True)
    fermentation_steps = pw.TextField(null=True)
    boil_time = pw.IntegerField(null=True)
    fermentation_start_date = pw.DateField(null=True)
    og = pw.DecimalField(decimal_places=1, null=True)
    fg = pw.DecimalField(decimal_places=1, null=True)
    brew_length = pw.DecimalField(decimal_places=2, null=True)
    fermentation_temperature = pw.IntegerField(null=True)
    final_amount = pw.DecimalField(decimal_places=2, null=True)
    bottling_date = pw.DateField(null=True)
    carbonation_type = pw.CharField(max_length=50, choices=choices.CARBONATION_CHOICES)
    carbonation_used = pw.TextField(null=True)
    is_public = pw.BooleanField(default=True)
    is_draft = pw.BooleanField(default=False)
    brewery = pw.ForeignKeyField(Brewery, related_name='brews')

    class Meta:
        db_table = 'brew'

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Brew %s by %s>' % (self.name.encode('utf-8'), self.brewery.name.encode('utf-8'))

    def save(self, *args, **kwargs):
        bjcp_style = u'%s %s' % (self.bjcp_style_code, self.bjcp_style_name)
        self.bjcp_style = bjcp_style.strip()
        if self.notes:
            self.notes_html = markdown.markdown(self.notes, safe_mode='remove')
        self.updated = datetime.datetime.utcnow()
        return super(Brew, self).save(*args, **kwargs)

    @property
    def absolute_url(self):
        return url_for('brew-details', brew_id=self.id)

    @classmethod
    def last_created(cls, limit=5):
        return cls.select().order_by(cls.created.desc()).limit(limit)

    @classmethod
    def last_updated(cls, limit=5):
        return cls.select().order_by(cls.updated.desc()).limit(limit)


class TastingNote(Model):
    author = pw.ForeignKeyField(BrewerProfile, related_name='tasting_notes')
    date = pw.DateField(index=True)
    text = pw.TextField()
    text_html = pw.TextField()
    brew = pw.ForeignKeyField(Brew, related_name='tasting_notes')

    class Meta:
        db_table = 'tasting_note'

    def __repr__(self):
        return '<TastingNote by %s for %s>' % (self.author.name.encode('utf-8'), self.brew.name.encode('utf-8'))

    def save(self, *args, **kwargs):
        self.text_html = markdown.markdown(self.text, safe_mode='remove')
        return super(TastingNote, self).save(*args, **kwargs)


class AdditionalFermentationStep(Model):
    date = pw.DateField(index=True)
    og = pw.DecimalField(decimal_places=1)
    fg = pw.DecimalField(decimal_places=1, null=True)
    is_last = pw.BooleanField(default=False)
    brew = pw.ForeignKeyField(Brew, related_name='additional_fermentation_steps')

    class Meta:
        db_table = 'fermentation_step'

    def __repr__(self):
        return '<AdditionalFermentationStep>'

