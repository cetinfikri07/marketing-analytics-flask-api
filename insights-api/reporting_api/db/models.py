from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column,Integer,String,Float,ForeignKey,PrimaryKeyConstraint
from sqlalchemy.dialects.mysql import VARCHAR,MEDIUMINT,DATE,BIGINT,FLOAT,SMALLINT,BOOLEAN
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from reporting_api.db import session

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    user_id = Column(SMALLINT,primary_key=True,nullable=False,autoincrement=True)
    email = Column(VARCHAR(50),nullable=False,unique=True)
    passwd = Column(VARCHAR(70),nullable=False)
    first_name = Column(VARCHAR(50),nullable=False)
    last_name = Column(VARCHAR(50),nullable=False)
    admin = Column(BOOLEAN,nullable=False,default=False)
    fb_access_token = Column(VARCHAR(128))

    accounts = relationship("Accounts",back_populates="users")

class Accounts(Base):
    __tablename__ = "accounts"

    account_id = Column(VARCHAR(250), primary_key=True,nullable=False)
    account_name = Column(VARCHAR(250))
    account_currency = Column(VARCHAR(3))
    user_id = Column(SMALLINT,ForeignKey('users.user_id'))

    users = relationship("Users",back_populates='accounts')
    campaigns = relationship("Campaigns",back_populates="accounts")

class Campaigns(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(VARCHAR(250),primary_key=True,nullable=False)
    account_id = Column(VARCHAR(250),ForeignKey("accounts.account_id"),nullable=False)
    campaign_name = Column(VARCHAR(45))
    accounts = relationship("Accounts",back_populates = "campaigns")
    adsets = relationship("Adsets",back_populates = "campaigns")


class Adsets(Base):
    __tablename__ = "adsets"

    adset_id = Column(VARCHAR(250),primary_key=True,nullable=False)
    campaign_id = Column(VARCHAR(250),ForeignKey("campaigns.campaign_id"),nullable=False)
    adset_name = Column(VARCHAR(45))
    campaigns = relationship("Campaigns")
    ads = relationship("Ads",back_populates="adsets")


class Ads(Base):
    __tablename__ = "ads"

    ad_id = Column(VARCHAR(45),primary_key=True,nullable=False)
    adset_id = Column(VARCHAR(150),ForeignKey("adsets.adset_id"),nullable=False)
    ad_name = Column(VARCHAR(250))
    adsets = relationship("Adsets",back_populates = "ads")
    ad_series = relationship("AdSeries",back_populates="ads")
    age_and_gender = relationship("AgeGender",back_populates="ads")
    country = relationship("Country", back_populates="ads")


class AdSeries(Base):
    __tablename__ = "ad_series"

    ad_id = Column(VARCHAR(250),ForeignKey("ads.ad_id"),nullable=False)
    date = Column(DATE)
    impressions = Column(BIGINT)
    clicks = Column(BIGINT)
    total_spend = Column(FLOAT)
    video_view = Column(BIGINT)
    comment = Column(BIGINT)
    link_click = Column(BIGINT)
    post_reaction = Column(BIGINT)
    landing_page_view = Column(BIGINT)
    post_engagement = Column(BIGINT)
    leadgen_grouped = Column(BIGINT)
    lead = Column(BIGINT)
    page_engagement = Column(BIGINT)
    onsite_conversion_post_save = Column(BIGINT)
    onsite_conversion_lead_grouped = Column(BIGINT)
    offsite_conversion_fb_pixel_lead = Column(BIGINT)
    frequency = Column(FLOAT)
    ads = relationship("Ads",back_populates="ad_series")
    __table_args__ = (PrimaryKeyConstraint('ad_id', 'date'),)



class AgeGender(Base):
    __tablename__ = "age_and_gender"

    ad_id = Column(VARCHAR(18),ForeignKey("ads.ad_id"),nullable=False)
    age = Column(VARCHAR(5))
    gender = Column(VARCHAR(6))
    date = Column(DATE)
    impressions = Column(BIGINT)
    clicks = Column(BIGINT)
    total_spend = Column(FLOAT)
    video_view = Column(BIGINT)
    comment = Column(BIGINT)
    link_click = Column(BIGINT)
    post_reaction = Column(BIGINT)
    landing_page_view = Column(BIGINT)
    post_engagement = Column(BIGINT)
    leadgen_grouped = Column(BIGINT)
    lead = Column(BIGINT)
    page_engagement = Column(BIGINT)
    onsite_conversion_post_save = Column(BIGINT)
    onsite_conversion_lead_grouped = Column(BIGINT)
    offsite_conversion_fb_pixel_lead = Column(BIGINT)
    frequency = Column(FLOAT)
    ads = relationship("Ads", back_populates="age_and_gender")
    __table_args__ = (PrimaryKeyConstraint('ad_id', 'age',"gender","date"),)


class Country(Base):
    __tablename__ = "country"

    ad_id = Column(VARCHAR(18),ForeignKey("ads.ad_id"),nullable=False)
    country = Column(VARCHAR(5))
    date = Column(DATE)
    impressions = Column(BIGINT)
    clicks = Column(BIGINT)
    total_spend = Column(FLOAT)
    video_view = Column(BIGINT)
    comment = Column(BIGINT)
    link_click = Column(BIGINT)
    post_reaction = Column(BIGINT)
    landing_page_view = Column(BIGINT)
    post_engagement = Column(BIGINT)
    leadgen_grouped = Column(BIGINT)
    lead = Column(BIGINT)
    page_engagement = Column(BIGINT)
    onsite_conversion_post_save = Column(BIGINT)
    onsite_conversion_lead_grouped = Column(BIGINT)
    offsite_conversion_fb_pixel_lead = Column(BIGINT)
    frequency = Column(FLOAT)
    ads = relationship("Ads", back_populates="country")
    __table_args__ = (PrimaryKeyConstraint('ad_id', 'country',"date"),)