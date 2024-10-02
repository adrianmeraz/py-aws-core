import json
from importlib.resources import as_file

import respx

from py_aws_core.clients import RetryClient
from py_aws_core.testing import BaseTestFixture
from py_aws_core.spoofing.proxyrack import exceptions, proxyrack_api
from . import const as test_const


class ActiveConnectionsTests(BaseTestFixture):
    """
        Active Connections Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('active_conns.json')
        with as_file(source) as active_conns_json:
            mocked_route_active_conns = self.create_ok_route(
                method='GET',
                url__eq='http://api.proxyrack.net/active_conns',
                _json=json.loads(active_conns_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_active_connections = proxyrack_api.GetActiveConnections.call(client)
            self.assertEqual(2, len(r_active_connections.connections))

        self.assertEqual(1, mocked_route_active_conns.call_count)

    @respx.mock
    def test_ProxyRackError(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('active_conns.json')
        with as_file(source) as active_conns_json:
            mocked_route_active_conns = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/active_conns',
                response_status_code=400,
                response_json=json.loads(active_conns_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            with self.assertRaises(exceptions.ProxyRackException):
                proxyrack_api.GetActiveConnections.call(client)

        self.assertEqual(1, mocked_route_active_conns.call_count)


class PostTempAPIKeyTests(BaseTestFixture):
    """
        API Keys Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('passwords.json')
        with as_file(source) as passwords_json:
            mocked_route_passwords = self.create_route(
                method='POST',
                url__eq='http://api.proxyrack.net/passwords?expirationSeconds=60',
                response_status_code=200,
                response_json=json.loads(passwords_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_generate_temp_api_key = proxyrack_api.PostTempAPIKey.call(client, expiration_seconds=60)
            self.assertEqual('temp-bf3702-be83a4-0bbfc1-be7f58-62cfff', r_generate_temp_api_key.api_key)

        self.assertEqual(1, mocked_route_passwords.call_count)

    @respx.mock
    def test_ProxyRackError(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('passwords.json')
        with as_file(source) as passwords_json:
            mocked_route_passwords = self.create_route(
                method='POST',
                url__eq='http://api.proxyrack.net/passwords?expirationSeconds=60',
                response_status_code=400,
                response_json=json.loads(passwords_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            with self.assertRaises(exceptions.ProxyRackException):
                proxyrack_api.PostTempAPIKey.call(
                    client,
                    expiration_seconds=60
                )
        self.assertEqual(1, mocked_route_passwords.call_count)


class StatsTests(BaseTestFixture):
    """
        Stats Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('stats.json')
        with as_file(source) as stats_json:
            mocked_route_stats = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/stats',
                response_status_code=200,
                response_json=json.loads(stats_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_stats = proxyrack_api.GetStats.call(client=client)
            self.assertEqual(r_stats.thread_limit, 10000)

        self.assertEqual(mocked_route_stats.call_count, 1)

    @respx.mock
    def test_400(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('stats.json')
        with as_file(source) as stats_json:
            mocked_route_stats = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/stats',
                response_status_code=400,
                response_json=json.loads(stats_json.read_text(encoding='utf-8'))
            )

        with self.assertRaises(exceptions.ProxyRackException):
            with RetryClient() as client:
                proxyrack_api.GetStats.call(client=client)

        self.assertTrue(mocked_route_stats.called)


class IspsTests(BaseTestFixture):
    """
        Isps Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('us_isps.json')
        with as_file(source) as us_isps_json:
            mocked_route_us_isps = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/countries/US/isps',
                response_status_code=200,
                response_json=json.loads(us_isps_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_isps = proxyrack_api.GetISPs.call(client=client, country='US')
            self.assertEqual(len(r_isps.isps), 54)

        self.assertEqual(mocked_route_us_isps.call_count, 1)

    @respx.mock
    def test_400(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('us_isps.json')
        with as_file(source) as us_isps_json:
            mocked_route_us_isps = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/countries/US/isps',
                response_status_code=400,
                response_json=json.loads(us_isps_json.read_text(encoding='utf-8'))
            )

        with self.assertRaises(exceptions.ProxyRackException):
            with RetryClient() as client:
                proxyrack_api.GetISPs.call(client=client, country='US')

        self.assertEqual(mocked_route_us_isps.call_count, 1)


class CountriesTests(BaseTestFixture):
    """
        Countries Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('countries.json')
        with as_file(source) as countries_json:
            mocked_route_countries = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/countries',
                response_status_code=200,
                response_json=json.loads(countries_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_countries = proxyrack_api.GetCountries.call(client=client)
            self.assertEqual(len(r_countries.countries), 205)

        self.assertEqual(mocked_route_countries.call_count, 1)

    @respx.mock
    def test_400(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('countries.json')
        with as_file(source) as countries_json:
            mocked_route_countries = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/countries',
                response_status_code=400,
                response_json=json.loads(countries_json.read_text(encoding='utf-8'))
            )

        with self.assertRaises(exceptions.ProxyRackException):
            with RetryClient() as client:
                proxyrack_api.GetCountries.call(client=client)

        self.assertEqual(mocked_route_countries.call_count, 1)


class CitiesTests(BaseTestFixture):
    """
        Cities Tests
    """

    @respx.mock
    def test_ok(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('cities.json')
        with as_file(source) as cities_json:
            mocked_route_cities = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/cities',
                response_status_code=200,
                response_json=json.loads(cities_json.read_text(encoding='utf-8'))
            )

        with RetryClient() as client:
            r_cities = proxyrack_api.GetCities.call(client=client)

        self.assertEqual(len(r_cities.cities), 82)
        self.assertEqual(mocked_route_cities.call_count, 1)

    @respx.mock
    def test_400(self):
        source = test_const.TEST_RESOURCE_PATH.joinpath('cities.json')
        with as_file(source) as cities_json:
            mocked_route_cities = self.create_route(
                method='GET',
                url__eq='http://api.proxyrack.net/cities',
                response_status_code=400,
                response_json=json.loads(cities_json.read_text(encoding='utf-8'))
            )

        with self.assertRaises(exceptions.ProxyRackException):
            with RetryClient() as client:
                proxyrack_api.GetCities.call(client=client)

        self.assertEqual(mocked_route_cities.call_count, 1)


class CountryIPCountTests(BaseTestFixture):
    """
        Cities Tests
    """

    @respx.mock
    def test_ok(self):
        mocked_route_ip_count = self.create_route(
            method='GET',
            url__eq='http://api.proxyrack.net/countries/US/count',
            response_status_code=200,
            response_text='152'
        )

        with RetryClient() as client:
            r_country_ip_count = proxyrack_api.GetCountryIPCount.call(client=client, country='US')
            self.assertEqual(r_country_ip_count, '152')

        self.assertEqual(mocked_route_ip_count.call_count, 1)

    @respx.mock
    def test_400(self):
        mocked_route_ip_count = self.create_route(
            method='GET',
            url__eq='http://api.proxyrack.net/countries/US/count',
            response_status_code=400,
            response_text='152'
        )

        with self.assertRaises(exceptions.ProxyRackException):
            with RetryClient() as client:
                proxyrack_api.GetCountryIPCount.call(client=client, country='US')

        self.assertEqual(mocked_route_ip_count.call_count, 1)
