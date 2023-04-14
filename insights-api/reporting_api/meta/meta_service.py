from sqlalchemy import func, text,case
from collections import defaultdict
import datetime
import jwt

from reporting_api.db.models import AdSeries, Accounts, Ads, Adsets, Campaigns, AgeGender, Country,Users
from reporting_api.meta.utils import flatten_list
from reporting_api.db import session
from reporting_api import app
from pprint import pprint


class MetaService:
    def __init__(self):
        self.level_map = {
            'ad': [Ads.ad_id, Ads.ad_name, Adsets.adset_id, Campaigns.campaign_id, Accounts.account_id,Accounts.account_currency],
            'adset': [Adsets.adset_id, Adsets.adset_name, Campaigns.campaign_id, Accounts.account_id,Accounts.account_currency],
            'campaign': [Campaigns.campaign_id, Campaigns.campaign_name, Accounts.account_id,Accounts.account_currency],
            'account': [Accounts.account_id, Accounts.account_name,Accounts.account_currency]
        }

    def parse_dates(self, body):
        date_start = datetime.datetime.strptime(body.get("date_start"), "%Y-%m-%d").date()
        date_stop = datetime.datetime.strptime(body.get("date_stop"), "%Y-%m-%d").date()

        return date_start, date_stop

    def get_level_ids(self, field, date_start, date_stop, account_id):
        # get id list
        level_ids = session.query(field). \
            select_from(AdSeries).join(Ads, Ads.ad_id == AdSeries.ad_id). \
            join(Adsets, Adsets.adset_id == Ads.adset_id). \
            join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
            join(Accounts, Accounts.account_id == Campaigns.account_id). \
            filter(AdSeries.date >= date_start). \
            filter(AdSeries.date <= date_stop). \
            filter(Accounts.account_id == text(account_id)). \
            distinct().all()

        level_ids = [t[0] for t in level_ids]

        return level_ids

    def merge_dicts(self, dict1, dict2, _id):
        d = defaultdict(dict)
        for item in dict1 + dict2:
            d[item[_id]].update(item)

        return list(d.values())

    def sum_by_dates(self, account_id, sum_fields, date_start, date_stop, level_fields):

        sum_funcs = [func.round(func.sum(getattr(AdSeries, field)),2).label(field + '_sum') for field in sum_fields]

        result = session.query(*sum_funcs, *level_fields). \
            select_from(AdSeries).join(Ads, Ads.ad_id == AdSeries.ad_id). \
            join(Adsets, Adsets.adset_id == Ads.adset_id). \
            join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
            join(Accounts, Accounts.account_id == Campaigns.account_id). \
            filter(AdSeries.date >= date_start). \
            filter(AdSeries.date <= date_stop). \
            filter(Accounts.account_id == text(account_id)). \
            group_by(level_fields[0]).all()

        result = [r._asdict() for r in result]

        return result

    def daily_series(self, account_id, series_fields, date_start, date_stop, level_fields, level):
        field_series = [func.round(getattr(AdSeries, field),2).label(field) for field in series_fields]
        level_ids = self.get_level_ids(level_fields[0], date_start, date_stop, account_id)

        obj_list = []
        for _id in level_ids:
            subquery = (
                session.query(AdSeries.date, *field_series, *level_fields).
                select_from(AdSeries).join(Ads, Ads.ad_id == AdSeries.ad_id).
                join(Adsets, Adsets.adset_id == Ads.adset_id).
                join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id).
                join(Accounts, Accounts.account_id == Campaigns.account_id).
                filter(AdSeries.date >= date_start).
                filter(AdSeries.date <= date_stop).
                filter(Accounts.account_id == text(account_id)).
                filter(level_fields[0] == _id).
                subquery()
            )

            sum_subquery = [func.sum(subquery.c[s]).label(s) for s in series_fields]

            result = (
                session.query(subquery.c.date, *sum_subquery).
                group_by(subquery.c.date)
            ).all()

            result = [r._asdict() for r in result]

            obj = {level + '_id': _id, 'series': []}
            for row in result:
                row['date'] = row['date'].strftime("%Y-%m-%d")
                obj['series'].append(row)

            obj_list.append(obj)

        return obj_list

    def age_gender_breakdown(self, account_id, series_fields, breakdowns, date_start, date_stop, level_fields, level, pivot=False):
        # get attrites of each object from params
        field_series = [func.round(func.sum(getattr(AgeGender, field)),2).label(field) for field in series_fields]
        breakdowns = [getattr(AgeGender, breakdown) for breakdown in breakdowns]
        level_ids = self.get_level_ids(level_fields[0], date_start, date_stop, account_id)

        obj_list = []
        for _id in level_ids:
            result = session.query(AgeGender.date, *breakdowns, *field_series). \
                select_from(AgeGender).join(Ads, Ads.ad_id == AgeGender.ad_id). \
                join(Adsets, Adsets.adset_id == Ads.adset_id). \
                join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
                join(Accounts, Accounts.account_id == Campaigns.account_id). \
                filter(AgeGender.date >= date_start). \
                filter(AgeGender.date <= date_stop). \
                filter(Accounts.account_id == text(account_id)). \
                filter(level_fields[0] == _id). \
                filter(AgeGender.gender != 'unknown'). \
                group_by(AgeGender.date, *breakdowns)

            if pivot:
                subquery = result.subquery()
                result = session.query(
                    subquery.c.gender,
                    func.sum(
                        case(
                            (subquery.c.age == '18-24', subquery.c[series_fields[0]]),
                            else_=0
                        )
                    ).label('18-24'),
                    func.sum(
                        case(
                            (subquery.c.age == '25-34', subquery.c[series_fields[0]]),
                            else_=0
                        )
                    ).label('25-34'),
                    func.sum(
                        case(
                            (subquery.c.age == '45-54', subquery.c[series_fields[0]]),
                            else_=0
                        )
                    ).label('45-54'),
                    func.sum(
                        case(
                            (subquery.c.age == '55-64', subquery.c[series_fields[0]]),
                            else_=0
                        )
                    ).label('55-64')
                ).group_by(subquery.c.gender).all()

                result = [r._asdict() for r in result]
                pivot = {}
                for row in result:
                    for k,v in row.items():
                        if k != 'gender':
                            if k not in pivot:
                                pivot[k] = {'male':0,'female':0}

                            pivot[k][row['gender']] += v
                result = [[series_fields[0],'male','female']]
                for k,v in pivot.items():
                    result.append([k, v['male'], v['female']])

                obj = {level + '_id': _id, 'pivot_table': result}
                obj_list.append(obj)
            else:
                result = [r._asdict() for r in result]

                obj = {level + '_id': _id, 'series': []}
                for row in result:
                    row['date'] = row['date'].strftime("%Y-%m-%d")
                    obj['series'].append(row)

                obj['series'].sort(key= lambda x: x['date'])
                obj_list.append(obj)

        return obj_list

    def country_breakdown(self, account_id, series_fields, breakdowns, date_start, date_stop, level_fields, level):
        # get attrites of each object from params
        field_series = [getattr(Country, field).label(field) for field in series_fields]
        breakdowns = [getattr(Country, breakdown).label(breakdown) for breakdown in breakdowns]
        level_ids = self.get_level_ids(level_fields[0], date_start, date_stop, account_id)

        obj_list = []
        for _id in level_ids:
            result = session.query(Country.date, *breakdowns, *field_series). \
                select_from(Country).join(Ads, Ads.ad_id == Country.ad_id). \
                join(Adsets, Adsets.adset_id == Ads.adset_id). \
                join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
                join(Accounts, Accounts.account_id == Campaigns.account_id). \
                filter(Country.date >= date_start). \
                filter(Country.date <= date_stop). \
                filter(Accounts.account_id == text(account_id)). \
                filter(level_fields[0] == _id)

            result = [r._asdict() for r in result]

            obj = {level + '_id': _id, 'series': []}
            for row in result:
                row['date'] = row['date'].strftime("%Y-%m-%d")
                obj['series'].append(row)

            obj_list.append(obj)

        return obj_list

    def calculate_kpis(self, account_id, kpi_fields, action_fields, date_start, date_stop, level_fields):
        if action_fields:
            kpi_funcs = {
                'cpc': func.round((func.sum(AdSeries.total_spend) / func.sum(AdSeries.clicks)),2).label('cpc'),
                'ctr': func.round((func.sum(AdSeries.clicks) / func.sum(AdSeries.impressions)),2).label('ctr'),
                'cpa': [func.round((func.sum(AdSeries.total_spend) / func.sum(getattr(AdSeries, field))),2).label("cpa_" + field) for
                        field in action_fields],
                'cr': [func.round((func.sum(getattr(AdSeries, field)) / func.sum(AdSeries.clicks)),2).label('cr_' + field) for field
                       in action_fields]}

        else:
            kpi_funcs = {
                'cpc': func.round((func.sum(AdSeries.total_spend) / func.sum(AdSeries.clicks)),2).label('cpc'),
                'ctr': func.round((func.sum(AdSeries.clicks) / func.sum(AdSeries.impressions)),2).label('ctr')
            }

        funcs = [kpi_funcs[key] if key in kpi_funcs.keys() else key for key in kpi_fields]
        funcs = flatten_list(funcs)

        # calculate cpc and ctr
        result = session.query(
            *funcs,
            *level_fields,
        ).select_from(AdSeries).join(Ads, Ads.ad_id == AdSeries.ad_id). \
            join(Adsets, Adsets.adset_id == Ads.adset_id). \
            join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
            join(Accounts, Accounts.account_id == Campaigns.account_id). \
            filter(AdSeries.date >= date_start). \
            filter(AdSeries.date <= date_stop). \
            filter(Accounts.account_id == text(account_id)). \
            group_by(level_fields[0]).all()

        result = [r._asdict() for r in result]

        return result

    def user_levels(self,request):
        body = request.get_json()
        access_token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(access_token,app.config['SECRET_KEY'])

        user_id = decoded_token['user_id']
        level_type = body.get('levelType')

        id_name_fields = self.level_map[level_type][:2]
        result = session.query(*id_name_fields).select_from(Ads). \
            join(Adsets, Adsets.adset_id == Ads.adset_id). \
            join(Campaigns, Campaigns.campaign_id == Adsets.campaign_id). \
            join(Accounts, Accounts.account_id == Campaigns.account_id). \
            join(Users, Users.user_id == Accounts.user_id). \
            filter(Accounts.user_id == user_id).distinct().all()

        result = [r._asdict() for r in result]
        return result

    def get_report_by_level(self, request):
        body = request.get_json()
        date_start, date_stop = self.parse_dates(body)  # sum,series
        account_id = body.get('account_id', None)  # sum,series
        level = body.get('level', None)  # sum,series
        level_id = level + '_id'

        sum_fields = body.get('fields', None)
        series_fields = body.get('series', None)
        kpi_fields = body.get('kpis', None)
        action_fields = body.get('actions', None)
        breakdowns = body.get('breakdowns', None)
        pivot = body.get('pivot')

        level_fields = self.level_map[level]

        functions = {
            "fields": lambda: self.sum_by_dates(account_id, sum_fields, date_start, date_stop, level_fields),
            "kpis": lambda: self.calculate_kpis(account_id, kpi_fields, action_fields, date_start, date_stop,
                                                level_fields),
            "series": lambda: self.daily_series(account_id, series_fields, date_start, date_stop, level_fields, level),
        }

        if breakdowns:
            if 'country' in breakdowns and len(breakdowns) == 1:
                functions['series'] = lambda: self.country_breakdown(account_id, series_fields, breakdowns, date_start,
                                                                     date_stop, level_fields, level)
            else:
                functions['series'] = lambda: self.age_gender_breakdown(account_id, series_fields, breakdowns,
                                                                        date_start, date_stop, level_fields, level,pivot)

        merged_results = {}
        for key, value in body.items():  # key: fields, values: ['click']
            if key in functions:
                func = functions[key]
                try:
                    result = func()
                except Exception as err:
                    print(err)
                    return {'error': err.__repr__()}, 400
                for r in result:
                    if r[level_id] not in merged_results:
                        merged_results[r[level_id]] = {}
                    merged_results[r[level_id]].update(r)

        return list(merged_results.values()), 200
