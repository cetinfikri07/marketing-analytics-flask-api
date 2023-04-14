from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
import jwt
import re

from reporting_api import app
from reporting_api.db import session
from reporting_api.db.models import Accounts, Campaigns, Adsets, Ads, Users, AdSeries, AgeGender, Country
from reporting_api.meta import config


class RegisterAccount:
    def __init__(self):
        self.app_id = config['env_variables']['APP_ID']
        self.app_secret = config['env_variables']['APP_SECRET']
        # self.access_token = config['env_variables']['ACCESS_TOKEN']
        self.today = date.today()
        self.levels_fields = {
            'account': [AdsInsights.Field.account_id, AdsInsights.Field.account_name,
                        AdsInsights.Field.account_currency],
            'campaign': [AdsInsights.Field.account_id, AdsInsights.Field.campaign_id, AdsInsights.Field.campaign_name],
            'adset': [AdsInsights.Field.campaign_id, AdsInsights.Field.adset_id, AdsInsights.Field.adset_name],
            'ad': [AdsInsights.Field.adset_id, AdsInsights.Field.ad_id, AdsInsights.Field.ad_name]
        }

        self.tables = [Accounts, Campaigns, Adsets, Ads]

    def insert_tables(self, request):
        account_id = request.json['facebook_account_id']
        since = request.json['since']
        until = request.json['until']

        jwt_token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(jwt_token,app.config['SECRET_KEY'])
        user_id = decoded_token['user_id']

        since = datetime.strptime(since, '%Y-%m-%d')
        until = datetime.strptime(until, '%Y-%m-%d')

        # get user's access_token
        try:
            access_token = session.query(Users.fb_access_token). \
                filter(Users.user_id == user_id).one()
            if len(access_token) == 0:
                result = {'error': {'message': 'Access token is not found', 'code': 409}}
                return result

            access_token = access_token[0]
        except Exception as err:
            result = {'error': {'message': f'Unexpected error {err}', 'code': 409}}

        # init facebook ads api
        FacebookAdsApi.init(self.app_id, self.app_secret, access_token)
        account = AdAccount('act_' + account_id)

        # insert account,camapign,adset and ads
        for table, level, field in zip(self.tables, self.levels_fields.keys(), self.levels_fields.values()):
            try:
                insights = account.get_insights(params={'level': level}, fields={*field})
            except FacebookRequestError as err:
                return err.body()

            for insight in insights:
                for date in ['date_start', 'date_stop']:
                    del insight[date]
                if table == Accounts:
                    new_record = table(**insight, user_id=user_id)
                else:
                    new_record = table(**insight)

                print(new_record)
                session.add(new_record)
            try:
                session.commit()
            except IntegrityError as err:
                match = re.search(r"Duplicate entry", err._message())
                if match:
                    err_message = match.group(0)
                result = {'error': {"message": f'Failed to register account: {err_message}', 'code': 409}}
                print(result)
                session.rollback()

                return result

        # insert ad_series,age_and_gender,country
        num_days = (until - since).days
        ad_series_fields = [
            AdsInsights.Field.ad_id,
            AdsInsights.Field.date_start,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.spend,
            AdsInsights.Field.actions,
            AdsInsights.Field.frequency
        ]
        for table, breakdown in zip([AdSeries, AgeGender, Country], [None, ['age', 'gender'], ['country']]):
            for i in range(1, num_days):
                dt = (until - timedelta(i)).strftime("%Y-%m-%d")
                params = {'level': 'ad', 'time_range': {'since': dt, 'until': dt}, "breakdowns": breakdown}
                try:
                    insights = account.get_insights(params=params, fields={*ad_series_fields})
                except FacebookRequestError as err:
                    return err.body()

                insights = [dict(item) for item in insights]
                actions = {}
                for ad in insights:
                    if ad.get('actions'):
                        for _type in ad['actions']:
                            actions[_type['action_type']] = _type['value']
                    if table == AdSeries:
                        new_record = AdSeries(ad_id=ad.get("ad_id"),
                                              date=ad.get("date_start"),
                                              impressions=ad.get("impressions"),
                                              clicks=ad.get("clicks"),
                                              total_spend=ad.get("spend"),
                                              video_view=actions.get("video_view", 0),
                                              comment=actions.get("comment", 0),
                                              link_click=actions.get("link_click", 0),
                                              post_reaction=actions.get("post_reaction", 0),
                                              landing_page_view=actions.get("landing_page_view", 0),
                                              post_engagement=actions.get("post_engagement", 0),
                                              leadgen_grouped=actions.get("leadgen_grouped", 0),
                                              lead=actions.get("lead", 0),
                                              page_engagement=actions.get("page_engagement", 0),
                                              onsite_conversion_post_save=actions.get("onsite_conversion_post_save", 0),
                                              onsite_conversion_lead_grouped=actions.get(
                                                  "onsite_conversion_lead_grouped", 0),
                                              offsite_conversion_fb_pixel_lead=actions.get(
                                                  "offsite_conversion_fb_pixel_lead", 0),
                                              frequency=ad.get("frequency")
                                              )
                    elif table == AgeGender:
                        new_record = AgeGender(
                            ad_id=ad.get("ad_id"),
                            age=ad.get("age"),
                            gender=ad.get("gender"),
                            date=ad.get("date_start"),
                            impressions=ad.get("impressions"),
                            clicks=ad.get("clicks"),
                            total_spend=ad.get("spend"),
                            video_view=actions.get("video_view", 0),
                            comment=actions.get("comment", 0),
                            link_click=actions.get("link_click", 0),
                            post_reaction=actions.get("post_reaction", 0),
                            landing_page_view=actions.get("landing_page_view", 0),
                            post_engagement=actions.get("post_engagement", 0),
                            leadgen_grouped=actions.get("leadgen_grouped", 0),
                            lead=actions.get("lead", 0),
                            page_engagement=actions.get("page_engagement", 0),
                            onsite_conversion_post_save=actions.get("onsite_conversion_post_save", 0),
                            onsite_conversion_lead_grouped=actions.get("onsite_conversion_lead_grouped", 0),
                            offsite_conversion_fb_pixel_lead=actions.get("offsite_conversion_fb_pixel_lead", 0),
                            frequency=ad.get("frequency"))
                    else:
                        new_record = Country(
                            ad_id=ad.get("ad_id"),
                            country=ad.get("country"),
                            date=ad.get("date_start"),
                            impressions=ad.get("impressions"),
                            clicks=ad.get("clicks"),
                            total_spend=ad.get("spend"),
                            video_view=actions.get("video_view", 0),
                            comment=actions.get("comment", 0),
                            link_click=actions.get("link_click", 0),
                            post_reaction=actions.get("post_reaction", 0),
                            landing_page_view=actions.get("landing_page_view", 0),
                            post_engagement=actions.get("post_engagement", 0),
                            leadgen_grouped=actions.get("leadgen_grouped", 0),
                            lead=actions.get("lead", 0),
                            page_engagement=actions.get("page_engagement", 0),
                            onsite_conversion_post_save=actions.get("onsite_conversion_post_save", 0),
                            onsite_conversion_lead_grouped=actions.get("onsite_conversion_lead_grouped", 0),
                            offsite_conversion_fb_pixel_lead=actions.get("offsite_conversion_fb_pixel_lead", 0),
                            frequency=ad.get("frequency"))
                    print(new_record)
                    session.add(new_record)
                try:
                    session.commit()
                except Exception as err:
                    error_message = {'error': {"message": f'Failed to insert {new_record} to {table}: {err}'}}
                    print(error_message)
                    session.rollback()

        result = {'status': 'success', 'message': 'Account registered succesfully'}
        return result
