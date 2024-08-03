from py_aws_core import logs
from py_aws_core.db_dynamo import get_db_client
from py_aws_core.db_session import SessionDBAPI

logger = logs.logger
db_client = get_db_client()


def rehydrate_session_from_database(client):
    session_id = client.session_id
    logger.info(f'Session ID: {session_id} -> Rehydrating session...')
    r_session = SessionDBAPI.GetSessionQuery.call(db_client=db_client, _id=session_id)
    if not r_session.sessions:
        logger.info(f'Session ID: {session_id} -> No prior session found.')
        return
    client.b64_decode_and_set_cookies(b64_cookies=r_session.session_b64_cookies)
    logger.info(f'Session ID: {session_id} -> Rehydrated {len(client.cookies.jar)} cookies')


def write_session_to_database(client):
    session_id = client.session_id
    logger.info(f'Session ID: {session_id} -> Writing cookies to database...')
    b64_cookies = client.b64_encoded_cookies
    c_maps = [SessionDBAPI.build_session_map(_id=client.session_id, b64_cookies=b64_cookies)]
    db_client.write_maps_to_db(item_maps=c_maps)
    logger.info(f'Session ID: {session_id} -> Wrote cookies to database')
